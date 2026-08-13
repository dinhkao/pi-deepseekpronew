"""upright — contrabass (gay)

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `upright`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _hp, _lp
from .._core import hz, nn, put


def upright(b_, t0, m, dur, g=0.30, gl=0.0, growl=0.22):
    """Double bass, pizzicato: thumpy, woody, decays fast."""
    m = nn(m)
    dur = max(float(dur), 0.06)
    rel = min(0.10, dur * 0.35 + 0.02)
    L = int((min(dur, 2.0) + rel) * SR)
    t = np.arange(L) / SR
    R = np.random.default_rng(4400 + m)
    f0 = hz(m)
    ph = 2 * np.pi * np.cumsum(np.full(L, f0) * (1 + 0.010 * np.exp(-t / 0.05))) / SR
    x = np.zeros(L)
    for k, a, tau in [(1, 1.0, 0.75), (2, 0.52, 0.44), (3, 0.34, 0.30),
                      (4, 0.22, 0.20), (5, 0.15, 0.14), (6, 0.10, 0.10),
                      (7, 0.07, 0.08), (9, 0.04, 0.06)]:
        x += a * np.exp(-t / tau) * np.sin(ph * k + R.uniform(0, 6))
    thud = _lp(R.standard_normal(L), 260, 2) * np.exp(-t / 0.016) * 0.7
    click = _bp(R.standard_normal(L), 900, 3600, 2) * np.exp(-t / 0.0035) * 0.55
    y = _lp(x + thud + click, 3000, 2)
    y = np.tanh((_lp(y, 220, 2) * 0.8 + y * 0.6
                 + np.tanh(_bp(y, 400, 2400, 2) * 3.5) * growl) * 1.1)
    y = _hp(y, 40, 2)
    rn = int(rel * SR)
    if 0 < rn < L:
        y[-rn:] *= np.linspace(1, 0, rn) ** 1.2
    put(b_, t0, y, g)
