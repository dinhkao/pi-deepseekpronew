"""Helper dung chung, trich tu geeselib/folk.py.

Trich nguyen van tu `geeselib/folk.py` cua geese-3d-country.
Chua: `_T`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


# Trim do bang tools/calibrate.py — dua moi thu ve RMS ~0.12 o gain 1.0.
_T = {'banjo': 0.501, 'fiddle': 0.059, 'gong': 0.144, 'washboard': 4.27,
      'jugbass': 0.323, 'fairorgan': 0.130, 'bones': 3.81, 'march_bass': 0.570}
