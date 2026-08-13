"""celeste — celesta

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `celeste`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _fadeout, _hp, _lp, _ramp
from .._core import hz, nn, put
from .._lib.inst import damp
from .._lib.keys import _T


def celeste(b_, t0, m, dur=None, g=0.05, ring=2.2, seed=0):
    L = int((ring + 0.25) * SR)
    R = np.random.default_rng(seed + 6)
    t = np.arange(L) / SR
    f = hz(nn(m))
    y = np.zeros(L)
    for r, tau, a in ((1.0, 1.5, 1.0), (2.0, 0.9, 0.42), (3.01, 0.5, 0.22),
                      (4.02, 0.3, 0.12), (6.1, 0.16, 0.06)):
        y += np.sin(2 * np.pi * f * r * t + R.uniform(0, 6)) * a * np.exp(-t / tau)
    y = _lp(_hp(y, 200, 2), 8000, 2)
    if dur:
        y = damp(y, dur, ring=ring, rel=0.10)
    put(b_, t0, _fadeout(_ramp(y, 1.5), 30.0), g * _T['celeste'])
