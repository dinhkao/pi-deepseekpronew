"""Helper dung chung, trich tu geeselib/keys.py.

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `_T`, `_tron_tape`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _bp, _hp, _lp, tape_wobble


# Chuan hoa muc ra — xem chu thich cung ten trong gtr.py.
# polysynth va moogbass KHONG co trong bang vi chung goi arp2600, da trim roi.
_T = {'combo_organ': 0.269, 'saloon': 0.671, 'tack': 0.603, 'mellotron': 0.292,
      'mellotron_flute': 0.301, 'arp2600': 0.904, 'theremin': 0.290,
      'glocken': 0.855, 'celeste': 0.382}


def _tron_tape(y, seed=0, wow=7.0):
    y = tape_wobble(y, wow_rate=0.6, wow_cents=wow, flutter_rate=8.6,
                    flutter_cents=wow * 0.35)
    y = _lp(y, 6000, 3)
    y = _hp(y, 90, 2)
    R = np.random.default_rng(seed + 88)
    y = y + _bp(R.standard_normal(len(y)), 300, 5000, 2) * 0.0022   # hiss bang
    return y
