"""pipeorgan — dai phong cam

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `pipeorgan`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, env
from .._core import hz, nn, put


def pipeorgan(b_, t0, notes, dur, g=0.06, wind=1.0):
    L = int(dur * SR) + int(0.4 * SR)
    t = np.arange(L) / SR
    R = np.random.default_rng(int(t0 * 331) % 9999)
    e = env(L, 0.10, 0.10, 0.96, 0.35)
    for m in np.atleast_1d(notes):
        f = hz(nn(m))
        for k, a in [(0.5, 0.45), (1, 1.0), (2, 0.72), (3, 0.40), (4, 0.46),
                     (6, 0.22), (8, 0.26), (12, 0.10), (16, 0.09)]:
            ff = f * k
            if ff > SR / 2.2:
                continue
            chiff = np.exp(-t / 0.035) * 0.35 if k >= 4 else 0.0
            put(b_, t0, (np.sin(2 * np.pi * ff * t * (1 + R.normal(0, 0.0004)) + R.uniform(0, 6))
                         * (a + chiff)) * e * 0.055, g)
    put(b_, t0, _bp(R.standard_normal(L), 400, 2600, 2) * e * 0.020 * wind, g)
