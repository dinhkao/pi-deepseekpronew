"""banjo_roll — banjo cuon Scruggs

Trich nguyen van tu `geeselib/folk.py` cua geese-3d-country.
Chua: `banjo_roll`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._core import nn
from ..folk.banjo import banjo


def banjo_roll(b_, bar0, notes, span=4.0, g=0.09, sub=0.25, seed=0,
               pattern=(0, 2, 1, 2), drone_note=None, hum=None):
    """Cuon banjo kieu Scruggs: mot mau ngon tay co dinh chay tren cac not
    hop am. `drone_note` la day thu 5 — no KHONG doi theo hop am, do la dac
    diem cua cay dan, va cung la thu tao ra cam giac "khong tro ve"."""
    from .._core import HUM
    H = hum or HUM
    v = sorted(nn(x) for x in notes)
    n = int(round(span / sub))
    for k in range(n):
        bt = bar0 + k * sub
        idx = pattern[k % len(pattern)]
        if drone_note is not None and k % len(pattern) == len(pattern) - 1:
            m = nn(drone_note)
        else:
            m = v[idx % len(v)]
        banjo(b_, H.t(bt), m, sub * 0.95, g=H.g(g, bt) * (1.0 if k % 4 == 0 else 0.78),
              seed=seed + k)
