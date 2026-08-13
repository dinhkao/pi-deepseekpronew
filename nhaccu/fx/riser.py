"""riser — tieng dang len

Trich nguyen van tu `geeselib/arrange.py` cua geese-3d-country.
Chua: `riser`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp
from .._core import T, put


def riser(b_, beat0, beats, g=0.05, seed=0, f0=200.0, f1=6000.0, kind='noise'):
    """Cau noi dang len truoc mot cu bung."""
    t0, t1 = T(beat0), T(beat0 + beats)
    L = int((t1 - t0) * SR)
    if L < 64:
        return
    R = np.random.default_rng(seed + 31)
    t = np.arange(L) / SR
    p = t / t[-1]
    if kind == 'noise':
        x = R.standard_normal(L)
        y = np.zeros(L)
        blk = 2048
        for i in range(0, L, blk):
            j = min(i + blk, L)
            fc = f0 * (f1 / f0) ** (p[i])
            y[i:j] = _bp(x[i:j], max(fc * 0.6, 60), min(fc * 1.8, 18000), 2)
        y *= p ** 1.6
    else:
        f = f0 * (f1 / f0) ** p
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * p ** 2
    put(b_, t0, y, g)
