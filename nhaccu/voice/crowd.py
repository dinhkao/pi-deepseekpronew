"""crowd — dam dong

Trich nguyen van tu `geeselib/voice.py` cua geese-3d-country.
Chua: `crowd`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR
from .._core import HUM, T, nn, put
from ..voice.phon import phon
from ..voice.sing import sing


def crowd(b_, bar0, cells, g=0.09, n=9, seed=800, lex=None, transpose=0,
          spread=38.0, jit=0.040, bar_beats=4, hum=None, octaves=(0, 0, 0, 12, -12)):
    """Ca phong hat theo — lech nhieu hon `gang` cua greeplib, kem chuyen dong."""
    H = hum or HUM
    R = np.random.default_rng(seed)
    for k in range(n):
        ds = float(R.normal(0, spread)) / 100.0
        oc = octaves[k % len(octaves)]
        for i, c in enumerate(cells):
            off, d, note = c[0], c[1], c[2]
            syl = c[3] if len(c) > 3 else 'a'
            if note is None:
                continue
            bt = bar0 + off
            dd = max(T(bt + d) - T(bt), 0.08)
            x, pre = sing(nn(note) + transpose + oc, dd, phon(syl, lex),
                          vel=0.80, style='gang', seed=seed + k * 307 + i * 11,
                          fshift=float(1.0 + R.normal(0, 0.045)))
            put(b_, H.t(bt, bar_beats) + float(R.normal(0, jit)) - pre / SR,
                x, g / np.sqrt(n) * 1.7 * (2 ** (ds / 12.0)) ** 0)
