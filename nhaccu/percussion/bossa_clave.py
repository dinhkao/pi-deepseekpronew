"""bossa_clave — clave bossa

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `bossa_clave`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


def bossa_clave(P, kit, beat0, v=0.42, rim=True):
    """The bossa cross-stick pattern: 1, 1a, 2&, 3&, 4a-ish (2-bar)."""
    for h in (0, 3, 6, 10, 12):
        P.hit('lperc', beat0 + h * 0.25, h, kit.clave(vel=v * (1.0 if h in (0, 6) else 0.75)))
