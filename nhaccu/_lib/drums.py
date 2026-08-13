"""Helper dung chung, trich tu greeplib/drums.py.

Trich nguyen van tu `greeplib/drums.py` cua geese-3d-country.
Chua: `IDEAL`, `JMN`, `MORD`, `AIRLOADED`, `modal`, `bessel_gains`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy.special import jv
from .._dsp import SR


# Ideal circular-membrane mode ratios, and the air-loaded (real drum) set.
IDEAL = [1.0000, 1.5934, 2.1356, 2.2952, 2.6528, 2.9172, 3.1551, 3.4998, 3.5983, 3.6470]


JMN = [2.405, 3.832, 5.136, 5.520, 6.380, 7.016, 7.588, 8.417, 8.654, 8.771]


MORD = [0, 1, 2, 0, 3, 1, 4, 2, 0, 5]


AIRLOADED = [1.00, 1.50, 1.98, 2.44, 2.89, 3.36]


def modal(f0, taus, gains, L, rg, glide=0.05, tg=0.02, detune_cents=0,
          ratios=IDEAL):
    t = np.arange(L) / SR
    g = 1 + glide * np.exp(-t / tg)
    ph = 2 * np.pi * np.cumsum(g) / SR
    det = 2 ** (detune_cents / 1200)
    out = np.zeros(L)
    for r, tau, gn in zip(ratios, taus, gains):
        f = f0 * r * det
        if f > SR / 2.2:
            continue
        out += gn * np.exp(-t / tau) * np.sin(ph * f + rg.uniform(0, 2 * np.pi))
    return out


def bessel_gains(r_rel, rg, n=10, jitter=0.08):
    """Modal amplitudes for a strike at relative radius r_rel (0 = centre)."""
    r = np.clip(r_rel + rg.normal(0, jitter), 0.0, 0.92)
    g = [abs(jv(MORD[i], JMN[i] * r)) * 10 ** (rg.normal(0, 0.35)) for i in range(n)]
    g = np.array(g)
    return g / (g.max() + 1e-9)
