"""drop — cat het

Trich nguyen van tu `geeselib/arrange.py` cua geese-3d-country.
Chua: `drop`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR
from .._core import T


def drop(b_, beat0, beats, fade=0.05):
    """Cat sach mot khoang trong mot stem (dung de tao khoang lang)."""
    i0, i1 = int(T(beat0) * SR), int(T(beat0 + beats) * SR)
    i1 = min(i1, len(b_))
    if i1 <= i0:
        return b_
    nf = min(int(fade * SR), (i1 - i0) // 2)
    if nf > 1:
        b_[i0:i0 + nf] *= np.linspace(1, 0, nf)
        b_[i1 - nf:i1] *= np.linspace(0, 1, nf)
        b_[i0 + nf:i1 - nf] = 0.0
    else:
        b_[i0:i1] = 0.0
    return b_
