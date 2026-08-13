"""banjo — banjo 5 day

Trich nguyen van tu `geeselib/folk.py` cua geese-3d-country.
Chua: `banjo`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _fadeout, _hp, _lp, _peak, _ramp
from .._core import nn, put
from .._lib.folk import _T
from .._lib.inst import damp, ks


def banjo(b_, t0, m, dur, g=0.10, seed=0, ring=None, bright=1.0, drone=False):
    """Banjo 5 day: mat trong, cau ngua cung, tat rat nhanh.

    Khac guitar o cho nao: banjo gan nhu khong co dai duoi 200 Hz (mat trong
    nho, khong co thung go cong huong), va boi am cao tat CHAM hon boi am thap
    — nguoc voi day guitar. Nen o day dung `ks` it giam xoc roi cong huong
    manh o 400 Hz va 3 kHz, va cat sach duoi 180 Hz.
    """
    x = ks(nn(m), dur + 0.35, damp=0.9930, bright=0.92, seed=seed)
    x = damp(x, dur, ring=ring if ring is not None else min(dur * 0.7, 0.55),
             rel=0.020)
    y = _peak(x, 420, 1.6, 5.0)                 # cong huong mat trong
    y = _peak(y, 3100 * bright, 1.2, 6.0)       # cau ngua kim loai
    y = _hp(y, 180, 2)                          # banjo khong co dai tram
    y = _lp(y, 9000, 2)
    y = np.tanh(y * 1.6)
    put(b_, t0, _fadeout(_ramp(y, 1.0), 18.0), g * _T['banjo'])
