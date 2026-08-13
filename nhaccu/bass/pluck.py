"""pluck — day bass mo hinh vat ly

Trich nguyen van tu `greeplib/bassgtr.py` cua geese-3d-country.
Chua: `STRING_CHAR`, `_loss_pole`, `_allpass`, `_group_delay`, `_tune`, `_loop_filter`, `_excite`, `_comb`, `_STR_CACHE`, `pluck`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _bp, _hp, _lp, _peak
from .._core import hz


# Per-string character. Lower strings are wound heavier: darker, longer
# sustain, more inharmonicity. The G string is thin and dies quickly.
STRING_CHAR = {
    0: dict(B=2.6e-4, t60=5.6, fc=1150.0, bright=0.72, level=1.00),
    1: dict(B=1.7e-4, t60=5.0, fc=1450.0, bright=0.80, level=0.97),
    2: dict(B=1.0e-4, t60=4.3, fc=1900.0, bright=0.88, level=0.94),
    3: dict(B=6.0e-5, t60=3.6, fc=2500.0, bright=0.96, level=0.90),
}


def _loss_pole(fc):
    """One-pole coefficient for a given corner, in Hz.

    This is the single most important number in the model. It sets how much
    faster the high partials die than the fundamental, which is most of what
    the ear uses to tell a string from an oscillator. Put the corner up at
    6 kHz -- which is what you get if you pick the coefficient by feel -- and
    every harmonic decays at the same rate and the note sounds like an organ
    with a fast attack."""
    return float(np.clip(np.exp(-2.0 * np.pi * fc / SR), 0.05, 0.97))


def _allpass(c, order=1):
    """(c + z^-1) / (1 + c z^-1), raised to `order`."""
    b = np.array([c, 1.0])
    a = np.array([1.0, c])
    bb, aa = np.array([1.0]), np.array([1.0])
    for _ in range(order):
        bb = np.convolve(bb, b)
        aa = np.convolve(aa, a)
    return bb, aa


def _group_delay(b, a, w):
    """Group delay of an IIR at one normalised frequency, in samples."""
    try:
        _, gd = sg.group_delay((b, a), w=[w])
        return float(gd[0])
    except Exception:
        return 0.0


def _tune(f0, loss_a, loss_g, disp_c, disp_n):
    """Split the required loop delay between the delay line and the allpasses.

    Everything in the loop has its own delay, and the stiffness allpasses have
    a lot of it. Ignore that and the string is physically longer than you asked
    for and the note plays flat -- 35 cents flat on a low E, which is not a
    subtle effect. So: measure what the filters cost at the fundamental, and
    give the delay line only what is left over.
    """
    period = SR / f0
    w0 = 2 * np.pi * f0 / SR
    b_l = np.array([loss_g * (1.0 - loss_a)])
    a_l = np.array([1.0, -loss_a])
    if disp_n > 0 and abs(disp_c) > 1e-6:
        b_d, a_d = _allpass(disp_c, disp_n)
    else:
        b_d, a_d = np.array([1.0]), np.array([1.0])
    b = np.convolve(b_l, b_d)
    a = np.convolve(a_l, a_d)
    gd = _group_delay(b, a, w0)
    remaining = period - gd
    if remaining < 4.0:                      # very high notes: drop the stiffness
        return max(int(round(period)), 4), 0.0, 0
    N = int(np.floor(remaining))
    frac = float(np.clip(remaining - N, 0.0, 0.999))
    return N, frac, disp_n


def _loop_filter(frac, loss_a, loss_g, disp_c, disp_n):
    """Everything in the feedback path, multiplied into one IIR.

    * a one-pole lowpass  -> frequency-dependent decay (highs die first)
    * a fractional-delay allpass -> exact tuning between integer samples
    * a cascade of allpasses -> stiffness, which stretches the partials sharp
    """
    b_l = np.array([loss_g * (1.0 - loss_a)])
    a_l = np.array([1.0, -loss_a])
    c = (1.0 - frac) / (1.0 + frac)
    b_f, a_f = _allpass(c, 1)
    if disp_n > 0 and abs(disp_c) > 1e-6:
        b_d, a_d = _allpass(disp_c, disp_n)
    else:
        b_d, a_d = np.array([1.0]), np.array([1.0])
    b = np.convolve(np.convolve(b_l, b_f), b_d)
    a = np.convolve(np.convolve(a_l, a_f), a_d)
    return b, a


def _excite(N, pluck_pos, hardness, seed, open_string=False):
    """What the finger or pick actually leaves on the string.

    A triangular displacement peaking at the pluck point (this is what puts
    the comb there), plus a short noise burst for the contact itself.
    """
    R = np.random.default_rng(seed)
    p = int(np.clip(pluck_pos * N, 2, N - 2))
    tri = np.empty(N)
    tri[:p] = np.linspace(0.0, 1.0, p)
    tri[p:] = np.linspace(1.0, 0.0, N - p)
    burst = R.standard_normal(N)
    burst = _lp(burst, 900 + 6500 * hardness, 2)
    burst *= np.exp(-np.arange(N) / (N * (0.10 + 0.25 * (1 - hardness))))
    exc = tri * (1.0 - 0.35 * hardness) + burst * (0.30 + 0.55 * hardness)
    exc -= exc.mean()
    return exc / (np.abs(exc).max() + 1e-9)


def _comb(x, delay_samples, depth=1.0):
    """y = x - depth * x delayed. One null every SR/delay Hz."""
    d = int(round(delay_samples))
    if d < 1:
        return x
    y = x.copy()
    y[d:] -= depth * x[:-d]
    return y


_STR_CACHE = {}


def pluck(midi, ring, vel=1.0, string=0, fret=0, pluck_pos=0.19,
          pickup_pos=0.115, hardness=0.35, seed=0, damp_extra=0.0):
    """Render one plucked note as raw string motion, before any amplifier.

    `ring` is how long the string is allowed to sound, in seconds -- the
    player passes the time until the next note on this same string, which is
    what actually stops a bass note.
    """
    key = (int(midi), round(ring, 2), round(vel, 2), string, fret,
           round(pluck_pos, 3), round(pickup_pos, 3), round(hardness, 2),
           seed % 8, round(damp_extra, 2))
    if key in _STR_CACHE:
        return _STR_CACHE[key]

    ch = STRING_CHAR[string]
    f0 = hz(midi)
    ring = float(np.clip(ring, 0.05, 6.0))
    n_out = int(ring * SR) + int(0.05 * SR)

    # --- decay: T60 falls with pitch and with fret position (a stopped
    #     string is shorter and its damping at the fret is lossier) ---
    t60 = ch['t60'] * (0.55 + 0.45 * np.exp(-fret / 9.0))
    t60 *= (1.0 - 0.45 * damp_extra)
    if fret == 0:
        t60 *= 1.25                       # open strings ring on
    # loop gain that yields that T60 at the fundamental
    loss_g = float(np.clip(10.0 ** (-3.0 / (t60 * f0)), 0.90, 0.99999))
    # one-pole in the loop: how much faster the highs go. A stopped string is
    # damped at the fret, so higher positions lose their top end sooner.
    loss_a = _loss_pole(ch['fc'] * (1.0 - 0.30 * min(fret, 14) / 14.0)
                        * (1.0 - 0.45 * damp_extra))

    # --- stiffness: allpass dispersion, stronger on the wound low strings ---
    B = ch['B']
    disp_c = float(np.clip(-0.30 * np.tanh(B * 4.2e3), -0.45, 0.0))
    disp_n = 4 if string <= 1 else 2
    N, frac, disp_n = _tune(f0, loss_a, loss_g, disp_c, disp_n)
    n_out = int(ring * SR) + int(0.05 * SR)

    # --- two polarisations: same string, two planes, slightly different ---
    out = np.zeros(n_out + N * 2)
    R = np.random.default_rng(9000 + int(midi) * 13 + seed)
    for pol, (detune, amp_p, extra_loss) in enumerate(
            [(0.0, 1.0, 1.0), (float(R.uniform(0.0006, 0.0018)), 0.62, 0.984)]):
        Np, fracp, dnp = _tune(f0 * (1 - detune), loss_a, loss_g * extra_loss,
                               disp_c, disp_n)
        bp, ap = _loop_filter(fracp, loss_a, loss_g * extra_loss, disp_c, dnp)
        buf = _excite(Np, pluck_pos + (0.02 if pol else 0.0), hardness,
                      seed * 7 + pol * 101 + int(midi))
        buf = _comb(buf, Np * pluck_pos, 0.92)      # the pluck-position comb
        zi = np.zeros(max(len(ap), len(bp)) - 1)
        periods = int(np.ceil((n_out + Np) / Np))
        acc = np.empty(periods * Np)
        for k in range(periods):
            acc[k * Np:(k + 1) * Np] = buf
            buf, zi = sg.lfilter(bp, ap, buf, zi=zi)
        seg = acc[:n_out + N]
        out[:len(seg)] += seg * amp_p

    y = out[:n_out]
    # --- the pickup only sees one point on the string ---
    y = _comb(y, N * pickup_pos, 0.86)
    # magnetic pickup + tone circuit: a broad resonance, then it stops
    y = _peak(y, 2400 * (0.7 + 0.3 * ch['bright']), 1.4, 0.55)
    y = _lp(y, 5200, 2)
    y = _hp(y, 32, 2)

    # --- body and neck: weak on a solid body, but not nothing ---
    y = _peak(y, 96, 3.2, 0.16)
    y = _peak(y, 208, 2.4, 0.10)

    # --- attack: the string takes a couple of ms to get going, and the
    #     finger makes a noise of its own on the way past ---
    t = np.arange(len(y)) / SR
    y *= np.minimum(1.0, t / 0.0022)
    thump = _lp(R.standard_normal(len(y)), 420, 2) * np.exp(-t / 0.0075) * 0.22
    nail = _bp(R.standard_normal(len(y)), 1400, 5200, 2) * np.exp(-t / 0.0035) * 0.30 * hardness
    y = y + thump + nail

    # --- the note is stopped by a hand, not by running out of buffer ---
    rel = int(min(0.045, ring * 0.30) * SR)
    if 0 < rel < len(y):
        y[-rel:] *= np.linspace(1, 0, rel) ** 1.4
        # the mute itself makes a small sound
        mute = _lp(R.standard_normal(rel), 700, 2) * np.exp(-np.arange(rel) / SR / 0.006)
        y[-rel:] += mute * 0.05 * vel

    y = y / (np.abs(y).max() + 1e-9) * ch['level'] * vel
    y = y.astype(np.float32)
    _STR_CACHE[key] = y
    return y
