"""voxorgan — organ Vox combo

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `voxorgan`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from ..keys.organ import organ


def voxorgan(b_, t0, notes, dur, g=0.07, viby=1.0):
    organ(b_, t0, notes, dur, g=g,
          drawbars=[(1, 1.0), (2, .60), (3, .34), (4, .40), (5, .14), (6, .20), (8, .16)],
          viby=viby)
