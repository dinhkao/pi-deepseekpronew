"""washboard — ban giat

Trich nguyen van tu `geeselib/folk.py` cua geese-3d-country.
Chua: `washboard`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _hp
from .._core import put
from .._lib.folk import _T


def washboard(b_, t0, dur=0.25, g=0.09, seed=0, strokes=5):
    """Ban giat: mot cai gat keo qua nhieu ganh — nhieu cu go rat gan nhau."""
    L = int(dur * SR)
    R = np.random.default_rng(seed + 88)
    y = np.zeros(L)
    for k in range(strokes):
        off = int((k / strokes) * dur * 0.7 * SR + R.uniform(0, 0.004) * SR)
        seg = _bp(R.standard_normal(L), 2200, 9000, 2) * np.exp(-np.arange(L) / (0.004 * SR))
        y += np.concatenate([np.zeros(off), seg])[:L] * (1.0 - k * 0.11)
    put(b_, t0, _hp(y, 1500, 2), g * _T['washboard'])
