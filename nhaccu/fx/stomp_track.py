"""stomp_track — dam chan tap the

Trich nguyen van tu `geeselib/arrange.py` cua geese-3d-country.
Chua: `stomp_track`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _lp
from .._core import HUM, put


def stomp_track(b_, beats, g=0.14, seed=0, n_people=6, spread=0.024,
                bar_beats=4, hum=None):
    """Dam chan tren san go."""
    H = hum or HUM
    R = np.random.default_rng(seed + 901)
    for bt in beats:
        t0 = H.t(bt, bar_beats)
        for k in range(n_people):
            L = int(0.35 * SR)
            t = np.arange(L) / SR
            f = R.uniform(52, 78)
            y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.055)
            y += _lp(R.standard_normal(L), 380, 2) * np.exp(-t / 0.020) * 0.7
            y += _bp(R.standard_normal(L), 700, 2400, 2) * np.exp(-t / 0.006) * 0.25
            put(b_, t0 + float(R.normal(0, spread)), np.tanh(y * 1.4),
                g / np.sqrt(n_people) * 1.5 * R.uniform(0.75, 1.15))
