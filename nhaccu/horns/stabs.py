"""stabs — ken cham pha

Trich nguyen van tu `greeplib/horns.py` cua geese-3d-country.
Chua: `stabs`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._core import T
from ..horns.section import section


def stabs(b_, bar0, cells, g=0.10, voices=None, seed=0, hum=None, bar_beats=4, **kw):
    """cells = [(offset_beats, dur_beats, [notes], vel), ...] -- the shout
    chorus / mambo punch writing that runs through the whole record."""
    from .._core import HUM
    H = hum or HUM
    for i, c in enumerate(cells):
        off, d, notes = c[0], c[1], c[2]
        vel = c[3] if len(c) > 3 else 1.0
        bt = bar0 + off
        t0 = H.t(bt, bar_beats)
        dd = max(T(bt + d) - T(bt), 0.05)
        section(b_, t0, notes, dd, g=H.g(g, bt, bar_beats=bar_beats) * vel,
                voices=voices, vel=float(np.clip(vel, 0.3, 1.4)), seed=seed + i * 3, **kw)
