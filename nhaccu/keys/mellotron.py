"""mellotron — mellotron (be day)

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `mellotron`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _ramp, env
from .._core import hz, nn, put
from .._lib.keys import _T, _tron_tape


def mellotron(b_, t0, notes, dur, g=0.06, seed=0, attack=0.09, wobble=8.0):
    """Mellotron dan: moi phim la mot bang rieng, nen moi not wow khac nhau."""
    L = int((dur + 0.5) * SR)
    R = np.random.default_rng(seed + 121)
    out = np.zeros(L)
    for j, m in enumerate(np.atleast_1d(notes)):
        f = hz(nn(m))
        t = np.arange(L) / SR
        y = np.zeros(L)
        for k in range(1, 15):
            amp = 1.0 / (k ** 1.35)
            det = 1 + float(R.normal(0, 0.0016))
            y += np.sin(2 * np.pi * f * k * det * t + R.uniform(0, 6)) * amp
        y += _bp(R.standard_normal(L), 800, 4000, 2) * 0.05
        y = _tron_tape(y, seed=seed + j * 17, wow=wobble)
        a = env(L, attack, 0.25, 0.80, 0.22)
        # bang mellotron chi dai 8 giay roi het — cho no yeu dan neu giu qua lau
        if dur > 6.5:
            a *= np.clip(1.25 - (np.arange(L) / SR) / 8.0, 0.0, 1.0)
        out += y * a
    out /= max(len(np.atleast_1d(notes)), 1) ** 0.6
    put(b_, t0, _ramp(out, 4.0), g * _T['mellotron'])
