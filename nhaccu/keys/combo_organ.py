"""combo_organ — combo organ co drive

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `combo_organ`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _blpulse, _hp, _lp, _peak, _ramp, env, phase
from .._core import hz, nn, put
from .._lib.keys import _T


def combo_organ(b_, t0, notes, dur, g=0.07, viby=1.0, drive=1.6, bright=1.0,
                perc=0.0, seed=0):
    """Farfisa/Vox: song vuong loc nong, khong co Leslie, hoi re — dung y do."""
    L = int((dur + 0.10) * SR)
    R = np.random.default_rng(seed + 313)
    t = np.arange(L) / SR
    y = np.zeros(L)
    vib = 1 + (0.004 * viby) * np.sin(2 * np.pi * 6.9 * t + R.uniform(0, 6))
    for m in np.atleast_1d(notes):
        f = hz(nn(m))
        for mult, gg in ((1.0, 1.0), (2.0, 0.62), (3.0, 0.30), (4.0, 0.34),
                         (6.0, 0.16), (8.0, 0.20)):
            ph = phase(np.full(L, f * mult) * vib, L)
            y += _blpulse(ph, 0.32, 22) * gg
    y = y / max(len(np.atleast_1d(notes)), 1)
    if perc > 0:
        y = y * (1 + perc * 2.2 * np.exp(-t / 0.09))
    y = _peak(y, 1500 * bright, 1.0, 4.0)
    y = _lp(np.tanh(y * drive), 6200 * bright, 3)
    y = _hp(y, 120, 2)
    a = env(L, 0.006, 0.03, 0.94, 0.045)
    put(b_, t0, _ramp(y * a, 2.0), g * _T['combo_organ'])
