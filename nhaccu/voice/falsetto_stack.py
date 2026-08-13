"""falsetto_stack — chong giong gia thanh

Trich nguyen van tu `geeselib/voice.py` cua geese-3d-country.
Chua: `falsetto_stack`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR
from .._core import HUM, T, nn, put
from .._harmony import pcs_of
from .._lib.voice import _snap_all
from ..voice.phon import phon
from ..voice.sing import sing


def falsetto_stack(b_, bar0, cells, chords=None, g=0.05, seed=600, lex=None,
                   transpose=12, n=3, bar_beats=4, hum=None):
    """Chong be falsetto — mau Jeff Buckley cua `I See Myself`."""
    H = hum or HUM
    R = np.random.default_rng(seed)
    for i, c in enumerate(cells):
        off, d, note = c[0], c[1], c[2]
        syl = c[3] if len(c) > 3 else 'a'
        if note is None:
            continue
        base = nn(note) + transpose
        ms = [base]
        if chords:
            pcs = pcs_of(chords[i % len(chords)])
            ms = _snap_all(base, pcs, (0, -3, -8), lo=58, hi=90)[:n]
        bt = bar0 + off
        dd = max(T(bt + d) - T(bt), 0.09)
        for j, m in enumerate(ms):
            x, pre = sing(m, dd, phon(syl, lex), vel=0.58, style='falsetto',
                          seed=seed + i * 17 + j * 41,
                          fshift=float(1.0 + R.normal(0, 0.02)))
            put(b_, H.t(bt, bar_beats) + float(R.normal(0, 0.012)) - pre / SR,
                x, g / np.sqrt(len(ms)) * 1.5)
