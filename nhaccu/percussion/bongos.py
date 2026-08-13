"""bongos — bongo

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `bongos`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._lib.latin import _steps


def bongos(P, kit, beat0, row='M.mM.mM.mM.mM.mM', v=0.42, arc=1.0, sub=0.25):
    """M macho open, m macho quiet, H hembra open, h hembra quiet, S slap"""
    vmap = {
        'M': (0.95, dict(hembra=False, art='open')),
        'm': (0.52, dict(hembra=False, art='tip')),
        'H': (0.95, dict(hembra=True, art='open')),
        'h': (0.52, dict(hembra=True, art='tip')),
        'S': (1.00, dict(hembra=False, art='slap')),
        'u': (0.60, dict(hembra=True, art='mute')),
    }
    _steps(P, kit, 'lperc', beat0, row, kit.bongo, sub, vmap, arc, v)
