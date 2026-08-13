"""organ — organ Hammond (drawbar)

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `organ`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, env
from .._core import hz, nn, put


def organ(b_, t0, notes, dur, g=0.07, drawbars=None, perc=0.0, viby=1.0):
    """Tonewheel organ. Default drawbars are a fat 88 8000 000 sort of sound."""
    L = int(dur * SR) + int(0.1 * SR)
    t = np.arange(L) / SR
    e = env(L, 0.010, 0.05, 0.96, 0.05)
    db = drawbars or [(0.5, 0.45), (1, 1.0), (2, 0.55), (3, 0.30),
                      (4, 0.35), (6, 0.16), (8, 0.12)]
    for m in np.atleast_1d(notes):
        m = nn(m)
        f = hz(m)
        x = np.zeros(L)
        for k, amp in db:
            ff = f * k
            if ff > SR / 2.2:
                continue
            x += np.sin(2 * np.pi * ff * t * (1 + 0.0006 * k)) * amp
        if perc:
            x += np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.18) * perc
        x *= (1 + 0.05 * viby * np.sin(2 * np.pi * 6.6 * t + f))
        put(b_, t0, np.tanh(x * 0.55) * e * 0.16, g)
