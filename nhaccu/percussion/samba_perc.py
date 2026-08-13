"""samba_perc — go samba

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `samba_perc`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


def samba_perc(P, kit, beat0, v=0.5, intensity=1.0, bar=0):
    """Surdo on 2 (and a ghost on 1), tamborim teleco-teco, chocalho 16ths,
    agogo on the offbeats.  This is a batucada squeezed into a pop bar."""
    P.hit('lperc', beat0 + 0.0, 0, kit.surdo(vel=v * 0.42, tune=74, muted=True))
    P.hit('lperc', beat0 + 2.0, 8, kit.surdo(vel=v * 1.05, tune=72))
    tam = '..X.XX.X.X.XX.X.' if bar % 2 == 0 else '..X.XX.XX.X..XX.'
    for i, c in enumerate(tam):
        if c == 'X':
            P.hit('lperc', beat0 + i * 0.25, i, kit.tamborim(vel=v * 0.55 * intensity))
    for i in range(16):
        P.hit('lperc', beat0 + i * 0.25, i,
              kit.chocalho(vel=v * (0.42 if i % 2 == 0 else 0.26) * intensity))
    for i in (2, 6, 10, 14):
        P.hit('lperc', beat0 + i * 0.25, i, kit.agogo(vel=v * 0.38 * intensity, low=(i % 8 == 2)))
    for i in (3, 7, 11, 15):
        P.hit('lperc', beat0 + i * 0.25, i, kit.caixa(vel=v * 0.34 * intensity, art='ghost'))
