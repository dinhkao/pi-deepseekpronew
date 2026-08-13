"""moogbass — bass synth kieu Moog

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `moogbass`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from ..keys.arp2600 import arp2600


def moogbass(b_, t0, m, dur, g=0.16, cutoff=340.0, res=3.0, env_amt=1500.0,
             seed=0, glide_from=None, drive=2.0):
    arp2600(b_, t0, m, dur, g=g, cutoff=cutoff, res=res, env_amt=env_amt,
            atk=0.004, dec=0.16, sus=0.30, rel=0.06, wave='saw', det=4.0,
            sub=0.75, seed=seed, glide_from=glide_from, drive=drive)
