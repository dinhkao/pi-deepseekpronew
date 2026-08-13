"""lead_double — giong chinh nhan doi

Trich nguyen van tu `geeselib/voice.py` cua geese-3d-country.
Chua: `lead_double`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._lib.voice import LEAD_DEFAULTS


def lead_double(b_, bar0, cells, g=0.055, style='declaim', seed=77, **kw):
    from ..voice.vdouble import vdouble
    d = dict(LEAD_DEFAULTS)
    d['vib'] = 8.0
    d.update(kw)
    vdouble(b_, bar0, cells, g=g, style=style, seed=seed, **d)
