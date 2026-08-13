"""melodica — melodica

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `melodica`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _fadeout, _lp, _ramp, env
from .._core import hz, nn, put


def melodica(b_, t0, m, dur, g=0.10, seed=0):
    m = nn(m)
    L = int(dur * SR) + int(0.20 * SR)
    t = np.arange(L) / SR
    R = np.random.default_rng(2100 + int(m) * 5 + seed)
    f0 = hz(m)
    bend = 1 - 0.016 * np.exp(-t / 0.040)
    vib = 1 + 0.0032 * np.sin(2 * np.pi * 5.1 * t + R.uniform(0, 6)) * np.clip((t - 0.25) * 2.5, 0, 1)
    ph = 2 * np.pi * np.cumsum(f0 * bend * vib) / SR
    x = np.zeros(L)
    for k, a in [(1, 1.00), (2, 0.26), (3, 0.52), (4, 0.14), (5, 0.28), (6, 0.08), (7, 0.15), (9, 0.07)]:
        if f0 * k < SR / 2.2:
            x += a * np.sin(ph * k + R.uniform(0, 6))
    chiff = _bp(R.standard_normal(L), 1200, 5200, 2) * np.exp(-t / 0.030) * 0.55
    air = _bp(R.standard_normal(L), 900, 4000, 2) * 0.030
    x = (x * 0.62 + chiff + air) * env(L, 0.022, 0.10, 0.88, min(0.14, dur * 0.35 + 0.04))
    put(b_, t0, _fadeout(_ramp(_lp(x, 7000, 2), 1.0), 22.0), g)
