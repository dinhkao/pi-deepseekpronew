"""gospel — be gospel

Trich nguyen van tu `geeselib/voice.py` cua geese-3d-country.
Chua: `gospel`

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


def gospel(b_, bar0, cells, chords, g=0.06, seed=500, lex=None, transpose=0,
           bar_beats=4, hum=None, lift=True):
    """Dan gospel: 3 be nu cao + 2 be nam, rung sau, vao hoi tre va len dan.

    `lift` cho ca dan dang len trong tung cau — dac trung cua gospel that,
    khong phai giu deu mot muc.
    """
    H = hum or HUM
    R = np.random.default_rng(seed)
    n = len(cells)
    for i, c in enumerate(cells):
        off, d, note = c[0], c[1], c[2]
        syl = c[3] if len(c) > 3 else 'o'
        if note is None:
            continue
        sym = chords[i % len(chords)] if isinstance(chords, (list, tuple)) else chords
        pcs = pcs_of(sym)
        base = nn(note) + transpose
        top = _snap_all(base, pcs, (0, -3, -5), lo=60, hi=84)
        low = _snap_all(base - 12, pcs, (0, -5), lo=40, hi=64)
        arc = (0.78 + 0.34 * (i / max(n - 1, 1))) if lift else 1.0
        bt = bar0 + off
        dd = max(T(bt + d) - T(bt), 0.10)
        for j, m in enumerate(top):
            x, pre = sing(m, dd, phon(syl, lex), vel=0.72 * arc, style='soft',
                          seed=seed + i * 23 + j * 9,
                          fshift=float(1.06 + R.normal(0, 0.03)), vib=34.0)
            put(b_, H.t(bt, bar_beats) + float(R.normal(0, 0.022)) - pre / SR,
                x, g * 0.80)
        for j, m in enumerate(low):
            x, pre = sing(m, dd, phon(syl, lex), vel=0.62 * arc, style='soft',
                          seed=seed + 700 + i * 19 + j * 13,
                          fshift=float(0.95 + R.normal(0, 0.03)), vib=22.0)
            put(b_, H.t(bt, bar_beats) + float(R.normal(0, 0.024)) - pre / SR,
                x, g * 0.62)
