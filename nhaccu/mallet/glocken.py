"""glocken — glockenspiel

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `glocken`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _fadeout, _hp, _ramp
from .._core import hz, nn, put
from .._lib.inst import damp
from .._lib.keys import _T


def glocken(b_, t0, m, dur=None, g=0.05, ring=1.6, seed=0):
    L = int((ring + 0.2) * SR)
    R = np.random.default_rng(seed + 5)
    t = np.arange(L) / SR
    f = hz(nn(m))
    y = np.zeros(L)
    for k, (r, tau, a) in enumerate(((1.0, 0.95, 1.0), (2.76, 0.42, 0.55),
                                     (5.40, 0.20, 0.30), (8.93, 0.11, 0.16),
                                     (13.3, 0.06, 0.08))):
        y += np.sin(2 * np.pi * f * r * t + R.uniform(0, 6)) * a * np.exp(-t / tau)
    y += _bp(R.standard_normal(L), 4000, 12000, 2) * np.exp(-t / 0.004) * 0.5
    y = _hp(y, 400, 2)
    if dur:
        y = damp(y, dur, ring=ring, rel=0.08)
    put(b_, t0, _fadeout(_ramp(y, 0.8), 25.0), g * _T['glocken'])
