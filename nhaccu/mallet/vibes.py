"""vibes — vibraphone

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `vibes`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _hp
from .._core import hz, nn, put


def vibes(b_, t0, m, dur, g=0.10, motor=0.0, motor_rate=5.5, mallet=0.5,
          seed=0, ring=None):
    """Vibraphone. Bars are tuned 1 : 4 : 10, and the motor is a real
    amplitude tremolo on the resonators, not a filter wobble.

    `dur` is how long the note actually sounds, damper included. An earlier
    version always added 2.2 s of ring on top, which at any real tempo means
    the note is still sounding two chords later -- the bar is in tune, the
    note is in tune, and the passage is not. Pass `ring` to ask for more."""
    m = nn(m)
    ring = dur if ring is None else ring
    rel = min(0.30, ring * 0.35 + 0.05)
    L = int((min(ring, 6.0) + rel) * SR)
    t = np.arange(L) / SR
    R = np.random.default_rng(1900 + m * 3 + seed)
    f = hz(m)
    x = np.zeros(L)
    for r, a, tau in [(1.0, 1.0, 2.4), (3.98, 0.30, 0.85), (10.1, 0.12, 0.30),
                      (2.01, 0.07, 0.45), (17.6, 0.05, 0.14)]:
        ff = f * r * (1 + R.normal(0, 0.0025))
        if ff > SR / 2.2:
            continue
        x += a * np.exp(-t / tau) * np.sin(2 * np.pi * ff * t + R.uniform(0, 6))
    click = _bp(R.standard_normal(L), 1200, 6000, 2) * np.exp(-t / 0.0030) * mallet
    x = x + click
    if motor:
        x *= (1 - motor * 0.5) + motor * 0.5 * (1 + np.sin(2 * np.pi * motor_rate * t + R.uniform(0, 6)))
    x *= np.minimum(1, t * 2600)
    rn = int(rel * SR)
    if 0 < rn < L:
        x[-rn:] *= np.linspace(1, 0, rn) ** 1.4
    put(b_, t0, _hp(x, 120, 2), g)
