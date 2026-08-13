"""clap_track — vo tay tap the

Trich nguyen van tu `geeselib/arrange.py` cua geese-3d-country.
Chua: `clap_track`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp
from .._core import HUM, put


def clap_track(b_, beats, g=0.10, seed=0, n_people=7, spread=0.028, bar_beats=4,
               hum=None):
    """Vo tay that: nhieu nguoi, lech nhau — mot nguoi vo 7 lan la mot nguoi."""
    H = hum or HUM
    R = np.random.default_rng(seed + 900)
    for bt in beats:
        t0 = H.t(bt, bar_beats)
        for k in range(n_people):
            L = int(0.24 * SR)
            t = np.arange(L) / SR
            f1 = R.uniform(900, 1500)
            f2 = R.uniform(2200, 3800)
            y = _bp(R.standard_normal(L), f1, f2, 2) * np.exp(-t / R.uniform(0.006, 0.014))
            y += _bp(R.standard_normal(L), 1100, 3000, 2) * np.exp(-t / 0.045) * 0.30
            put(b_, t0 + float(R.normal(0, spread)), y,
                g / np.sqrt(n_people) * 1.5 * R.uniform(0.7, 1.2))
