"""jugbass — bass thoi vo binh

Trich nguyen van tu `geeselib/folk.py` cua geese-3d-country.
Chua: `jugbass`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _lp, _ramp, env
from .._core import hz, nn, put
from .._lib.folk import _T


def jugbass(b_, t0, m, dur, g=0.14, seed=0):
    """Tieng thoi vao vo binh: gan nhu chi co mot boi am, rat nhieu hoi."""
    L = int((dur + 0.10) * SR)
    R = np.random.default_rng(seed + 21)
    t = np.arange(L) / SR
    f = hz(nn(m))
    y = np.sin(2 * np.pi * f * t) + 0.22 * np.sin(4 * np.pi * f * t)
    y += _bp(R.standard_normal(L), max(f * 2, 260), 1400, 2) * 0.30
    a = env(L, 0.030, 0.06, 0.80, 0.055)
    y = _lp(y * a, 1600, 2)
    put(b_, t0, _ramp(y, 4.0), g * _T['jugbass'])
