"""choir_satb — hop xuong SATB

Trich nguyen van tu `geeselib/voice.py` cua geese-3d-country.
Chua: `choir_satb`

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


def choir_satb(b_, bar0, cells, chords, g=0.055, seed=400, lex=None,
               transpose=0, voices=(0, -3, -7, -12, -19), style='soft',
               n_per_part=2, spread=14.0, vowel=None, bar_beats=4, hum=None):
    """Dan dong ca 4-5 be. `chords` la ky hieu hop am cho tung cell.

    `voices` chi la GOI Y khoang cach; not thuc te luon duoc chot vao hop am.
    `n_per_part` nguoi mot be, moi nguoi lech cu va lech nhip rieng —
    do la thu bien 5 giong thanh mot dan dong ca thay vi 5 lan cung mot giong.
    """
    H = hum or HUM
    R = np.random.default_rng(seed)
    for i, c in enumerate(cells):
        off, d, note = c[0], c[1], c[2]
        syl = vowel or (c[3] if len(c) > 3 else 'o')
        if note is None:
            continue
        sym = chords[i % len(chords)] if isinstance(chords, (list, tuple)) else chords
        pcs = pcs_of(sym)
        base = nn(note) + transpose
        parts = _snap_all(base, pcs, voices)
        bt = bar0 + off
        dd = max(T(bt + d) - T(bt), 0.09)
        for j, m in enumerate(parts):
            for k in range(n_per_part):
                fs = float(1.0 + R.normal(0, 0.030))
                jit = float(R.normal(0, 0.019))
                x, pre = sing(m, dd, phon(syl, lex), vel=0.62, style=style,
                              seed=seed + i * 31 + j * 7 + k * 101, fshift=fs,
                              vib=26.0 + R.normal(0, 6))
                put(b_, H.t(bt, bar_beats) + jit - pre / SR, x,
                    g / np.sqrt(len(parts) * n_per_part) * 2.0)
