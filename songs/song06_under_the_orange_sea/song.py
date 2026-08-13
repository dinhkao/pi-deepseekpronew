"""Under the Orange Sea — bai 6, DNA: "Yellow Submarine" (G major singalong).

Gimmick: gang chorus + hieu ung am thanh (song bien, party crowd, ban nhac
dieu hanh choi LECH hop am, tieng tau ngam), in-medias-res vocal pickup,
echo "thuyen truong" o verse 5, drumstick taps, pentatonic khong F#.
"""
from __future__ import annotations

import numpy as np

from nhaccu._core import T, buf
from nhaccu._dsp import SR, _lp, _bp, _ramp, _fadeout
from nhaccu.drums import Kit, Performer, bar_drums
from nhaccu.guitar.acgtr import acgtr
from nhaccu.guitar.jangle import jangle
from nhaccu.bass.natbass import natbass
from nhaccu.folk.fairorgan import fairorgan
from nhaccu.folk.march_bass import march_bass
from nhaccu.folk.washboard import washboard
from nhaccu.folk.gong import gong
from nhaccu.mallet.glass import glass
from nhaccu.fx.riser import riser
from nhaccu.voice import lead, gang, crowd

from songs._engine import Song, Track, audit, audit_vocal_f0

# -------------------------------------------------------------- form marks --

B_V1 = 0        # 8 bars (band vao tu beat 8)
B_V2 = 32       # 8 bars + waves
B_R1 = 64       # 8 bars
B_V3 = 96       # 8 bars + party + marching band
B_R2 = 128      # 8 bars + drumsticks
B_V4 = 160      # 8 bars + submarine noises
B_V5 = 192      # 8 bars + echo captain
B_R3 = 224      # 8 bars rich chorus
B_OUT = 256     # 8 bars fade
END = 288

VERSE_CH = [(0, 4, [7, 11, 2], 'G'), (4, 2, [2, 6, 9], 'D'),
            (6, 2, [0, 4, 7], 'C'), (8, 2, [7, 11, 2], 'G'),
            (10, 2, [4, 7, 11], 'Em'), (12, 4, [9, 0, 4], 'Am'),
            (16, 2, [9, 0, 4], 'Am'), (18, 2, [2, 6, 9], 'D'),
            (20, 4, [7, 11, 2], 'G'), (24, 2, [0, 4, 7], 'C'),
            (26, 2, [7, 11, 2], 'G'), (28, 4, [2, 6, 9], 'D')]
REFR_CH = [(0, 4, [7, 11, 2], 'G'), (4, 4, [2, 6, 9], 'D'),
           (8, 8, [7, 11, 2], 'G'), (16, 4, [7, 11, 2], 'G'),
           (20, 4, [2, 6, 9], 'D'), (24, 8, [7, 11, 2], 'G')]

CHORDS = []
for bv in (B_V1, B_V2, B_V3, B_V4, B_V5):
    CHORDS += [(bv + s, bv + e, p, sy) for s, e, p, sy in VERSE_CH]
for br in (B_R1, B_R2, B_R3, B_OUT):
    CHORDS += [(br + s, br + e, p, sy) for s, e, p, sy in REFR_CH]

SCALE_GPENT = {7, 9, 11, 2, 4}         # G A B D E (khong F#, C chi passing)
ALLOW = {'C4', 'C5'}
TENSIONS = {7: {9}, 2: {11, 9}, 9: {7, 2}, 4: {9, 2}, 0: {2}}


# ------------------------------------------------------------- lyrics/cells --

V1_LYR = [
    "down in the town where I was born",
    "lived a man who watched the sea",
    "and he told us of a world be low",
    "of an or ange sea down far be low",
]
V2_LYR = [
    "the wa ter there is warm and green",
    "the strang est light I have ev er seen",
    "the fish wear hats and shake your hand",
    "and of fer tours of the sil ver sand",
]
V3_LYR = [
    "the cap tain is a friend ly clam",
    "he plays the drums in side a can",
    "the mer maids sing in har mo ny",
    "down in the town un der the sea",
]
V5_LYR = [
    "so come a long and bring a friend",
    "the or ange sea will nev er end",
    "we'll sail a way on waves of gold",
    "the best old sto ry ev er told",
]


def _verse(b0, lines, echo=False):
    cells = []
    for k, line in enumerate(lines):
        words = line.split()
        base = b0 + k * 8
        n = len(words)
        step = 7.5 / n
        for i, w in enumerate(words):
            d = step * (1.8 if i == n - 1 else 1.0)
            cells.append((base + i * step, d, None, w, 1.0))
    if echo:
        # echo captain: lap lai cau cuoi, nho va tre
        last = [c for c in cells if c[0] >= b0 + 24]
        cells += [(c[0] + 1.0, c[1] * 0.9, c[2], c[3], 0.5) for c in last]
    return cells


def _mel_v(k, i, n):
    rows = [
        ['D4', 'B3', 'D4', 'B3', 'D4', 'B3', 'A3', 'B3'],
        ['D4', 'B3', 'D4', 'B3', 'E4', 'D4', 'B3', 'A3'],
        ['D4', 'B3', 'D4', 'B3', 'D4', 'B3', 'E4', 'D4', 'B3'],
        ['D4', 'B3', 'D4', 'B3', 'E4', 'D4', 'B3', 'A3', 'A3'],
    ]
    r = rows[k]
    return r[i % len(r)]


def _verse_cells(b0, lines, echo=False):
    cells = []
    for k, line in enumerate(lines):
        words = line.split()
        base = b0 + k * 8
        n = len(words)
        step = 7.5 / n
        for i, w in enumerate(words):
            d = step * (1.8 if i == n - 1 else 1.0)
            cells.append((base + i * step, d, _mel_v(k, i, n), w, 1.0))
    if echo:
        last = [c for c in cells if c[0] >= b0 + 24]
        cells += [(c[0] + 1.0, c[1] * 0.9, c[2], c[3], 0.45) for c in last]
    return cells


def _refrain(b0):
    return [
        (b0 + 0, 0.5, 'B3', 'we', 1.0), (b0 + 0.5, 0.5, 'D4', 'all', 1.0),
        (b0 + 1, 0.5, 'B3', 'live', 1.0), (b0 + 1.5, 0.5, 'D4', 'un', 1.0),
        (b0 + 2, 0.5, 'B3', 'der', 1.0), (b0 + 2.5, 0.5, 'D4', 'the', 1.0),
        (b0 + 3, 0.5, 'B3', 'or', 1.0), (b0 + 3.5, 0.5, 'A3', 'ange', 1.0),
        (b0 + 4, 3.0, 'D4', 'sea', 1.0), (b0 + 7, 1.0, 'D4', 'sea', 1.0),
        (b0 + 16, 0.5, 'B3', 'un', 1.0), (b0 + 16.5, 0.5, 'D4', 'der', 1.0),
        (b0 + 17, 0.5, 'B3', 'the', 1.0), (b0 + 17.5, 0.5, 'D4', 'or', 1.0),
        (b0 + 18, 0.5, 'B3', 'ange', 1.0), (b0 + 18.5, 0.5, 'A3', 'sea', 1.0),
        (b0 + 19, 4.0, 'B3', 'sea', 1.0), (b0 + 23, 1.0, 'B3', 'sea', 1.0),
    ]


def _waves(b):
    """Song bien: noise loc thap, swell cham (verse 2 tro di)."""
    R = np.random.default_rng(55)
    for t0 in (T(B_V2), T(B_R1 + 8), T(B_V3 + 16), T(B_V4), T(B_OUT)):
        L = int(7.0 * SR)
        t = np.arange(L) / SR
        x = _lp(R.standard_normal(L), 900, 2)
        e = np.sin(np.pi * t / 7.0) ** 2
        x = x * e * 0.10
        i = int(t0 * SR)
        n = min(L, len(b) - i)
        b[i:i + n] += x[:n]
    return b


def _submarine_fx(b):
    # gong = tieng chuong tau, glass = ping sonar, riser = may moc
    gong(b, T(B_V4) + 0.1, g=0.16)
    gong(b, T(B_V4 + 16) + 0.1, g=0.12)
    for k, m in enumerate(['C5', 'G5', 'E5', 'A5']):
        glass(b, T(B_V4 + 8) + k * 0.4, m, 0.8, g=0.10)
    riser(b, T(B_V4 + 24) + 0.2, 3.0, g=0.05)


class UnderTheOrangeSea(Song):
    name = 'song06_under_the_orange_sea'
    bpm = 112
    beats = END
    human = 9
    laid = 0.004

    def _band(self, tr_bass, tr_gtr, tr_drum):
        # bass root don gian
        for bv in (B_V1, B_V2, B_V3, B_V4, B_V5):
            seq = ['G2', 'D2', 'C2', 'G2', 'E2', 'A2', 'A2', 'D2',
                   'G2', 'C2', 'G2', 'D2']
            t = bv
            for m in seq:
                natbass(tr_bass.b, T(t), m, 1.8, g=0.30)
                t += 2
        for br in (B_R1, B_R2, B_R3, B_OUT):
            for k in range(8):
                m = 'G2' if k % 4 < 2 else 'D2'
                natbass(tr_bass.b, T(br + k * 4), m, 3.6, g=0.30)
        # guitar acoustic strum + jangle
        for bv in (B_V1, B_V2, B_V3, B_V4, B_V5):
            for k in range(32):
                acgtr(tr_gtr.b, T(bv + k * 0.5) + 0.02, 'G3', 0.3, g=0.065)
        for br in (B_R1, B_R2, B_R3, B_OUT):
            for k in range(16):
                jangle(tr_gtr.b, T(br + k), 'G3', 0.4, g=0.06)
        # drums: mem, hat nhe
        kit = Kit(seed=7)
        P = Performer(kit, T(END) + 4, seed=29)
        beat = {'K': 'K...K...K...K...',
                'S': '....S.......S...',
                'H': 'H.hH.hH.hH.hH'}
        for bv in (B_V1, B_V2, B_V3, B_V4, B_V5):
            for bar in range(bv + 8, bv + 32, 4):
                bar_drums(P, bar, beat, vk=0.7, vs=0.7, vh=0.4)
        for br in (B_R1, B_R2, B_R3, B_OUT):
            for bar in range(br, br + 32, 4):
                bar_drums(P, bar, beat, vk=0.7, vs=0.7, vh=0.42)
            # drumstick taps (cross-stick) o refrain 2
            if br == B_R2:
                for beat_ in range(br + 8, br + 24, 2):
                    P.S(beat_, 0, 0.4, art='cross')
        for bar in range(B_R1, B_R3 + 32, 8):
            P.CL(bar + 4, 0, 0.4); P.CL(bar + 12, 8, 0.4)
        P.apply_chokes()
        for v in P.bus.values():
            v = np.asarray(v).ravel()
            n = min(len(tr_drum.b), len(v))
            tr_drum.b[:n] += v[:n]

    def _fx_party(self, tr):
        # party + marching band choi LECH hop am (YS: "the chords they
        # play clash with the backing track")
        R = np.random.default_rng(3)
        for beat in range(B_V3, B_V3 + 32, 8):
            crowd(tr.b, beat, [(0, 0.5, 'E4', 'hey', 1.0),
                               (1, 0.5, 'D4', 'ho', 1.0),
                               (2, 1.0, 'E4', 'hey', 1.0)], g=0.05)
        for k in range(8):
            fairorgan(tr.b, T(B_V3 + 4 + k * 4), ['C4', 'E4', 'G4'], 1.5,
                      g=0.030)
        for k in range(4):
            march_bass(tr.b, T(B_V3 + 4 + k * 8) + 0.1, g=0.05)
            washboard(tr.b, T(B_V3 + 4 + k * 8) + 0.9, g=0.05)
        _waves(tr.b)
        _submarine_fx(tr.b)

    def _vocals(self, tracks):
        lead_tr = Track('lead', pan=0.0, gain=1.0, verb=0.14, vocal=True,
                        squash=True)
        gang_tr = Track('gang', pan=0.0, gain=1.0, verb=0.16, vocal=True)

        v1 = _verse_cells(B_V1, V1_LYR)
        v2 = _verse_cells(B_V2, V2_LYR)
        v3 = _verse_cells(B_V3, V3_LYR)
        v5 = _verse_cells(B_V5, V5_LYR, echo=True)
        r1 = _refrain(B_R1)
        r2 = _refrain(B_R2)
        r3 = _refrain(B_R3)
        r_out = _refrain(B_OUT)

        for cells, seed in ((v1, 1), (v2, 2), (v3, 3), (v5, 4)):
            lead(lead_tr.b, 0, cells, g=0.24, seed=seed)
        # Ringo-style lead o refrain cung gang
        for cells, seed in ((r1, 5), (r2, 6), (r3, 7), (r_out, 8)):
            lead(lead_tr.b, 0, cells, g=0.20, seed=seed)
            gang(gang_tr.b, 0, cells, g=0.075, n=6, seed=seed)
        # refrain 3: hop xuong giau hon (them 1 gang nua octave)
        gang(gang_tr.b, B_R3, r3, g=0.05, n=4, seed=77)

        tracks += [lead_tr, gang_tr]

        # --------------------------------------------------- audit ----
        all_v = v1 + v2 + v3 + v5 + r1 + r2 + r3 + r_out
        probs = audit(all_v, CHORDS, SCALE_GPENT, 'vocal', allow=ALLOW,
                      tensions=TENSIONS)
        for p in probs:
            print('  [AUDIT]', p)
        probs, n_ok = audit_vocal_f0(all_v, lead_tr.b, 'lead-f0', None)
        print('  [F0] kiem tra %d not hat, %d van de' % (n_ok, len(probs)))
        for p in probs:
            print('  [F0]', p)

    def build(self, tracks, vocal=True):
        bass_tr = Track('bass', pan=0.0, gain=1.0, verb=0.08)
        gtr_tr = Track('guitar', pan=-0.25, gain=1.0, verb=0.12)
        drum_tr = Track('drums', pan=0.0, gain=1.0, verb=0.14)
        fx_tr = Track('fx', pan=0.3, gain=1.0, verb=0.3)

        self._band(bass_tr, gtr_tr, drum_tr)
        self._fx_party(fx_tr)
        tracks += [bass_tr, gtr_tr, drum_tr, fx_tr]
        if vocal:
            self._vocals(tracks)
