"""songo — songo

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `songo`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from ..percussion.cascara_pattern import cascara_pattern
from ..percussion.congas import congas


def songo(P, kit, beat0, v=0.5):
    congas(P, kit, beat0, 'B.hSO.hB..hSO.hh', v=v * 1.0)
    cascara_pattern(P, kit, beat0, v=v * 0.7)
