"""ebow — ebow (day ngan lien tuc)

Trich nguyen van tu `geeselib/gtr.py` cua geese-3d-country.
Chua: `ebow`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _ramp
from .._core import hz, nn, put
from .._lib.gtr import _T, gtr_amp


def ebow(b_, t0, m, dur, g=0.10, seed=0, drive=5.0, swell_s=0.35, bright=1.0):
    """EBow: day duoc kich lien tuc — khong co tieng gay, chi co dang len."""
    L = int((dur + 0.35) * SR)
    R = np.random.default_rng(seed + 707)
    f = hz(nn(m))
    t = np.arange(L) / SR
    ph = 2 * np.pi * f * t * (1 + 0.0006 * np.sin(2 * np.pi * 0.7 * t + R.uniform(0, 6)))
    y = np.zeros(L)
    for k in range(1, 13):
        y += np.sin(ph * k + R.uniform(0, 6)) / (k ** 1.55)
    a = np.clip(t / max(swell_s, 1e-3), 0, 1) ** 1.6
    rel = np.clip((dur + 0.30 - t) / 0.30, 0, 1)
    y = y * a * rel
    y = gtr_amp(y, drive=drive, tone=0.55, bright=bright, sag=0.2)
    put(b_, t0, _ramp(y, 6.0), g * _T['ebow'])
