"""jangle — guitar sach leng keng

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `jangle`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _bp, _fadeout
from .._core import put
from .._lib.inst import damp, ks


def jangle(b_, t0, m, dur, g=0.10, seed=0, ring=None):
    x = ks(m, dur, 0.9962, 0.72, seed).astype(np.float64)
    put(b_, t0, damp(_fadeout(_bp(x, 110, 6600, 2), 22.0), dur, ring), g)
