"""marimba — marimba

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `marimba`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _fadeout, _ramp
from .._core import hz, nn, put


def marimba(b_, t0, m, dur, g=0.10, seed=0, ring=None):
    m = nn(m)
    ring = dur if ring is None else ring
    L = int((min(ring, 3.0) + 0.06) * SR)
    t = np.arange(L) / SR
    R = np.random.default_rng(2300 + m + seed)
    f = hz(m)
    x = np.zeros(L)
    for r, a, tau in [(1.0, 1.0, 0.62), (3.9, 0.34, 0.16), (9.2, 0.14, 0.07), (2.0, 0.05, 0.20)]:
        ff = f * r
        if ff > SR / 2.2:
            continue
        x += a * np.exp(-t / tau) * np.sin(2 * np.pi * ff * t + R.uniform(0, 6))
    x += _bp(R.standard_normal(L), 900, 4500, 2) * np.exp(-t / 0.0025) * 0.5
    put(b_, t0, _fadeout(_ramp(x * np.minimum(1, t * 3000)), 40.0), g)
