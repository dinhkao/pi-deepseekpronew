"""theremin — theremin

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `theremin`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _ramp, env, phase
from .._core import hz, nn, put
from .._lib.keys import _T


def theremin(b_, t0, m, dur, g=0.09, glide_from=None, vib=45.0, seed=0,
             bright=0.35):
    """Theremin/onde: sin gan nhu thuan, vuot lien tuc, rung sau."""
    L = int((dur + 0.18) * SR)
    R = np.random.default_rng(seed + 77)
    t = np.arange(L) / SR
    f0 = hz(nn(m))
    f = np.full(L, f0)
    if glide_from is not None:
        gn = max(int(min(0.30, dur * 0.7) * SR), 2)
        s = np.linspace(0, 1, gn)
        s = s * s * (3 - 2 * s)
        f[:gn] = hz(nn(glide_from)) * (1 - s) + f0 * s
    on = np.clip((t - 0.16) / 0.30, 0, 1)
    f = f * 2 ** ((vib * on * np.sin(2 * np.pi * 5.6 * t + R.uniform(0, 6))) / 1200.0)
    ph = phase(f, L)
    y = np.sin(ph) + bright * 0.30 * np.sin(2 * ph) + bright * 0.10 * np.sin(3 * ph)
    a = env(L, 0.09, 0.15, 0.92, 0.14)
    put(b_, t0, _ramp(y * a, 5.0), g * _T['theremin'])
