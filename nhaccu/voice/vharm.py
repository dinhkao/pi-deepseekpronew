"""vharm — be hoa giong

Trich nguyen van tu `greeplib/singer.py` cua geese-3d-country.
Chua: `vharm`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR
from .._core import nn, put
from ..voice.phon import phon
from ..voice.sing import sing


def vharm(b_, bar0, cells, intervals=(4,), g=0.07, style='soft', seed=131,
          lex=None, transpose=0, chord_pcs=None, **kw):
    """Stacked harmony. If `chord_pcs` is given (a list of pitch classes per
    cell), the interval is snapped to the nearest chord tone."""
    from .._core import HUM, T as _T
    for i, c in enumerate(cells):
        off, d, note = c[0], c[1], c[2]
        syl = c[3] if len(c) > 3 else 'a'
        if note is None:
            continue
        base = nn(note) + transpose
        bt = bar0 + off
        dd = max(_T(bt + d) - _T(bt), 0.06)
        for j, iv in enumerate(intervals):
            m = base + iv
            if chord_pcs:
                pcs = chord_pcs[i % len(chord_pcs)]
                for step in range(0, 5):
                    if (m + step) % 12 in pcs:
                        m = m + step
                        break
                    if (m - step) % 12 in pcs:
                        m = m - step
                        break
            x, pre = sing(m, dd, phon(syl, lex), vel=0.7, style=style,
                          seed=seed + i * 17 + j * 5, **kw)
            put(b_, HUM.t(bt) - pre / SR, x, g)
