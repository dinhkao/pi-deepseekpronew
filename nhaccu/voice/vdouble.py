"""vdouble — nhan doi giong

Trich nguyen van tu `greeplib/singer.py` cua geese-3d-country.
Chua: `vdouble`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR
from .._core import nn, put
from ..voice.phon import phon
from ..voice.sing import sing


def vdouble(b_, bar0, cells, g=0.09, style='croon', seed=77, lex=None,
            transpose=0, offset_ms=14.0, fshift=1.02, **kw):
    """A second take, slightly late and slightly different -- the classic
    double-track. Never a copy: different seed means different jitter."""
    from .._core import HUM, T as _T
    prev = None
    for i, c in enumerate(cells):
        off, d, note = c[0], c[1], c[2]
        syl = c[3] if len(c) > 3 else 'a'
        if note is None:
            prev = None
            continue
        m = nn(note) + transpose
        bt = bar0 + off
        t0 = HUM.t(bt) + offset_ms / 1000.0
        dd = max(_T(bt + d) - _T(bt), 0.06)
        x, pre = sing(m, dd, phon(syl, lex), vel=0.85, style=style,
                      seed=seed + i * 29, glide_from=prev, fshift=fshift, **kw)
        put(b_, t0 - pre / SR, x, g)
        prev = m
