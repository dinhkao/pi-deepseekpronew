"""She Never Said — bai 7, DNA: "She Said She Said" (Bb Mixolydian).

Gimmick: CHI 4 hop am ca bai (Bb Ab Eb Fm), break doi nhịp 4+4 | 3+3+3 |
6+3 | 6+3 voi pivot Fm->Eb, nen nang moi thu (Fairchild-style limiting),
organ tron rat nho (subliminal), guitar antiphonal tra loi vocal, coda
canon 8ths deu.
"""
from __future__ import annotations

import numpy as np

from nhaccu._core import T, buf
from nhaccu._dsp import SR
from nhaccu.drums import Kit, Performer, bar_drums, merge
from nhaccu.guitar.fuzz import fuzz
from nhaccu.guitar.leadgtr import leadgtr
from nhaccu.bass.natbass import natbass
from nhaccu.keys.organ import organ
from nhaccu.voice import lead, vharm

from songs._engine import Song, Track, audit, audit_vocal_f0

# -------------------------------------------------------------- form marks --

B_INTRO = 0     # 2 bars
B_V1 = 8        # 8 bars
B_V2 = 40       # 8 bars
B_BR1 = 72      # 35 beats (doi nhịp!)
B_V3 = 107      # 8 bars
B_BR2 = 139     # 35 beats
B_V4 = 174      # 8 bars
B_CODA = 206    # 56 beats
END = 262

VERSE_CH = []
for i in range(3):
    VERSE_CH += [(2 * i * 4 + 0, 2 * i * 4 + 2, [10, 2, 5], 'Bb'),
                 (2 * i * 4 + 2, 2 * i * 4 + 4, [8, 0, 3], 'Ab'),
                 (2 * i * 4 + 4, 2 * i * 4 + 8, [3, 7, 10], 'Eb')]
VERSE_CH += [(24, 26, [10, 2, 5], 'Bb'), (26, 28, [8, 0, 3], 'Ab'),
             (28, 30, [3, 7, 10], 'Eb'), (30, 32, [10, 2, 5], 'Bb')]

BREAK_CH = [(0, 4, [10, 2, 5], 'Bb'), (4, 8, [10, 2, 5], 'Bb'),
            (8, 11, [8, 0, 3], 'Ab'), (11, 14, [10, 2, 5], 'Bb'),
            (14, 17, [5, 8, 0], 'Fm'), (17, 23, [10, 2, 5], 'Bb'),
            (23, 26, [3, 7, 10], 'Eb'), (26, 32, [10, 2, 5], 'Bb'),
            (32, 35, [3, 7, 10], 'Eb')]

CHORDS = [(B_INTRO, B_INTRO + 8, [10, 2, 5], 'Bb')]
for bv in (B_V1, B_V2, B_V3, B_V4):
    CHORDS += [(bv + s, bv + e, p, sy) for s, e, p, sy in VERSE_CH]
for bb in (B_BR1, B_BR2):
    CHORDS += [(bb + s, bb + e, p, sy) for s, e, p, sy in BREAK_CH]
CHORDS += [(B_CODA, B_CODA + 56, [10, 2, 5], 'Bb')]

SCALE_BBMIXO = {10, 0, 2, 3, 5, 7, 8}   # Bb C D Eb F G Ab
ALLOW = set()
TENSIONS = {10: {2}, 3: {2}, 8: {0}, 5: {}}


# ------------------------------------------------------------- lyrics/cells --

def _verse(b0, lines):
    cells = []
    for k, line in enumerate(lines):
        words = line.split()
        base = b0 + k * 8
        n = len(words)
        step = 7.5 / n
        for i, w in enumerate(words):
            d = step * (1.8 if i == n - 1 else 1.0)
            cells.append((base + i * step, d, None, w, 1.0))
    return cells


V_LYR = [
    "she said she said she knows what it's like to be gone",
    "she said she said she knows where the shad ows come from",
    "she said she said she knows what it's like to be dead",
    "she said she said and she nev er said a word",
]


def _mel_v(i, n):
    return ['F4', 'D4', 'F4', 'D4', 'F4', 'D4', 'F4', 'Eb4', 'D4', 'C4',
            'D4', 'Eb4'][i % 12]


def _verse_cells(b0, lines):
    cells = []
    for k, line in enumerate(lines):
        words = line.split()
        base = b0 + k * 8
        n = len(words)
        step = 7.5 / n
        for i, w in enumerate(words):
            d = step * (1.8 if i == n - 1 else 1.0)
            cells.append((base + i * step, d, _mel_v(i, n), w, 1.0))
    return cells


def _break(b0):
    return [
        (b0 + 0, 0.5, 'F4', 'she', 1.0), (b0 + 0.5, 0.5, 'D4', 'said', 1.0),
        (b0 + 1, 0.5, 'F4', 'you', 1.0), (b0 + 1.5, 0.5, 'D4', "don't", 1.0),
        (b0 + 2, 0.5, 'F4', 'un', 1.0), (b0 + 2.5, 0.5, 'Eb4', 'der', 1.0),
        (b0 + 3, 0.5, 'D4', 'stand', 1.0), (b0 + 3.5, 0.5, 'C4', 'what', 1.0),
        (b0 + 4, 0.5, 'D4', 'I', 1.0), (b0 + 4.5, 0.5, 'Eb4', 'said', 1.0),
        (b0 + 5, 0.5, 'F4', 'I', 1.0), (b0 + 5.5, 2.5, 'D4', 'said', 1.0),
        (b0 + 8, 0.5, 'F4', 'no', 1.0), (b0 + 8.5, 0.5, 'Eb4', 'no', 1.0),
        (b0 + 9, 1.0, 'C4', 'no', 1.0), (b0 + 10, 0.5, 'Eb4', "you're", 1.0),
        (b0 + 10.5, 0.5, 'D4', 'wrong', 1.0), (b0 + 11, 1.0, 'D4', 'when', 1.0),
        (b0 + 12, 0.5, 'C4', 'I', 1.0), (b0 + 12.5, 0.5, 'Eb4', 'was', 1.0),
        (b0 + 13, 1.0, 'F4', 'a', 1.0), (b0 + 14, 3.0, 'F4', 'boy', 1.0),
        (b0 + 17, 0.5, 'D4', 'ev', 1.0), (b0 + 17.5, 0.5, 'Eb4', 'ry', 1.0),
        (b0 + 18, 0.5, 'D4', 'thing', 1.0), (b0 + 18.5, 0.5, 'C4', 'was', 1.0),
        (b0 + 19, 3.0, 'D4', 'bright', 1.0),
        (b0 + 23, 0.5, 'D4', 'ev', 1.0), (b0 + 23.5, 0.5, 'Eb4', 'ry', 1.0),
        (b0 + 24, 0.5, 'D4', 'thing', 1.0), (b0 + 24.5, 0.5, 'Eb4', 'was', 1.0),
        (b0 + 25, 1.0, 'Eb4', 'bright', 1.0),
        (b0 + 26, 0.5, 'D4', 'ev', 1.0), (b0 + 26.5, 0.5, 'Eb4', 'ry', 1.0),
        (b0 + 27, 0.5, 'D4', 'thing', 1.0), (b0 + 27.5, 0.5, 'C4', 'was', 1.0),
        (b0 + 28, 3.0, 'D4', 'bright', 1.0),
        (b0 + 32, 0.5, 'Eb4', 'ev', 1.0), (b0 + 32.5, 0.5, 'D4', 'ry', 1.0),
        (b0 + 33, 0.5, 'Eb4', 'thing', 1.0), (b0 + 33.5, 0.5, 'D4', 'was', 1.0),
        (b0 + 34, 1.0, 'Eb4', 'bright', 1.0),
    ]


def _coda(b0):
    cells = []
    for rep in range(7):
        for k, (m, syl) in enumerate([('F4', 'she'), ('D4', 'nev'),
                                      ('F4', 'er'), ('D4', 'said')]):
            cells.append((b0 + rep * 8 + k * 0.5, 0.5, m, syl, 0.9))
    return cells


class SheNeverSaid(Song):
    name = 'song07_she_never_said'
    bpm = 124
    beats = END
    human = 10
    laid = 0.0

    def _bass(self, tr):
        def nb(t0, m, d, g=0.30):
            natbass(tr.b, T(t0), m, d, g=g)
        for bv in (B_V1, B_V2, B_V3, B_V4):
            seq = ['Bb2', 'Ab2', 'Eb2', 'Eb2'] * 3 + ['Bb2', 'Ab2', 'Eb2',
                                                     'Bb2']
            t = bv
            for m in seq:
                nb(t, m, 1.9, g=0.32)
                t += 2
        for bb in (B_BR1, B_BR2):
            for s, e, p, sy in BREAK_CH:
                root = ['Bb2', 'Ab2', 'Eb2', 'F2'][[10, 8, 3, 5].index(p[0])]
                nb(bb + s, root, e - s - 0.3, g=0.30)
        for k in range(14):
            nb(B_CODA + k * 4, 'Bb2', 3.6, g=0.30)

    def _drums(self, tr):
        kit = Kit(seed=7)
        P = Performer(kit, T(END) + 4, seed=33)
        rock = {'K': 'K...K...K...K...',
                'S': '....S.......S...',
                'H': 'H.hH.hH.hH.hH'}
        for bv in (B_V1, B_V2, B_V3, B_V4):
            for bar in range(bv, bv + 32, 4):
                bar_drums(P, bar, rock, vh=0.5)
            # fancy footwork cuoi phrase (Ringo signature)
            P.roll(bv + 30, 1.5, 0.25, 0.3, 0.55)
        for bb in (B_BR1, B_BR2):
            # break: trong theo meter, 8ths deu (Pollack)
            t = bb
            for s, e, p, sy in BREAK_CH:
                n = e - s
                for k in range(n):
                    if k % 2 == 0:
                        P.K(t + k, int(k * 8), 0.8)
                    else:
                        P.H(t + k, int(k * 8), 0.4, 0.0, 'tip')
                t += n
        # coda: 8ths deu — giai phong syncopation (Pollack: "free skid")
        for k in range(56):
            P.K(B_CODA + k * 0.5, int(k * 4) % 16, 0.6 if k % 2 == 0 else 0.5)
            P.H(B_CODA + k * 0.5, int(k * 4) % 16, 0.35, 0.0, 'tip')
        P.apply_chokes()
        for v in P.bus.values():
            v = np.asarray(v).ravel()
            n = min(len(tr.b), len(v))
            tr.b[:n] += v[:n]

    def _guitars(self, tr_f, tr_l):
        # rhythm fuzz: Bb power + Ab Eb moves
        for bv in (B_V1, B_V2, B_V3, B_V4):
            seq = [('Bb3', 2), ('Ab3', 2), ('Eb3', 4)] * 3 + [('Bb3', 2),
                                                              ('Ab3', 2),
                                                              ('Eb3', 2),
                                                              ('Bb3', 2)]
            t = bv
            for m, d in seq:
                fuzz(tr_f.b, T(t) + 0.01, m, d - 0.2, g=0.075)
                t += d
        for bb in (B_BR1, B_BR2):
            for s, e, p, sy in BREAK_CH:
                m = ['Bb3', 'Ab3', 'Eb3', 'F3'][[10, 8, 3, 5].index(p[0])]
                fuzz(tr_f.b, T(bb + s) + 0.01, m, e - s - 0.3, g=0.07)
        for k in range(14):
            fuzz(tr_f.b, T(B_CODA + k * 4) + 0.01, 'Bb3', 3.6, g=0.06)
        # guitar antiphonal: tra loi vocal sau moi cau (Pollack)
        for bv in (B_V1, B_V2, B_V3, B_V4):
            for k in range(4):
                b0 = bv + k * 8 + 6
                for j, m in enumerate(['F4', 'Eb4', 'D4']):
                    leadgtr(tr_l.b, T(b0 + j * 0.5), m, 0.4, g=0.20)
        for bb in (B_BR1, B_BR2):
            for j, m in enumerate(['F4', 'Eb4', 'D4', 'C4']):
                leadgtr(tr_l.b, T(bb + 5 + j * 0.5), m, 0.4, g=0.18)

    def _organ_subliminal(self, tr):
        for bv in (B_V1, B_V2, B_V3, B_V4):
            organ(tr.b, T(bv), ['Bb3', 'D4', 'F4'], 30.0, g=0.016)
        for bb in (B_BR1, B_BR2):
            organ(tr.b, T(bb), ['Bb3', 'D4', 'F4'], 34.0, g=0.016)

    def _vocals(self, tracks):
        lead_tr = Track('lead', pan=0.0, gain=1.0, verb=0.12, vocal=True,
                        squash=True)
        bv_tr = Track('backing', pan=-0.3, gain=0.85, verb=0.1, vocal=True)

        v1 = _verse_cells(B_V1, V_LYR)
        v2 = _verse_cells(B_V2, V_LYR)
        v3 = _verse_cells(B_V3, V_LYR)
        v4 = _verse_cells(B_V4, V_LYR)
        br1 = _break(B_BR1)
        br2 = _break(B_BR2)
        co = _coda(B_CODA)

        for cells, seed in ((v1, 1), (v2, 2), (v3, 3), (v4, 4), (br1, 5),
                            (br2, 6), (co, 7)):
            lead(lead_tr.b, 0, cells, g=0.24, seed=seed)
        # canon o coda: giong 2 lech 2 beats (Pollack: canonic imitation)
        vharm(bv_tr.b, B_CODA + 2, _coda(B_CODA), intervals=(0,), g=0.06,
              seed=51, transpose=-12)

        tracks += [lead_tr, bv_tr]

        # --------------------------------------------------- audit ----
        all_v = v1 + v2 + br1 + v3 + br2 + v4 + co
        probs = audit(all_v, CHORDS, SCALE_BBMIXO, 'vocal', allow=ALLOW,
                      tensions=TENSIONS)
        for p in probs:
            print('  [AUDIT]', p)
        probs, n_ok = audit_vocal_f0(all_v, lead_tr.b, 'lead-f0', None)
        print('  [F0] kiem tra %d not hat, %d van de' % (n_ok, len(probs)))
        for p in probs:
            print('  [F0]', p)

    def build(self, tracks, vocal=True):
        bass_tr = Track('bass', pan=0.0, gain=1.0, verb=0.06, squash=True)
        drum_tr = Track('drums', pan=0.0, gain=1.0, verb=0.1, squash=True)
        fuz_tr = Track('fuzz', pan=-0.3, gain=0.95, verb=0.08, squash=True)
        lgt_tr = Track('leadgtr', pan=0.3, gain=0.9, verb=0.14)
        org_tr = Track('organ', pan=0.15, gain=1.0, verb=0.1)

        self._bass(bass_tr)
        self._drums(drum_tr)
        self._guitars(fuz_tr, lgt_tr)
        self._organ_subliminal(org_tr)
        tracks += [bass_tr, drum_tr, fuz_tr, lgt_tr, org_tr]
        if vocal:
            self._vocals(tracks)
