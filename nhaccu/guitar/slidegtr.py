"""slidegtr — guitar slide

Trich nguyen van tu `geeselib/gtr.py` cua geese-3d-country.
Chua: `slidegtr`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _fadeout, _ramp
from .._core import nn, put
from .._lib.gtr import _T, gtr_amp, spring
from .._lib.inst import damp, ks


def slidegtr(b_, t0, m_from, m_to, dur, g=0.12, seed=0, drive=4.5,
             hold=0.42, vib=18.0):
    """Guitar bottleneck. Vuot bang cach doc lai mau — mot lan render duy nhat,
    KHONG noi nhieu doan (tranh khe hut bien do, KIEM-TRA muc 4.3)."""
    span = abs(nn(m_to) - nn(m_from))
    x = ks(nn(m_from), dur + 0.5 + span * 0.01, damp=0.9976, bright=0.62, seed=seed)
    L = int((dur + 0.25) * SR)
    t = np.arange(L) / SR
    k = max(t[-1] * (1 - hold), 1e-3)
    prog = np.clip(t / k, 0, 1)
    prog = prog * prog * (3 - 2 * prog)
    semis = (nn(m_to) - nn(m_from)) * prog
    semis = semis + (vib / 100.0) * np.sin(2 * np.pi * 5.4 * t) * np.clip((t - k) / 0.25, 0, 1)
    # tich luy ty le doc mau -> vi tri doc
    ratio = 2 ** (semis / 12.0)
    pos = np.cumsum(ratio)
    pos = np.clip(pos, 0, len(x) - 2)
    i0 = pos.astype(int)
    fr = pos - i0
    y = x[i0] * (1 - fr) + x[i0 + 1] * fr
    y = damp(y, dur, ring=dur * 0.9, rel=0.05)
    y = gtr_amp(y, drive=drive, tone=0.55, bright=0.95, sag=0.25)
    y = spring(y, wet=0.22)
    put(b_, t0, _fadeout(_ramp(y, 2.5), 30.0), g * _T['slidegtr'])
