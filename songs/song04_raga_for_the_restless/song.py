"""Raga for the Restless — bai 4, DNA: "Love You To" (C Dorian drone, An Do).

Gimmick: drone C + tanpura + tabla (nhac cu tu _sitar.py), KHONG drum kit,
khong bass guitar, nhịp 3/4 chen vao giua 4/4 (lead-in + refrain bar 4),
intro out-of-tempo voi glissando sitar, call-and-response sitar, tambourine
tu verse 2 (Ringo trong LYT).
"""
from __future__ import annotations

import numpy as np

from nhaccu._core import T, buf
from nhaccu._dsp import SR
from nhaccu.drums import Kit, Performer
from nhaccu.voice import lead

from songs._sitar import sitar, tanpura, tabla
from songs._engine import Song, Track, audit, audit_vocal_f0

# -------------------------------------------------------------- form marks --
# verse = 8 bars 4/4 + lead-in 3/4 + 4/4 (39 beats) — dung nhip le cua LYT
# refrain = 4+4+4+3+4+4 (23 beats, bar 4 la 3/4)
B_INTRO = 0     # 16 out-of-tempo
B_V1 = 16       # 39
B_R1 = 55       # 23
B_V2 = 78       # 39
B_R2 = 117      # 23
B_SOLO = 140    # 40
B_V3 = 180      # 39
B_R3 = 219      # 23
B_OUT = 242     # 32
END = 274

CHORDS = []


def _vch(bv, end):
    # drone C, nghieng ve Bb o cuoi (flat-VII cua LYT)
    CHORDS.append((bv, bv + 24, [0, 4, 7], 'C'))
    CHORDS.append((bv + 24, bv + 28, [10, 2, 5], 'Bb'))
    CHORDS.append((bv + 28, end, [0, 4, 7], 'C'))


for bv in (B_V1, B_V2, B_V3):
    _vch(bv, bv + 39)
for br in (B_R1, B_R2, B_R3):
    CHORDS.append((br, br + 16, [0, 4, 7], 'C'))
    CHORDS.append((br + 16, br + 20, [10, 2, 5], 'Bb'))
    CHORDS.append((br + 20, br + 23, [0, 4, 7], 'C'))
CHORDS += [(B_SOLO, B_SOLO + 32, [0, 4, 7], 'C'),
           (B_SOLO + 32, B_SOLO + 40, [10, 2, 5], 'Bb'),
           (B_OUT, B_OUT + 32, [0, 4, 7], 'C')]

SCALE_CDOR = {0, 2, 3, 5, 7, 9, 10}     # C D Eb F G A Bb
ALLOW = set()
TENSIONS = {0: {3, 10, 2}, 10: {}}       # Eb (b3 dorian), Bb, D (9th)


# ------------------------------------------------------------- lyrics/cells --

def _verse(b0, lines, tail):
    cells = []
    for k, line in enumerate(lines):
        words = line.split()
        base = b0 + k * 8
        n = len(words)
        step = 7.5 / n
        for i, w in enumerate(words):
            d = step * (1.8 if i == n - 1 else 1.0)
            cells.append((base + i * step, d, None, w, 1.0))
    cells.append((b0 + 30, 1.5, 'C4', tail, 1.0))
    return cells


def _mel(k, i, n):
    # quanh G4 (5th - "high center of gravity" cua LYT), Eb4 mau dorian
    rows = [
        ['G4', 'G4', 'G4', 'F4', 'G4', 'F4', 'Eb4', 'F4', 'G4', 'F4', 'Eb4'],
        ['G4', 'F4', 'G4', 'F4', 'Eb4', 'D4', 'Eb4', 'F4', 'G4', 'F4', 'Eb4'],
        ['G4', 'F4', 'G4', 'F4', 'Eb4', 'F4', 'G4', 'F4', 'Eb4', 'D4', 'D4'],
        ['G4', 'F4', 'G4', 'F4', 'Eb4', 'D4', 'Eb4', 'D4', 'Eb4', 'D4', 'D4'],
    ]
    r = rows[k]
    return r[i % len(r)]


def _verse_cells(b0, lines, tail):
    cells = []
    for k, line in enumerate(lines):
        words = line.split()
        base = b0 + k * 8
        n = len(words)
        step = 7.5 / n
        for i, w in enumerate(words):
            d = step * (1.8 if i == n - 1 else 1.0)
            cells.append((base + i * step, d, _mel(k, i, n), w, 1.0))
    cells.append((b0 + 30, 1.5, 'C4', tail, 1.0))
    return cells


V1_LYR = [
    "the mind is a riv er that nev er stands still",
    "it runs through the night and it runs through the hill",
    "no hand can hold it and no wall can dam",
    "it runs to the sea as the sea runs dry",
]
V2_LYR = [
    "the bod y is a tem ple with bells that won't chime",
    "it waits for a hand that is keep ing no time",
    "the bells are all rust ed the ropes are all frayed",
    "the tem ple still stands though the god has strayed",
]
V3_LYR = [
    "the world is a wheel that is turn ing too fast",
    "it spins through the fu ture and in to the past",
    "the spokes are all brok en the rim is all bent",
    "the wheel keeps on turn ing it nev er relents",
]


def _refrain(b0):
    return [
        (b0 + 0, 1.0, 'G4', 'rest', 1.0), (b0 + 1, 1.0, 'Eb4', 'less', 1.0),
        (b0 + 2, 2.0, 'D4', 'rest', 1.0), (b0 + 4, 1.0, 'C4', 'less', 1.0),
        (b0 + 5, 2.0, 'C4', 'rest', 1.0), (b0 + 7, 1.0, 'Eb4', 'less', 1.0),
        # bar 3-4 (12-16): sitar response hook (instrumental)
        # Bb (flat-VII): chi dung chord tones Bb D F
        (b0 + 16, 1.0, 'F4', 'no', 1.0), (b0 + 17, 1.0, 'D4', 'one', 1.0),
        (b0 + 18, 1.0, 'F4', 'can', 1.0), (b0 + 19, 1.0, 'D4', 'hold', 1.0),
        (b0 + 20, 1.0, 'D4', 'the', 1.0), (b0 + 21, 1.5, 'Eb4', 'riv', 1.0),
        (b0 + 22.5, 1.5, 'C4', 'er', 1.0),
    ]


# sitar hook (Pollack: motif C D Eb D C Bb (slide) C)
def _sitar_hook(b, t0, g=0.16, seed=3):
    sitar(b, t0, 'C4', 0.4, g=g, seed=seed)
    sitar(b, t0 + 0.12, 'D4', 0.35, g=g * 0.9, seed=seed + 1)
    sitar(b, t0 + 0.24, 'Eb4', 0.35, g=g * 0.9, seed=seed + 2)
    sitar(b, t0 + 0.36, 'D4', 0.3, g=g * 0.85, seed=seed + 3)
    sitar(b, t0 + 0.48, 'C4', 0.3, g=g * 0.85, seed=seed + 4)
    sitar(b, t0 + 0.60, 'Bb3', 0.5, g=g * 0.9, seed=seed + 5, gl=40)
    sitar(b, t0 + 0.78, 'C4', 1.2, g=g, seed=seed + 6)


SOLO_NOTES = ['C4', 'D4', 'Eb4', 'G4', 'F4', 'Eb4', 'D4', 'C4',
              'Bb3', 'C4', 'D4', 'Eb4', 'F4', 'G4', 'F4', 'Eb4',
              'D4', 'Eb4', 'C4', 'D4', 'Eb4', 'G4', 'Bb4', 'A4',
              'G4', 'F4', 'Eb4', 'D4', 'C4', 'Bb3', 'C4', 'D4',
              'Eb4', 'C4', 'D4', 'Eb4', 'F4', 'Eb4', 'D4', 'C4']


class RagaForTheRestless(Song):
    name = 'song04_raga_for_the_restless'
    bpm = 104
    beats = END
    human = 6
    laid = 0.008

    def _drone(self, tr):
        # tanpura cycle: Pa sa sa Sa -> G2 C3 C3 C2 (C drone, open fifth)
        for beat in range(0, END, 4):
            note = ['C3', 'G2', 'C3', 'C2'][(beat // 4) % 4]
            tanpura(tr.b, T(beat), note, 5.5, g=0.10, seed=(beat // 4) % 7)
        # open-fifth drone phu: C2+G2 rat nhe (tanpura khong co 3rd)
        for beat in range(B_V1, END, 16):
            sitar(tr.b, T(beat), 'C2', 14.0, g=0.05, seed=11)

    def _tabla(self, tr):
        # teentaal-ish: ge o dau moi 4, na o moi beat, te o giua
        on = False
        for beat in range(B_V1, END):
            if B_SOLO <= beat < B_SOLO + 40:
                on = True
            if B_R1 <= beat < B_R1 + 23 or B_R2 <= beat < B_R2 + 23 \
                    or B_R3 <= beat < B_R3 + 23:
                on = True
            if B_V1 <= beat < B_V1 + 39 or B_V2 <= beat < B_V2 + 39 \
                    or B_V3 <= beat < B_V3 + 39:
                on = True
            if B_OUT <= beat < B_OUT + 16:
                on = True
            if B_INTRO <= beat < B_V1:
                on = False
            if not on:
                continue
            if beat % 4 == 0:
                tabla(tr.b, T(beat), 'ge', g=0.24, seed=beat)
            if beat % 4 == 1:
                tabla(tr.b, T(beat), 'na', g=0.30, seed=beat)
            if beat % 4 == 2:
                tabla(tr.b, T(beat), 'te', g=0.22, seed=beat)
            if beat % 4 == 3:
                tabla(tr.b, T(beat), 'na', g=0.26, seed=beat)
            if beat % 8 == 6:
                tabla(tr.b, T(beat + 0.5), 'na', g=0.18, seed=beat + 99)

    def _tamb(self, tr):
        kit = Kit(seed=7)
        P = Performer(kit, T(END) + 4, seed=31)
        for beat in range(B_V2, B_OUT):
            if beat % 2 == 0:
                P.TB(beat, 0, 0.4)
        P.apply_chokes()
        for v in P.bus.values():
            v = np.asarray(v).ravel()
            n = min(len(tr.b), len(v))
            tr.b[:n] += v[:n]

    def _sitar_parts(self, tr):
        # intro out-of-tempo: glissando + noodle (Pollack: 11-not C major
        # scale xuong, F# red herring, C Dorian motif)
        for k, m in enumerate(['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4',
                               'C5', 'B4', 'A4', 'G4', 'F4', 'E4', 'D4',
                               'C4', 'G3']):
            sitar(tr.b, T(B_INTRO) + k * 0.09, m, 0.3, g=0.11, seed=k,
                  gl=25 if k in (0, 7) else 0)
        _sitar_hook(tr.b, T(B_INTRO + 2.5) + 0.6)
        _sitar_hook(tr.b, T(B_INTRO + 4.0) + 1.0)
        # hooks o lead-in va refrain (call-and-response)
        for bv in (B_V1, B_V2, B_V3):
            _sitar_hook(tr.b, T(bv + 32) + 0.1, seed=7)      # lead-in 3/4
            _sitar_hook(tr.b, T(bv + 35) + 0.1, seed=8)      # lead-in 4/4
        for br in (B_R1, B_R2, B_R3):
            _sitar_hook(tr.b, T(br + 12) + 0.1, seed=9)      # bar 3
            _sitar_hook(tr.b, T(br + 15) + 0.1, seed=10)     # bar 4 (3/4)
        # solo: ornate, irrational groupings, glides
        for i, m in enumerate(SOLO_NOTES):
            beat = B_SOLO + i * 1.0
            gl = 30 if i % 6 == 0 else 0
            sitar(tr.b, T(beat), m, 0.75, g=0.13, seed=i, gl=gl)
        # outro noodle fade
        for i, m in enumerate(SOLO_NOTES[:16]):
            sitar(tr.b, T(B_OUT + i * 0.9), m, 0.7, g=0.10, seed=i + 50,
                  gl=25 if i % 5 == 0 else 0)
        _sitar_hook(tr.b, T(B_OUT + 16) + 0.2, seed=14)
        _sitar_hook(tr.b, T(B_OUT + 20) + 0.4, seed=15, g=0.12)

    def _vocals(self, tracks):
        lead_tr = Track('lead', pan=0.0, gain=1.0, verb=0.18, vocal=True,
                        squash=True)
        v1 = _verse_cells(B_V1, V1_LYR, 'ah')
        v2 = _verse_cells(B_V2, V2_LYR, 'ah')
        v3 = _verse_cells(B_V3, V3_LYR, 'ah')
        r1 = _refrain(B_R1)
        r2 = _refrain(B_R2)
        r3 = _refrain(B_R3)
        for cells, seed in ((v1, 1), (v2, 2), (v3, 3), (r1, 4), (r2, 5),
                            (r3, 6)):
            lead(lead_tr.b, 0, cells, g=0.24, seed=seed)
        tracks += [lead_tr]

        # --------------------------------------------------- audit ----
        all_v = v1 + r1 + v2 + r2 + v3 + r3
        probs = audit(all_v, CHORDS, SCALE_CDOR, 'vocal', allow=ALLOW,
                      tensions=TENSIONS)
        for p in probs:
            print('  [AUDIT]', p)
        probs, n_ok = audit_vocal_f0(all_v, lead_tr.b, 'lead-f0', None)
        print('  [F0] kiem tra %d not hat, %d van de' % (n_ok, len(probs)))
        for p in probs:
            print('  [F0]', p)

    def build(self, tracks, vocal=True):
        drone_tr = Track('tanpura', pan=-0.3, gain=1.0, verb=0.22)
        tab_tr = Track('tabla', pan=0.25, gain=1.0, verb=0.14)
        sit_tr = Track('sitar', pan=0.1, gain=1.0, verb=0.24)
        tamb_tr = Track('tambourine', pan=-0.2, gain=0.9, verb=0.12)

        self._drone(drone_tr)
        self._tabla(tab_tr)
        self._sitar_parts(sit_tr)
        self._tamb(tamb_tr)
        tracks += [drone_tr, tab_tr, sit_tr, tamb_tr]
        if vocal:
            self._vocals(tracks)
