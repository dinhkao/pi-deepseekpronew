"""acgtr — guitar thung day thep

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `acgtr`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _bp, _fadeout, _ramp, env
from .._core import put
from .._lib.inst import damp, ks


def acgtr(b_, t0, m, dur, g=0.13, seed=0, bright=0.72, ring=None):
    """Steel-string acoustic."""
    x = ks(m, min(dur + 0.35, 1.7), 0.9962, bright, seed).astype(np.float64)
    L = len(x)
    body = np.zeros(L)
    for fr_, q, a in [(102, 9, 0.55), (196, 14, 0.35), (392, 18, 0.22), (2400, 7, 0.16)]:
        bq, aq = sg.iirpeak(fr_ / (SR / 2), q)
        body += sg.lfilter(bq, aq, x) * a
    y = _bp(x + body, 90, 9000, 2)
    y *= env(L, 0.002, 0.09, 0.62, min(0.14, dur * 0.5 + 0.03))
    put(b_, t0, damp(_fadeout(_ramp(y, 0.6), 18.0), dur, ring), g)
