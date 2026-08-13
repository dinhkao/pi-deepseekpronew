"""Sunshower Sunday — bai 8, DNA: "Good Day Sunshine" (A major, V-of-V).

Gimmick: intro E open-fifth 4-to-the-bar co hoc, refrain B-F# (V-of-V chain!)
voi accent 3+3+2, verse A F#7 B7 E7 A, piano solo pivot sang D major, coda
F7 LEN NUA CUNG + vocal cascading echoes, snare triplet "rat-ta-ta-tat".
"""
from __future__ import annotations

import numpy as np

from nhaccu._core import T, buf
from nhaccu._dsp import SR
from nhaccu.drums import Kit, Performer, bar_drums
from nhaccu.guitar.jangle import jangle
from nhaccu.bass.natbass import natbass
from nhaccu.keys.piano import piano
from nhaccu.voice import lead, vharm

from songs._engine import Song, Track, audit, audit_vocal_f0

# -------------------------------------------------------------- form marks --

B_INTRO = 0     # 4 bars E open fifth
B_R1 = 16       # 6 bars
B_V1 = 40       # 8 bars
B_R2 = 72       # 6 bars
B_V2 = 96       # 8 bars (half 2 = piano solo in D)
B_R3 = 128      # 6 bars
B_V3 = 152      # 8 bars
B_R4 = 184      # 6 bars
B_R5 = 208      # 6 bars (double refrain)
B_OUT = 232     # 8 bars F7 cascade
END = 264

REFR_CH = [(0, 4, [11, 3, 6], 'B'), (4, 4, [6, 10, 1], 'F#'),
           (8, 4, [11, 3, 6], 'B'), (12, 4, [6, 10, 1], 'F#'),
           (16, 8, [4, 8, 11, 2], 'E7')]
VERSE_CH = [(0, 4, [9, 1, 4], 'A'), (4, 4, [6, 10, 1, 4], 'F#7'),
            (8, 4, [11, 3, 6, 9], 'B7'), (12, 4, [4, 8, 11, 2], 'E7'),
            (16, 4, [9, 1, 4], 'A'), (20, 4, [6, 10, 1, 4], 'F#7'),
            (24, 4, [11, 3, 6, 9], 'B7'), (28, 4, [4, 8, 11, 2], 'E7')]
SOLO_CH = [(0, 4, [9, 1, 4], 'A'), (4, 4, [6, 10, 1, 4], 'F#7'),
           (8, 4, [11, 3, 6, 9], 'B7'), (12, 4, [4, 8, 11, 2], 'E7'),
           (16, 4, [2, 6, 9], 'D'), (20, 4, [7, 11, 2], 'G'),
           (24, 4, [9, 1, 4, 7], 'A7'), (28, 4, [2, 6, 9], 'D')]

CHORDS = [(B_INTRO, B_INTRO + 16, [4, 8, 11, 2], 'E')]
for br in (B_R1, B_R2, B_R3, B_R4, B_R5):
    CHORDS += [(br + s, br + e, p, sy) for s, e, p, sy in REFR_CH]
CHORDS += [(B_V1 + s, B_V1 + e, p, sy) for s, e, p, sy in VERSE_CH]
CHORDS += [(B_V2 + s, B_V2 + e, p, sy) for s, e, p, sy in SOLO_CH]
CHORDS += [(B_V3 + s, B_V3 + e, p, sy) for s, e, p, sy in VERSE_CH]
CHORDS += [(B_OUT, B_OUT + 32, [5, 9, 0, 3], 'F7')]

SCALE_A = {9, 11, 1, 2, 4, 6, 8}       # A B C# D E F# G#
ALLOW = {'A#3', 'A#4', 'D#4', 'D#5', 'F4', 'F5', 'C4', 'C5', 'Eb4', 'Eb5'}
TENSIONS = {11: {1}, 6: {8}, 4: {9, 6}, 9: {11}, 2: {9, 11, 4}, 7: {9},
            5: {2, 4}}


# ------------------------------------------------------------- lyrics/cells --

def _refrain(b0):
    return [
        (b0 + 0, 0.75, 'F#4', 'sun', 1.0), (b0 + 0.75, 0.5, 'E4', 'show', 1.0),
        (b0 + 1.25, 0.5, 'D#4', 'er', 1.0), (b0 + 1.75, 0.75, 'C#4', 'sun', 1.0),
        (b0 + 2.5, 2.0, 'D#4', 'day', 1.0),
        (b0 + 4.5, 0.5, 'C#4', 'sun', 1.0), (b0 + 5, 0.5, 'B3', 'show', 1.0),
        (b0 + 5.5, 0.5, 'C#4', 'er', 1.0), (b0 + 6, 0.75, 'D#4', 'sun', 1.0),
        (b0 + 6.75, 2.0, 'C#4', 'day', 1.0),
        (b0 + 9, 0.75, 'F#4', 'sun', 1.0), (b0 + 9.75, 0.5, 'E4', 'show', 1.0),
        (b0 + 10.25, 0.5, 'D#4', 'er', 1.0), (b0 + 10.75, 0.75, 'C#4', 'sun', 1.0),
        (b0 + 11.5, 2.0, 'D#4', 'day', 1.0),
        (b0 + 13.5, 0.5, 'C#4', 'sun', 1.0), (b0 + 14, 0.5, 'B3', 'show', 1.0),
        (b0 + 14.5, 0.5, 'C#4', 'er', 1.0), (b0 + 15, 0.75, 'D#4', 'sun', 1.0),
        (b0 + 15.75, 2.0, 'C#4', 'day', 1.0),
        (b0 + 18, 0.75, 'E4', 'and', 1.0), (b0 + 18.75, 0.5, 'D4', 'the', 1.0),
        (b0 + 19.25, 0.5, 'C#4', 'rain', 1.0), (b0 + 19.75, 0.5, 'B3', 'goes', 1.0),
        (b0 + 20.25, 0.5, 'C#4', 'a', 1.0), (b0 + 20.75, 3.0, 'D4', 'way', 1.0),
    ]


def _verse(b0):
    c1 = [(b0 + 0, 0.5, 'A4', 'she', 1.0), (b0 + 0.5, 0.5, 'G#4', 'wakes', 1.0),
          (b0 + 1, 0.5, 'A4', 'the', 1.0), (b0 + 1.5, 0.5, 'G#4', 'town', 1.0),
          (b0 + 2, 0.5, 'A4', 'with', 1.0), (b0 + 2.5, 0.5, 'B4', 'a', 1.0),
          (b0 + 3, 1.5, 'C#5', 'song', 1.0)]
    c2 = [(b0 + 8, 0.5, 'B4', 'and', 1.0), (b0 + 8.5, 0.5, 'A4', 'the', 1.0),
          (b0 + 9, 0.5, 'B4', 'song', 1.0), (b0 + 9.5, 0.5, 'A4', 'says', 1.0),
          (b0 + 10, 0.5, 'B4', 'come', 1.0), (b0 + 10.5, 0.5, 'G#4', 'a', 1.0),
          (b0 + 11, 1.5, 'B4', 'long', 1.0)]
    c3 = [(b0 + 16, 0.5, 'A4', 'she', 1.0), (b0 + 16.5, 0.5, 'G#4', 'wakes', 1.0),
          (b0 + 17, 0.5, 'A4', 'the', 1.0), (b0 + 17.5, 0.5, 'G#4', 'town', 1.0),
          (b0 + 18, 0.5, 'A4', 'with', 1.0), (b0 + 18.5, 0.5, 'B4', 'a', 1.0),
          (b0 + 19, 1.5, 'C#5', 'song', 1.0)]
    c4 = [(b0 + 24, 0.5, 'B4', 'ev', 1.0), (b0 + 24.5, 0.5, 'A4', 'ry', 1.0),
          (b0 + 25, 0.5, 'B4', 'one', 1.0), (b0 + 25.5, 0.5, 'A4', 'is', 1.0),
          (b0 + 26, 0.5, 'B4', 'sing', 1.0), (b0 + 26.5, 0.5, 'G#4', 'ing', 1.0),
          (b0 + 27, 0.5, 'A4', 'a', 1.0), (b0 + 27.5, 1.5, 'E4', 'long', 1.0)]
    return c1 + c2 + c3 + c4


def _outro(b0):
    # F7 cascade: 3 giong lech nhau 2 beats, nho dan
    base = [(0, 0.75, 'F4', 'sun', 1.0), (0.75, 0.5, 'Eb4', 'show', 1.0),
            (1.25, 0.5, 'D4', 'er', 1.0), (1.75, 0.75, 'C4', 'sun', 1.0),
            (2.5, 2.0, 'D4', 'day', 1.0)]
    cells = []
    for rep, shift in enumerate((0, 2, 4)):
        for off, d, m, syl, v in base:
            cells.append((b0 + rep * 8 + off + shift, d, m, syl,
                          [1.0, 0.55, 0.3][rep] * v))
    return cells


class SunshowerSunday(Song):
    name = 'song08_sunshower_sunday'
    bpm = 120
    beats = END
    human = 12
    laid = 0.0

    def _bass(self, tr):
        def nb(t0, m, d, g=0.30):
            natbass(tr.b, T(t0), m, d, g=g)
        for br in (B_R1, B_R2, B_R3, B_R4, B_R5):
            for k, m in enumerate(['B2', 'F#2', 'B2', 'F#2', 'E2', 'E2']):
                nb(br + k * 4, m, 3.6)
        for bv, ch in ((B_V1, VERSE_CH), (B_V3, VERSE_CH)):
            for s, e, p, sy in ch:
                nb(bv + s, ['A2', 'F#2', 'B2', 'E2'][[9, 6, 11, 4].index(p[0])],
                   e - s - 0.3)
        for s, e, p, sy in SOLO_CH:
            nb(B_V2 + s, ['A2', 'F#2', 'B2', 'E2', 'D2', 'G2', 'A2', 'D2']
               [[9, 6, 11, 4, 2, 7, 9, 2].index(p[0])], e - s - 0.3)
        for k in range(8):
            nb(B_OUT + k * 4, 'F2', 3.6)

    def _drums(self, tr):
        kit = Kit(seed=7)
        P = Performer(kit, T(END) + 4, seed=41)
        beat = {'K': 'K...K...K...K...',
                'S': '....S.......S...',
                'H': 'H.hH.hH.hH.hH'}
        for br in (B_R1, B_R2, B_R3, B_R4, B_R5):
            for bar in range(br, br + 24, 4):
                bar_drums(P, bar, beat, vh=0.48)
        for bv in (B_V1, B_V2, B_V3):
            for bar in range(bv, bv + 32, 4):
                bar_drums(P, bar, beat, vh=0.45)
        # snare triplet "rat-ta-ta-tat" cuoi bar 2/4 cua refrain (tu R2)
        for br in (B_R2, B_R3, B_R4, B_R5):
            for off in (6, 14):
                P.roll(br + off, 0.5, 0.1667, 0.35, 0.6)
        # intro: chi hat + kick mem (mechanical E 4-to-bar la piano)
        for bar in range(B_INTRO, B_INTRO + 16, 4):
            P.H(bar, 0, 0.3); P.H(bar + 1, 4, 0.25)
            P.H(bar + 2, 8, 0.3); P.H(bar + 3, 12, 0.25)
        for bar in range(B_OUT, B_OUT + 32, 4):
            P.CR(bar, 0, v=0.6)
        P.apply_chokes()
        for v in P.bus.values():
            v = np.asarray(v).ravel()
            n = min(len(tr.b), len(v))
            tr.b[:n] += v[:n]

    def _piano_gtr(self, tr_p, tr_j):
        # intro: E open fifth, 4-to-the-bar co hoc (Pollack: "mechanical")
        for bar in range(B_INTRO, B_INTRO + 16, 4):
            for k in range(4):
                m = ['E2', 'B2', 'E2', 'B2'][k]
                piano(tr_p.b, T(bar + k), m, ring=1.2, g=0.13)
        # piano solo o nua sau verse 2 (pivot D major)
        solo = ['D5', 'C#5', 'B4', 'A4', 'G4', 'F#4', 'E4', 'D4',
                'D4', 'E4', 'F#4', 'G4', 'A4', 'B4', 'C#5', 'D5',
                'D5', 'C#5', 'B4', 'C#5', 'A4', 'B4', 'C#5', 'A4',
                'F#4', 'G4', 'A4', 'F#4', 'D4', 'E4', 'F#4', 'A4']
        for i, m in enumerate(solo):
            piano(tr_p.b, T(B_V2 + 16 + i * 0.5), m, ring=1.5, g=0.12)
        # jangle chords
        for bv in (B_V1, B_V2, B_V3):
            for bar in range(bv, bv + 32, 4):
                for k in range(4):
                    jangle(tr_j.b, T(bar + k), 'A3', 0.4, g=0.055)
        for br in (B_R1, B_R2, B_R3, B_R4, B_R5):
            for k in range(6):
                jangle(tr_j.b, T(br + k * 4), 'B3', 0.4, g=0.055)
        for bar in range(B_OUT, B_OUT + 32, 4):
            for k in range(4):
                jangle(tr_j.b, T(bar + k), 'F3', 0.4, g=0.05)

    def _vocals(self, tracks):
        lead_tr = Track('lead', pan=0.0, gain=1.0, verb=0.14, vocal=True,
                        squash=True)
        bv_tr = Track('backing', pan=-0.3, gain=0.8, verb=0.12, vocal=True)

        r1 = _refrain(B_R1)
        r2 = _refrain(B_R2)
        r3 = _refrain(B_R3)
        r4 = _refrain(B_R4)
        r5 = _refrain(B_R5)
        v1 = _verse(B_V1)
        v3 = _verse(B_V3)
        out = _outro(B_OUT)

        for cells, seed in ((r1, 1), (v1, 2), (r2, 3), (r3, 4), (v3, 5),
                            (r4, 6), (r5, 7), (out, 8)):
            lead(lead_tr.b, 0, cells, g=0.24, seed=seed)
        # cascading echoes: backing tham gia outro
        for rep, shift in enumerate((1, 2)):
            cells = [(B_OUT + rep * 8 + off + shift, d, m, syl,
                      0.4 * v) for off, d, m, syl, v in
                     [(0, 0.75, 'F4', 'sun', 1.0), (0.75, 0.5, 'Eb4', 'show', 1.0),
                      (1.25, 0.5, 'D4', 'er', 1.0), (1.75, 0.75, 'C4', 'sun', 1.0),
                      (2.5, 2.0, 'D4', 'day', 1.0)]]
            vharm(bv_tr.b, 0, cells, intervals=(0,), g=0.05, seed=61)

        tracks += [lead_tr, bv_tr]

        # --------------------------------------------------- audit ----
        all_v = r1 + v1 + r2 + r3 + v3 + r4 + r5 + out
        probs = audit(all_v, CHORDS, SCALE_A, 'vocal', allow=ALLOW,
                      tensions=TENSIONS)
        for p in probs:
            print('  [AUDIT]', p)
        probs, n_ok = audit_vocal_f0(all_v, lead_tr.b, 'lead-f0', None)
        print('  [F0] kiem tra %d not hat, %d van de' % (n_ok, len(probs)))
        for p in probs:
            print('  [F0]', p)

    def build(self, tracks, vocal=True):
        bass_tr = Track('bass', pan=0.0, gain=1.0, verb=0.08)
        drum_tr = Track('drums', pan=0.0, gain=1.0, verb=0.12)
        pno_tr = Track('piano', pan=-0.3, gain=1.0, verb=0.16)
        jag_tr = Track('jangle', pan=0.3, gain=0.9, verb=0.1)

        self._bass(bass_tr)
        self._drums(drum_tr)
        self._piano_gtr(pno_tr, jag_tr)
        tracks += [bass_tr, drum_tr, pno_tr, jag_tr]
        if vocal:
            self._vocals(tracks)
