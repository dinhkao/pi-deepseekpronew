"""bossa_perc — go bossa

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `bossa_perc`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


def bossa_perc(P, kit, beat0, v=0.34, bar=0):
    """Brushed shaker and a cross-stick -- the whole point is restraint."""
    for i in range(8):
        P.hit('lperc', beat0 + i * 0.5, i * 2, kit.cabasa(vel=v * (0.9 if i % 2 == 0 else 0.55)))
    for h in ((0, 3, 6, 10, 12) if bar % 2 == 0 else (0, 3, 6, 10, 13)):
        P.hit('lperc', beat0 + h * 0.25, h, kit.clave(vel=v * 0.62))
