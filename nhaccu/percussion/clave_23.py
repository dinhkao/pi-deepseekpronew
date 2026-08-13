"""clave_23 — clave 2-3

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `clave_23`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


def clave_23(P, kit, beat0, v=0.5, son=True, rev=False):
    """Son clave 2-3 (or 3-2 with rev=True). The spine of everything Cuban."""
    three = [0, 3, 6] if son else [0, 3, 6.5]
    two = [8, 12] if son else [8, 12]
    hits = (three + two) if not rev else (two + three)
    if rev:
        hits = [h - 8 if h >= 8 else h + 8 for h in (three + two)]
    for h in sorted(hits):
        P.hit('lperc', beat0 + h * 0.25, int(h) % 16, kit.clave(vel=v))
