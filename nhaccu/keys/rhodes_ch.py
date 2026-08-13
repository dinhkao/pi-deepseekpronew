"""rhodes_ch — Rhodes (hop am)

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `rhodes_ch`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from ..keys.rhodes import rhodes


def rhodes_ch(b_, t0, notes, dur, g=0.08, **kw):
    for i, m in enumerate(np.atleast_1d(notes)):
        rhodes(b_, t0 + i * 0.004, m, dur, g=g * (1 - 0.05 * i), **kw)
