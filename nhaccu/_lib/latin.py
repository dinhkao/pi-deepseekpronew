"""Helper dung chung, trich tu greeplib/latin.py.

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `_steps`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


def _steps(P, kit, bus, beat0, row, fn, sub=0.25, vmap=None, arc=1.0, v=1.0):
    vmap = vmap or {}
    for i, c in enumerate(row):
        if c == '.':
            continue
        vv, kwargs = vmap.get(c, (1.0, {}))
        P.hit(bus, beat0 + i * sub, int(i * (0.25 / sub)) % 16,
              fn(vel=v * vv, **kwargs), v=1.0, arc=arc)
