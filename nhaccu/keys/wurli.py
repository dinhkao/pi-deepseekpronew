"""wurli — Wurlitzer

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `wurli`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _fadeout, _lp
from .._core import hz, nn, put


def wurli(b_, t0, m, dur, g=0.13, det=0.0):
    m = nn(m)
    L = int(max(dur, 0.75) * SR) + int(0.4 * SR)
    t = np.arange(L) / SR
    f = hz(m) * 2 ** (det / 1200)
    ph = 2 * np.pi * np.cumsum(np.full(L, f)) / SR
    idx = 2.1 * np.exp(-t * 5.5) + 0.35
    x = np.sin(ph + idx * np.sin(ph * 2)) + np.sin(ph * 1.001) * 0.4
    x *= np.exp(-t * 2.4) * np.minimum(1, t * 260)
    x *= (1 + 0.10 * np.sin(2 * np.pi * 5.4 * t))
    put(b_, t0, _fadeout(np.tanh(_lp(x, 4200, 2) * 1.3), 30.0), g)
