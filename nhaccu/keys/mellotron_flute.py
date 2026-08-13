"""mellotron_flute — mellotron (sao)

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `mellotron_flute`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _ramp, env
from .._core import hz, nn, put
from .._lib.keys import _T, _tron_tape


def mellotron_flute(b_, t0, notes, dur, g=0.06, seed=0):
    L = int((dur + 0.45) * SR)
    R = np.random.default_rng(seed + 909)
    out = np.zeros(L)
    t = np.arange(L) / SR
    for j, m in enumerate(np.atleast_1d(notes)):
        f = hz(nn(m))
        y = (np.sin(2 * np.pi * f * t) + 0.30 * np.sin(4 * np.pi * f * t)
             + 0.10 * np.sin(6 * np.pi * f * t))
        y += _bp(R.standard_normal(L), max(f * 1.4, 700), 7000, 2) * 0.16   # hoi thoi
        y = _tron_tape(y, seed=seed + j * 23, wow=10.0)
        out += y * env(L, 0.07, 0.2, 0.85, 0.20)
    out /= max(len(np.atleast_1d(notes)), 1) ** 0.6
    put(b_, t0, _ramp(out, 4.0), g * _T['mellotron_flute'])
