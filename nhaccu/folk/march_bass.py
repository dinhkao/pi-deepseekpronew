"""march_bass — trong tram hanh khuc

Trich nguyen van tu `geeselib/folk.py` cua geese-3d-country.
Chua: `march_bass`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _fadeout, _hp, _lp, _ramp
from .._core import put
from .._lib.folk import _T


def march_bass(b_, t0, dur=0.6, g=0.14, seed=0, tune=52.0):
    """Trong tram hanh khuc: mat da, khong co day snare, ngan rat lau."""
    L = int(dur * SR)
    R = np.random.default_rng(seed + 55)
    t = np.arange(L) / SR
    y = np.zeros(L)
    for k, (r, a, tau) in enumerate(((1.0, 1.0, 0.30), (1.59, 0.42, 0.16),
                                     (2.14, 0.24, 0.10), (2.30, 0.16, 0.07))):
        y += np.sin(2 * np.pi * tune * r * t + R.uniform(0, 6)) * a * np.exp(-t / tau)
    y += _lp(R.standard_normal(L), 900, 2) * np.exp(-t / 0.010) * 0.55
    y = np.tanh(_hp(y, 34, 2) * 1.7)
    put(b_, t0, _fadeout(_ramp(y, 1.5), 30.0), g * _T['march_bass'])
