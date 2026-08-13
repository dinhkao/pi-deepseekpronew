"""lead_soft — giong chinh (nhe)

Trich nguyen van tu `geeselib/voice.py` cua geese-3d-country.
Chua: `lead_soft`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._lib.voice import LEAD_DEFAULTS


def lead_soft(b_, bar0, cells, g=0.24, **kw):
    d = dict(LEAD_DEFAULTS)
    d['vib'] = 9.0
    d.update(kw)
    from ..voice.vline import vline
    vline(b_, bar0, cells, g=g, style='croon', **d)
