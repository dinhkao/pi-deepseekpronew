"""Perpetual Motion — bai 9, DNA: "And Your Bird Can Sing" + "For No One".

Gimmick: riff baroque perpetual-motion even-8ths (2 guitar quang 3/6 song
song), bridge chromatic descending bass G#-G-F#-F-E, doan HORN SOLO kieu
For No One (french horn + tack piano chat + walking bass) o vi (C#m),
ending IV 6/4 (A/E) bat ngo.
"""
from __future__ import annotations

import numpy as np

from nhaccu._core import T, buf
from nhaccu._dsp import SR
from nhaccu.drums import Kit, Performer, bar_drums, merge
from nhaccu.guitar.jangle import jangle
from nhaccu.guitar.leadgtr import leadgtr
from nhaccu.guitar.crunch import crunch
from nhaccu.bass.natbass import natbass
from nhaccu.keys.tack import tack
from nhaccu.horns.horn import horn
from nhaccu.voice import lead, vharm

from songs._engine import Song, Track, audit, audit_vocal_f0

# -------------------------------------------------------------- form marks --

B_INTRO = 0     # 4 bars riff
B_V1 = 16       # 8 bars
B_V2 = 48       # 8 bars
B_BR1 = 80      # 8 bars
B_SOLO = 112    # 8 bars (riff over verse, V thay IV)
B_HORN = 144    # 8 bars For-No-One horn section (C#m)
B_V3 = 176      # 8 bars
B_BR2 = 208     # 8 bars
B_SOLO2 = 240   # 8 bars
B_OUT = 272     # 4 bars riff + IV6/4 ending
END = 288

VERSE_CH = [(0, 16, [4, 8, 11], 'E'), (16, 4, [6, 9, 1], 'F#m'),
            (20, 4, [9, 1, 4], 'A'), (24, 8, [4, 8, 11], 'E')]
BRIDGE_CH = [(0, 16, [8, 11, 3], 'G#m'), (16, 4, [4, 8, 11], 'E'),
             (20, 8, [6, 9, 1], 'F#m'), (28, 4, [11, 3, 6], 'B')]
HORN_CH = [(0, 4, [1, 4, 8], 'C#m'), (4, 4, [8, 0, 3], 'G#'),
           (8, 8, [1, 4, 8], 'C#m'), (16, 4, [8, 0, 3], 'G#'),
           (20, 4, [1, 4, 8], 'C#m'), (24, 4, [6, 9, 1], 'F#'),
           (28, 4, [8, 0, 3], 'G#')]
SOLO_CH = [(0, 16, [4, 8, 11], 'E'), (16, 4, [6, 9, 1], 'F#m'),
           (20, 4, [11, 3, 6], 'B'), (24, 8, [4, 8, 11], 'E')]

CHORDS = [(B_INTRO, B_INTRO + 16, [4, 8, 11], 'E')]
for bv in (B_V1, B_V2, B_V3):
    CHORDS += [(bv + s, bv + e, p, sy) for s, e, p, sy in VERSE_CH]
for bb in (B_BR1, B_BR2):
    CHORDS += [(bb + s, bb + e, p, sy) for s, e, p, sy in BRIDGE_CH]
CHORDS += [(B_HORN + s, B_HORN + e, p, sy) for s, e, p, sy in HORN_CH]
for bs in (B_SOLO, B_SOLO2):
    CHORDS += [(bs + s, bs + e, p, sy) for s, e, p, sy in SOLO_CH]
CHORDS += [(B_OUT, B_OUT + 12, [4, 8, 11], 'E'),
           (B_OUT + 12, B_OUT + 16, [4, 9, 1], 'A/E')]

SCALE_E = {4, 6, 8, 9, 11, 1, 3}       # E F# G# A B C# D#
ALLOW = {'C4', 'C5', 'B#3', 'B#4'}     # B# = C cua hop am G# (horn)
TENSIONS = {4: {1, 9}, 6: {11, 1}, 9: {11}, 8: {4}, 11: {1}, 1: {2, 6}}


# ------------------------------------------------------------ baroque riff --

RIF1 = ['E4', 'F#4', 'G#4', 'F#4', 'E4', 'F#4', 'G#4', 'F#4',
        'E4', 'G#4', 'B4', 'G#4', 'F#4', 'G#4', 'B4', 'G#4',
        'A4', 'G#4', 'F#4', 'E4', 'F#4', 'G#4', 'A4', 'G#4',
        'B4', 'A4', 'G#4', 'F#4', 'E4', 'D#4', 'E4', 'F#4']
# giong 2: quang 3 diatonic len (parallel sixths/tenths kieu AYBCS)
_SCALE_E_NOTES = ['E4', 'F#4', 'G#4', 'A4', 'B4', 'C#5', 'D#5', 'E5',
                  'F#5', 'G#5', 'A5']


def _riff(b, t0, g=0.10, hi=False):
    for i, m in enumerate(RIF1):
        if hi:
            try:
                idx = _SCALE_E_NOTES.index(m) + 2
                m = _SCALE_E_NOTES[min(idx, len(_SCALE_E_NOTES) - 1)]
            except ValueError:
                m = 'F#4'   # D#4 -> F#4 (3rd diatonic)
        jangle(b, T(t0) + i * 0.5, m, 0.4, g=g)
        leadgtr(b, T(t0) + i * 0.5, m, 0.38, g=g * 0.8)


# ------------------------------------------------------------- lyrics/cells --

def _verse(b0, lines):
    cells = []
    for k, line in enumerate(lines):
        words = line.split()
        base = b0 + k * 8
        n = len(words)
        step = 7.0 / n
        for i, w in enumerate(words):
            d = step * (1.8 if i == n - 1 else 1.0)
            cells.append((base + i * step, d, None, w, 1.0))
    return cells


V_LYR = [
    "you tell me you have heard it all",
    "ev ry sound and ev ry call",
    "but you don't hear me",
    "you can see me walk ing out the door",
]
V2_LYR = [
    "you tell me that you know the score",
    "ev ry game and ev ry war",
    "but you don't hear me",
    "I've been stand ing here since half past four",
]
V3_LYR = [
    "you tell me you have seen it all",
    "ev ry rise and ev ry fall",
    "but you don't hear me",
    "and your bird is sing ing through it all",
]


def _mel_v(k, i, n):
    rows = [
        ['B3', 'C#4', 'B3', 'C#4', 'B3', 'C#4', 'B3', 'C#4', 'B3'],
        ['B3', 'C#4', 'B3', 'C#4', 'B3', 'C#4', 'B3'],
        ['C#4', 'B3', 'C#4', 'A3', 'F#3'],
        ['B3', 'C#4', 'B3', 'C#4', 'B3', 'C#4', 'B3', 'A3', 'B3'],
    ]
    r = rows[k]
    return r[i % len(r)]


def _verse_cells(b0, lines):
    cells = []
    for k, line in enumerate(lines):
        words = line.split()
        base = b0 + k * 8
        n = len(words)
        step = 7.0 / n
        for i, w in enumerate(words):
            d = step * (1.8 if i == n - 1 else 1.0)
            cells.append((base + i * step, d, _mel_v(k, i, n), w, 1.0))
    return cells


def _bridge(b0):
    return [
        (b0 + 0, 0.5, 'D#4', 'if', 1.0), (b0 + 0.5, 0.5, 'E4', 'I', 1.0),
        (b0 + 1, 0.5, 'D#4', 'could', 1.0), (b0 + 1.5, 0.5, 'E4', 'fly', 1.0),
        (b0 + 2, 0.5, 'D#4', "I'd", 1.0), (b0 + 2.5, 0.5, 'E4', 'float', 1.0),
        (b0 + 3, 0.5, 'D#4', 'a', 1.0), (b0 + 3.5, 1.5, 'B3', 'way', 1.0),
        (b0 + 8, 0.5, 'B3', 'if', 1.0), (b0 + 8.5, 0.5, 'C#4', 'I', 1.0),
        (b0 + 9, 0.5, 'B3', 'could', 1.0), (b0 + 9.5, 0.5, 'C#4', 'sing', 1.0),
        (b0 + 10, 0.5, 'B3', "I'd", 1.0), (b0 + 10.5, 0.5, 'C#4', 'find', 1.0),
        (b0 + 11, 0.5, 'B3', 'the', 1.0), (b0 + 11.5, 1.5, 'G#3', 'key', 1.0),
        (b0 + 16, 0.5, 'B3', 'but', 1.0), (b0 + 16.5, 0.5, 'C#4', 'ev', 1.0),
        (b0 + 17, 0.5, 'B3', 'ry', 1.0), (b0 + 17.5, 0.5, 'C#4', 'note', 1.0),
        (b0 + 18, 0.5, 'B3', 'comes', 1.0), (b0 + 18.5, 0.5, 'C#4', 'back', 1.0),
        (b0 + 19, 0.5, 'B3', 'to', 1.0), (b0 + 19.5, 1.5, 'E4', 'me', 1.0),
    ]


HORN_MEL = [('E4', 1.0), ('G#4', 0.5), ('B4', 0.5), ('C#5', 1.0),
            ('G#4', 1.0), ('B4', 0.5), ('C#5', 0.5), ('D#5', 1.0),
            ('C#5', 0.5), ('B4', 0.5), ('G#4', 1.0), ('B4', 0.5),
            ('C#5', 0.5), ('G#4', 1.0), ('E4', 1.0), ('C#4', 1.0),
            ('E4', 0.5), ('G#4', 0.5), ('B4', 1.0), ('C#5', 1.0),
            ('B4', 0.5), ('C#5', 0.5), ('F#5', 1.0), ('E5', 1.0),
            ('C#5', 0.5), ('B4', 0.5), ('G#4', 0.5), ('B4', 0.5),
            ('C#5', 1.5)]


class PerpetualMotion(Song):
    name = 'song09_perpetual_motion'
    bpm = 138
    beats = END
    human = 13
    laid = 0.0

    def _bass(self, tr):
        def nb(t0, m, d, g=0.30):
            natbass(tr.b, T(t0), m, d, g=g)
        for bv in (B_V1, B_V2, B_V3):
            nb(bv, 'E2', 15.0)
            nb(bv + 16, 'F#2', 3.6); nb(bv + 20, 'A2', 3.6)
            nb(bv + 24, 'E2', 7.0)
        for bs in (B_SOLO, B_SOLO2):
            nb(bs, 'E2', 15.0)
            nb(bs + 16, 'F#2', 3.6); nb(bs + 20, 'B2', 3.6)
            nb(bs + 24, 'E2', 7.0)
        for bb in (B_BR1, B_BR2):
            # chromatic descending bass G# G F# F E (Pollack)
            for k, m in enumerate(['G#2', 'G2', 'F#2', 'F2']):
                nb(bb + k * 4, m, 3.6)
            nb(bb + 16, 'E2', 3.6)
            nb(bb + 20, 'F#2', 7.0); nb(bb + 28, 'B2', 3.6)
        # horn section: walking bass kieu For No One
        for k, m in enumerate(['C#2', 'G#2', 'C#2', 'C#2', 'G#2', 'C#2',
                               'F#2', 'G#2']):
            nb(B_HORN + k * 4, m, 3.4)
        nb(B_OUT, 'E2', 11.0)
        nb(B_OUT + 12, 'E2', 3.4)   # A/E: bass E (6/4 inversion!)

    def _drums(self, tr):
        kit = Kit(seed=7)
        P = Performer(kit, T(END) + 4, seed=45)
        rock = {'K': 'K...K...K...K...',
                'S': '....S.......S...',
                'H': 'H.hH.hH.hH.hH'}
        for bv in (B_V1, B_V2, B_V3):
            for bar in range(bv, bv + 32, 4):
                bar_drums(P, bar, rock, vh=0.5)
        for bs in (B_SOLO, B_SOLO2):
            for bar in range(bs, bs + 32, 4):
                bar_drums(P, bar, rock, vh=0.5)
        for bb in (B_BR1, B_BR2):
            for bar in range(bb, bb + 32, 4):
                bar_drums(P, bar, rock, vh=0.45)
                P.CL(bar, 0, 0.5); P.CL(bar + 2, 8, 0.5)
        for bar in range(B_HORN, B_HORN + 32, 4):
            bar_drums(P, bar, rock, vh=0.42)
            P.TB(bar, 0, 0.4); P.TB(bar + 1, 4, 0.4)
            P.TB(bar + 2, 8, 0.4); P.TB(bar + 3, 12, 0.4)
        for bar in range(B_INTRO, B_INTRO + 16, 4):
            bar_drums(P, bar, rock, vh=0.5)
        for bar in range(B_OUT, B_OUT + 16, 4):
            bar_drums(P, bar, rock, vh=0.5)
        P.roll(B_OUT + 15, 0.75, 0.25, 0.35, 0.6)
        P.apply_chokes()
        for v in P.bus.values():
            v = np.asarray(v).ravel()
            n = min(len(tr.b), len(v))
            tr.b[:n] += v[:n]

    def _guitars(self, tr_r, tr_c):
        # riff o intro, solos, outro
        for b0 in (B_INTRO, B_OUT):
            _riff(tr_r.b, b0, g=0.10)
            _riff(tr_c.b, b0, g=0.08, hi=True)
        for bs in (B_SOLO, B_SOLO2):
            for bar in range(0, 32, 8):
                for i in range(16):
                    m = RIF1[i % len(RIF1)]
                    leadgtr(tr_r.b, T(bs + bar + i * 0.5), m, 0.4, g=0.12)
        # rhythm crunch o verse + bridge
        for bv in (B_V1, B_V2, B_V3):
            for bar in range(bv, bv + 32, 4):
                for k in range(8):
                    crunch(tr_c.b, T(bar + k * 0.5), 'E3', 0.3, g=0.07)
        for bb in (B_BR1, B_BR2):
            for bar in range(bb, bb + 32, 4):
                for k in range(8):
                    crunch(tr_c.b, T(bar + k * 0.5), 'G#3', 0.3, g=0.065)

    def _horn_section(self, tr_h, tr_t):
        # french horn solo (For No One) + tack piano chat quarter
        t = B_HORN
        for m, d in HORN_MEL:
            horn(tr_h.b, T(t), m, d * 0.9, g=0.09, voice='frenchhorn',
                 art='legato', seed=int(t) % 7)
            t += d
        for bar in range(B_HORN, B_HORN + 32, 4):
            for k in range(4):
                tack(tr_t.b, T(bar + k), 'C#3', 0.3, g=0.055)
        for bar in range(B_HORN + 4, B_HORN + 32, 8):
            for k in range(4):
                tack(tr_t.b, T(bar + k), 'G#2', 0.3, g=0.05)

    def _vocals(self, tracks):
        lead_tr = Track('lead', pan=0.0, gain=1.0, verb=0.1, vocal=True,
                        squash=True)
        bv_tr = Track('backing', pan=-0.3, gain=0.8, verb=0.08, vocal=True)

        v1 = _verse_cells(B_V1, V_LYR)
        v2 = _verse_cells(B_V2, V2_LYR)
        v3 = _verse_cells(B_V3, V3_LYR)
        br1 = _bridge(B_BR1)
        br2 = _bridge(B_BR2)

        for cells, seed in ((v1, 1), (v2, 2), (br1, 3), (v3, 4), (br2, 5)):
            lead(lead_tr.b, 0, cells, g=0.24, seed=seed)
        # bold/italic backing o even phrases (Pollack)
        for cells in (v1, v2, v3):
            vharm(bv_tr.b, 0, cells, intervals=(-4,), g=0.06, seed=71)

        tracks += [lead_tr, bv_tr]

        # --------------------------------------------------- audit ----
        all_v = v1 + v2 + br1 + v3 + br2
        probs = audit(all_v, CHORDS, SCALE_E, 'vocal', allow=ALLOW,
                      tensions=TENSIONS)
        for p in probs:
            print('  [AUDIT]', p)
        probs, n_ok = audit_vocal_f0(all_v, lead_tr.b, 'lead-f0', None)
        print('  [F0] kiem tra %d not hat, %d van de' % (n_ok, len(probs)))
        for p in probs:
            print('  [F0]', p)

    def build(self, tracks, vocal=True):
        bass_tr = Track('bass', pan=0.0, gain=1.0, verb=0.06)
        drum_tr = Track('drums', pan=0.0, gain=1.0, verb=0.1)
        rif_tr = Track('riff', pan=-0.3, gain=1.0, verb=0.1)
        gtr_tr = Track('guitars', pan=0.3, gain=0.9, verb=0.08)
        hrn_tr = Track('horn', pan=0.15, gain=1.0, verb=0.2)
        tack_tr = Track('tack_piano', pan=-0.2, gain=0.9, verb=0.14)

        self._bass(bass_tr)
        self._drums(drum_tr)
        self._guitars(rif_tr, gtr_tr)
        self._horn_section(hrn_tr, tack_tr)
        tracks += [bass_tr, drum_tr, rif_tr, gtr_tr, hrn_tr, tack_tr]
        if vocal:
            self._vocals(tracks)
