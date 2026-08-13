"""lead — giong chinh (declaim)

Trich nguyen van tu `geeselib/voice.py` cua geese-3d-country.
Chua: `lead`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._lib.voice import LEAD_DEFAULTS


def lead(b_, bar0, cells, g=0.26, style='declaim', **kw):
    """Be hat chinh. Mac dinh da chinh de nghe ro chu nhat co the."""
    from ..voice.vline import vline
    d = dict(LEAD_DEFAULTS)
    d.update(kw)
    vline(b_, bar0, cells, g=g, style=style, **d)
