"""accordion — accordion

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `accordion`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _fadeout, env
from .._core import hz, nn, put


def accordion(b_, t0, notes, dur, g=0.07, det=11.0):
    L = int(dur * SR) + int(0.15 * SR)
    t = np.arange(L) / SR
    R = np.random.default_rng(int(t0 * 57) % 9999)
    e = env(L, 0.045, 0.09, 0.93, 0.11)
    bel = 1 + 0.055 * np.sin(2 * np.pi * 1.7 * t + R.uniform(0, 6))
    for m in np.atleast_1d(notes):
        f = hz(nn(m))
        for c in (-det, 0.0, det):
            ph = 2 * np.pi * np.cumsum(np.full(L, f * 2 ** (c / 1200))) / SR
            x = np.zeros(L)
            for k, a in [(1, 1.0), (2, .50), (3, .42), (4, .26), (5, .20),
                         (6, .14), (7, .10), (8, .07)]:
                if f * k > SR / 2.2:
                    break
                x += np.sin(ph * k + R.uniform(0, 6)) * a / (k ** 0.3)
            put(b_, t0, _fadeout(_bp(x, 120, 5600, 2) * e * bel * 0.030, 22.0), g)
