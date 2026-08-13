"""pad — ken nen

Trich nguyen van tu `greeplib/horns.py` cua geese-3d-country.
Chua: `pad`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from ..horns.section import section


def pad(b_, t0, notes, dur, g=0.06, voices=None, seed=0, **kw):
    """Long sustained horn bed, swelling, for the big cinematic moments."""
    section(b_, t0, notes, dur, g=g, voices=voices or ['frenchhorn', 'frenchhorn', 'trombone', 'tuba'],
            art='swell', vel=0.55, seed=seed, spread=0.020, det=8.0, **kw)
