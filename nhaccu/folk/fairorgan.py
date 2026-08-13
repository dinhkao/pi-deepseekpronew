"""fairorgan — dan hoi cho phien

Trich nguyen van tu `geeselib/folk.py` cua geese-3d-country.
Chua: `fairorgan`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _hp, _lp, _peak, _ramp, env, phase
from .._core import hz, nn, put
from .._lib.folk import _T


def fairorgan(b_, t0, notes, dur, g=0.07, seed=0, ranks=(1, 2, 3, 4, 6),
              wobble=1.0, reed=0.5):
    """Dan hoi cho phien (fairground organ): nhieu hang ong cung keu mot luc,
    moi hang lech cu mot chut, va co mot cai quat lam ca dan rung deu deu.

    Khac `combo_organ` o cho: day la ONG GIO, khong phai mach dien — nen co
    tieng hoi thoi, cac hang lech nhau nhieu hon, va rung cham hon."""
    L = int((dur + 0.14) * SR)
    R = np.random.default_rng(seed + 3131)
    t = np.arange(L) / SR
    trem = 1 + 0.010 * wobble * np.sin(2 * np.pi * 4.4 * t + R.uniform(0, 6))
    out = np.zeros(L)
    ns = np.atleast_1d(notes)
    for m in ns:
        f = hz(nn(m))
        for r in ranks:
            det = 1 + float(R.normal(0, 0.0032))
            ph = phase(np.full(L, f * r) * trem * det, L)
            wave = np.sin(ph)
            if r >= 3:                      # hang luoi gà: co hoa am le
                wave = 0.55 * wave + 0.45 * np.tanh(np.sin(ph) * 3.0) * reed
            out += wave / (r ** 0.85)
        out += _bp(R.standard_normal(L), 900, 5000, 2) * 0.030   # hoi thoi
    out /= max(len(ns), 1) ** 0.6
    out = _peak(out, 1200, 1.0, 3.0)
    out = _lp(_hp(out, 130, 2), 7500, 2)
    a = env(L, 0.035, 0.08, 0.92, 0.075)
    put(b_, t0, _ramp(out * a, 3.0), g * _T['fairorgan'])
