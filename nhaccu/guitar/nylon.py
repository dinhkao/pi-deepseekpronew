"""nylon — guitar day nylon

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `nylon`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _bp, _fadeout, _ramp, env
from .._core import put
from .._lib.inst import damp, ks


def nylon(b_, t0, m, dur, g=0.12, seed=0, bright=0.44, body=1.0, ring=None):
    """Classical/bossa nylon-string guitar: warm, fast decay, strong body."""
    x = ks(m, min(dur + 0.45, 2.0), 0.9958, bright, seed).astype(np.float64)
    L = len(x)
    res = np.zeros(L)
    for fr_, q, a in [(96, 11, 0.65), (192, 15, 0.32), (400, 12, 0.24), (2100, 6, 0.12)]:
        bq, aq = sg.iirpeak(fr_ / (SR / 2), q)
        res += sg.lfilter(bq, aq, x) * a * body
    y = _bp(x + res, 78, 6500, 2)
    y *= env(L, 0.002, 0.12, 0.55, min(0.18, dur * 0.5 + 0.04))
    put(b_, t0, damp(_fadeout(_ramp(y, 0.6), 22.0), dur, ring), g)
