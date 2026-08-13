"""baritone — guitar baritone

Trich nguyen van tu `geeselib/gtr.py` cua geese-3d-country.
Chua: `baritone`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _fadeout, _ramp
from .._core import nn, put
from .._lib.gtr import _T, gtr_amp, spring
from .._lib.inst import damp, ks


def baritone(b_, t0, m, dur, g=0.12, seed=0, drive=6.0, ring=None):
    """Guitar baritone (len day day, xuong quang 4-5). Mau spaghetti western."""
    x = ks(nn(m), dur + 0.4, damp=0.9978, bright=0.50, seed=seed)
    x = damp(x, dur, ring=ring if ring is not None else dur * 0.8, rel=0.04)
    y = gtr_amp(x, drive=drive, tone=0.40, bright=0.85, sag=0.3, size=1.25)
    y = spring(y, wet=0.26)
    put(b_, t0, _fadeout(_ramp(y, 2.0), 28.0), g * _T['baritone'])
