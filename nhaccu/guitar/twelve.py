"""twelve — guitar 12 day

Trich nguyen van tu `geeselib/gtr.py` cua geese-3d-country.
Chua: `twelve`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _fadeout, _lp, _peak, _ramp
from .._core import nn, put
from .._lib.gtr import _T
from .._lib.inst import damp, ks


def twelve(b_, t0, notes, dur, g=0.07, seed=0, spread=0.010):
    """12 day: moi not doi thanh cap, cap tren cao hon mot quang tam."""
    for i, m in enumerate(sorted(nn(x) for x in notes)):
        for j, (om, gg, dt) in enumerate(((0, 1.0, 0.0), (12, 0.62, 9.0))):
            x = ks(m + om, dur + 0.35, damp=0.9974, bright=0.78, seed=seed + i * 5 + j * 31)
            x = damp(x, dur, ring=dur * 0.9, rel=0.05)
            c = 2 ** (dt / 1200.0)
            pos = np.clip(np.arange(len(x)) * c, 0, len(x) - 2)
            i0 = pos.astype(int)
            fr = pos - i0
            x = x[i0] * (1 - fr) + x[i0 + 1] * fr
            x = _peak(x, 2400, 1.2, 3.0)
            x = _lp(x, 7000, 2)
            put(b_, t0 + i * spread + j * 0.004, _fadeout(_ramp(x, 2.0), 25.0), g * gg * _T['twelve'])
