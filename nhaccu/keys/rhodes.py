"""rhodes — Rhodes

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `rhodes`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _lp
from .._core import hz, nn, put


def rhodes(b_, t0, m, dur, g=0.12, bark=1.0, tine=1.0, det=0.0):
    """Electric piano: an FM tine (bell) transient over a sine body, with the
    bark that appears only when you hit it hard."""
    m = nn(m)
    L = int(min(dur + 0.9, 4.0) * SR)
    t = np.arange(L) / SR
    R = np.random.default_rng(700 + m)
    f = hz(m) * 2 ** (det / 1200)
    ph = 2 * np.pi * np.cumsum(np.full(L, f)) / SR
    idx = (3.6 * np.exp(-t / 0.055) + 0.55 * np.exp(-t / 0.9)) * tine
    tin = np.sin(ph * 1.0 + idx * np.sin(ph * 14.0))
    body = np.sin(ph) + 0.20 * np.sin(ph * 2) + 0.06 * np.sin(ph * 3)
    x = body * np.exp(-t / (1.5 + 90.0 / max(hz(m), 40))) + tin * np.exp(-t / 0.42) * 0.55
    knock = _lp(R.standard_normal(L), 1600, 2) * np.exp(-t / 0.0045) * 0.30 * bark
    x = (x + knock) * np.minimum(1, t * 900)
    x = _lp(x, 6500, 2)
    rel = int(min(0.22, dur * 0.4 + 0.05) * SR)
    if 0 < rel < L:
        x[-rel:] *= np.linspace(1, 0, rel) ** 1.3
    put(b_, t0, np.tanh(x * 1.15), g)
