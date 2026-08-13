"""guaguanco — guaguanco

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `guaguanco`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from ..percussion.clave_23 import clave_23
from ..percussion.congas import congas


def guaguanco(P, kit, beat0, v=0.5):
    congas(P, kit, beat0, 'B.tSt.OpB.tSt.Op', v=v)
    clave_23(P, kit, beat0, v=v * 0.8, rev=True)
