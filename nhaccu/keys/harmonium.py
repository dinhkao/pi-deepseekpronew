"""harmonium — harmonium

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `harmonium`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _fadeout, env
from .._core import hz, nn, put


def harmonium(b_, t0, notes, dur, g=0.07, det=7.0, puff=1.0):
    L = int(dur * SR) + int(0.25 * SR)
    t = np.arange(L) / SR
    R = np.random.default_rng(int(t0 * 1000) % 9999)
    e = env(L, 0.075, 0.12, 0.94, 0.16)
    bell_ = 1 + 0.045 * np.sin(2 * np.pi * 4.3 * t + R.uniform(0, 6)) + 0.022 * np.sin(2 * np.pi * 0.9 * t)
    for m in np.atleast_1d(notes):
        f = hz(nn(m))
        x = np.zeros(L)
        for c in (0.0, det):
            ph = 2 * np.pi * np.cumsum(np.full(L, f * 2 ** (c / 1200))) / SR
            for k, a in [(1, 1.0), (2, .60), (3, .42), (4, .28), (5, .19),
                         (6, .14), (7, .09), (8, .07)]:
                if f * k > SR / 2.2:
                    break
                x += np.sin(ph * k + R.uniform(0, 6)) * a / (k ** 0.35)
        put(b_, t0, _fadeout(_bp(x, 90, 5200, 2) * e * bell_ * 0.045, 25.0), g)
    put(b_, t0, _bp(np.random.default_rng(7).standard_normal(L), 700, 3800, 2) * e * 0.025 * puff, g)
