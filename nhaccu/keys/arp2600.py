"""arp2600 — ARP 2600

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `_ladder`, `arp2600`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _blpulse, _blsaw, _hp, _ramp, env, phase
from .._core import hz, nn, put
from .._lib.keys import _T


def _ladder(x, cut, res=2.4):
    """Bo loc ladder 4 cuc, cut la mang (bien thien theo thoi gian).

    Chay theo KHOI 64 mau: he so coi nhu khong doi trong khoi. Sai so nghe
    khong ra, nhanh hon vong theo mau khoang 60 lan.
    """
    n = len(x)
    cut = np.clip(cut, 30.0, SR * 0.44)
    out = np.empty(n)
    zi = [np.zeros(1) for _ in range(4)]
    fb = 0.0
    # 64 mau la nua chu ky o E4 -> phan hoi cong huong duoc cap nhat qua tho
    # va keo cao do do duoc lech toi +33 cent. 16 mau dua ve duoi 3 cent.
    blk = 16
    i = 0
    while i < n:
        j = min(i + blk, n)
        fc = float(np.mean(cut[i:j]))
        gk = 1.0 - np.exp(-2 * np.pi * fc / SR)
        seg = x[i:j] - fb * res * 0.24
        for s in range(4):
            seg, zi[s] = sg.lfilter([gk], [1.0, -(1.0 - gk)], seg, zi=zi[s])
        out[i:j] = seg
        fb = float(seg[-1]) if len(seg) else fb
        i = j
    return out * (1.0 + res * 0.16)


def arp2600(b_, t0, m, dur, g=0.10, cutoff=1600.0, res=2.6, env_amt=2200.0,
            atk=0.006, dec=0.22, sus=0.45, rel=0.10, wave='saw', det=8.0,
            sub=0.4, seed=0, glide_from=None, pw=0.42, drive=1.5):
    """Mono synth kieu ARP 2600: 2 VCO + ladder co cong huong + ADSR len bo loc."""
    L = int((dur + rel + 0.05) * SR)
    R = np.random.default_rng(seed + 2600)
    f0 = hz(nn(m))
    fa = np.full(L, f0)
    if glide_from is not None:
        gn = max(int(min(0.09, dur * 0.5) * SR), 2)
        s = np.linspace(0, 1, gn)
        fa[:gn] = hz(nn(glide_from)) * (1 - s) + f0 * s
    t = np.arange(L) / SR
    fa = fa * (1 + 0.0012 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.25) / 0.3, 0, 1))
    d2 = 2 ** (det / 1200.0)
    p1 = phase(fa, L)
    p2 = phase(fa * d2, L)
    if wave == 'saw':
        osc = _blsaw(p1, 26) + _blsaw(p2, 26) * 0.85
    elif wave == 'pulse':
        osc = _blpulse(p1, pw, 26) + _blpulse(p2, 0.5 - pw * 0.3, 26) * 0.8
    else:
        osc = _blsaw(p1, 26) + _blpulse(p2, pw, 26) * 0.8
    if sub > 0:
        osc += _blpulse(phase(fa * 0.5, L), 0.5, 20) * sub
    osc += R.standard_normal(L) * 0.012
    e = env(L, atk, dec, sus, rel)
    ef = env(L, atk, dec * 1.1, sus * 0.8, rel * 1.2)
    y = _ladder(osc * 0.30, cutoff + env_amt * ef, res)
    y = np.tanh(y * drive)
    y = _hp(y, 40, 2)
    put(b_, t0, _ramp(y * e, 2.0), g * _T['arp2600'])
