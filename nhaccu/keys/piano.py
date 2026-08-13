"""piano — piano

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `piano`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR
from .._core import nn, put
from .._lib.inst import _piano_raw


def piano(b_, t0, m, ring=3.0, g=0.10):
    m = nn(m)
    x = _piano_raw(m).astype(np.float64)
    n = int(min(ring, len(x) / SR) * SR)
    if n < len(x):
        rel = int(0.16 * SR)
        x = x[:n + rel].copy()
        if rel > 0 and len(x) > rel:
            x[-rel:] *= np.linspace(1, 0, rel) ** 1.6
    put(b_, t0, x, g)
