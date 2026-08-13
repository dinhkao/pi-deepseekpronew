"""bell — chuong

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `bell`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _fadeout, _hp
from .._core import hz, nn, put


def bell(b_, t0, m, dur, g=0.05, seed=0):
    m = nn(m)
    L = int(min(dur, 6.0) * SR) + int(0.3 * SR)
    t = np.arange(L) / SR
    f = hz(m)
    R = np.random.default_rng(1100 + m * 3 + seed)
    x = np.zeros(L)
    for r, a, tau in [(1.0, 1.0, 1.5), (2.00, 0.52, 0.95), (3.01, 0.30, 0.62),
                      (4.17, 0.20, 0.42), (5.43, 0.12, 0.30), (6.79, 0.07, 0.20)]:
        if f * r > SR / 2.2:
            break
        x += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * r * (1 + R.normal(0, 0.0012)) * t + R.uniform(0, 6.28))
    x *= np.minimum(1, t * 3000)
    put(b_, t0, _fadeout(_hp(x, 200, 2), 140.0), g)
