"""mambo_bell — chuong mambo

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `mambo_bell`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


def mambo_bell(P, kit, beat0, v=0.46):
    for h in (0, 2, 4, 6, 8, 10, 12, 14):
        mouth = h % 4 == 0
        P.hit('lperc', beat0 + h * 0.25, h, kit.campana(vel=v * (1.0 if mouth else 0.62), mouth=mouth))
