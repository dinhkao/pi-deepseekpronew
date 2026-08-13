"""The Long Goodbye — bai 10, DNA: "Tomorrow Never Knows" + "Got To Get You
Into My Life" (C drone + brass soul).

Gimmick: MOT HOP AM (C pedal, Bb flat-VII nua sau moi verse), trong
syncopation cung o "three-and" (human drum loop), tape-loop ostinato
C-D-E-F-E-C lap y het (clav), brass stabs close-mic cho Bb section,
chromatic bass descent B-Bb-A-G# (GTGYIML), giong qua Leslie tu nua sau,
"beep" dung giua bai, outro tan ra + tack piano flailing.
"""
from __future__ import annotations

import numpy as np

from nhaccu._core import T, buf
from nhaccu._dsp import SR, leslie, _lp, _ramp, _fadeout
from nhaccu.drums import Kit, Performer, bar_drums
from nhaccu.guitar.fuzz import fuzz
from nhaccu.bass.natbass import natbass
from nhaccu.keys.clav import clav
from nhaccu.keys.tack import tack
from nhaccu.keys.mellotron import mellotron
from nhaccu.horns.section import section
from nhaccu.voice import lead

from songs._engine import Song, Track, audit, audit_vocal_f0

# -------------------------------------------------------------- form marks --

B_INTRO = 0     # 24: drone 8 + rhythm 8 + loop 8
B_V1 = 24       # 32
B_V2 = 56       # 32
B_INSTR = 88    # 32: loops + brass
B_V3 = 120      # 32 (Leslie tu day)
B_V4 = 152      # 32
B_V5 = 184      # 32
B_OUT = 216     # 40: disintegration + tack piano
END = 256

CHORDS = [(B_INTRO, B_INTRO + 24, [0, 4, 7], 'C')]
for bv in (B_V1, B_V2, B_V3, B_V4, B_V5, B_INSTR):
    CHORDS += [(bv, bv + 16, [0, 4, 7], 'C'),
               (bv + 16, bv + 24, [10, 2, 5], 'Bb'),
               (bv + 24, bv + 32, [0, 4, 7], 'C')]
CHORDS += [(B_OUT, B_OUT + 40, [0, 4, 7], 'C')]

SCALE_CMIXO = {0, 2, 4, 5, 7, 9, 10}    # C D E F G A Bb
ALLOW = set()
TENSIONS = {0: {10, 2, 9}, 10: {0}}


# ------------------------------------------------------------- lyrics/cells --

def _verse(b0, line_a, line_b):
    return [
        (b0 + 0, 0.75, 'E4', 'turn', 1.0), (b0 + 0.75, 0.5, 'G4', 'out', 1.0),
        (b0 + 1.25, 0.5, 'E4', 'the', 1.0), (b0 + 1.75, 0.5, 'G4', 'light', 1.0),
        (b0 + 2.25, 0.5, 'E4', 'and', 1.0), (b0 + 2.75, 0.5, 'G4', 'let', 1.0),
        (b0 + 3.25, 0.5, 'E4', 'the', 1.0), (b0 + 3.75, 0.5, 'G4', 'riv', 1.0),
        (b0 + 4.25, 0.5, 'E4', 'er', 1.0), (b0 + 4.75, 3.0, 'C4', 'run', 1.0),
        (b0 + 8, 0.5, 'E4', 'all', 1.0), (b0 + 8.5, 0.5, 'G4', 'of', 1.0),
        (b0 + 9, 0.5, 'E4', 'the', 1.0), (b0 + 9.5, 0.5, 'G4', 'col', 1.0),
        (b0 + 10, 0.5, 'E4', 'ours', 1.0), (b0 + 10.5, 0.5, 'G4', 'are', 1.0),
        (b0 + 11, 0.5, 'E4', 'melt', 1.0), (b0 + 11.5, 0.5, 'G4', 'ing', 1.0),
        (b0 + 12, 0.5, 'E4', 'in', 1.0), (b0 + 12.5, 0.5, 'G4', 'to', 1.0),
        (b0 + 13, 3.0, 'C4', 'one', 1.0),
        (b0 + 16, 0.5, 'D4', 'noth', 1.0), (b0 + 16.5, 0.5, 'F4', 'ing', 1.0),
        (b0 + 17, 0.5, 'D4', 'is', 1.0), (b0 + 17.5, 0.5, 'F4', 'real', 1.0),
        (b0 + 18, 0.5, 'D4', 'and', 1.0), (b0 + 18.5, 0.5, 'F4', 'noth', 1.0),
        (b0 + 19, 0.5, 'D4', 'ing', 1.0), (b0 + 19.5, 0.5, 'F4', 'to', 1.0),
        (b0 + 20, 0.5, 'D4', 'get', 1.0), (b0 + 20.5, 0.5, 'F4', 'hung', 1.0),
        (b0 + 21, 0.5, 'D4', 'a', 1.0), (b0 + 21.5, 3.0, 'Bb3', 'bout', 1.0),
        (b0 + 24, 0.75, 'E4', 'turn', 1.0), (b0 + 24.75, 0.5, 'G4', 'out', 1.0),
        (b0 + 25.25, 0.5, 'E4', 'the', 1.0), (b0 + 25.75, 0.5, 'G4', 'light', 1.0),
        (b0 + 26.25, 0.5, 'E4', 'and', 1.0), (b0 + 26.75, 0.5, 'G4', 'let', 1.0),
        (b0 + 27.25, 0.5, 'E4', 'the', 1.0), (b0 + 27.75, 0.5, 'G4', 'riv', 1.0),
        (b0 + 28.25, 0.5, 'E4', 'er', 1.0), (b0 + 28.75, 3.0, 'C4', 'run', 1.0),
    ]


LOOP_MOTIF = ['C5', 'D4', 'E4', 'F4', 'E4', 'C5']   # jagged tape loop TNK


def _tape_loop(b, start_beat, reps, g=0.08):
    """Ostinato lap y het (tape loop): C D E F E C, moi 6 beats."""
    for r in range(reps):
        b0 = start_beat + r * 6
        for i, m in enumerate(LOOP_MOTIF):
            clav(b, T(b0 + i * 0.5), m, 0.42, g=g, seed=7)


def _seagull(b, t0, g=0.06):
    """Tape loop 'seagull': cua xuong, khong cao do xac dinh."""
    L = int(2.0 * SR)
    t = np.arange(L) / SR
    f = 1800 * np.exp(-t / 0.55) + 300
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)) * np.exp(-t / 1.2)
    R = np.random.default_rng(9)
    x += _lp(R.standard_normal(L), 5000, 2) * 0.15 * np.exp(-t / 0.9)
    x = _fadeout(_ramp(x, 40.0), 20.0) * g * 1.5
    i = int(t0 * SR)
    n = min(L, len(b) - i)
    b[i:i + n] += x[:n]


def _beep(b, t0):
    L = int(0.25 * SR)
    t = np.arange(L) / SR
    x = np.sin(2 * np.pi * 1046.5 * t) * np.exp(-t / 0.08) * 0.12
    i = int(t0 * SR)
    n = min(L, len(b) - i)
    b[i:i + n] += x[:n]


class TheLongGoodbye(Song):
    name = 'song10_the_long_goodbye'
    bpm = 110
    beats = END
    human = 14
    laid = 0.0

    def _bass(self, tr):
        def nb(t0, m, d, g=0.35):
            natbass(tr.b, T(t0), m, d, g=g)
        for bv in (B_V1, B_V2, B_V3, B_V4, B_V5, B_INSTR):
            nb(bv, 'C2', 15.5)
            # chromatic descent B Bb A G# (GTGYIML!)
            for k, m in enumerate(['B1', 'Bb1', 'A1', 'G#1']):
                nb(bv + 16 + k * 2, m, 1.8)
            nb(bv + 24, 'C2', 7.5)
        nb(B_INTRO, 'C2', 22.0)
        for k in range(10):
            nb(B_OUT + k * 4, 'C2', 3.6)

    def _drums(self, tr):
        kit = Kit(seed=7)
        P = Performer(kit, T(END) + 4, seed=51)
        # human drum loop: syncopation cung o "three-and" (TNK)
        loop = {'K': 'K...K.K...K.K...',
                'S': '....S.......S...',
                'H': 'H.hH.hH.hH.hH'}
        for bv in (B_V1, B_V2, B_V3, B_V4, B_V5, B_INSTR):
            for bar in range(bv, bv + 32, 4):
                bar_drums(P, bar, loop, vh=0.42)
        for bar in range(B_INTRO + 8, B_INTRO + 24, 4):
            bar_drums(P, bar, loop, vh=0.42)
        for bar in range(B_OUT, B_OUT + 40, 4):
            bar_drums(P, bar, loop, vh=0.35)
        # tambourine steady (TNK)
        for beat in range(B_V1, B_OUT, 2):
            P.TB(beat, 0, 0.35)
        P.apply_chokes()
        for v in P.bus.values():
            v = np.asarray(v).ravel()
            n = min(len(tr.b), len(v))
            tr.b[:n] += v[:n]

    def _brass_loops(self, tr_b, tr_l):
        # brass stabs close-mic cho Bb section (GTGYIML "washed out horns")
        for bv in (B_V1, B_V2, B_V3, B_V4, B_V5, B_INSTR):
            section(tr_b.b, T(bv + 16), ['Bb3', 'D4', 'F4', 'Bb4'], 1.2,
                    g=0.07, art='stab')
            section(tr_b.b, T(bv + 20), ['Bb3', 'D4', 'F4', 'Bb4'], 1.0,
                    g=0.06, art='stab')
        # intro: tamboura-like drone (TNK)
        mellotron(tr_b.b, T(B_INTRO), ['C3', 'G3', 'C4'], 8.0, g=0.05)
        # tape loops: jagged ostinato + seagull
        _tape_loop(tr_l.b, B_INTRO + 16, 2, g=0.07)
        for bv in (B_V1, B_V2, B_V3, B_V4, B_V5):
            _tape_loop(tr_l.b, bv + 8, 4, g=0.065)
        _tape_loop(tr_l.b, B_INSTR + 8, 4, g=0.08)
        _seagull(tr_l.b, T(B_INTRO + 16) + 1.0)
        _seagull(tr_l.b, T(B_INSTR + 20) + 0.5)
        _seagull(tr_l.b, T(B_OUT) + 1.0)
        # fuzz lead o instrumental (bluesy flat-7, Dorian bent minor 3rd)
        for k, m in enumerate(['C4', 'D4', 'Eb4', 'E4', 'G4', 'E4', 'C4',
                               'Bb3', 'C4', 'D4', 'Eb4', 'E4', 'G4', 'E4',
                               'D4', 'C4']):
            fuzz(tr_l.b, T(B_INSTR + k * 2), m, 1.6, g=0.11)
        # beep dung giua bai (TNK midpoint 1:28)
        _beep(tr_l.b, T(128) + 0.5)
        # outro: tack piano flailing + tan ra
        for k in range(60):
            m = ['C5', 'E5', 'G5', 'C5', 'D5', 'E5', 'F5', 'E5'][k % 8]
            tack(tr_l.b, T(B_OUT + k * 0.5), m, 0.25, g=0.045)
            if k > 40:
                break
        _seagull(tr_l.b, T(B_OUT + 24) + 0.5)

    def _vocals(self, tracks):
        lead_tr = Track('lead', pan=0.0, gain=1.0, verb=0.14, vocal=True,
                        squash=True)
        lesL = Track('leslie_L', pan=-0.7, gain=0.9, verb=0.16, vocal=True)
        lesR = Track('leslie_R', pan=0.7, gain=0.9, verb=0.16, vocal=True)

        v1 = _verse(B_V1, 'a', 'b')
        v2 = _verse(B_V2, 'a', 'b')
        v3 = _verse(B_V3, 'a', 'b')
        v4 = _verse(B_V4, 'a', 'b')
        v5 = _verse(B_V5, 'a', 'b')

        for cells, seed in ((v1, 1), (v2, 2)):
            lead(lead_tr.b, 0, cells, g=0.24, seed=seed)

        # Leslie tu nua sau (TNK): render rieng roi cho qua leslie()
        les_buf = buf()
        for cells, seed in ((v3, 3), (v4, 4), (v5, 5)):
            lead(les_buf, 0, cells, g=0.24, seed=seed)
        l, r = leslie(les_buf[:int(T(B_V5 + 32) * SR) + SR], rate=6.6,
                      depth=0.4)
        n = min(len(l), len(lesL.b))
        lesL.b[:n] += l[:n] * 0.7
        lesR.b[:n] += r[:n] * 0.7

        tracks += [lead_tr, lesL, lesR]

        # --------------------------------------------------- audit ----
        all_v = v1 + v2 + v3 + v4 + v5
        probs = audit(all_v, CHORDS, SCALE_CMIXO, 'vocal', allow=ALLOW,
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
        brs_tr = Track('brass_mello', pan=0.2, gain=1.0, verb=0.2)
        lop_tr = Track('loops', pan=-0.3, gain=1.0, verb=0.26)

        self._bass(bass_tr)
        self._drums(drum_tr)
        self._brass_loops(brs_tr, lop_tr)
        tracks += [bass_tr, drum_tr, brs_tr, lop_tr]
        if vocal:
            self._vocals(tracks)
