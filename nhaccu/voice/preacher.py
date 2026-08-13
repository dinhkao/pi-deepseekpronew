"""preacher — giong giang dao

Trich nguyen van tu `geeselib/voice.py` cua geese-3d-country.
Chua: `preacher`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _peak


def preacher(b_, bar0, cells, g=0.14, seed=700, lex=None, transpose=0,
             bar_beats=4, hum=None, room=0.35):
    """Giong giang dao: gan nhu noi, gao len cuoi cau, co tieng phong."""
    from ..voice.vline import vline
    tmp = np.zeros(len(b_))
    vline(tmp, bar0, cells, g=1.0, style='declaim', seed=seed, lex=lex,
          transpose=transpose, vib=6.0, glide=False, hum=hum,
          bar_beats=bar_beats, breath=0.04)
    y = np.tanh(tmp * 2.2)
    y = _peak(y, 1800, 1.1, 3.5)
    y = _bp(y, 180, 6500, 2)
    if room > 0:
        for d, gg in ((0.031, 0.42), (0.047, 0.30), (0.071, 0.20), (0.103, 0.13)):
            k = int(d * SR)
            y[k:] += tmp[:len(y) - k] * gg * room
    b_ += y * g
