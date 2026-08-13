"""vline — cau hat chinh

Trich nguyen van tu `greeplib/singer.py` cua geese-3d-country.
Chua: `vline`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR
from .._core import T, nn, put
from ..voice.phon import phon
from ..voice.sing import sing


def vline(b_, bar0, cells, g=0.16, style='croon', seed=0, lex=None,
          transpose=0, glide=True, hum=None, bar_beats=4, fshift=1.0,
          vel=1.0, **kw):
    """Sing a melody.

    cells = [(offset_beats, dur_beats, note|None, syllable), ...]
    A `None` note is a rest and also breaks the legato glide.
    """
    from .._core import HUM
    H = hum or HUM
    prev = None
    for i, c in enumerate(cells):
        off, d, note = c[0], c[1], c[2]
        syl = c[3] if len(c) > 3 else 'a'
        v = c[4] if len(c) > 4 else 1.0
        if note is None:
            prev = None
            continue
        m = nn(note) + transpose
        bt = bar0 + off
        t0 = H.t(bt, bar_beats)
        dd = max(T(bt + d) - T(bt), 0.06)
        x, pre = sing(m, dd, phon(syl, lex), vel=vel * v, style=style,
                      seed=seed + i * 13, glide_from=(prev if glide else None),
                      fshift=fshift, **kw)
        put(b_, t0 - pre / SR, x, H.g(g, bt, bar_beats=bar_beats))
        prev = m
