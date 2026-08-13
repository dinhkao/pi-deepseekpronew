"""octafuzz — fuzz cong quang tam tren

Trich nguyen van tu `geeselib/gtr.py` cua geese-3d-country.
Chua: `octafuzz`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _fadeout, _ramp
from .._core import put
from .._lib.gtr import _T, gtr_amp
from .._lib.inst import damp, ks


def octafuzz(b_, t0, m, dur, g=0.10, seed=0, up=1.0, **kw):
    """Fuzz co quang tam tren — chinh luu toan song. Tieng "kèn ngỗng"."""
    x = ks(m, dur + 0.30, damp=0.9966, bright=0.85, seed=seed)
    x = damp(x, dur, ring=dur * 0.5, rel=0.030)
    oct_ = np.abs(x) * 2.0 - np.mean(np.abs(x))   # chinh luu = tang quang tam
    y = np.tanh((x * 0.55 + oct_ * up * 0.75) * 22.0)
    y = gtr_amp(y, drive=4.5, tone=0.62, bright=1.1, sag=0.4)
    put(b_, t0, _fadeout(_ramp(y, 1.2), 22.0), g * _T['octafuzz'])
