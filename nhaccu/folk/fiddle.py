"""fiddle — fiddle (violin dan ca)

Trich nguyen van tu `geeselib/folk.py` cua geese-3d-country.
Chua: `fiddle`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _blsaw, _bp, _lp, _peak, _ramp, env, phase
from .._core import hz, nn, put
from .._lib.folk import _T


def fiddle(b_, t0, m, dur, g=0.10, seed=0, slide_from=None, vib=28.0,
           bow=0.5, rasp=0.35, double=None):
    """Dan vi keo kieu hoedown: vao khong co attack mem, keo manh, co tieng
    ma cua nhua thong (rasp), va truot vao not (slide_from).

    `double` la not thu hai keo cung luc tren day ben canh — day la mau dac
    trung cua fiddle. Not do PHAI duoc nguoi goi chon tu hop am, ham nay khong
    tu doan (muc 3.2).
    """
    L = int((dur + 0.14) * SR)
    R = np.random.default_rng(seed + 4400)
    t = np.arange(L) / SR
    f0 = hz(nn(m))
    f = np.full(L, f0)
    if slide_from is not None:
        gn = max(int(min(0.075, dur * 0.4) * SR), 2)
        s = np.linspace(0, 1, gn)
        s = s * s * (3 - 2 * s)
        f[:gn] = hz(nn(slide_from)) * (1 - s) + f0 * s
    on = np.clip((t - 0.10) / 0.18, 0, 1)
    f = f * 2 ** ((vib * on * np.sin(2 * np.pi * 6.1 * t + R.uniform(0, 6))) / 1200.0)

    ph = phase(f, L)
    y = _blsaw(ph, 30)                          # cung keo ~ song rang cua
    # ba cong huong than dan
    y = _peak(y, 300, 1.4, 4.0)
    y = _peak(y, 1100, 1.8, 5.0)
    y = _peak(y, 2600, 2.2, 3.5)
    # tieng ma nhua thong: nhieu loc bang, dieu bien theo toc do cung
    y = y + _bp(R.standard_normal(L), 1800, 7000, 2) * rasp * 0.09 * (0.6 + 0.4 * on)
    a = env(L, 0.018 + 0.03 * (1 - bow), 0.10, 0.90, 0.075)
    y = _lp(y * a, 9500, 2)
    put(b_, t0, _ramp(y, 3.0), g * _T['fiddle'])
    if double is not None:
        fiddle(b_, t0 + 0.004, double, dur, g=g * 0.72, seed=seed + 91,
               vib=vib * 0.8, bow=bow, rasp=rasp * 0.7)
