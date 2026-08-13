"""phon — chuyen chu sang am vi

Trich nguyen van tu `greeplib/singer.py` cua geese-3d-country.
Chua: `phon`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._lib.singer import LEX
from ..voice.g2p import g2p


def phon(syl, extra=None):
    """Syllable text -> phoneme string, checking LEX then a per-song dict."""
    s = str(syl).lower().strip(",.?!'\"-")
    if extra and s in extra:
        return extra[s]
    if s in LEX:
        return LEX[s]
    return g2p(s)
