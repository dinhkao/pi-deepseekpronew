"""natbass — bass dien gay ngon

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `_NB`, `natbass`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _hp, _lp, _peak
from .._core import hz, nn, put


_NB = {}


def natbass(b_, t0, m, dur, g=0.30, gl=0.0, bright=0.4, growl=0.45, sub=0.75):
    """Fingered electric bass through an amp.

    Two things this gets right that a plain filtered-oscillator bass does not:

    * **The note stops when you stop it.**  The buffer is exactly `dur` plus a
      short release.  An earlier version always added a fixed 0.3 s tail,
      which at any real tempo means every note overlaps the next one or two --
      the low end turns into one continuous smear and no line is audible.

    * **You hear a bass in the midrange, not the sub.**  Almost all the
      *pitch* information a listener uses sits between 300 Hz and 2 kHz.  So
      there is a parallel saturated band (the amp) mixed in on top of the
      fundamental, and the low end is deliberately trimmed underneath so it
      stops fighting the kick drum for headroom it does not need.
    """
    m = nn(m)
    dur = max(float(dur), 0.06)
    key = (m, round(dur, 3), round(bright, 2), round(growl, 2), round(sub, 2))
    if key not in _NB:
        f0 = hz(m)
        rel = min(0.11, dur * 0.42 + 0.025)
        L = int((min(dur, 3.0) + rel) * SR)
        t = np.arange(L) / SR
        R = np.random.default_rng(2400 + m * 7 + int(bright * 37))
        B = 0.00009
        nP = int(np.clip((SR / 2.4) // max(f0, 1), 4, 34))
        settle = 1 + 0.0075 * np.exp(-t / 0.042)
        out = np.zeros(L)
        for k in range(1, nP + 1):
            fk = f0 * k * np.sqrt(1 + B * k * k)
            if fk > SR / 2.3:
                break
            # upper partials must survive long enough to define the note
            tau = (1.9 / (k ** 0.58)) * float(1 + R.normal(0, 0.07))
            amp = (1.0 / (k ** 1.02)) * (0.85 if k % 2 == 0 else 1.0)
            ph = 2 * np.pi * np.cumsum(fk * settle) / SR
            out += amp * np.exp(-t / max(tau, 0.03)) * (
                np.sin(ph + R.uniform(0, 6))
                + 0.32 * np.sin(ph * float(1 + R.normal(0, 0.00035)) + R.uniform(0, 6)))
        out /= 1.9
        # finger/pick contact
        out = out + _bp(R.standard_normal(L), 700, 4000, 2) * np.exp(-t / 0.0055) * 0.30
        for fr, q, gg in [(95, 4.0, 0.22), (800, 2.0, 0.28), (1600, 2.0, 0.16)]:
            out = _peak(out, fr, q, gg)
        # filter envelope: bright for a third of a second, not a tenth
        br = _lp(out, 2600 + 1800 * bright, 2)
        dk = _lp(out, 900 + 500 * bright, 2)
        fe = np.exp(-t / 0.30)
        body = br * fe + dk * (1 - fe)
        # the amp: a saturated midrange copy is what makes a bass audible on
        # a phone speaker, and it is what a real rig does anyway
        amp_band = np.tanh(_bp(body, 500, 3000, 2) * 5.0) * growl
        lowend = _lp(body, 220, 2) * sub
        out = np.tanh((lowend + body * 0.55 + amp_band) * 1.15)
        out = _hp(out, 38, 2)
        out *= np.minimum(1, t / 0.0035)
        rn = int(rel * SR)
        if 0 < rn < L:
            out[-rn:] *= np.linspace(1, 0, rn) ** 1.25
        _NB[key] = out.astype(np.float32)
    x = _NB[key].astype(np.float64)
    if gl:
        L = len(x)
        tt = np.arange(L) / SR
        d = (2 ** ((gl * np.exp(-tt / 0.045)) / 12) - 1)
        idx = np.clip(np.cumsum(1 + d), 0, L - 1)
        i0 = idx.astype(int)
        fr = idx - i0
        x = x[i0] * (1 - fr) + x[np.minimum(i0 + 1, L - 1)] * fr
    put(b_, t0, x, g)
