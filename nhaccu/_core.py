"""Timeline, buffers, note names, and the humanizer.

The whole library is beat-based: `T(beat)` maps a beat position to seconds
through a tempo map, so a song can change tempo mid-bar without any of the
instrument code knowing about it.  Meters are handled by the *arrangement*
(you simply phrase in the right number of beats), which is what lets a bar of
7/8 sit next to a bar of 4/4 without special cases.
"""
from __future__ import annotations

import numpy as np

from ._dsp import SR

# --------------------------------------------------------------- tempo map --

TEMPO = [(0, 400, 120, 120)]      # (beat_start, beat_end, bpm_start, bpm_end)
_gb = None
_ct = None
TOTAL = None


def _bpm(b):
    for s, e, b0, b1 in TEMPO:
        if s <= b < e:
            return b0 + (b1 - b0) * (b - s) / max(e - s, 1e-9)
    return TEMPO[-1][3]


def configure(bpm0=120, bpm1=120, end=400):
    """Single tempo ramp from bpm0 to bpm1 over `end` beats."""
    return configure_map([(0, end, bpm0, bpm1)], end)


def configure_map(segs, end):
    """Multi-segment tempo map. segs = [(beat0, beat1, bpm0, bpm1), ...]

    Real tempo changes, not feel changes -- `The New Sound` does both, and
    they need to be different things.
    """
    global TEMPO, _gb, _ct, TOTAL
    TEMPO = list(segs)
    _gb = np.arange(0, end + 2, 0.004)
    _ct = np.concatenate([[0], np.cumsum(np.array([60.0 / _bpm(b) for b in _gb]) * 0.004)[:-1]])
    TOTAL = T(end) + 4
    return TOTAL


def T(b):
    """Beat -> seconds."""
    return float(np.interp(b, _gb, _ct))


def SPB(b):
    return 60.0 / _bpm(b)


def dur(b0, b1):
    """Seconds between two beat positions (never negative or zero)."""
    return max(T(b1) - T(b0), 0.02)


# ------------------------------------------------------------------ pitch ---

_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def _nn_str(s):
    n = _PC[s[0].upper()]
    i = 1
    while i < len(s) and s[i] in '#b':
        n += 1 if s[i] == '#' else -1
        i += 1
    return 12 * (int(s[i:]) + 1) + n


def nn(s):
    """'Bb3' or 58 -> MIDI number. Accepts either, everywhere."""
    if isinstance(s, (int, np.integer)):
        return int(s)
    if isinstance(s, float):
        return int(round(s))
    return _nn_str(s)


def hz(m):
    return 440.0 * 2 ** ((nn(m) - 69) / 12)


# ---------------------------------------------------------------- buffers ---

def buf():
    return np.zeros(int(TOTAL * SR) + SR)


def put(b, t0, x, g=1.0):
    """Sum a rendered signal into a stem at time t0 (seconds)."""
    i = int(t0 * SR)
    if i < 0:
        x = x[-i:]
        i = 0
    n = min(len(x), len(b) - i)
    if n > 0:
        b[i:i + n] += x[:n] * g
    return i


# --------------------------------------------------------------- humanize ---

class Hum:
    """Per-track feel: a FIXED offset per position-in-bar (a player's habit,
    repeating every bar) plus small Gaussian noise, plus metric accenting.

    `on=0` gives you a machine, which is occasionally what you want.
    """

    def __init__(self, seed=1, sig=0.0070, gsig=0.055, grid=16, laid=0.0):
        R = np.random.default_rng(seed)
        self.grid = grid
        self.sys = {p: float(R.normal(0, 0.0032)) for p in range(grid)}
        self.R = np.random.default_rng(seed + 77)
        self.sig = sig
        self.gsig = gsig
        self.on = 1.0
        self.laid = laid           # + = behind the beat, - = on top of it
        self.acc = [1.00, 0.52, 0.74, 0.60, 0.88, 0.52, 0.72, 0.62,
                    0.95, 0.52, 0.74, 0.60, 0.90, 0.55, 0.72, 0.66]

    def _pos(self, beat, bar_beats=4):
        return int(round((beat % bar_beats) * 4)) % self.grid

    def t(self, beat, bar_beats=4):
        p = self._pos(beat, bar_beats)
        late = 0.0035 if (p % 4 == 0) else (0.0055 if p % 4 == 3 else -0.0020)
        return T(beat) + (self.sys[p] + float(self.R.normal(0, self.sig))
                          + late + self.laid) * self.on

    def g(self, base, beat, arc=1.0, bar_beats=4):
        p = self._pos(beat, bar_beats)
        return base * self.acc[p % 16] * arc * (1 + float(self.R.normal(0, self.gsig)) * self.on)

    def flat(self):
        """A copy with metric accenting disabled (for held pads/strings)."""
        h = Hum(1)
        h.acc = [1.0] * 16
        h.sys = self.sys
        h.R = self.R
        h.sig = self.sig
        h.gsig = self.gsig * 0.4
        h.on = self.on
        return h


HUM = Hum()


def set_hum(h):
    global HUM
    HUM = h
    return h


# ------------------------------------------------------------------ swing ---

def swing8(beat, amt=0.0):
    """Push the off-beat eighth late. amt=0.66 -> triplet shuffle."""
    if amt <= 0:
        return beat
    f = beat - np.floor(beat)
    if abs(f - 0.5) < 1e-6:
        return np.floor(beat) + (0.5 + 0.5 * amt * 0.34 if amt < 0.6 else 2.0 / 3.0)
    return beat


def swing16(beat, amt=0.0):
    """Sixteenth-note swing -- the samba/partido-alto lilt."""
    if amt <= 0:
        return beat
    f = beat - np.floor(beat)
    for base in (0.0, 0.5):
        if abs(f - (base + 0.25)) < 1e-6:
            return np.floor(beat) + base + 0.25 + 0.25 * amt * 0.30
    return beat


# ------------------------------------------------------------- note players --

def play(fn, b_, bar0, cells, g=0.10, sw=0.0, gate=0.95, oct_=0,
         bar_beats=4, hum=None, **kw):
    """cells = [(offset_beats, dur_beats, note[, velocity]), ...]"""
    H = hum or HUM
    for c in cells:
        off, d, note = c[0], c[1], c[2]
        v = c[3] if len(c) > 3 else 1.0
        bt = swing8(bar0 + off, sw)
        t0 = H.t(bt, bar_beats)
        d2 = max((T(swing8(bar0 + off + d, sw)) - T(bt)) * gate, 0.045)
        fn(b_, t0, nn(note) + 12 * oct_, d2, g=H.g(g, bar0 + off, bar_beats=bar_beats) * v, **kw)


def play_ch(fn, b_, bar0, cells, g=0.07, sw=0.0, gate=0.95, bar_beats=4,
            hum=None, **kw):
    """For instruments that take a LIST of notes (organ, pad, choir, horns)."""
    H = hum or HUM
    for c in cells:
        off, d, notes = c[0], c[1], c[2]
        v = c[3] if len(c) > 3 else 1.0
        bt = swing8(bar0 + off, sw)
        t0 = H.t(bt, bar_beats)
        d2 = max((T(swing8(bar0 + off + d, sw)) - T(bt)) * gate, 0.05)
        fn(b_, t0, [nn(x) for x in notes], d2,
           g=H.g(g, bar0 + off, bar_beats=bar_beats) * v, **kw)


def hold(fn, b_, beat0, beats, notes, g=0.06, **kw):
    """A single sustained chord, straight on the grid (no humanizing)."""
    t0 = T(beat0)
    d = T(beat0 + beats) - t0
    fn(b_, t0, [nn(x) for x in np.atleast_1d(notes)], d, g=g, **kw)
