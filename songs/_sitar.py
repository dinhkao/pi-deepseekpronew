"""Nhac cu bo sung cho bai phong cach An Do (Love You To).

- sitar:   Karplus-Strong + jawari buzz + sympathetic drones + meend glide
- tanpura: drone 4 not lap (Pa-sa-sa-Sa), pluck cham, ring dai
- tabla:   dayan (treble, bend nhe) + bayan (bass, bend sau)

Viet theo phong cach cac instrument trong nhaccu/ (mono stem, put() vao buffer).
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg

from nhaccu._dsp import SR, _bp, _lp, _hp, _ramp, _fadeout, env
from nhaccu._core import hz, nn, put
from nhaccu._lib.inst import ks, damp


# ------------------------------------------------------------------- sitar --

_SIT = {}


def sitar(b_, t0, m, dur, g=0.14, seed=0, gl=0.0, ring=None, buzz=1.0):
    """Sitar don am. `gl` la meend (cents bend tu dau note, roi giam dan)."""
    m = nn(m)
    key = (m, round(dur, 2), seed % 8, round(gl), round(buzz, 1))
    if key not in _SIT:
        # day chinh: KS rat sang, it mat mat
        x = ks(m, dur + 0.5, damp=0.9987, bright=0.9, seed=seed).astype(np.float64)
        L = len(x)
        if gl:
            tt = np.arange(L) / SR
            d = (2 ** ((gl * np.exp(-tt / 0.12)) / 12) - 1)
            idx = np.clip(np.cumsum(1 + d), 0, L - 1)
            i0 = idx.astype(int)
            fr = idx - i0
            x = x[i0] * (1 - fr) + x[np.minimum(i0 + 1, L - 1)] * fr

        # jawari: cau dan cong tao tieng buzz theo bien do day
        R = np.random.default_rng(seed + 99)
        e = _lp(np.abs(x), 200, 2)
        e /= (e.max() + 1e-9)
        gate = np.clip((e - 0.12) / 0.88, 0, 1) ** 1.4
        buzzn = _bp(R.standard_normal(L), 1500, 5200, 2) * gate * 0.20 * buzz
        # thoi nhe o moi chu ky day rung -> "jawari" dac trung
        buzzn += _bp(R.standard_normal(L), 2400, 9000, 2) * (gate * 0.08)

        # sympathetic: day coi (C, G) nghe nhe theo
        sym = np.zeros(L)
        tt = np.arange(L) / SR
        for f, a in ((65.41, 0.05), (98.0, 0.035), (130.8, 0.03), (196.0, 0.02)):
            sym += a * np.sin(2 * np.pi * f * tt + R.uniform(0, 6)) * e
        x = x * 0.9 + sym + buzzn
        x = _hp(x, 70, 2)
        x = np.tanh(x * 1.2)
        _SIT[key] = _fadeout(_ramp(x, 1.5), 30.0).astype(np.float32)
    put(b_, t0, _SIT[key].astype(np.float64), g)


# ----------------------------------------------------------------- tanpura --

_TAN = {}


def tanpura(b_, t0, m, dur, g=0.10, seed=0):
    """Mot pluck tanpura: attack mem, nghe cham, ring dai 2-3s."""
    m = nn(m)
    key = (m, round(dur, 2), seed % 6)
    if key not in _TAN:
        L = int(dur * SR)
        t = np.arange(L) / SR
        R = np.random.default_rng(300 + m * 3 + seed)
        x = ks(m, dur, damp=0.9991, bright=0.5, seed=seed).astype(np.float64)
        if len(x) < L:
            x = np.concatenate([x, np.zeros(L - len(x))])
        x = x[:L]
        # pluck cham: goc len tu tu, roi ngam lau
        a = env(L, 0.030, 0.0, 1.0, 1.8)
        a = a * (1 + 0.10 * np.sin(2 * np.pi * 3.1 * t + R.uniform(0, 6)))
        x = x * a
        x = _bp(x, 60, 4200, 2)
        _TAN[key] = _fadeout(x, 40.0).astype(np.float32)
    put(b_, t0, _TAN[key].astype(np.float64), g)


_TAB = {}


def tabla(b_, t0, kind='na', g=0.30, seed=0):
    """Tabla mot tieng. kind: 'na' treble, 'ge' bass, 'te' treble nhe."""
    key = (kind, seed % 9)
    if key not in _TAB:
        R = np.random.default_rng(700 + seed)
        if kind == 'ge':
            L = int(0.55 * SR)
            t = np.arange(L) / SR
            f = 95 * (1 + 0.55 * np.exp(-t / 0.05))
            ph = 2 * np.pi * np.cumsum(f) / SR
            x = np.sin(ph) * np.exp(-t / 0.16)
            x += 0.5 * np.sin(2 * ph) * np.exp(-t / 0.07)
            x = _lp(x, 900, 2) * 1.4
        else:
            L = int(0.30 * SR)
            t = np.arange(L) / SR
            base = 210 if kind == 'na' else 260
            f = base * (1 + 0.16 * np.exp(-t / 0.012))
            ph = 2 * np.pi * np.cumsum(f) / SR
            x = np.sin(ph) * np.exp(-t / 0.11)
            x += 0.4 * np.sin(2.3 * ph) * np.exp(-t / 0.05)
            x += 0.2 * np.sin(3.5 * ph) * np.exp(-t / 0.03)
            tick = _hp(R.standard_normal(L), 2500, 2) * np.exp(-t / 0.0022)
            x = _hp(x, 120, 2) * 1.2 + tick * 0.5
        _TAB[key] = _fadeout(_ramp(x, 0.5), 6.0).astype(np.float32)
    put(b_, t0, _TAB[key].astype(np.float64), g)
