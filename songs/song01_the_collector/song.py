"""The Collector — bai 1, DNA: "Taxman" (D Mixolydian, khong co V chord).

Gimmick: bass ostinato rang cua 1 bar + stab D major/minor + cymbal slash,
tang dan do day (tambourine -> cowbell -> be "Collector!" 3 giong).
"""
from __future__ import annotations

import numpy as np

from nhaccu._core import T, nn, buf
from nhaccu._dsp import SR
from nhaccu.drums import Kit, Performer, bar_drums, merge
from nhaccu.guitar.fuzz import fuzz
from nhaccu.guitar.jangle import jangle
from nhaccu.guitar.leadgtr import leadgtr
from nhaccu.bass.natbass import natbass
from nhaccu.voice import lead, vharm, gang, falsetto_stack, spoken

from songs._engine import Song, Track, audit, audit_vocal_f0

# -------------------------------------------------------------- form marks --

B_COUNT = 0     # 1 bar  count-in
B_INTRO = 4     # 2 bars vamp
B_V1 = 12       # 13 bars (8 + 5)
B_V2 = 64       # 13 bars
B_BR = 116      # 9 bars bridge
B_SOLO = 152    # 13 bars (verse = guitar solo)
B_V4 = 204      # 14 bars (refrain mo rong voi F)
B_OUT = 260     # 6 bars fade
END = 284

SCALE_DMIXO = {2, 4, 6, 7, 9, 11, 0}     # D E F# G A B C
ALLOW = {'F2', 'F3', 'F4'}               # F-natural cho chord F (outro)
# not mau cho phep tren downbeat (mixo b7 / sus4 / added-6 kieu Beatles)
TENSIONS = {2: {0, 4, 9}, 0: {9}, 7: {9}, 5: {}}

CHORDS = []
for _v in (B_V1, B_V2, B_SOLO):
    CHORDS += [(_v + 0, _v + 32, [2, 6, 9], 'D'),
               (_v + 32, _v + 40, [0, 4, 7], 'C'),
               (_v + 40, _v + 44, [7, 11, 2], 'G'),
               (_v + 44, _v + 52, [2, 6, 9], 'D')]
CHORDS += [(B_BR + 0, B_BR + 12, [2, 6, 9], 'D'),
           (B_BR + 12, B_BR + 16, [0, 4, 7], 'C'),
           (B_BR + 16, B_BR + 28, [2, 6, 9], 'D'),
           (B_BR + 28, B_BR + 36, [0, 4, 7], 'C')]
CHORDS += [(B_V4 + 0, B_V4 + 32, [2, 6, 9], 'D'),
           (B_V4 + 32, B_V4 + 40, [0, 4, 7], 'C'),
           (B_V4 + 40, B_V4 + 44, [7, 11, 2], 'G'),
           (B_V4 + 44, B_V4 + 48, [2, 6, 9], 'D'),
           (B_V4 + 48, B_V4 + 56, [5, 9, 0], 'F'),
           (B_V4 + 56, B_V4 + 60, [2, 6, 9], 'D')]
CHORDS += [(B_OUT, B_OUT + 24, [2, 6, 9], 'D')]

# ------------------------------------------------------------- lyrics/cells --

V1_LYR = [
    (0, "he comes a round on a mon day night"),
    (8, "count ing ev ry can dle burn ing bright"),
    (16, "he takes a num ber for ev ry name"),
    (24, "and files it a way in a gold en frame"),
]
V2_LYR = [
    (0, "you can hide your mon ey in the floor"),
    (8, "he will find it knock ing at your door"),
    (16, "you can bur y sil ver in the sand"),
    (24, "he will dig it up with his bare hands"),
]
V4_LYR = [
    (0, "he came a round on a mon day night"),
    (8, "and left me noth ing but a can dle light"),
    (16, "he knows the hours I let slip by"),
    (24, "he knows the truth be hind the lie"),
]

# mantra giai dieu quanh A-C (pentatonic, nhan flat 7) — 4 cau, moi cau 1 day
V1_N = [
    ['A3', 'A3', 'A3', 'G3', 'A3', 'C4', 'A3', 'G3', 'A3', 'A3', 'A3', 'G3', 'A3', 'C4', 'A3', 'G3'],
    ['C4', 'A3', 'G3', 'A3', 'C4', 'A3', 'A3', 'G3', 'A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'A3', 'G3'],
    ['A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'A3', 'A3', 'A3', 'A3', 'G3', 'A3', 'C4', 'A3', 'A3', 'D4'],
    ['A3', 'A3', 'A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'A3', 'A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'D4'],
]
V2_N = [
    ['A3', 'A3', 'A3', 'G3', 'A3', 'C4', 'A3', 'G3', 'A3', 'A3', 'A3', 'G3', 'A3', 'C4', 'A3', 'G3'],
    ['C4', 'A3', 'G3', 'A3', 'C4', 'A3', 'A3', 'G3', 'A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'A3', 'G3'],
    ['A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'A3', 'A3', 'A3', 'A3', 'G3', 'A3', 'C4', 'A3', 'A3', 'D4'],
    ['A3', 'A3', 'A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'A3', 'A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'D4'],
]
V4_N = [
    ['A3', 'A3', 'A3', 'G3', 'A3', 'C4', 'A3', 'G3', 'A3', 'A3', 'A3', 'G3', 'A3', 'C4', 'A3', 'G3'],
    ['C4', 'A3', 'G3', 'A3', 'C4', 'A3', 'A3', 'G3', 'A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'A3', 'G3'],
    ['A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'A3', 'A3', 'A3', 'A3', 'G3', 'A3', 'C4', 'A3', 'A3', 'D4'],
    ['A3', 'A3', 'A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'A3', 'A3', 'A3', 'A3', 'A3', 'C4', 'C4', 'D4'],
]


def _cells(base, lyric, notes4):
    cells = []
    for k, (off, line) in enumerate(lyric):
        words = line.split()
        b = base + off
        # cau 1-3: day dac 2 bars; cau cuoi ket som cho stab chiem beat 15-16
        span = 15 if off == 24 else 16
        n = len(words)
        step = span / n
        nt = notes4[k]
        for i, w in enumerate(words):
            d = step * (1.6 if i == n - 1 else 1.0)
            cells.append((b + i * step, d, nt[i % len(nt)], w, 1.0))
    return cells


def _refrain(base):
    # C(8) G(4) D(8) — 20 beats, dung theo Taxman (flat-VII IV I)
    return [
        (base + 0, 1.0, 'A3', 'here', 1.0), (base + 1, 1.0, 'A3', 'comes', 1.0),
        (base + 2, 1.0, 'G3', 'the', 1.0), (base + 3, 0.75, 'A3', 'col', 1.0),
        (base + 3.75, 0.75, 'C4', 'lec', 1.0), (base + 4.5, 2.0, 'A3', 'tor', 1.0),
        (base + 6.5, 1.5, 'C4', 'now', 1.0),
        (base + 8, 1.0, 'B3', 'he', 1.0), (base + 9, 1.0, 'A3', 'takes', 1.0),
        (base + 10, 1.0, 'G3', 'what', 1.0), (base + 11, 1.0, 'A3', 'he', 1.0),
        (base + 12, 3.0, 'D4', 'wants', 1.0),
        (base + 16, 1.0, 'A3', 'no', 1.0), (base + 17, 1.0, 'F#3', 'noth', 1.0),
        (base + 18, 1.0, 'A3', 'ing', 1.0), (base + 19, 3.0, 'D3', 'left', 1.0),
    ]


def _refrain_final(base):
    # C(8) G(4) D(4) F(8) D(4) — outro Taxman: flat-III bat ngo
    return [
        (base + 0, 1.0, 'A3', 'here', 1.0), (base + 1, 1.0, 'A3', 'comes', 1.0),
        (base + 2, 1.0, 'G3', 'the', 1.0), (base + 3, 0.75, 'A3', 'col', 1.0),
        (base + 3.75, 0.75, 'C4', 'lec', 1.0), (base + 4.5, 2.0, 'A3', 'tor', 1.0),
        (base + 6.5, 1.5, 'C4', 'now', 1.0),
        (base + 8, 1.0, 'B3', 'he', 1.0), (base + 9, 1.0, 'A3', 'takes', 1.0),
        (base + 10, 1.0, 'G3', 'what', 1.0), (base + 11, 1.0, 'A3', 'he', 1.0),
        (base + 12, 3.0, 'D4', 'wants', 1.0),
        (base + 16, 1.0, 'A3', 'no', 1.0), (base + 17, 1.0, 'A3', 'noth', 1.0),
        (base + 18, 1.0, 'A3', 'ing', 1.0), (base + 19, 2.0, 'F3', 'left', 1.0),
        (base + 21, 1.0, 'A3', 'at', 1.0), (base + 22, 3.0, 'C4', 'all', 1.0),
        (base + 25, 1.0, 'A3', 'the', 1.0), (base + 26, 0.75, 'F#3', 'col', 1.0),
        (base + 26.75, 0.75, 'A3', 'lec', 1.0), (base + 27.5, 2.5, 'D3', 'tor', 1.0),
    ]


def _bridge(base):
    return [
        (base + 0, 0.5, 'C4', 'he', 1.0), (base + 0.5, 0.5, 'A3', 'does', 1.0),
        (base + 1, 0.5, 'C4', 'not', 1.0), (base + 1.5, 0.5, 'D4', 'take', 1.0),
        (base + 2, 0.5, 'C4', 'the', 1.0), (base + 2.5, 0.5, 'A3', 'things', 1.0),
        (base + 3, 1.5, 'C4', 'you', 1.0), (base + 4.5, 2.5, 'A3', 'buy', 1.0),
        (base + 8, 0.5, 'C4', 'he', 1.0), (base + 8.5, 0.5, 'A3', 'on', 1.0),
        (base + 9, 0.5, 'C4', 'ly', 1.0), (base + 9.5, 0.5, 'D4', 'takes', 1.0),
        (base + 10, 0.5, 'C4', 'the', 1.0), (base + 10.5, 0.5, 'A3', 'time', 1.0),
        (base + 11, 1.5, 'C4', 'gone', 1.0), (base + 12.5, 3.5, 'A3', 'by', 1.0),
        (base + 16, 0.5, 'C4', 'he', 1.0), (base + 16.5, 0.5, 'A3', 'does', 1.0),
        (base + 17, 0.5, 'C4', 'not', 1.0), (base + 17.5, 0.5, 'D4', 'want', 1.0),
        (base + 18, 0.5, 'C4', 'your', 1.0), (base + 18.5, 0.5, 'A3', 'gold', 1.0),
        (base + 19, 0.5, 'C4', 'or', 1.0), (base + 19.5, 2.5, 'A3', 'land', 1.0),
        (base + 24, 0.5, 'C4', 'he', 1.0), (base + 24.5, 0.5, 'A3', 'on', 1.0),
        (base + 25, 0.5, 'C4', 'ly', 1.0), (base + 25.5, 0.5, 'D4', 'wants', 1.0),
        (base + 26, 0.5, 'C4', 'the', 1.0), (base + 26.5, 0.5, 'A3', 'hour', 1.0),
        (base + 27, 0.5, 'C4', 'glass', 1.0), (base + 27.5, 3.5, 'A3', 'sand', 1.0),
    ]


# ------------------------------------------------------------- arrangements --

OST = {2: ['D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'C2'],
       0: ['C2', 'C2', 'C2', 'C2', 'C2', 'C2', 'C2', 'C2'],
       7: ['G2', 'G2', 'G2', 'G2', 'G2', 'G2', 'G2', 'G2'],
       5: ['F2', 'F2', 'F2', 'F2', 'F2', 'F2', 'F2', 'F2']}
_OV = [1.0, 0.62, 0.95, 0.66, 0.88, 0.70, 1.0, 0.82]

STAB_MAJ = ['D3', 'F#3', 'A3', 'C4']
STAB_MIN = ['D3', 'F3', 'A3', 'C4']


class Collector(Song):
    name = 'song01_the_collector'
    bpm = 132
    beats = END
    human = 7
    laid = 0.0

    # ------------------------------------------------------------ bass ----
    def _bass(self, tr):
        def chord_at(beat):
            for s, e, p, sy in CHORDS:
                if s <= beat < e:
                    return p[0]
            return 2
        for bar in range(0, END, 4):
            pc = chord_at(bar)
            notes = OST[pc]
            for i, m in enumerate(notes):
                off = bar + i * 0.5
                t0 = T(off)
                natbass(tr.b, t0, m, 0.5, g=0.30 * _OV[i])

    # ------------------------------------------------------------ drums ----
    def _drums(self, tr):
        kit = Kit(seed=7)
        P = Performer(kit, T(END) + 4, seed=11)
        rock = {'K': 'K...K...K...K...',
                'S': '....S.......S...',
                'H': 'H.hH.hH.hH.hH'}
        for bar in range(B_INTRO, B_OUT + 20, 4):
            pat = dict(rock)
            # cymbal slash + stab dong bo o dau moi cap bar le
            if (bar - B_INTRO) % 8 == 0 and B_INTRO <= bar < B_V4:
                P.CR(bar, 0, v=0.8)
                pat = merge(pat, {'K': 'K...K...K...K.K.'})
            # fill nhe cuoi moi 4-bar phrase (giu nang luong)
            if B_INTRO <= bar < B_OUT and (bar - B_INTRO) % 16 == 12:
                P.roll(bar + 3.25, 0.75, 0.25, 0.30, 0.55)
            if bar == B_BR - 4 or bar == B_SOLO - 4 or bar == B_V4 - 4:
                P.roll(bar + 14, 2.0, 0.25, 0.3, 0.6)
            bar_drums(P, bar, pat, vh=0.45, ktune=44.0)
        # tambourine tu verse 2, cowbell tu solo verse
        for bar in range(B_V2, B_BR, 2):
            P.TB(bar + 0.0, 0, 0.55); P.TB(bar + 1.0, 4, 0.5)
            P.TB(bar + 2.0, 8, 0.55); P.TB(bar + 3.0, 12, 0.5)
        for bar in range(B_BR, B_V4, 2):
            P.ST(bar + 0.5, 2, 0.6, tune=620, damp=3.0)
            P.ST(bar + 2.5, 10, 0.55, tune=620, damp=3.0)
        for bar in range(B_V4, B_OUT, 2):
            P.TB(bar + 0.0, 0, 0.5); P.TB(bar + 1.0, 4, 0.5)
            P.ST(bar + 0.5, 2, 0.5, tune=620, damp=3.0)
        P.apply_chokes()
        for v in P.bus.values():
            v = np.asarray(v).ravel()
            n = min(len(tr.b), len(v))
            tr.b[:n] += v[:n]

    # ------------------------------------------------------------ guitar ---
    def _stabs(self, tr, from_bar, to_bar):
        """Stab D major/minor o dau bar 2,4,6,8 (obbligato spaces)."""
        alt = False
        for bar in range(from_bar, to_bar, 8):
            for k in (4, 16, 20, 28):
                b0 = bar + k
                if b0 >= to_bar:
                    continue
                ch = STAB_MIN if alt else STAB_MAJ
                alt = not alt
                for j, m in enumerate(ch):
                    fuzz(tr.b, T(b0) + j * 0.008, m, 0.35, g=0.10)

    def _rhythm(self, tr):
        for bar in range(B_INTRO, B_OUT + 20, 4):
            for i in range(8):
                jangle(tr.b, T(bar + i * 0.5), 'D3', 0.3, g=0.075)

    def _solo(self, tr):
        """Modal run kieu Paul trong Taxman: nhanh, bent, vi quanh mixo."""
        run = ['D4', 'E4', 'F#4', 'G4', 'A4', 'B4', 'C5', 'D5',
               'C5', 'A4', 'G4', 'F#4', 'E4', 'D4', 'E4', 'C4',
               'D4', 'E4', 'G4', 'A4', 'C5', 'D5', 'E5', 'C5',
               'A4', 'G4', 'A4', 'F#4', 'D4', 'E4', 'F#4', 'A4']
        base = B_SOLO
        for bar in range(0, 28, 4):
            for i, m in enumerate(run):
                if bar + i * 0.5 >= 28:
                    break
                leadgtr(tr.b, T(base + bar + i * 0.5), m, 0.42, g=0.24)
        # giu giong len nua sau: doubling ostinato +12
        for bar in range(B_V4, B_OUT, 4):
            for i, m in enumerate(['D4', 'D4', 'D4', 'D4', 'D4', 'D4', 'D4', 'C4']):
                leadgtr(tr.b, T(bar + i * 0.5), m, 0.4, g=0.20)

    # ------------------------------------------------------------ vocals ----
    def _vocals(self, tracks):
        lead_tr = Track('lead', pan=0.0, gain=1.0, verb=0.12, vocal=True,
                        squash=True)
        adt_tr = Track('lead_adt', pan=0.35, gain=0.5, verb=0.12, vocal=True)
        bv_tr = Track('backing', pan=-0.35, gain=0.9, verb=0.10, vocal=True)

        v1 = _cells(B_V1, V1_LYR, V1_N)
        v2 = _cells(B_V2, V2_LYR, V2_N)
        v4 = _cells(B_V4, V4_LYR, V4_N)
        r1 = _refrain(B_V1 + 32)
        r2 = _refrain(B_V2 + 32)
        r4 = _refrain_final(B_V4 + 32)
        br = _bridge(B_BR)

        for cells, seed in ((v1, 1), (v2, 2), (v4, 3), (r1, 4), (r2, 5), (r4, 6), (br, 7)):
            lead(lead_tr.b, 0, cells, g=0.26, seed=seed)
            lead(adt_tr.b, 0, cells, g=0.13, seed=seed + 40)

        # be "the Col lec tor" 3 giong (solo verse + final verse)
        tag = [(0, 0.5, 'D4', 'the', 1.0), (0.5, 0.5, 'D4', 'col', 1.0),
               (1, 0.5, 'C4', 'lec', 1.0), (1.5, 1.5, 'D4', 'tor', 1.0)]
        gang(bv_tr.b, B_SOLO + 4, tag, g=0.10, n=4)
        gang(bv_tr.b, B_V4 + 4, tag, g=0.10, n=4)
        gang(bv_tr.b, B_V4 + 12, tag, g=0.10, n=4)
        # falsetto "ha ha" o obbligato spaces verse solo
        ha = [(0, 0.5, 'D4', 'ha', 1.0), (0.5, 0.5, 'D4', 'ha', 0.9)]
        falsetto_stack(bv_tr.b, B_SOLO + 20, ha, g=0.045, n=2, transpose=12)
        falsetto_stack(bv_tr.b, B_SOLO + 28, ha, g=0.045, n=2, transpose=12)

        # count-in noi cham
        ct = [(0, 0.6, 'D3', 'one', 1.0), (0.7, 0.6, 'C#3', 'two', 1.0),
              (1.4, 0.6, 'C3', 'three', 1.0), (2.1, 1.4, 'B2', 'four', 1.0)]
        spoken(lead_tr.b, 0, ct, g=0.20)

        tracks += [lead_tr, adt_tr, bv_tr]

        # -------------------------------------------------- audit ----
        all_v = v1 + r1 + v2 + r2 + br + v4 + r4
        for cells, lb in ((all_v, 'vocal'),):
            probs = audit(cells, CHORDS, SCALE_DMIXO, lb, allow=ALLOW,
                          tensions=TENSIONS)
            for p in probs:
                print('  [AUDIT]', p)
        probs, n_ok = audit_vocal_f0(all_v, lead_tr.b, 'lead-f0', None)
        print('  [F0] kiem tra %d not hat, %d van de' % (n_ok, len(probs)))
        for p in probs:
            print('  [F0]', p)
        # bass audit
        bass_cells = []
        for bar in range(0, END, 4):
            pc = 2
            for s, e, p, sy in CHORDS:
                if s <= bar < e:
                    pc = p[0]
                    break
            for i, m in enumerate(OST[pc]):
                bass_cells.append((bar + i * 0.5, 0.5, m, 1.0))
        probs = audit(bass_cells, CHORDS, SCALE_DMIXO, 'bass', allow=ALLOW,
                      bass=True)
        for p in probs:
            print('  [AUDIT]', p)

    # ------------------------------------------------------------- build ----
    def build(self, tracks, vocal=True):
        bass_tr = Track('bass', pan=0.0, gain=1.0, verb=0.05)
        drum_tr = Track('drums', pan=0.0, gain=1.0, verb=0.12)
        gtr_tr = Track('guitars', pan=-0.3, gain=1.0, verb=0.10)
        gtr2_tr = Track('guitars2', pan=0.3, gain=0.85, verb=0.10)

        self._bass(bass_tr)
        self._drums(drum_tr)
        self._stabs(gtr_tr, B_INTRO, B_V4)
        self._rhythm(gtr_tr)
        self._solo(gtr2_tr)
        tracks += [bass_tr, drum_tr, gtr_tr, gtr2_tr]
        if vocal:
            self._vocals(tracks)
