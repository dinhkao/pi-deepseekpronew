"""unison — ken dong am

Trich nguyen van tu `greeplib/horns.py` cua geese-3d-country.
Chua: `unison`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._core import T, nn
from ..horns.horn import horn


def unison(b_, bar0, cells, g=0.10, voice='trumpet', octaves=(0,), seed=0,
           hum=None, bar_beats=4, **kw):
    """A single line doubled at chosen octaves -- the big unison heads."""
    from .._core import HUM
    H = hum or HUM
    for i, c in enumerate(cells):
        off, d, note = c[0], c[1], c[2]
        vel = c[3] if len(c) > 3 else 1.0
        bt = bar0 + off
        t0 = H.t(bt, bar_beats)
        dd = max(T(bt + d) - T(bt), 0.05)
        for j, o in enumerate(octaves):
            horn(b_, t0 + j * 0.004, nn(note) + 12 * o, dd,
                 g=H.g(g, bt, bar_beats=bar_beats) * vel * (1.0 - 0.12 * j),
                 voice=voice, vel=float(np.clip(vel, 0.3, 1.4)),
                 seed=seed + i * 7 + j, **kw)
