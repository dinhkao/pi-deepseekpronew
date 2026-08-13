"""Paper Face — bai 2, DNA: "Eleanor Rigby" (E Dorian, string octet).

Gimmick: khong co trong. String octet 4 be (vln1 vln2 vla cello) bowed chat,
inner voice xuong nua cung D-C#-C-B o refrain, mo dau bang VI-i (C-Em),
appoggiatura 6-5 tren C ("added-sixth" kieu Beatles).
"""
from __future__ import annotations

import numpy as np

from nhaccu._core import T, buf
from nhaccu._dsp import SR
from nhaccu.string_section.strings import strings
from nhaccu.string_section.pizz import pizz
from nhaccu.voice import lead, vharm

from songs._engine import Song, Track, audit, audit_vocal_f0

# -------------------------------------------------------------- form marks --

B_INTRO = 0     # 8 bars (C Em C Em)
B_V1 = 32       # 5 bars verse
B_R1 = 52       # 8 bars refrain
B_V2 = 84       # 5 bars
B_R2 = 104      # 8 bars
B_BR = 136      # 8 bars bridge (= intro music)
B_V3 = 168      # 5 bars
B_R3 = 188      # 8 bars
B_OUT = 220     # 10 bars outro (refrain couplet + tag)
END = 260

# chords: (start, end, [pcs], sym) — theo Pollack: Em, C, Am, A passing
def _ch(beat, n, sym, pcs):
    return (beat, beat + n, pcs, sym)

CHORDS = []
for b0 in (B_INTRO, B_BR):
    CHORDS += [_ch(b0, 8, 'C', [0, 4, 7]), _ch(b0 + 8, 8, 'Em', [4, 7, 11]),
               _ch(b0 + 16, 8, 'C', [0, 4, 7]), _ch(b0 + 24, 8, 'Em', [4, 7, 11])]
for bv in (B_V1, B_V2, B_V3):
    CHORDS += [_ch(bv, 12, 'Em', [4, 7, 11]), _ch(bv + 12, 4, 'C', [0, 4, 7]),
               _ch(bv + 16, 4, 'Em', [4, 7, 11])]
for br in (B_R1, B_R2, B_R3):
    # inner voice D C# C B -> nguy Em, A(passing), C, Em
    for k, (n, sym, pcs) in enumerate([(4, 'Em', [4, 7, 11]), (4, 'A', [9, 1, 4]),
                                       (4, 'C', [0, 4, 7]), (4, 'Em', [4, 7, 11])]):
        CHORDS.append(_ch(br + k * 4, n, sym, pcs))
        CHORDS.append(_ch(br + 16 + k * 4, n, sym, pcs))
CHORDS += [_ch(B_OUT, 8, 'Em', [4, 7, 11]), _ch(B_OUT + 8, 4, 'A', [9, 1, 4]),
           _ch(B_OUT + 12, 4, 'C', [0, 4, 7]), _ch(B_OUT + 16, 24, 'Em', [4, 7, 11])]

SCALE_EDOR = {4, 6, 7, 9, 11, 1, 2}     # E F# G A B C# D
ALLOW = {'C2', 'C3', 'C4', 'C5'}        # C-natural cua harmony (VI chord)
TENSIONS = {4: {2, 9}, 0: {11, 2}, 9: {11, 2}}   # maj7/9th/11th mau Beatles


# ------------------------------------------------------------- lyrics/cells --

def _verse1(b0):
    return [
        (b0 + 0.5, 1, 'B3', 'pa', 1.0), (b0 + 1.5, 1, 'B3', 'per', 1.0),
        (b0 + 2.5, 1, 'B3', 'face', 1.0), (b0 + 3.5, 1, 'C#4', 'on', 1.0),
        (b0 + 4.5, 1, 'B3', 'the', 1.0), (b0 + 5.5, 1, 'A3', 'mid', 1.0),
        (b0 + 6.5, 1, 'B3', 'night', 1.0), (b0 + 7.5, 3, 'C#4', 'train', 1.0),
        (b0 + 11.5, 1, 'B3', 'pa', 1.0), (b0 + 12.5, 1, 'B3', 'per', 1.0),
        (b0 + 13.5, 1, 'B3', 'face', 1.0), (b0 + 14.5, 1, 'D4', 'in', 1.0),
        (b0 + 15.5, 1, 'C#4', 'the', 1.0), (b0 + 16.5, 1, 'B3', 'fall', 1.0),
        (b0 + 17.5, 1, 'A3', 'ing', 1.0), (b0 + 18.5, 2, 'B3', 'rain', 1.0),
        (b0 + 21.5, 0.75, 'E4', 'fold', 1.0), (b0 + 22.25, 0.75, 'D4', 'ing', 1.0),
        (b0 + 23, 0.75, 'C#4', 'cranes', 1.0), (b0 + 23.75, 0.75, 'B3', 'of', 1.0),
        (b0 + 24.5, 1.5, 'B3', 'grey', 1.0),
    ]


def _verse2(b0):
    return [
        (b0 + 0.5, 1, 'B3', 'pa', 1.0), (b0 + 1.5, 1, 'B3', 'per', 1.0),
        (b0 + 2.5, 1, 'B3', 'face', 1.0), (b0 + 3.5, 1, 'C#4', 'in', 1.0),
        (b0 + 4.5, 1, 'B3', 'a', 1.0), (b0 + 5.5, 1, 'A3', 'crowd', 1.0),
        (b0 + 6.5, 1, 'B3', 'ed', 1.0), (b0 + 7.5, 3, 'C#4', 'room', 1.0),
        (b0 + 11.5, 1, 'B3', 'pa', 1.0), (b0 + 12.5, 1, 'B3', 'per', 1.0),
        (b0 + 13.5, 1, 'B3', 'face', 1.0), (b0 + 14.5, 1, 'D4', 'with', 1.0),
        (b0 + 15.5, 1, 'C#4', 'a', 1.0), (b0 + 16.5, 1, 'B3', 'si', 1.0),
        (b0 + 17.5, 1, 'A3', 'lent', 1.0), (b0 + 18.5, 2, 'B3', 'tune', 1.0),
        (b0 + 21.5, 0.75, 'E4', 'wait', 1.0), (b0 + 22.25, 0.75, 'D4', 'ing', 1.0),
        (b0 + 23, 0.75, 'C#4', 'for', 1.0), (b0 + 23.75, 1.25, 'B3', 'the', 1.0),
        (b0 + 25, 1.0, 'A3', 'light', 1.0),
    ]


def _verse3(b0):
    return [
        (b0 + 0.5, 1, 'B3', 'pa', 1.0), (b0 + 1.5, 1, 'B3', 'per', 1.0),
        (b0 + 2.5, 1, 'B3', 'face', 1.0), (b0 + 3.5, 1, 'C#4', 'in', 1.0),
        (b0 + 4.5, 1, 'B3', 'the', 1.0), (b0 + 5.5, 1, 'A3', 'fad', 1.0),
        (b0 + 6.5, 1, 'B3', 'ing', 1.0), (b0 + 7.5, 3, 'C#4', 'glow', 1.0),
        (b0 + 11.5, 1, 'B3', 'pa', 1.0), (b0 + 12.5, 1, 'B3', 'per', 1.0),
        (b0 + 13.5, 1, 'B3', 'face', 1.0), (b0 + 14.5, 1, 'D4', 'that', 1.0),
        (b0 + 15.5, 1, 'C#4', 'I', 1.0), (b0 + 16.5, 1, 'B3', 'used', 1.0),
        (b0 + 17.5, 1, 'A3', 'to', 1.0), (b0 + 18.5, 2, 'B3', 'know', 1.0),
        (b0 + 21.5, 0.75, 'E4', 'no', 1.0), (b0 + 22.25, 0.75, 'D4', 'one', 1.0),
        (b0 + 23, 0.75, 'C#4', 'sees', 1.0), (b0 + 23.75, 0.75, 'B3', 'be', 1.0),
        (b0 + 24.5, 0.75, 'A3', 'hind', 1.0), (b0 + 25.25, 1.75, 'B3', 'the', 1.0),
        (b0 + 27, 1.5, 'E3', 'show', 1.0),
    ]


def _refrain(b0, top):
    """top=1: dinh E4; top=2: dinh G4 (lan 2 phai xa hon — Pollack)."""
    if top == 1:
        n1, n2, n3, n4 = 'E4', 'D4', 'C#4', 'B3'
        tail1, tail2 = ('A3', 1.0, 'in'), ('B3', 1.0, 'their')
        tail3, tail4 = ('C#4', 2.0, 'plac'), ('B3', 4.0, 'es')
    else:
        n1, n2, n3, n4 = 'G4', 'F#4', 'E4', 'D4'
        tail1, tail2 = ('B3', 1.0, 'in'), ('A3', 1.0, 'their')
        tail3, tail4 = ('B3', 2.0, 'plac'), ('E4', 4.0, 'es')
    return [
        (b0 + 0.5, 1, n1, 'all', 1.0), (b0 + 1.5, 1, n1, 'the', 1.0),
        (b0 + 2.5, 1, n1, 'pa', 1.0), (b0 + 3.5, 1, n2, 'per', 1.0),
        (b0 + 4.5, 1, n3, 'fac', 1.0), (b0 + 5.5, 2, n4, 'es', 1.0),
        (b0 + 7.5, tail1[1], tail1[0], tail1[2], 1.0),
        (b0 + 8.5, tail2[1], tail2[0], tail2[2], 1.0),
        (b0 + 9.5, tail3[1], tail3[0], tail3[2], 1.0),
        (b0 + 11.5, tail4[1], tail4[0], tail4[2], 1.0),
        (b0 + 16.5, 1, n1, 'all', 1.0), (b0 + 17.5, 1, n1, 'the', 1.0),
        (b0 + 18.5, 1, n1, 'pa', 1.0), (b0 + 19.5, 1, n2, 'per', 1.0),
        (b0 + 20.5, 1, n3, 'fac', 1.0), (b0 + 21.5, 2, n4, 'es', 1.0),
        (b0 + 23.5, tail1[1], tail1[0], tail1[2], 1.0),
        (b0 + 24.5, tail2[1], tail2[0], tail2[2], 1.0),
        (b0 + 25.5, tail3[1], tail3[0], tail3[2], 1.0),
        (b0 + 27.5, tail4[1], tail4[0], tail4[2], 1.0),
    ]


# ------------------------------------------------------------ string parts --

def _vln(b, t0, m, dur, g=0.09, atk=0.05, seed=1):
    strings(b, t0, m, dur, g=g, atk=atk, seed=seed)


class PaperFace(Song):
    name = 'song02_paper_face'
    bpm = 104
    beats = END
    human = 4
    laid = 0.004

    # ------------------------------------------------------ arrangement ----
    def _strings(self, tr_v, tr_c):
        """vln1+vln2 -> tr_v (trai/phai), vla+cello -> tr_c."""
        # ---------------- intro/bridge: C Em x2, chop ngat ----------------
        for b0 in (B_INTRO, B_BR):
            # warp: quarter notes chat (short bows)
            for bar in range(0, 32, 4):
                pc, sym = (0, 'C') if bar % 8 < 4 else (4, 'Em')
                roots = {0: ['C4', 'E4', 'G4', 'C5'], 4: ['E4', 'G4', 'B4', 'E5']}
                third = {0: ['G3', 'C4', 'E4', 'G4'], 4: ['B3', 'E4', 'G4', 'B4']}
                for k in range(4):
                    _vln(tr_v.b, T(b0 + bar + k), roots[pc][k], 0.35, g=0.085)
                    _vln(tr_v.b, T(b0 + bar + k), third[pc][k], 0.35, g=0.075,
                         seed=5)
                for k in range(4):
                    _vln(tr_c.b, T(b0 + bar + k), 'E3' if pc == 4 else 'C3',
                         0.35, g=0.12)
            # melodic counter-figure cello (Pollack: "continuously varied")
            for k, m in enumerate(['C4', 'B3', 'A3', 'B3', 'G3', 'A3', 'B3', 'G3']):
                _vln(tr_c.b, T(b0 + 16 + k * 0.5) + 0.25, m, 0.4, g=0.075)

        # ---------------- verses: warp + cello counters ----------------
        for bv in (B_V1, B_V2, B_V3):
            for bar in range(0, 5):
                b0 = bv + bar * 4
                if bar < 3:
                    top = ['E4', 'G4', 'B4', 'G4']
                    mid = ['B3', 'E4', 'G4', 'E4']
                    bass_n = 'E2'
                elif bar == 3:
                    top = ['G4', 'E4', 'C4', 'E4']
                    mid = ['C4', 'G3', 'E3', 'G3']
                    bass_n = 'C2'
                else:
                    top = ['E4', 'B3', 'G3', 'B3']
                    mid = ['B3', 'G3', 'E3', 'G3']
                    bass_n = 'E2'
                for k in range(4):
                    _vln(tr_v.b, T(b0 + k), top[k], 0.4, g=0.072)
                    _vln(tr_v.b, T(b0 + k), mid[k], 0.4, g=0.062, seed=9)
                    _vln(tr_c.b, T(b0 + k), bass_n, 0.4, g=0.125)
            # cello emphatic low E mid-bar 3 (tre sau chord — chi tiet ER)
            _vln(tr_c.b, T(bv + 10.5), 'E2', 1.2, g=0.10)
            # appoggiatura 6-5: vln tren C chord cuoi verse (A4 -> G4)
            _vln(tr_v.b, T(bv + 15.5), 'A4', 0.5, g=0.07)
            _vln(tr_v.b, T(bv + 16.0), 'G4', 0.6, g=0.07)

        # ---------------- refrains: inner voice D C# C B ----------------
        for br in (B_R1, B_R2, B_R3):
            for half in (0, 16):
                inner = ['D4', 'C#4', 'C4', 'B3']
                bass_n = ['E2', 'A2', 'C2', 'E2']
                for k in range(4):
                    _vln(tr_c.b, T(br + half + k * 4), inner[k], 4.0, g=0.085)
                    _vln(tr_c.b, T(br + half + k * 4), bass_n[k], 4.0, g=0.085)
                # top strings: pad nhe + violin mockingbird tail
                for k in range(2):
                    _vln(tr_v.b, T(br + half + k * 8), 'E4', 7.5, g=0.055)
                _vln(tr_v.b, T(br + half + 7.0), 'E5', 0.5, g=0.06, seed=3)
                _vln(tr_v.b, T(br + half + 7.5), 'D5', 0.5, g=0.06, seed=3)
                _vln(tr_v.b, T(br + half + 8.0), 'C#5', 0.5, g=0.06, seed=3)
                _vln(tr_v.b, T(br + half + 8.5), 'B4', 0.5, g=0.06, seed=3)

        # ---------------- outro: mockingbird in quarter notes ----------------
        for k, m in enumerate(['E4', 'D4', 'C#4', 'B3']):
            _vln(tr_v.b, T(B_OUT + k * 2), m, 1.8, g=0.075)
        for k in range(4):
            _vln(tr_c.b, T(B_OUT + k * 4), 'E2', 4.0, g=0.085)
        _vln(tr_v.b, T(B_OUT + 16), 'E4', 4.0, g=0.06)
        _vln(tr_c.b, T(B_OUT + 16), 'E2', 4.0, g=0.09)
        _vln(tr_c.b, T(B_OUT + 20), 'E3', 4.0, g=0.08)

    # ------------------------------------------------------------ vocals ----
    def _vocals(self, tracks):
        lead_tr = Track('lead', pan=0.0, gain=1.0, verb=0.16, vocal=True,
                        squash=True)
        tag_tr = Track('tag', pan=-0.3, gain=0.8, verb=0.14, vocal=True)

        v1 = _verse1(B_V1)
        v2 = _verse2(B_V2)
        v3 = _verse3(B_V3)
        r1 = _refrain(B_R1, 1)
        r2 = _refrain(B_R2, 2)
        r3 = _refrain(B_R3, 2)
        r_out = _refrain(B_OUT, 2)

        for cells, seed in ((v1, 1), (v2, 2), (v3, 3), (r1, 4), (r2, 5),
                            (r3, 6), (r_out, 7)):
            lead(lead_tr.b, 0, cells, g=0.24, seed=seed, style='soft')
            # Paul double-track refrain
            if cells in (r1, r2, r3, r_out):
                lead(lead_tr.b, 0, cells, g=0.09, seed=seed + 40,
                     style='soft')

        # John-style sotto-voce tag o intro/bridge/outro
        tag = [(0, 1.0, 'E3', 'pa', 1.0), (1, 1.0, 'D3', 'per', 1.0),
               (2, 1.0, 'C#3', 'face', 1.0), (3, 3.0, 'B2', None, 1.0)]
        lead(tag_tr.b, B_INTRO + 16, tag, g=0.20, seed=11, style='soft')
        lead(tag_tr.b, B_BR + 16, tag, g=0.20, seed=12, style='soft')
        lead(tag_tr.b, B_OUT + 16, tag, g=0.18, seed=13, style='soft')

        tracks += [lead_tr, tag_tr]

        # --------------------------------------------------- audit ----
        all_v = v1 + r1 + v2 + r2 + v3 + r3 + r_out
        probs = audit(all_v, CHORDS, SCALE_EDOR, 'vocal', allow=ALLOW,
                      tensions=TENSIONS)
        for p in probs:
            print('  [AUDIT]', p)
        probs, n_ok = audit_vocal_f0(all_v, lead_tr.b, 'lead-f0', None)
        print('  [F0] kiem tra %d not hat, %d van de' % (n_ok, len(probs)))
        for p in probs:
            print('  [F0]', p)

    # ------------------------------------------------------------- build ----
    def build(self, tracks, vocal=True):
        vln_tr = Track('vln', pan=-0.45, gain=1.0, verb=0.22)
        vla_tr = Track('vla_cello', pan=0.45, gain=1.0, verb=0.22)
        self._strings(vln_tr, vla_tr)
        tracks += [vln_tr, vla_tr]
        if vocal:
            self._vocals(tracks)
