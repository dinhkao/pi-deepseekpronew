"""gang — hat tap the

Trich nguyen van tu `greeplib/singer.py` cua geese-3d-country.
Chua: `gang`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR
from .._core import nn, put
from ..voice.phon import phon
from ..voice.sing import sing


def gang(b_, bar0, cells, g=0.10, n=5, spread=22.0, jit=0.022, seed=0,
         lex=None, transpose=0, octave_up=0.30, style='gang', **kw):
    """A room full of men shouting the hook. Detune and timing scatter do all
    the work -- five identical voices is one loud voice."""
    from .._core import HUM, T as _T
    R = np.random.default_rng(int(bar0 * 97) % 99991 + seed)
    for k in range(n):
        dsemi = float(R.normal(0, spread)) / 100.0
        jj = float(R.normal(0, jit))
        up = 12 if k >= n - 2 else 0
        for i, c in enumerate(cells):
            off, d, note = c[0], c[1], c[2]
            syl = c[3] if len(c) > 3 else 'a'
            if note is None:
                continue
            m = nn(note) + transpose + up
            bt = bar0 + off
            dd = max(_T(bt + d) - _T(bt), 0.06)
            x, pre = sing(m, dd, phon(syl, lex), vel=0.8, style=style,
                          seed=seed + k * 311 + i * 13,
                          fshift=float(1.0 + R.normal(0, 0.035)), **kw)
            # detune by resampling a hair -- cheaper than re-synthesising
            put(b_, HUM.t(bt) + jj - pre / SR, x, g / np.sqrt(n) * 1.55)
