"""Every Little Window — bai 5, DNA: "Here, There and Everywhere" (G major).

Gimmick: intro G-Bb-Am-D7 (flat-III cross-relation!), verse dung F#m7b5
(nua-diminished hiem), bridge deceptive sang Bb/Gm roi ve G nhu nang chieu,
be "ooh" block, finger snaps, outro plagal I-IV-I.
"""
from __future__ import annotations

import numpy as np

from nhaccu._core import T, buf, nn
from nhaccu._dsp import SR
from nhaccu.drums import Kit, Performer, bar_drums
from nhaccu.guitar.jangle import jangle
from nhaccu.guitar.leadgtr import leadgtr
from nhaccu.bass.natbass import natbass
from nhaccu.voice import lead, oohs

from songs._engine import Song, Track, audit, audit_vocal_f0

# -------------------------------------------------------------- form marks --

B_INTRO = 0     # 4 bars
B_V1 = 16       # 8 bars
B_V2 = 48       # 8 bars
B_BR1 = 80      # 6 bars
B_V3 = 104      # 8 bars
B_BR2 = 136     # 6 bars
B_V4 = 160      # 8 bars
B_OUT = 192     # 4 bars (plagal tag)
END = 208

CHORDS = []
CHORDS += [(0, 4, [7, 11, 2], 'G'), (4, 4, [10, 2, 5], 'Bb'),
           (8, 4, [9, 0, 4], 'Am'), (12, 4, [2, 6, 9, 0], 'D7')]
for bv in (B_V1, B_V2, B_V3, B_V4):
    CHORDS += [(bv + 0, 4, [7, 11, 2], 'G'), (bv + 4, 4, [0, 4, 7], 'C'),
               (bv + 8, 4, [7, 11, 2], 'G'), (bv + 12, 4, [0, 4, 7], 'C'),
               (bv + 16, 2, [6, 9, 0, 4], 'F#m7b5'),
               (bv + 18, 2, [11, 3, 6, 9], 'B7'),
               (bv + 20, 2, [6, 9, 0, 4], 'F#m7b5'),
               (bv + 22, 2, [11, 3, 6, 9], 'B7'),
               (bv + 24, 2, [4, 7, 11], 'Em'), (bv + 26, 2, [9, 0, 4], 'Am'),
               (bv + 28, 2, [0, 4, 7], 'C'), (bv + 30, 2, [2, 6, 9, 0], 'D7')]
for bb in (B_BR1, B_BR2):
    CHORDS += [(bb + 0, 4, [10, 2, 5], 'Bb'), (bb + 4, 4, [7, 10, 2], 'Gm'),
               (bb + 8, 4, [0, 3, 7], 'Cm'), (bb + 12, 4, [2, 6, 9, 0], 'D7'),
               (bb + 16, 4, [7, 10, 2], 'Gm'), (bb + 20, 4, [0, 3, 7], 'Cm'),
               (bb + 24, 8, [2, 6, 9, 0], 'D7')]
CHORDS += [(B_OUT, B_OUT + 4, [7, 11, 2], 'G'),
           (B_OUT + 4, B_OUT + 8, [0, 4, 7], 'C'),
           (B_OUT + 8, B_OUT + 16, [7, 11, 2], 'G')]

SCALE_G = {7, 9, 11, 0, 2, 4, 6}       # G A B C D E F#
ALLOW = {'Bb2', 'Bb3', 'Bb4', 'Eb3', 'Eb4', 'Eb5', 'D#4', 'D#5',
         'F2', 'F3', 'F4', 'F5'}   # bridge o Bb/Gm/Cm (F = 5th Bb, 7th Gm)
TENSIONS = {4: {6, 9}, 2: {9, 4}, 0: {2, 9}, 9: {11, 6}, 6: {11}, 11: {9},
            7: {11}}


# ------------------------------------------------------------- lyrics/cells --

V1_LYR = [
    "here in the light of the win dow pane",
    "here ev ry col our has a name",
    "watch ing the morn ing find ing its way",
    "through ev ry lit tle win dow",
]
V2_LYR = [
    "here where the dust floats in the sun",
    "here where the day has just be gun",
    "know ing your face will ap pear in the glass",
    "through ev ry lit tle win dow",
]
V3_LYR = [
    "here as the blue sky turns to grey",
    "here as the hours drift a way",
    "wait ing for you at the end of the day",
    "through ev ry lit tle win dow",
]
V4_LYR = [
    "here with your hand a gainst the pane",
    "here where the rain writes out your name",
    "tell ing the world that you will re main",
    "through ev ry lit tle win dow",
]


def _mel_c1(i, n):
    return ['G4', 'A4', 'B4', 'A4', 'G4', 'F#4', 'G4', 'E4'][i % 8]


def _mel_c2(i, n):
    return ['G4', 'A4', 'B4', 'A4', 'G4', 'F#4', 'G4', 'E4'][i % 8]


def _mel_c3(i, n):
    return ['A4', 'C5', 'A4', 'C5', 'A4', 'F#4', 'A4', 'F#4', 'A4', 'A4'][i % 10]


def _mel_c4(i, n):
    return ['G4', 'A4', 'B4', 'A4', 'G4', 'A4', 'E4', 'E4'][i % 8]


def _verse_cells(b0, lines):
    cells = []
    for k, line in enumerate(lines[:2]):
        words = line.split()
        base = b0 + k * 8
        cells.append((base, 2.0, 'D4', words[0], 1.0))
        rest = words[1:]
        n = len(rest)
        step = 5.0 / n
        mel = [_mel_c1(i, n) for i in range(n)]
        for i, w in enumerate(rest):
            d = step * (1.7 if i == n - 1 else 1.0)
            cells.append((base + 2.5 + i * step, d, mel[i], w, 1.0))
    for k, line in enumerate(lines[2:]):
        words = line.split()
        base = b0 + 16 + k * 8
        n = len(words)
        step = 7.0 / n
        mel = [_mel_c3(i, n) if k == 0 else _mel_c4(i, n) for i in range(n)]
        for i, w in enumerate(words):
            d = step * (1.8 if i == n - 1 else 1.0)
            cells.append((base + i * step, d, mel[i], w, 1.0))
    return cells


def _bridge(b0):
    return [
        (b0 + 0, 1.0, 'D4', 'ev', 1.0), (b0 + 1, 0.5, 'F4', 'ry', 1.0),
        (b0 + 1.5, 0.5, 'G4', 'lit', 1.0), (b0 + 2, 0.5, 'F4', 'tle', 1.0),
        (b0 + 2.5, 0.5, 'D4', 'win', 1.0), (b0 + 3, 0.5, 'F4', 'dow', 1.0),
        (b0 + 3.5, 1.5, 'D4', 'knows', 1.0),
        (b0 + 8, 1.0, 'Eb4', 'it', 1.0), (b0 + 9, 0.5, 'D4', 'knows', 1.0),
        (b0 + 9.5, 0.5, 'Eb4', 'that', 1.0), (b0 + 10, 0.5, 'D4', 'light', 1.0),
        (b0 + 10.5, 0.5, 'C4', 'is', 1.0), (b0 + 11, 0.5, 'D4', 'nev', 1.0),
        (b0 + 11.5, 0.5, 'Eb4', 'er', 1.0), (b0 + 12, 2.0, 'D4', 'far', 1.0),
        (b0 + 16, 1.0, 'Bb3', 'I', 1.0), (b0 + 17, 0.5, 'D4', 'love', 1.0),
        (b0 + 17.5, 0.5, 'G4', 'you', 1.0), (b0 + 18, 0.5, 'F4', 'here', 1.0),
        (b0 + 18.5, 0.5, 'D4', 'and', 1.0), (b0 + 19, 0.5, 'Eb4', 'ev', 1.0),
        (b0 + 19.5, 0.5, 'D4', 'ry', 1.0), (b0 + 20, 2.0, 'C4', 'where', 1.0),
        (b0 + 22, 2.0, 'D4', 'where', 1.0),
    ]


def _outro(b0):
    return [
        (b0 + 0, 2.0, 'G4', 'here', 1.0), (b0 + 2, 1.0, 'D4', 'there', 1.0),
        (b0 + 3, 0.5, 'C5', 'and', 1.0), (b0 + 3.5, 0.5, 'B4', 'ev', 1.0),
        (b0 + 4, 0.5, 'A4', 'ry', 1.0), (b0 + 4.5, 0.5, 'G4', 'lit', 1.0),
        (b0 + 5, 0.5, 'E4', 'tle', 1.0), (b0 + 5.5, 1.5, 'D4', 'win', 1.0),
        (b0 + 7, 1.5, 'C4', 'dow', 1.0),
    ]


class EveryLittleWindow(Song):
    name = 'song05_every_little_window'
    bpm = 86
    beats = END
    human = 8
    laid = 0.006

    def _bass(self, tr):
        def nb(t0, m, d, g=0.30):
            natbass(tr.b, T(t0), m, d, g=g)
        for bv in (B_V1, B_V2, B_V3, B_V4):
            for k, m in enumerate(['G2', 'C2', 'G2', 'C2']):
                nb(bv + k * 4, m, 3.6)
            # half-note walking nua sau verse (F# B F# B E A C D)
            for k, m in enumerate(['F#2', 'B2', 'F#2', 'B2', 'E2', 'A2',
                                   'C2', 'D2']):
                nb(bv + 16 + k * 2, m, 1.8)
        for bb in (B_BR1, B_BR2):
            for k, m in enumerate(['Bb2', 'G2', 'C2', 'D2', 'G2', 'C2', 'D2']):
                nb(bb + k * 4, m, 3.6)
        nb(B_OUT, 'G2', 3.6); nb(B_OUT + 4, 'C2', 3.6)
        nb(B_OUT + 8, 'G2', 7.0)

    def _drums(self, tr):
        kit = Kit(seed=7)
        P = Performer(kit, T(END) + 4, seed=17)
        soft = {'K': 'K...K...K...K...',
                'S': '....x.......x...',
                'H': 'H...H...H...H...'}
        for bar in range(B_V1, B_V4 + 32, 4):
            bar_drums(P, bar, soft, vk=0.62, vs=0.5, vh=0.3)
        for bb in (B_BR1, B_BR2):
            for bar in range(bb, bb + 32, 4):
                bar_drums(P, bar, soft, vk=0.55, vs=0.45, vh=0.28)
        # finger snaps verse cuoi + outro
        for beat in range(B_V4, B_V4 + 32, 4):
            P.CL(beat + 1, 4, 0.5); P.CL(beat + 3, 12, 0.5)
        for beat in range(B_OUT, B_OUT + 16, 2):
            P.CL(beat, 0, 0.45)
        P.apply_chokes()
        for v in P.bus.values():
            v = np.asarray(v).ravel()
            n = min(len(tr.b), len(v))
            tr.b[:n] += v[:n]

    def _guitars(self, tr_j, tr_l):
        # jangle chords nhe
        for bv in (B_V1, B_V2, B_V3, B_V4):
            for k in range(8):
                jangle(tr_j.b, T(bv + k * 4), 'G3', 0.5, g=0.05)
        for bb in (B_BR1, B_BR2):
            for k in range(8):
                jangle(tr_j.b, T(bb + k * 4), 'D3', 0.5, g=0.05)
        # lead guitar licks o bridge (selective double-track kieu HTAE)
        for bb in (B_BR1, B_BR2):
            for k, m in enumerate(['Bb3', 'D4', 'F4', 'G4', 'F4', 'D4',
                                   'Bb3', 'G3']):
                leadgtr(tr_l.b, T(bb + k * 2), m, 1.5, g=0.14)
                if k % 3 == 0:
                    leadgtr(tr_l.b, T(bb + k * 2) + 0.03, nn(m) + 12, 1.2,
                            g=0.08)

    def _vocals(self, tracks):
        lead_tr = Track('lead', pan=0.0, gain=1.0, verb=0.18, vocal=True,
                        squash=True)
        ooh_tr = Track('oohs', pan=-0.3, gain=0.9, verb=0.2, vocal=True)

        v1 = _verse_cells(B_V1, V1_LYR)
        v2 = _verse_cells(B_V2, V2_LYR)
        v3 = _verse_cells(B_V3, V3_LYR)
        v4 = _verse_cells(B_V4, V4_LYR)
        br1 = _bridge(B_BR1)
        br2 = _bridge(B_BR2)
        out = _outro(B_OUT)

        for cells, seed in ((v1, 1), (v2, 2), (v3, 3), (v4, 4), (br1, 5),
                            (br2, 6), (out, 7)):
            lead(lead_tr.b, 0, cells, g=0.23, seed=seed, style='soft')

        # "ooh" block harmonies tren nhung not dai (HTAE trademark)
        for cells in (v1, v2, v3, v4, br1, br2, out):
            oohs(ooh_tr.b, 0, cells, g=0.055, n=3, seed=41, style='soft')

        tracks += [lead_tr, ooh_tr]

        # --------------------------------------------------- audit ----
        all_v = v1 + v2 + br1 + v3 + br2 + v4 + out
        probs = audit(all_v, CHORDS, SCALE_G, 'vocal', allow=ALLOW,
                      tensions=TENSIONS)
        for p in probs:
            print('  [AUDIT]', p)
        probs, n_ok = audit_vocal_f0(all_v, lead_tr.b, 'lead-f0', None)
        print('  [F0] kiem tra %d not hat, %d van de' % (n_ok, len(probs)))
        for p in probs:
            print('  [F0]', p)

    def build(self, tracks, vocal=True):
        bass_tr = Track('bass', pan=0.0, gain=1.0, verb=0.1)
        drum_tr = Track('drums', pan=0.0, gain=1.0, verb=0.16)
        jag_tr = Track('jangle', pan=-0.35, gain=0.9, verb=0.14)
        lgt_tr = Track('leadgtr', pan=0.35, gain=0.9, verb=0.18)

        self._bass(bass_tr)
        self._drums(drum_tr)
        self._guitars(jag_tr, lgt_tr)
        tracks += [bass_tr, drum_tr, jag_tr, lgt_tr]
        if vocal:
            self._vocals(tracks)
