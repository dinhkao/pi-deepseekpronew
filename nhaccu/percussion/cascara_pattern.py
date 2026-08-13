"""cascara_pattern — cascara

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `cascara_pattern`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


def cascara_pattern(P, kit, beat0, v=0.40):
    for h in (0, 2, 3, 5, 7, 8, 10, 12, 13, 15):
        P.hit('lperc', beat0 + h * 0.25, h, kit.cascara(vel=v * (1.0 if h % 4 == 0 else 0.72)))
