"""pno — piano (not roi)

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `pno`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from ..keys.piano import piano


def pno(b_, t0, m, dur, g=0.1):
    """Piano with the ring time scaled to the written note length."""
    piano(b_, t0, m, ring=float(np.clip(dur * 1.6 + 0.35, 0.45, 2.8)), g=g)
