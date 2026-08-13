"""bones — go xuong

Trich nguyen van tu `geeselib/folk.py` cua geese-3d-country.
Chua: `bones`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _hp
from .._core import put
from .._lib.folk import _T


def bones(b_, t0, dur=0.12, g=0.08, seed=0):
    """Go xuong / thia: hai cu go go rat ngan, cao do xac dinh."""
    L = int(dur * SR)
    R = np.random.default_rng(seed + 99)
    t = np.arange(L) / SR
    y = np.zeros(L)
    for f, off, a in ((1450, 0.0, 1.0), (1180, 0.028, 0.7)):
        s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.4 * t))
        s = s * np.exp(-t / 0.006)
        y += np.concatenate([np.zeros(int(off * SR)), s])[:L] * a
    put(b_, t0, _hp(y, 700, 2), g * _T['bones'])
