"""congas — conga

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `congas`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._lib.latin import _steps


def congas(P, kit, beat0, row='O.hSo.hO..hS.o.h', v=0.55, tune=200.0, arc=1.0, sub=0.25):
    """O open, o open-quiet, S slap, s slap-quiet, h heel, t tip, m mute, B bass"""
    vmap = {
        'O': (1.00, dict(tune=tune, art='open')),
        'o': (0.62, dict(tune=tune, art='open')),
        'P': (1.00, dict(tune=tune * 0.78, art='open')),   # low drum (tumba)
        'p': (0.60, dict(tune=tune * 0.78, art='open')),
        'S': (0.95, dict(tune=tune, art='slap')),
        's': (0.55, dict(tune=tune, art='slap')),
        'h': (0.42, dict(tune=tune, art='heel')),
        't': (0.34, dict(tune=tune, art='tip')),
        'm': (0.60, dict(tune=tune, art='mute')),
        'B': (0.90, dict(tune=tune * 0.72, art='bass')),
    }
    _steps(P, kit, 'lperc', beat0, row, kit.conga, sub, vmap, arc, v)
