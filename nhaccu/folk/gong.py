"""gong — cong

Trich nguyen van tu `geeselib/folk.py` cua geese-3d-country.
Chua: `gong`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _fadeout, _hp, _lp, _ramp
from .._core import put
from .._lib.folk import _T


def gong(b_, t0, dur=6.0, g=0.09, seed=0, size=1.0, swell=0.0):
    """Cong lon: rat nhieu mode khong dieu hoa, len dan roi tat rat cham.

    `swell` > 0 thi danh nhe roi to dan — dung de dan vao mot doan.
    """
    L = int(dur * SR)
    R = np.random.default_rng(seed + 777)
    t = np.arange(L) / SR
    y = np.zeros(L)
    base = 62.0 / size
    for k in range(26):
        fq = base * (1.0 + 1.37 * k ** 0.86) * (1 + R.normal(0, 0.02))
        tau = dur * (0.42 / (1 + k * 0.22))
        y += (np.sin(2 * np.pi * fq * t + R.uniform(0, 6))
              * np.exp(-t / max(tau, 0.05)) / (1 + k * 0.5))
    y += _lp(R.standard_normal(L), 2600, 2) * np.exp(-t / 0.06) * 0.5
    # cong that "no" ra dan: nang luong doi len dai cao trong 0.3 s dau
    y = y * (1 + 0.8 * np.clip(t / 0.30, 0, 1) * np.exp(-t / 1.2))
    if swell > 0:
        y = y * np.clip(t / max(swell, 1e-3), 0, 1) ** 1.4
    y = _hp(y, 40, 2)
    put(b_, t0, _fadeout(_ramp(y, 4.0), 60.0), g * _T['gong'])
