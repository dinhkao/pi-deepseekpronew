"""Kit — bo trong

Trich nguyen van tu `greeplib/drums.py` cua geese-3d-country.
Chua: `Kit`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _bp, _hp, _lp, _ramp
from .._lib.drums import AIRLOADED, bessel_gains, modal


class Kit:
    def __init__(self, seed=7):
        self.rng = np.random.default_rng(seed)
        self._cache = {}

    # ----------------------------------------------------------------- kick --
    def kick(self, vel=1.0, tune=48.0, click=1.0, mode='acoustic'):
        R = self.rng
        L = int(0.55 * SR)
        t = np.arange(L) / SR
        det = 2 ** (R.normal(0, 28) / 1200)
        if mode == 'acoustic':
            body = np.zeros(L)
            for k in range(1, 7):
                f = (tune * k * 0.9 + 7) * det
                tau = 0.26 / (k ** 0.72)
                body += (1.0 / k ** 0.9) * np.exp(-t / tau) * np.sin(2 * np.pi * f * t + R.uniform(0, 2 * np.pi))
            body *= 1 + 0.09 * np.exp(-t / 0.025)
        elif mode == '808':
            f = tune * det * (1 + 1.15 * np.exp(-t / 0.018))
            body = np.sin(2 * np.pi * np.cumsum(f) / SR + R.uniform(0, 2 * np.pi)) * np.exp(-t / 0.42)
            body += np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * np.exp(-t / 0.05) * 0.22
        else:
            f = tune * det * (1 + 2.6 * np.exp(-t / 0.030))
            body = np.sin(2 * np.pi * np.cumsum(f) / SR + R.uniform(0, 2 * np.pi)) * np.exp(-t / 0.16)
            body += np.sin(2 * np.pi * np.cumsum(f * 0.5) / SR) * np.exp(-t / 0.22) * 0.5
        fm = np.sin(2 * np.pi * 185 * det * t + (2.2 * np.exp(-t / 0.04)) * np.sin(2 * np.pi * 259 * t))
        body += fm * np.exp(-t / 0.045) * 0.24
        n = R.standard_normal(L) * np.exp(-t / 0.0045)
        cl = _lp(_hp(n, 220), 4200) * click * 0.5 * vel
        return _ramp(np.tanh(_hp(body * vel + cl, 32, 4) * 1.5))

    # ---------------------------------------------------------------- snare --
    def snare(self, vel=1.0, tune=205.0, art='center'):
        R = self.rng
        L = int(0.42 * SR)
        t = np.arange(L) / SR
        r_rel = {'center': 0.12, 'edge': 0.62, 'ghost': 0.34, 'rim': 0.20, 'cross': 0.80}[art]
        g = bessel_gains(r_rel, R)
        taus = np.array([0.045, 0.20, 0.17, 0.055, 0.14, 0.11, 0.09, 0.08, 0.05, 0.07]) * (1 + R.normal(0, 0.10, 10))
        if art == 'rim':
            taus *= 0.7
        det = R.normal(0, 30)
        mem = modal(tune, taus, g, L, R, glide=0.06, tg=0.02, detune_cents=det)
        mem += modal(tune * 1.42, taus * 0.8, g * 0.55, L, R, glide=0.05, tg=0.018,
                     detune_cents=det + R.normal(0, 18)) * 0.6
        envm = np.abs(sg.lfilter(*sg.butter(2, 120 / (SR / 2), 'low'), np.abs(mem)))
        envm /= (envm.max() + 1e-9)
        thr = {'ghost': 0.42, 'center': 0.14, 'edge': 0.20, 'rim': 0.06, 'cross': 0.85}[art]
        wire_env = np.clip(envm - thr, 0, None) / (1 - thr)
        n = R.standard_normal(L)
        wire = _bp(n, 1100, 9500, 3)
        buzz = (R.random(L) < 0.055).astype(float)
        buzz = sg.lfilter([1], [1, -0.90], buzz)
        wire = wire * (0.55 + 0.85 * buzz / (buzz.max() + 1e-9))
        d = int(R.uniform(0.0005, 0.003) * SR)
        wire = np.concatenate([np.zeros(d), wire])[:L]
        wire *= wire_env * np.exp(-t / R.uniform(0.11, 0.24))
        stick = _bp(R.standard_normal(L), 2200, 7000, 2) * np.exp(-t / 0.0035)
        if art == 'rim':
            shell = _bp(R.standard_normal(L), 420, 900, 2) * np.exp(-t / 0.035) * 1.1
            x = (mem * 0.55 + wire * 1.5 + stick * 1.5 + shell) * vel * 2.2
        elif art == 'cross':
            wood = _bp(R.standard_normal(L), 1300, 3400, 2) * np.exp(-t / 0.006) * 2.2
            x = (mem * 0.16 + wood + wire * 0.10) * vel * 1.5
        elif art == 'ghost':
            x = (mem * 0.85 + wire * 0.55 + stick * 0.35) * vel * 0.22
        else:
            x = (mem * 0.75 + wire * 1.0 + stick * 0.8) * vel
        return _ramp(np.tanh(x * 1.25))

    def flam(self, vel=1.0, tune=205.0, art='center'):
        R = self.rng
        gap = int(R.uniform(0.012, 0.032) * SR)
        a = self.snare(vel * R.uniform(0.30, 0.48), tune * 1.01, 'ghost')
        b = self.snare(vel, tune, art)
        out = np.zeros(max(len(a), len(b)) + gap)
        out[:len(a)] += a
        out[gap:gap + len(b)] += b
        return out

    # ------------------------------------------------------------------ toms --
    def tom(self, vel=1.0, tune=120.0, art='center'):
        R = self.rng
        L = int(0.7 * SR)
        t = np.arange(L) / SR
        g = bessel_gains(0.20 if art == 'center' else 0.6, R, n=6)
        taus = np.array([0.30, 0.42, 0.34, 0.26, 0.20, 0.16]) * (1 + R.normal(0, 0.12, 6))
        x = modal(tune, taus, g, L, R, glide=0.08, tg=0.03,
                  detune_cents=R.normal(0, 35), ratios=AIRLOADED)
        x += modal(tune * 1.06, taus * 0.85, g * 0.5, L, R, glide=0.07, tg=0.028,
                   ratios=AIRLOADED) * 0.5
        stick = _bp(R.standard_normal(L), 1800, 5500, 2) * np.exp(-t / 0.004)
        return _ramp(np.tanh((x + stick * 0.5) * vel * 1.2))

    def ctom(self, vel=1.0, tune=150.0):
        """Single-headed concert tom: dry, short, clearly pitched."""
        R = self.rng
        L = int(0.34 * SR)
        t = np.arange(L) / SR
        g = bessel_gains(0.16, R, n=6)
        taus = np.array([0.115, 0.145, 0.100, 0.070, 0.052, 0.038]) * (1 + R.normal(0, 0.09, 6))
        x = modal(tune, taus, g, L, R, glide=0.13, tg=0.020,
                  detune_cents=R.normal(0, 22), ratios=AIRLOADED)
        stick = _bp(R.standard_normal(L), 2000, 6500, 2) * np.exp(-t / 0.0030) * 0.8
        return _ramp(np.tanh((x + stick) * vel * 1.35))

    # -------------------------------------------------------------- cymbals --
    def _cym(self, L, nmodes, fmin, fmax, tau_lo, tau_hi, seed, migrate=0.10):
        R = np.random.default_rng(seed)
        t = np.arange(L) / SR
        f = np.sort(R.uniform(fmin, fmax, nmodes))
        f = f * (1 + R.normal(0, 0.02, nmodes))
        tau = np.clip(tau_hi * (f / fmin) ** (-0.62) * (1 + R.normal(0, 0.18, nmodes)), tau_lo, tau_hi)
        ph = R.uniform(0, 2 * np.pi, nmodes)
        amp = (f / fmin) ** (-0.42) * (1 + R.normal(0, 0.35, nmodes))
        atk = migrate * (f - fmin) / (fmax - fmin) + 0.0008
        out = np.zeros(L)
        for i in range(0, nmodes, 200):
            ff = f[i:i + 200][:, None]
            tt = tau[i:i + 200][:, None]
            aa = amp[i:i + 200][:, None]
            pp = ph[i:i + 200][:, None]
            kk = atk[i:i + 200][:, None]
            out += (aa * np.exp(-t / tt) * (1 - np.exp(-t / kk)) * np.sin(2 * np.pi * ff * t + pp)).sum(0)
        return out / (np.abs(out).max() + 1e-9)

    def hat(self, vel=1.0, openness=0.0, art='tip', variant=None):
        R = self.rng
        v = int(R.integers(0, 7)) if variant is None else variant
        o = float(np.clip(openness, 0, 1))
        key = ('hat', round(o, 2), art, v)
        if key not in self._cache:
            L = int((0.06 + 0.75 * o) * SR)
            tau_hi = 0.045 + 0.62 * o
            a = self._cym(L, 260, 320, 15500, 0.012, tau_hi, seed=9000 + v * 13 + int(o * 100), migrate=0.05 * o)
            b = self._cym(L, 260, 320, 15500, 0.012, tau_hi, seed=9500 + v * 13 + int(o * 100), migrate=0.05 * o)
            delta = 0.004 + 0.016 * o
            bb = np.interp(np.clip(np.arange(L) * (1 + delta), 0, L - 1), np.arange(L), b)
            x = a + bb * (0.55 + 0.45 * o)
            if o < 0.15:
                buzz = (np.random.default_rng(7 + v).random(L) < 0.09).astype(float)
                x = x * (1 + 0.5 * buzz)
            self._cache[key] = (x / (np.abs(x).max() + 1e-9)).astype(np.float32)
        x = self._cache[key].astype(np.float64).copy()
        L = len(x)
        t = np.arange(L) / SR
        if art == 'edge':
            x = _bp(x, 380, 11000, 2) * 1.6
        elif art == 'tip':
            x = _bp(x, 900, 15000, 2)
        elif art == 'foot':
            x = _bp(x, 200, 4200, 2) * 1.2
        sh = 2 ** (R.normal(0, 0.018))
        idx = np.clip(np.arange(L) * sh, 0, L - 1)
        i0 = idx.astype(int)
        fr = idx - i0
        x = x[i0] * (1 - fr) + x[np.minimum(i0 + 1, L - 1)] * fr
        return _ramp(x * vel * np.exp(-t / (0.05 + 0.85 * o)))

    def crash(self, vel=1.0, size=1.0, variant=None):
        R = self.rng
        v = int(R.integers(0, 4)) if variant is None else variant
        key = ('crash', round(size, 2), v)
        if key not in self._cache:
            self._cache[key] = self._cym(int(1.5 * size * SR), 700, 260, 15800, 0.10,
                                         1.35 * size, seed=3000 + v * 17, migrate=0.22).astype(np.float32)
        x = self._cache[key].astype(np.float64)
        L = len(x)
        sh = 2 ** (R.normal(0, 0.02))
        idx = np.clip(np.arange(L) * sh, 0, L - 1)
        i0 = idx.astype(int)
        fr = idx - i0
        return _ramp((x[i0] * (1 - fr) + x[np.minimum(i0 + 1, L - 1)] * fr) * vel)

    def splash(self, vel=1.0, variant=None):
        R = self.rng
        v = int(R.integers(0, 3)) if variant is None else variant
        key = ('splash', v)
        if key not in self._cache:
            self._cache[key] = self._cym(int(0.55 * SR), 420, 600, 16000, 0.05, 0.45,
                                         seed=5200 + v * 9, migrate=0.06).astype(np.float32)
        return _ramp(self._cache[key].astype(np.float64) * vel)

    def ride(self, vel=1.0, bell=False, variant=None):
        R = self.rng
        v = int(R.integers(0, 5)) if variant is None else variant
        key = ('ride', bell, v)
        if key not in self._cache:
            L = int(0.95 * SR)
            x = self._cym(L, 60, 520, 7000, 0.20, 0.85, seed=4400 + v * 11, migrate=0.02) if bell else \
                self._cym(L, 420, 330, 14000, 0.06, 0.72, seed=4000 + v * 11, migrate=0.10)
            self._cache[key] = x.astype(np.float32)
        x = self._cache[key].astype(np.float64)
        ping = _bp(R.standard_normal(len(x)), 2500, 7000, 2) * np.exp(-np.arange(len(x)) / SR / 0.006)
        return _ramp((x + ping * (0.45 if not bell else 0.8)) * vel)

    # ------------------------------------------------------------- handheld --
    def clap(self, vel=1.0):
        R = self.rng
        L = int(0.45 * SR)
        t = np.arange(L) / SR
        out = np.zeros(L)
        for i in range(int(R.integers(3, 7))):
            d = int(max(0, R.normal(i * 0.011, 0.003)) * SR)
            b = _bp(R.standard_normal(L), 1050, 4400, 2) * np.exp(-t / 0.006)
            out[d:] += b[:L - d] * R.uniform(0.6, 1.0)
        tail = _bp(R.standard_normal(L), 900, 3600, 2) * np.exp(-t / 0.055) * 0.55
        return _ramp((out + tail) * vel)

    def tamb(self, vel=1.0):
        R = self.rng
        L = int(0.3 * SR)
        t = np.arange(L) / SR
        x = np.zeros(L)
        for fr in (4700, 6100, 7900, 9800, 12200):
            b, a = sg.iirpeak(fr / (SR / 2), R.uniform(45, 75))
            x += sg.lfilter(b, a, R.standard_normal(L))
        jingle = (R.random(L) < 0.14).astype(float)
        return _ramp(x * np.exp(-t / R.uniform(0.028, 0.055)) * (0.6 + 0.7 * jingle) * vel * 0.45)

    def shaker(self, vel=1.0):
        R = self.rng
        L = int(0.16 * SR)
        t = np.arange(L) / SR
        return _ramp(_bp(R.standard_normal(L), 4200, 13000, 2) * np.exp(-t / R.uniform(0.016, 0.030)) * vel * 0.5)

    def steel(self, vel=1.0, tune=330.0, damp=1.0):
        """Struck metal -- anvil, brake drum, the clatter in a Greep breakdown."""
        R = self.rng
        L = int(min(2.2 / damp, 2.2) * SR)
        t = np.arange(L) / SR
        ratios = [1.0, 2.756, 5.404, 8.933, 13.35, 18.64, 2.01, 4.11]
        amps = [1.0, 0.52, 0.30, 0.17, 0.09, 0.05, 0.22, 0.13]
        x = np.zeros(L)
        for r, a in zip(ratios, amps):
            f = tune * r * (1 + R.normal(0, 0.004))
            if f > SR / 2.2:
                continue
            tau = (0.95 / damp) / (r ** 0.55)
            x += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * t + R.uniform(0, 6.28))
        strike = _bp(R.standard_normal(L), 3000, 11000, 2) * np.exp(-t / 0.0018) * 0.7
        return _ramp(np.tanh((x + strike) * vel * 0.9) * 0.9)
