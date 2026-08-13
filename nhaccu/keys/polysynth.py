"""polysynth — synth da am

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `polysynth`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from ..keys.arp2600 import arp2600


def polysynth(b_, t0, notes, dur, g=0.06, cutoff=1300.0, res=1.4, atk=0.03,
              det=11.0, seed=0, wave='saw', env_amt=900.0):
    """Poly hop am — moi giong mot ban ladder rieng, lech cu doc lap."""
    for i, m in enumerate(np.atleast_1d(notes)):
        arp2600(b_, t0 + i * 0.003, m, dur, g=g, cutoff=cutoff, res=res,
                env_amt=env_amt, atk=atk, dec=0.3, sus=0.72, rel=0.14,
                wave=wave, det=det, sub=0.0, seed=seed + i * 37)
