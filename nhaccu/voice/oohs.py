"""oohs — ngan "ooh"

Trich nguyen van tu `greeplib/singer.py` cua geese-3d-country.
Chua: `oohs`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR
from .._core import nn, put
from ..voice.sing import sing


def oohs(b_, bar0, cells, g=0.07, vowel='u', n=3, seed=201, transpose=0,
         style='soft', **kw):
    """Wordless backing vowels on the long notes only."""
    from .._core import HUM, T as _T
    R = np.random.default_rng(seed)
    for i, c in enumerate(cells):
        off, d, note = c[0], c[1], c[2]
        if note is None or d < 0.9:
            continue
        bt = bar0 + off
        dd = max(_T(bt + d) - _T(bt), 0.2)
        for k in range(n):
            x, pre = sing(nn(note) + transpose, dd, vowel, vel=0.62, style=style,
                          seed=seed + i * 7 + k * 41,
                          fshift=float(1.0 + R.normal(0, 0.03)), **kw)
            put(b_, HUM.t(bt) + float(R.normal(0, 0.012)) - pre / SR,
                x, g / np.sqrt(n) * 1.4)
