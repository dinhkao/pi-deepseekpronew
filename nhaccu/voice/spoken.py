"""spoken — noi

Trich nguyen van tu `greeplib/singer.py` cua geese-3d-country.
Chua: `spoken`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from ..voice.vline import vline


def spoken(b_, bar0, cells, g=0.13, seed=0, lex=None, transpose=0, **kw):
    """Half-spoken aside. Narrow pitch range, no vibrato, hard consonants."""
    vline(b_, bar0, cells, g=g, style='declaim', seed=seed, lex=lex,
          transpose=transpose, vib=3.0, glide=False, **kw)
