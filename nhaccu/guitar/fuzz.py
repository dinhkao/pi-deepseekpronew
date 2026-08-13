"""fuzz — guitar fuzz

Trich nguyen van tu `geeselib/gtr.py` cua geese-3d-country.
Chua: `fuzz`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _fadeout, _lp, _ramp, fold
from .._core import put
from .._lib.gtr import _T, gtr_amp
from .._lib.inst import damp, ks


def fuzz(b_, t0, m, dur, g=0.12, drive=26.0, seed=0, gate=0.0, bright=1.0,
         ring=None, tone=0.55):
    """Fuzz silicon: cat gan nhu vuong, nhieu hoa am le. Tieng `2122`."""
    x = ks(m, dur + 0.30, damp=0.9968, bright=0.80, seed=seed)
    x = damp(x, dur, ring=ring if ring is not None else dur * 0.55, rel=0.030)
    y = np.tanh(x * drive)
    y = fold(y, 0.22) * 0.35 + y * 0.65
    if gate > 0:                                  # velcro fuzz: tat khi nho
        e = _lp(np.abs(x), 22, 2)
        e /= (e.max() + 1e-9)
        y *= np.clip((e - gate) / max(1 - gate, 1e-6), 0, 1) ** 0.6
    y = gtr_amp(y, drive=5.0, tone=tone, bright=bright, sag=0.5)
    put(b_, t0, _fadeout(_ramp(y, 1.2), 22.0), g * _T['fuzz'])
