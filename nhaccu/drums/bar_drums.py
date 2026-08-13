"""bar_drums — danh mot o nhip

Trich nguyen van tu `greeplib/drums.py` cua geese-3d-country.
Chua: `VS`, `bar_drums`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


# ------------------------------------------------------------ pattern lang --
# K kick | S snare | s medium | g ghost | r rimshot | x cross-stick
# H hat closed | h soft hat | o open hat | R ride | B ride bell | C crash
# T concert tom | t tambourine | k shaker | . rest
VS = {'S': 1.00, 's': 0.62, 'g': 0.30}


def bar_drums(P, bar_beat, pat, arc=1.0, vk=1.0, vs=1.0, vh=0.55,
              kmode='acoustic', ktune=48.0, stune=205.0, ttune=150.0,
              hopen=0.55, swing=0.0, ride_bell=False, sub=0.25, steps=16):
    """Read a step-string and play one bar. `sub` is the step length in beats."""
    for inst, row in pat.items():
        for i, c in enumerate(row[:steps]):
            if c == '.':
                continue
            sw = swing * sub * 0.5 if (i % 2 == 1) else 0.0
            b = bar_beat + i * sub + sw
            if c == 'K':
                P.K(b, i, vk * 0.95, arc=arc, mode=kmode, tune=ktune)
            elif c == 'k' and inst == 'K':
                P.K(b, i, vk * 0.62, arc=arc, mode=kmode, tune=ktune)
            elif c in 'Ssg':
                P.S(b, i, vs * VS[c], art=('ghost' if c == 'g' else 'center'), arc=arc, tune=stune)
            elif c == 'r':
                P.S(b, i, vs * 0.95, art='rim', arc=arc, tune=stune)
            elif c == 'x':
                P.S(b, i, vs * 0.70, art='cross', arc=arc, tune=stune)
            elif c == 'f':
                P.S(b, i, vs, art='flam', arc=arc, tune=stune)
            elif c == 'H':
                P.H(b, i, vh, 0.0, 'tip', arc=arc)
            elif c == 'h':
                P.H(b, i, vh * 0.52, 0.0, 'tip', arc=arc)
            elif c == 'o':
                P.H(b, i, vh * 1.15, hopen, 'edge', arc=arc, choke_beat=b + sub)
            elif c == 'R':
                P.RD(b, i, vh * 1.25, bell=ride_bell, arc=arc)
            elif c == 'B':
                P.RD(b, i, vh * 1.5, bell=True, arc=arc)
            elif c == 'C':
                P.CR(b, i, vk * 0.85)
            elif c == 'T':
                P.CT(b, i, vs * 0.8, tune=ttune, arc=arc)
            elif c == 't':
                P.TB(b, i, vh * 0.9, arc=arc)
            elif c == 'z':
                P.SH(b, i, vh * 0.9, arc=arc)
