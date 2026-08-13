"""walk — walking bass

Trich nguyen van tu `greeplib/bassgtr.py` cua geese-3d-country.
Chua: `walk`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


def walk(player, prog, beat0, reps=1, base=None, swing=0.0, vel=0.9):
    """A walking line: root, an approach from a step away, chord tones."""
    ev = prog.events(beat0, reps)
    for i, (bt, d, vo, bs, sym, pcs) in enumerate(ev):
        nxt = ev[(i + 1) % len(ev)][3]
        root = bs + 12 if bs < 33 else bs
        third = root + (3 if 3 in [(p - bs) % 12 for p in pcs] else 4)
        fifth = root + 7
        appr = (nxt + 12 if nxt < 33 else nxt) + (-1 if i % 2 else 1)
        steps = [root, third, fifth, appr]
        n = int(round(d))
        for k in range(n):
            player.note(bt + k, 1.0, steps[k % 4], vel * (1.0 if k == 0 else 0.82))
