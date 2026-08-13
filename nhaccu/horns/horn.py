"""horn — ken don

Trich nguyen van tu `greeplib/horns.py` cua geese-3d-country.
Chua: `horn`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _fadeout, _peak, _ramp, env, swell
from .._core import hz, nn, put
from .._lib.horns import ODD_ONLY, VOICES


def horn(b_, t0, m, dur, g=0.10, voice='trumpet', art='tongued', vel=1.0,
         seed=0, det=0.0, vib=1.0, fall=0.0, growl=0.0, air=1.0):
    """One horn note.

    `vel` drives brightness as well as level, which is what makes a section
    stab sound like a stab instead of a loud sustain.
    """
    m = nn(m)
    (nh, tilt, bl, bh, forms, noise, atk, scoop, vr, vd, lo, hi) = VOICES[voice]
    L = int(min(dur + 0.35, 8.0) * SR)
    if L < 64:
        return
    t = np.arange(L) / SR
    R = np.random.default_rng(6000 + m * 7 + seed * 13 + hash(voice) % 1000)
    f0 = hz(m) * 2 ** (det / 1200.0)

    # ---- amplitude & brightness shapes per articulation ----
    if art == 'stab':
        atk *= 0.45
        amp = np.exp(-t / max(dur * 0.42, 0.05)) * np.minimum(1, t / max(atk, 1e-4))
        bcurve = 1.0
    elif art == 'swell':
        amp = swell(L, 0.62, 1.8)
        bcurve = 0.55 + 0.45 * amp
    elif art == 'legato':
        atk *= 2.2
        amp = env(L, atk, 0.08, 0.92, min(0.16, dur * 0.35 + 0.04))
        bcurve = 0.85
    else:  # tongued
        amp = env(L, atk, 0.06, 0.86, min(0.13, dur * 0.35 + 0.03))
        bcurve = 0.80 + 0.20 * np.minimum(1, t / 0.05)

    bright = np.clip((bl + (bh - bl) * vel) * bcurve, 0.05, 0.985)
    if np.isscalar(bright):
        bright = np.full(L, bright)
    # the attack transient is always brighter than the body
    bright = np.clip(bright + 0.10 * np.exp(-t / 0.030), 0.05, 0.985)

    # ---- pitch contour ----
    pitch = np.ones(L)
    if scoop:
        pitch *= 2 ** ((scoop * np.exp(-t / max(atk * 1.6, 0.012))) / 12.0)
    if vib and vd:
        onset = np.clip((t - min(0.22, dur * 0.35)) / 0.35, 0, 1)
        pitch *= 1 + vd * vib * onset * np.sin(2 * np.pi * vr * (1 + 0.06 * np.sin(2 * np.pi * 0.7 * t)) * t
                                               + R.uniform(0, 6))
    if art == 'shake':
        onset = np.clip((t - 0.05) / 0.10, 0, 1)
        pitch *= 2 ** ((0.55 * onset * np.sin(2 * np.pi * 6.8 * t)) / 12.0)
    if art == 'rip':
        pitch *= 2 ** ((-5.0 * np.exp(-t / 0.045)) / 12.0)
    if art == 'doit':
        tail = np.clip((t - dur * 0.72) / max(dur * 0.28, 0.04), 0, 1)
        pitch *= 2 ** ((3.5 * tail ** 2) / 12.0)
        amp = amp * (1 - 0.55 * tail)
    if art == 'fall' or fall:
        amt = fall if fall else 7.0
        tail = np.clip((t - dur * 0.60) / max(dur * 0.40, 0.05), 0, 1)
        pitch *= 2 ** ((-amt * tail ** 1.6) / 12.0)
        amp = amp * (1 - 0.75 * tail ** 1.3)
    if growl:
        pitch *= 1 + 0.010 * growl * np.sin(2 * np.pi * 28.0 * t)

    ph = 2 * np.pi * np.cumsum(f0 * pitch) / SR

    # ---- additive body: harmonic k gets amplitude bright^(k-1) / k^tilt ----
    odd = ODD_ONLY.get(voice, 1.0)
    x = np.zeros(L)
    logb = np.log(np.clip(bright, 1e-4, 0.999))
    for k in range(1, nh + 1):
        fk = f0 * k
        if fk > SR / 2.25:
            break
        a = np.exp(logb * (k - 1)) / (k ** tilt)
        if k % 2 == 0:
            a = a * odd
        x += a * np.sin(ph * k + R.uniform(0, 2 * np.pi) * 0.15)

    # ---- breath / air ----
    if noise > 0 and air > 0:
        nz = R.standard_normal(L)
        band = _bp(nz, max(f0 * 0.8, 200), min(f0 * 9, 12000), 2)
        chiff = np.exp(-t / 0.028) * 1.6 + 1.0
        x += band * noise * air * chiff * (0.4 + 0.6 * bright)

    x *= amp

    # ---- bore / bell resonances ----
    y = x
    for f, q, gg in forms:
        y = _peak(y, f, q, gg)
    y = _bp(y, lo, hi, 2)
    if growl:
        y = np.tanh(y * (1 + 2.0 * growl))

    y = _fadeout(_ramp(y, 1.2), 22.0)
    put(b_, t0, np.tanh(y * 0.75) * 1.1, g)
