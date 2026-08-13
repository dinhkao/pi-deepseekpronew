"""glass — ly thuy tinh

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `glass`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _lp, _ramp, env
from .._core import hz, nn, put


def glass(b_, t0, m, dur, g=0.05, voices=4, cents=8.0, cut=2600, seed=0,
          ring=None):
    """Glassy pad -- inharmonic partials, many detuned voices, slow attack."""
    m = nn(m)
    ring = dur if ring is None else ring
    f0 = hz(m)
    L = int((min(ring, 8.0) + 0.12) * SR)
    t = np.arange(L) / SR
    R = np.random.default_rng(1200 + m * 7 + seed * 13)
    ratios = np.array([1.0, 2.66, 4.83, 7.10, 9.60, 12.40])
    amps = np.array([1.0, 0.40, 0.30, 0.22, 0.16, 0.11])
    det = np.linspace(-1, 1, max(voices, 2)) * cents + R.normal(0, 1.6, max(voices, 2))
    x = np.zeros(L)
    for d in det[:voices]:
        for r, a in zip(ratios, amps):
            f = f0 * r * 2 ** (d / 1200.0)
            if f < SR / 2.2:
                x += a * np.sin(2 * np.pi * f * t + R.uniform(0, 6.28))
    x /= max(voices, 1)
    x *= env(L, 0.34, 0.25, 0.86, min(0.55, dur * 0.35 + 0.12))
    put(b_, t0, _ramp(_lp(x, cut, 2), 3.0), g)
