"""jazzbox — guitar hop jazz

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `jazzbox`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _bp, _fadeout, _peak, _ramp, env
from .._core import put
from .._lib.inst import damp, ks


def jazzbox(b_, t0, m, dur, g=0.12, seed=0, tone=0.35, ring=None):
    """Hollow-body electric with the tone rolled off -- the comping guitar."""
    x = ks(m, min(dur + 0.5, 2.2), 0.9970, 0.30 + tone * 0.4, seed).astype(np.float64)
    L = len(x)
    y = _bp(x, 110, 2600 + 2600 * tone, 2)
    y = _peak(y, 420, 3.0, 0.30)
    y *= env(L, 0.003, 0.13, 0.68, min(0.20, dur * 0.5 + 0.05))
    put(b_, t0, damp(_fadeout(_ramp(y, 0.7), 25.0), dur, ring), g)
