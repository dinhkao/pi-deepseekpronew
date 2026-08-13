"""pizz — dan day gay pizzicato

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `pizz`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _fadeout, _ramp
from .._core import hz, nn, put


def pizz(b_, t0, m, dur, g=0.10, seed=0):
    """Pizzicato strings -- short, woody, section-wide."""
    m = nn(m)
    L = int(min(dur + 0.5, 1.2) * SR)
    t = np.arange(L) / SR
    out = np.zeros(L)
    for i in range(3):
        R = np.random.default_rng(5100 + m * 7 + seed * 3 + i)
        f = hz(m) * 2 ** (R.normal(0, 6) / 1200)
        x = np.zeros(L)
        for k, a, tau in [(1, 1.0, 0.26), (2, 0.5, 0.16), (3, 0.3, 0.10),
                          (4, 0.18, 0.07), (5, 0.10, 0.05)]:
            x += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * k * t + R.uniform(0, 6))
        x += _bp(R.standard_normal(L), 1200, 5000, 2) * np.exp(-t / 0.0025) * 0.4
        off = int(abs(R.normal(0.004, 0.003)) * SR)
        n = min(L - off, L)
        out[off:off + n] += x[:n] / 3
    put(b_, t0, _fadeout(_ramp(np.tanh(out * 1.2)), 25.0), g)
