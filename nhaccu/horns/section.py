"""section — be ken 4 be

Trich nguyen van tu `greeplib/horns.py` cua geese-3d-country.
Chua: `section`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._core import nn
from .._lib.horns import QUARTET
from ..horns.horn import horn


def section(b_, t0, notes, dur, g=0.09, voices=None, art='tongued', vel=1.0,
            seed=0, spread=0.010, det=6.0, vib=1.0, **kw):
    """Play a voicing with one player per note, top voice first.

    `spread` staggers the entries by a few milliseconds -- four horns never
    arrive on the same sample, and pretending they do is the single fastest
    way to sound synthetic.
    """
    ns = [nn(x) for x in np.atleast_1d(notes)]
    ns = sorted(ns, reverse=True)
    vs = voices or QUARTET
    R = np.random.default_rng(7100 + seed * 17)
    for i, m in enumerate(ns):
        v = vs[min(i, len(vs) - 1)]
        off = float(abs(R.normal(0, spread)))
        horn(b_, t0 + off, m, dur, g=g * (1.0 - 0.05 * i), voice=v, art=art,
             vel=vel * float(np.clip(1 + R.normal(0, 0.05), 0.7, 1.3)),
             seed=seed + i * 5, det=float(R.normal(0, det)), vib=vib, **kw)
