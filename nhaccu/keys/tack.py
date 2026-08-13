"""tack — piano gan dinh

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `tack`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _fadeout, _hp, _peak, _ramp
from .._core import nn, put
from .._lib.inst import _piano_raw, damp
from .._lib.keys import _T


def tack(b_, t0, m, dur=None, g=0.09, ring=1.4, seed=0):
    """Tack piano — dinh ghim tren bua. Rat nhieu transient kim loai."""
    x = _piano_raw(nn(m))
    R = np.random.default_rng(seed + 4)
    n = int(0.010 * SR)
    tick = _bp(R.standard_normal(len(x)), 2600, 9000, 2)
    tick[n:] = 0
    y = x + tick * 0.55 * (np.abs(x).max() + 1e-9)
    y = _peak(y, 3400, 1.6, 6.0)
    y = _hp(y, 150, 2)
    y = damp(y, dur if dur else ring, ring=ring, rel=0.06)
    put(b_, t0, _fadeout(_ramp(y, 1.0), 22.0), g * _T['tack'])
