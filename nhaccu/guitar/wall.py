"""wall — tuong guitar (hop am nhieu lop)

Trich nguyen van tu `geeselib/gtr.py` cua geese-3d-country.
Chua: `wall`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _fadeout, _ramp
from .._core import nn, put
from .._lib.gtr import _T, gtr_amp
from .._lib.inst import damp, ks


def wall(b_, t0, notes, dur, g=0.07, drive=18.0, seed=0, spread=0.008,
         bright=1.0, detune=7.0):
    """Buc tuong hop am meo — hai cay lech nhau, dung cho diep khuc."""
    R = np.random.default_rng(seed + 991)
    for i, m in enumerate(sorted(notes)):
        x = ks(nn(m), dur + 0.35, damp=0.9970,
               bright=0.72, seed=seed + i * 7)
        x = damp(x, dur, ring=dur * 0.7, rel=0.035)
        c = float(R.normal(0, detune)) / 1200.0
        if abs(c) > 1e-6:                          # lech cu bang doc lai mau
            idx = np.clip(np.arange(len(x)) * (2 ** c), 0, len(x) - 1)
            i0 = idx.astype(int)
            x = x[i0] * (1 - (idx - i0)) + x[np.minimum(i0 + 1, len(x) - 1)] * (idx - i0)
        y = np.tanh(x * drive)
        y = gtr_amp(y, drive=4.0, tone=0.5, bright=bright, sag=0.35)
        put(b_, t0 + i * spread, _fadeout(_ramp(y, 1.5), 25.0), g * _T['wall'])
