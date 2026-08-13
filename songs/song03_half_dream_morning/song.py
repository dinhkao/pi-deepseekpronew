"""Half-Dream Morning — bai 3, DNA: "I'm Only Sleeping" (E minor).

Gimmick: guitar solo CHOI NGUOC (render xuoi roi dao mang), refrain la CHORD
STREAM G-Am-Bm-Am-Cmaj7, verse 9 bar lech, vamp Em "dung thoi gian" truoc
bridge, be falsetto "oo-doo", ride beat luoi boozy, ADT split stereo.
"""
from __future__ import annotations

import numpy as np

from nhaccu._core import T, buf
from nhaccu._dsp import SR
from nhaccu.drums import Kit, Performer, bar_drums, merge
from nhaccu.guitar.jangle import jangle
from nhaccu.guitar.leadgtr import leadgtr
from nhaccu.bass.natbass import natbass
from nhaccu.keys.mellotron import mellotron
from nhaccu.voice import lead, falsetto_stack, vharm

from songs._engine import Song, Track, audit, audit_vocal_f0

# -------------------------------------------------------------- form marks --

B_V1 = 0        # 9 bars
B_R1 = 36       # refrain 6 bars + vamp 2 bars
B_BR1 = 68      # 4 bars
B_V2 = 84       # 9 bars (A' = backward guitar solo)
B_R2 = 120      # 6 bars
B_BR2 = 144     # 4 bars
B_V3 = 160      # 9 bars
B_R3 = 196      # refrain 6 + vamp 2
B_OUT = 228     # 8 bars (Cmaj7 stop -> backward guitar fade)
END = 260

VERSE_CH = [(0, 4, [4, 7, 11], 'Em'), (4, 4, [9, 0, 4], 'Am'),
            (8, 2, [7, 11, 2], 'G'), (10, 2, [0, 4, 7], 'C'),
            (12, 2, [7, 11, 2], 'G'), (14, 2, [11, 3, 6], 'B'),
            (16, 4, [4, 7, 11], 'Em'), (20, 4, [9, 0, 4], 'Am'),
            (24, 2, [7, 11, 2], 'G'), (26, 2, [0, 4, 7], 'C'),
            (28, 8, [9, 0, 4], 'Am')]
REFR_CH = [(0, 4, [7, 11, 2], 'G'), (4, 4, [9, 0, 4], 'Am'),
           (8, 4, [11, 2, 6], 'Bm'), (12, 4, [9, 0, 4], 'Am'),
           (16, 8, [0, 4, 7, 11], 'Cmaj7')]
BRIDGE_CH = [(0, 4, [2, 6, 9], 'D'), (4, 4, [4, 8, 11], 'E'),
             (8, 4, [9, 0, 4], 'Am'), (12, 4, [5, 9, 0], 'F')]

CHORDS = []
for bv in (B_V1, B_V2, B_V3):
    CHORDS += [(bv + s, bv + e, p, sy) for s, e, p, sy in VERSE_CH]
for br in (B_R1, B_R2, B_R3):
    CHORDS += [(br + s, br + e, p, sy) for s, e, p, sy in REFR_CH]
    if br != B_R2:
        CHORDS += [(br + 24, br + 32, [4, 7, 11], 'Em')]
for bb in (B_BR1, B_BR2):
    CHORDS += [(bb + s, bb + e, p, sy) for s, e, p, sy in BRIDGE_CH]
CHORDS += [(B_OUT, B_OUT + 8, [0, 4, 7, 11], 'Cmaj7'),
           (B_OUT + 8, B_OUT + 32, [4, 7, 11], 'Em')]

SCALE_EMIN = {4, 6, 7, 9, 11, 0, 2}     # E F# G A B C D
ALLOW = {'F2', 'F3', 'F4', 'D#3', 'D#4'}  # F (bridge), D# (B chord)
TENSIONS = {4: {2, 0}, 7: {9, 0}, 0: {9, 2}, 9: {11, 2}, 2: {0, 9, 4},
            11: {9}, 5: {}}


# ------------------------------------------------------------- lyrics/cells --

V1_LYR = [
    "when I wake up in the morn ing light",
    "half my mind is still in the night",
    "I could get up but I would rath er stay",
    "here where the hours drift a way",
]
V2_LYR = [
    "ly ing here with my eyes closed tight",
    "watch ing pict ures drift a cross the light",
    "pur ple trains and sil ver seas",
    "noth ing here is quite what it seems",
]
V3_LYR = [
    "peo ple run ning up and down the street",
    "nev er no tice the hours that they eat",
    "I would join them but I can not say",
    "why the day feels so far a way",
]


def _mel_verse(k, i, n):
    """Giai dieu verse: patter quanh tonic E4, xuong D-C o cuoi cau."""
    if k == 0:
        return ['E4', 'E4', 'E4', 'D4', 'E4', 'E4', 'D4', 'C4',
                'E4', 'E4', 'D4', 'C4', 'D4', 'C4', 'E4'][i % 15]
    if k == 1:
        return ['E4', 'E4', 'E4', 'D4', 'E4', 'E4', 'D4', 'D#4',
                'E4', 'E4', 'D4', 'D#4', 'D#4', 'E4'][i % 14]
    if k == 2:
        return ['E4', 'E4', 'E4', 'D4', 'E4', 'E4', 'D4', 'C4',
                'E4', 'E4', 'D4', 'C4', 'E4', 'E4', 'D4'][i % 15]
    return ['E4', 'E4', 'E4', 'D4', 'E4', 'E4', 'D4', 'C4',
            'E4', 'D4', 'C4', 'D4', 'C4', 'E4'][i % 14]


def _verse_cells(b0, lines):
    cells = []
    for k, line in enumerate(lines):
        words = line.split()
        base = b0 + k * 8
        n = len(words)
        step = 7.0 / n
        mel = [_mel_verse(k, i, n) for i in range(n)]
        for i, w in enumerate(words):
            d = step * (1.7 if i == n - 1 else 1.0)
            cells.append((base + i * step, d, mel[i], w, 1.0))
    # cau 4 (bar 7-9): them duoi
    cells.append((b0 + 28, 2.0, 'C4', 'way', 1.0))
    return cells


def _refrain(b0):
    return [
        (b0 + 0, 0.5, 'B4', 'please', 1.0), (b0 + 0.5, 0.5, 'A4', "don't", 1.0),
        (b0 + 1, 0.5, 'B4', 'wake', 1.0), (b0 + 1.5, 0.5, 'A4', 'me', 1.0),
        (b0 + 2, 0.5, 'B4', 'now', 1.0), (b0 + 2.5, 0.5, 'A4', "I'm", 1.0),
        (b0 + 3, 0.5, 'B4', 'miles', 1.0), (b0 + 3.5, 1.5, 'A4', 'away', 1.0),
        (b0 + 8, 0.5, 'B4', 'and', 1.0), (b0 + 8.5, 0.5, 'A4', 'af', 1.0),
        (b0 + 9, 0.5, 'B4', 'ter', 1.0), (b0 + 9.5, 0.5, 'A4', 'all', 1.0),
        (b0 + 10, 0.5, 'B4', "I'm", 1.0), (b0 + 10.5, 0.5, 'A4', 'on', 1.0),
        (b0 + 11, 0.5, 'B4', 'ly', 1.0), (b0 + 11.5, 0.5, 'C5', 'half', 1.0),
        (b0 + 12, 1.5, 'B4', 'a', 1.0), (b0 + 13.5, 2.5, 'E4', 'dream', 1.0),
        (b0 + 16, 0.5, 'B4', 'la', 1.0), (b0 + 16.5, 0.5, 'A4', 'la', 1.0),
        (b0 + 17, 0.5, 'B4', 'la', 1.0), (b0 + 17.5, 0.5, 'A4', 'la', 1.0),
        (b0 + 18, 0.5, 'B4', 'la', 1.0), (b0 + 18.5, 1.5, 'E4', 'la', 1.0),
    ]


def _bridge(b0):
    return [
        (b0 + 0, 0.5, 'D4', 'ev', 1.0), (b0 + 0.5, 0.5, 'C4', 'ry', 1.0),
        (b0 + 1, 0.5, 'D4', 'bod', 1.0), (b0 + 1.5, 0.5, 'C4', 'y', 1.0),
        (b0 + 2, 0.5, 'D4', 'thinks', 1.0), (b0 + 2.5, 0.5, 'C4', "I'm", 1.0),
        (b0 + 3, 0.5, 'D4', 'la', 1.0), (b0 + 3.5, 1.5, 'C4', 'zy', 1.0),
        (b0 + 8, 0.5, 'C4', 'I', 1.0), (b0 + 8.5, 0.5, 'B3', "don't", 1.0),
        (b0 + 9, 0.5, 'C4', 'mind', 1.0), (b0 + 9.5, 0.5, 'B3', 'I', 1.0),
        (b0 + 10, 0.5, 'C4', 'think', 1.0), (b0 + 10.5, 0.5, 'B3', "they're", 1.0),
        (b0 + 11, 0.5, 'C4', 'cra', 1.0), (b0 + 11.5, 1.5, 'B3', 'zy', 1.0),
        (b0 + 12, 0.5, 'C4', 'float', 1.0), (b0 + 12.5, 0.5, 'C4', 'ing', 1.0),
        (b0 + 13, 0.5, 'A3', 'a', 1.0), (b0 + 13.5, 1.5, 'C4', 'way', 1.0),
    ]


def _rev_gtr(tr, beat_end, notes, dur_each=0.38, g=0.16, seed=9):
    """Render mot cau lead xuoi roi DAO NGUOC (backwards guitar cua IOS)."""
    L = int((sum(dur_each for _ in notes) + 0.5) * SR)
    tmp = np.zeros(L)
    t = 0.0
    for m in notes:
        leadgtr(tmp, t, m, dur_each, g=0.30, seed=seed)
        t += dur_each
    y = tmp[::-1].copy()
    i = int(T(beat_end) * SR) - len(y)
    if i < 0:
        y = y[-i:]
        i = 0
    n = min(len(y), len(tr.b) - i)
    tr.b[i:i + n] += y[:n] * g


SOLO_A = ['A3', 'C4', 'E4', 'A4', 'C5', 'A4', 'E4', 'C4',
          'D4', 'E4', 'G4', 'E4', 'D4', 'C4', 'A3', 'C4',
          'E4', 'G4', 'A4', 'C5', 'A4', 'G4', 'E4', 'D4', 'C4']
SOLO_B = ['C4', 'E4', 'G4', 'C5', 'E5', 'C5', 'G4', 'E4',
          'F#4', 'G4', 'A4', 'B4', 'A4', 'G4', 'E4', 'D4',
          'C4', 'B3', 'A3', 'B3', 'C4', 'D4', 'E4', 'G4', 'E4']


class HalfDreamMorning(Song):
    name = 'song03_half_dream_morning'
    bpm = 96
    beats = END
    human = 5
    laid = 0.012

    def _bass(self, tr):
        def nb(t0, m, d, g=0.33):
            natbass(tr.b, T(t0), m, d, g=g)
        for bv in (B_V1, B_V2, B_V3):
            # lazy root notes + passing B giua C va Am (Pollack: walking touch)
            for bar in range(0, 9):
                b0 = bv + bar * 4
                if bar % 5 in (0,):
                    nb(b0, 'E2', 3.2)
                elif bar % 5 == 1:
                    nb(b0, 'A2', 3.2)
                elif bar % 5 == 2:
                    nb(b0, 'G2', 1.8); nb(b0 + 2, 'C2', 1.8)
                elif bar % 5 == 3:
                    nb(b0, 'G2', 1.8); nb(b0 + 2, 'B1', 1.8)
                else:
                    nb(b0, 'E2', 1.8); nb(b0 + 2, 'A2', 1.8)
            nb(bv + 28, 'A2', 3.2)
        for br in (B_R1, B_R2, B_R3):
            seq = [('G2', 3.6), ('A2', 3.6), ('B2', 3.6), ('A2', 3.6),
                   ('C2', 7.2)]
            t = br
            for m, d in seq:
                nb(t, m, d)
                t += 4
        for bb in (B_BR1, B_BR2):
            for k, m in enumerate(['D2', 'E2', 'A2', 'F2']):
                nb(bb + k * 4, m, 3.4)
        for bar in range(0, 8):
            nb(B_OUT + bar * 4, 'C2' if bar < 2 else 'E2', 3.6)

    def _drums(self, tr):
        kit = Kit(seed=7)
        P = Performer(kit, T(END) + 4, seed=23, laid=0.014)
        lazy = {'K': 'K...K...K...K...',
                'S': '....s.......s...',
                'R': 'R.R.R.R.R.R.R.R'}
        for bv in (B_V1, B_V2, B_V3):
            for bar in range(bv, bv + 36, 4):
                bar_drums(P, bar, lazy, vh=0.42)
        for br in (B_R1, B_R2, B_R3):
            for bar in range(br, br + 24, 4):
                if (bar - br) % 8 == 0:
                    P.CR(bar, 0, v=0.55)
                bar_drums(P, bar, lazy, vh=0.42)
            if br != B_R2:
                continue  # vamp: trong dung lai (time-stopping)
        for bb in (B_BR1, B_BR2):
            P.CR(bb, 0, v=0.6)
            for bar in range(bb, bb + 16, 4):
                bar_drums(P, bar, lazy, vh=0.40)
        # outro: chi ride
        for bar in range(B_OUT, B_OUT + 32, 4):
            P.RD(bar, 0, 0.4); P.RD(bar + 1, 4, 0.4)
            P.RD(bar + 2, 8, 0.4); P.RD(bar + 3, 12, 0.4)
        P.apply_chokes()
        for v in P.bus.values():
            v = np.asarray(v).ravel()
            n = min(len(tr.b), len(v))
            tr.b[:n] += v[:n]

    def _keys_gtr(self, tr_m, tr_j):
        # mellotron pad Em qua verses (nhung nhe), Cmaj7 o refrain
        for bv in (B_V1, B_V2, B_V3):
            for bar in range(bv, bv + 36, 4):
                mellotron(tr_m.b, T(bar), ['E3', 'G3', 'B3'], 3.6, g=0.045)
        for br in (B_R1, B_R2, B_R3):
            mellotron(tr_m.b, T(br), ['C4', 'E4', 'G4', 'B4'], 8.0, g=0.05)
            mellotron(tr_m.b, T(br + 16), ['C4', 'E4', 'G4', 'B4'], 8.0, g=0.05)
        for bb in (B_BR1, B_BR2):
            for k, ch in enumerate([['D3', 'F#3', 'A3'], ['E3', 'G#3', 'B3'],
                                    ['A3', 'C4', 'E4'], ['F3', 'A3', 'C4']]):
                mellotron(tr_m.b, T(bb + k * 4), ch, 3.6, g=0.05)
        # rhythm guitar jangle luoi
        for bv in (B_V1, B_V2, B_V3):
            for bar in range(bv, bv + 36, 4):
                for i in range(4):
                    jangle(tr_j.b, T(bar + i), 'E3', 0.5, g=0.055)

    def _guitar_solo(self, tr):
        # backward guitar: verse 2 A' section (bars 5-9 = beats 16-36)
        _rev_gtr(tr, B_V2 + 36, SOLO_A, g=0.13, seed=9)
        _rev_gtr(tr, B_V2 + 20, SOLO_A[:16], g=0.08, seed=11)
        # outro: backward noodle after stop
        _rev_gtr(tr, B_OUT + 16, SOLO_B, g=0.16, seed=13)
        _rev_gtr(tr, B_OUT + 32, SOLO_B[:12], g=0.11, seed=15)

    def _vocals(self, tracks):
        lead_tr = Track('lead', pan=-0.2, gain=1.0, verb=0.14, vocal=True,
                        squash=True)
        adt_tr = Track('lead_adt', pan=0.2, gain=0.55, verb=0.14, vocal=True)
        bv_tr = Track('backing', pan=0.3, gain=0.9, verb=0.12, vocal=True)

        v1 = _verse_cells(B_V1, V1_LYR)
        v2 = _verse_cells(B_V2, V2_LYR)
        v3 = _verse_cells(B_V3, V3_LYR)
        r1 = _refrain(B_R1)
        r2 = _refrain(B_R2)
        r3 = _refrain(B_R3)
        br1 = _bridge(B_BR1)
        br2 = _bridge(B_BR2)

        for cells, seed in ((v1, 1), (v2, 2), (v3, 3), (r1, 4), (r2, 5),
                            (r3, 6), (br1, 7), (br2, 8)):
            lead(lead_tr.b, 0, cells, g=0.24, seed=seed)
            lead(adt_tr.b, 0, cells, g=0.12, seed=seed + 40)

        # vamp "oo-doo" falsetto (sau refrain 1 va 3)
        ood = [(0, 0.5, 'E5', 'oo', 1.0), (0.5, 0.5, 'D5', 'doo', 0.9),
               (1, 0.5, 'B4', 'oo', 0.9), (1.5, 0.5, 'D5', 'doo', 0.8),
               (2, 0.5, 'E5', 'oo', 0.9), (2.5, 1.5, 'B4', 'doo', 0.8)]
        falsetto_stack(bv_tr.b, B_R1 + 24, ood, g=0.05, n=2, transpose=12)
        falsetto_stack(bv_tr.b, B_R3 + 24, ood, g=0.05, n=2, transpose=12)
        # Paul bluesy counterpoint o bridge (quang 3 duoi, chong voice)
        vharm(bv_tr.b, B_BR1, _bridge(B_BR1), intervals=(-3,), g=0.07,
              seed=31)
        vharm(bv_tr.b, B_BR2, _bridge(B_BR2), intervals=(-3,), g=0.07,
              seed=32)

        tracks += [lead_tr, adt_tr, bv_tr]

        # --------------------------------------------------- audit ----
        all_v = v1 + r1 + br1 + v2 + r2 + br2 + v3 + r3
        probs = audit(all_v, CHORDS, SCALE_EMIN, 'vocal', allow=ALLOW,
                      tensions=TENSIONS)
        for p in probs:
            print('  [AUDIT]', p)
        probs, n_ok = audit_vocal_f0(all_v, lead_tr.b, 'lead-f0', None)
        print('  [F0] kiem tra %d not hat, %d van de' % (n_ok, len(probs)))
        for p in probs:
            print('  [F0]', p)

    def build(self, tracks, vocal=True):
        bass_tr = Track('bass', pan=0.0, gain=1.0, verb=0.08)
        drum_tr = Track('drums', pan=0.0, gain=1.0, verb=0.14)
        mel_tr = Track('mellotron', pan=-0.35, gain=1.0, verb=0.2)
        jag_tr = Track('jangle', pan=0.25, gain=0.9, verb=0.1)
        rev_tr = Track('backwards_gtr', pan=0.4, gain=1.0, verb=0.24)

        self._bass(bass_tr)
        self._drums(drum_tr)
        self._keys_gtr(mel_tr, jag_tr)
        self._guitar_solo(rev_tr)
        tracks += [bass_tr, drum_tr, mel_tr, jag_tr, rev_tr]
        if vocal:
            self._vocals(tracks)
