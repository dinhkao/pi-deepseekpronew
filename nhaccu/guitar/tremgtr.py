"""tremgtr — guitar tremolo

Trich nguyen van tu `geeselib/gtr.py` cua geese-3d-country.
Chua: `tremgtr`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _fadeout, _ramp
from .._core import put
from .._lib.gtr import _T, gtr_amp, spring
from .._lib.inst import damp, ks


def tremgtr(b_, t0, m, dur, g=0.11, rate=5.2, depth=0.75, seed=0, clean=True,
            square=False, ring=None):
    """Guitar co tremolo bien do — mau "surf/cosmic country"."""
    x = ks(m, dur + 0.4, damp=0.9975, bright=0.55, seed=seed)
    x = damp(x, dur, ring=ring if ring is not None else dur * 0.85, rel=0.045)
    t = np.arange(len(x)) / SR
    lfo = np.sin(2 * np.pi * rate * t)
    if square:
        lfo = np.tanh(lfo * 6.0)
    y = x * (1.0 - depth * 0.5 * (1.0 - lfo))
    y = gtr_amp(y, drive=1.9 if clean else 6.0, tone=0.48, bright=1.05, sag=0.15)
    y = spring(y, wet=0.30)
    put(b_, t0, _fadeout(_ramp(y, 2.0), 30.0), g * _T['tremgtr'])
