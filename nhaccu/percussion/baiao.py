"""baiao — baiao

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `baiao`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


def baiao(P, kit, beat0, v=0.55, bar=0):
    """Zabumba on 1 and the 'and of 2', triangle on every eighth."""
    P.hit('lperc', beat0 + 0.0, 0, kit.zabumba(vel=v * 1.05, tune=94))
    P.hit('lperc', beat0 + 1.5, 6, kit.zabumba(vel=v * 0.85, tune=94))
    P.hit('lperc', beat0 + 2.0, 8, kit.zabumba(vel=v * 0.5, tune=94, stick=True))
    P.hit('lperc', beat0 + 3.0, 12, kit.zabumba(vel=v * 0.95, tune=94))
    P.hit('lperc', beat0 + 3.5, 14, kit.zabumba(vel=v * 0.45, tune=94, stick=True))
    for i in range(8):
        P.hit('lperc', beat0 + i * 0.5, i * 2,
              kit.triangle(vel=v * (0.5 if i % 2 == 0 else 0.30), open_=(i % 2 == 0)))
