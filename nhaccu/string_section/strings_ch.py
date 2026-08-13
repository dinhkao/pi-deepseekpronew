"""strings_ch — dan day (hop am)

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `strings_ch`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from ..string_section.strings import strings


def strings_ch(b_, t0, notes, dur, g=0.06, atk=0.22, seed=0, desks=3):
    for i, m in enumerate(np.atleast_1d(notes)):
        strings(b_, t0, m, dur, g=g, atk=atk, seed=seed + i * 3, desks=desks)
