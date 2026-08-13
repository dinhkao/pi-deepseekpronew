"""clav — clavinet

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `clav`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _bp, _fadeout, _peak, env
from .._core import put
from .._lib.inst import damp, ks


def clav(b_, t0, m, dur, g=0.11, seed=0, ring=None):
    """Clavinet: a very short, very bright plucked string through a filter."""
    x = ks(m, min(dur + 0.2, 1.0), 0.9930, 0.90, seed).astype(np.float64)
    L = len(x)
    y = _bp(x, 260, 5200, 2)
    y = _peak(y, 1600, 3.0, 0.55)
    y *= env(L, 0.001, 0.05, 0.35, min(0.10, dur * 0.4 + 0.02))
    put(b_, t0, damp(_fadeout(np.tanh(y * 1.4), 14.0), dur, ring), g)
