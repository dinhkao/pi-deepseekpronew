"""partido_alto — partido alto

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `partido_alto`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._lib.latin import _steps


def partido_alto(P, kit, beat0, v=0.5, bar=0):
    """The syncopated samba-funk cell -- pandeiro-led, much sparser than a
    full batucada, which is what makes it groove instead of clatter."""
    pan = 'O.tsO.tsO.tsO.ts' if bar % 2 == 0 else 'O.tsO.tOs.tsO.ts'
    vm = {'O': (1.0, dict(art='open')), 's': (0.85, dict(art='slap')),
          't': (0.45, dict(art='thumb')), 'j': (0.6, dict(art='jingle'))}
    _steps(P, kit, 'lperc', beat0, pan, kit.pandeiro, 0.25, vm, 1.0, v)
    P.hit('lperc', beat0 + 2.0, 8, kit.surdo(vel=v * 0.95, tune=70))
    P.hit('lperc', beat0 + 3.5, 14, kit.surdo(vel=v * 0.45, tune=70, muted=True))
    for i in (3, 6, 11, 14):
        P.hit('lperc', beat0 + i * 0.25, i, kit.tamborim(vel=v * 0.5))
