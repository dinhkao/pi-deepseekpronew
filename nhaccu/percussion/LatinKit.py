"""LatinKit — bo go Latin

Trich nguyen van tu `greeplib/latin.py` cua geese-3d-country.
Chua: `_membrane`, `LatinKit`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _bp, _hp, _lp, _ramp
from .._lib.drums import AIRLOADED, bessel_gains, modal


def _membrane(f0, L, r_rel, taus, R, glide=0.10, tg=0.02, detune=0.0):
    g = bessel_gains(r_rel, R, n=6)
    return modal(f0, taus, g, L, R, glide=glide, tg=tg,
                 detune_cents=detune, ratios=AIRLOADED)


class LatinKit:
    """One-shot generators. Stateless apart from the rng, cheap enough to call
    a few thousand times per song."""

    def __init__(self, seed=23):
        self.rng = np.random.default_rng(seed)
        self._c = {}

    # ------------------------------------------------------------- congas --
    def conga(self, vel=1.0, tune=200.0, art='open'):
        """art: open / slap / mute / heel / tip / bass"""
        R = self.rng
        cfg = {
            'open': (0.18, 0.42, 1.00, 0.55),
            'slap': (0.68, 0.085, 1.00, 1.90),
            'mute': (0.30, 0.055, 0.85, 0.75),
            'heel': (0.10, 0.070, 0.70, 0.30),
            'tip':  (0.72, 0.040, 0.35, 1.10),
            'bass': (0.05, 0.52, 1.15, 0.25),
        }[art]
        r_rel, dec, amp, edge = cfg
        L = int(min(dec * 3.2 + 0.10, 0.85) * SR)
        t = np.arange(L) / SR
        taus = np.array([1.00, 0.72, 0.55, 0.40, 0.30, 0.23]) * dec * (1 + R.normal(0, 0.09, 6))
        x = _membrane(tune, L, r_rel, taus, R, glide=0.09, tg=0.018, detune=R.normal(0, 22))
        x += _membrane(tune * 1.005, L, r_rel, taus * 0.82, R, glide=0.08, tg=0.016) * 0.45
        slap = _bp(R.standard_normal(L), 1500, 7000, 2) * np.exp(-t / (0.0035 + 0.004 * edge)) * edge
        if art == 'bass':
            x = _lp(x, 340, 2) * 1.5
        return _ramp(np.tanh((x * amp + slap * 0.8) * vel * 1.25))

    def bongo(self, vel=1.0, hembra=False, art='open'):
        tune = 330.0 if hembra else 520.0
        R = self.rng
        r_rel, dec, edge = {'open': (0.20, 0.14, 0.9),
                            'slap': (0.70, 0.045, 2.2),
                            'mute': (0.34, 0.030, 1.0),
                            'tip':  (0.62, 0.022, 0.6)}[art]
        L = int(min(dec * 4 + 0.06, 0.5) * SR)
        t = np.arange(L) / SR
        taus = np.array([1.0, 0.70, 0.52, 0.38, 0.28, 0.20]) * dec * (1 + R.normal(0, 0.10, 6))
        x = _membrane(tune, L, r_rel, taus, R, glide=0.13, tg=0.012, detune=R.normal(0, 25))
        slap = _bp(R.standard_normal(L), 2200, 9500, 2) * np.exp(-t / 0.0030) * edge
        return _ramp(np.tanh((x + slap * 0.75) * vel * 1.3))

    # -------------------------------------------------------------- surdo --
    def surdo(self, vel=1.0, tune=72.0, muted=False):
        R = self.rng
        dec = 0.10 if muted else 0.75
        L = int(min(dec * 2.6 + 0.15, 1.4) * SR)
        t = np.arange(L) / SR
        taus = np.array([1.0, 0.62, 0.44, 0.32, 0.24, 0.18]) * dec * (1 + R.normal(0, 0.08, 6))
        x = _membrane(tune, L, 0.10, taus, R, glide=0.16, tg=0.045, detune=R.normal(0, 18))
        beat = _lp(R.standard_normal(L), 900, 2) * np.exp(-t / 0.006) * 0.7
        x = _lp(x, 1600, 2)
        return _ramp(np.tanh((x * 1.2 + beat) * vel * 1.15))

    def zabumba(self, vel=1.0, tune=95.0, stick=False):
        """Baiao drum: a low boom with the mallet, a dry tap on the other head."""
        R = self.rng
        if stick:
            L = int(0.14 * SR)
            t = np.arange(L) / SR
            x = _bp(R.standard_normal(L), 900, 4200, 2) * np.exp(-t / 0.010)
            x += np.sin(2 * np.pi * 640 * t) * np.exp(-t / 0.012) * 0.5
            return _ramp(x * vel * 0.9)
        L = int(0.6 * SR)
        t = np.arange(L) / SR
        taus = np.array([0.34, 0.22, 0.16, 0.12, 0.09, 0.07]) * (1 + R.normal(0, 0.08, 6))
        x = _membrane(tune, L, 0.08, taus, R, glide=0.22, tg=0.030)
        return _ramp(np.tanh(_lp(x, 900, 2) * vel * 1.4))

    # ---------------------------------------------------------- small skins --
    def tamborim(self, vel=1.0):
        R = self.rng
        L = int(0.11 * SR)
        t = np.arange(L) / SR
        taus = np.array([0.030, 0.020, 0.014, 0.010, 0.008, 0.006]) * (1 + R.normal(0, 0.12, 6))
        x = _membrane(830.0, L, 0.30, taus, R, glide=0.20, tg=0.008, detune=R.normal(0, 30))
        stick = _bp(R.standard_normal(L), 2600, 11000, 2) * np.exp(-t / 0.0018) * 1.4
        return _ramp(np.tanh((x + stick) * vel * 1.5))

    def caixa(self, vel=1.0, art='center'):
        """Samba snare: tighter, brighter and buzzier than a kit snare."""
        R = self.rng
        L = int(0.24 * SR)
        t = np.arange(L) / SR
        r_rel = {'center': 0.15, 'ghost': 0.36, 'rim': 0.22}[art]
        taus = np.array([0.030, 0.10, 0.08, 0.035, 0.06, 0.05]) * (1 + R.normal(0, 0.10, 6))
        mem = _membrane(285.0, L, r_rel, taus, R, glide=0.07, tg=0.014, detune=R.normal(0, 28))
        wire = _bp(R.standard_normal(L), 2200, 12000, 3)
        buzz = sg.lfilter([1], [1, -0.86], (R.random(L) < 0.09).astype(float))
        wire *= (0.5 + 0.9 * buzz / (buzz.max() + 1e-9)) * np.exp(-t / R.uniform(0.045, 0.085))
        stick = _bp(R.standard_normal(L), 3000, 9000, 2) * np.exp(-t / 0.0022)
        amp = 0.28 if art == 'ghost' else 1.0
        return _ramp(np.tanh((mem * 0.6 + wire * 1.15 + stick * 0.7) * vel * amp * 1.3))

    def repique(self, vel=1.0, art='open'):
        R = self.rng
        L = int(0.20 * SR)
        t = np.arange(L) / SR
        dec = 0.055 if art == 'open' else 0.018
        taus = np.array([1.0, 0.7, 0.5, 0.36, 0.26, 0.20]) * dec * (1 + R.normal(0, 0.1, 6))
        x = _membrane(430.0, L, 0.22, taus, R, glide=0.16, tg=0.010)
        stick = _bp(R.standard_normal(L), 2000, 8000, 2) * np.exp(-t / 0.0024) * 1.2
        return _ramp(np.tanh((x + stick) * vel * 1.35))

    def pandeiro(self, vel=1.0, art='open'):
        """art: open / slap / thumb / jingle"""
        R = self.rng
        L = int(0.26 * SR)
        t = np.arange(L) / SR
        if art == 'jingle':
            head = np.zeros(L)
        else:
            dec = {'open': 0.075, 'slap': 0.022, 'thumb': 0.10}[art]
            taus = np.array([1.0, 0.68, 0.5, 0.36, 0.27, 0.2]) * dec * (1 + R.normal(0, 0.1, 6))
            head = _membrane(300.0 if art == 'thumb' else 420.0, L,
                             0.62 if art == 'slap' else 0.20, taus, R, glide=0.14, tg=0.010)
        jing = np.zeros(L)
        for fr in (5200, 6800, 8600, 10800, 13200):
            b, a = sg.iirpeak(fr / (SR / 2), R.uniform(50, 90))
            jing += sg.lfilter(b, a, R.standard_normal(L))
        rat = (R.random(L) < 0.16).astype(float)
        jing *= np.exp(-t / R.uniform(0.020, 0.045)) * (0.55 + 0.8 * rat)
        mixj = 0.55 if art != 'jingle' else 1.25
        return _ramp(np.tanh((head * 1.1 + jing * mixj) * vel * 1.2))

    # --------------------------------------------------------------- metal --
    def _bellmodes(self, L, f0, ratios, amps, taus, R, strike=(2500, 9000), sg_=0.9):
        t = np.arange(L) / SR
        x = np.zeros(L)
        for r, a, tau in zip(ratios, amps, taus):
            f = f0 * r * (1 + R.normal(0, 0.003))
            if f > SR / 2.2:
                continue
            x += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * t + R.uniform(0, 6.28))
        st = _bp(R.standard_normal(L), strike[0], strike[1], 2) * np.exp(-t / 0.0016) * sg_
        return x + st

    def agogo(self, vel=1.0, low=False):
        R = self.rng
        f0 = 640.0 if low else 830.0
        L = int(0.5 * SR)
        x = self._bellmodes(L, f0, [1.0, 2.41, 4.05, 5.92, 8.3],
                            [1.0, 0.55, 0.30, 0.16, 0.08],
                            [0.30, 0.20, 0.14, 0.09, 0.06], R)
        return _ramp(np.tanh(_hp(x, 300, 2) * vel * 1.1))

    def cowbell(self, vel=1.0, tune=560.0, damp=1.0):
        R = self.rng
        L = int(min(0.45 / damp, 0.45) * SR)
        x = self._bellmodes(L, tune, [1.0, 1.52, 2.48, 3.44, 4.87, 6.4],
                            [1.0, 0.82, 0.46, 0.28, 0.15, 0.09],
                            [0.22 / damp, 0.18 / damp, 0.12 / damp, 0.08 / damp,
                             0.055 / damp, 0.04 / damp], R, strike=(1800, 7000))
        return _ramp(np.tanh(_bp(x, 400, 9000, 2) * vel * 1.15))

    def campana(self, vel=1.0, mouth=False):
        """Mambo bell -- bigger and lower than a timbale bell."""
        return self.cowbell(vel * (1.15 if mouth else 0.9),
                            tune=420.0 if mouth else 505.0,
                            damp=0.85 if mouth else 1.3)

    def timbale(self, vel=1.0, hembra=False, art='open'):
        R = self.rng
        tune = 260.0 if hembra else 360.0
        L = int(0.4 * SR)
        t = np.arange(L) / SR
        dec = {'open': 0.10, 'rim': 0.030, 'roll': 0.055}[art]
        taus = np.array([1.0, 0.7, 0.5, 0.36, 0.26, 0.2]) * dec * (1 + R.normal(0, 0.1, 6))
        head = _membrane(tune, L, 0.18 if art != 'rim' else 0.55, taus, R, glide=0.12, tg=0.012)
        shell = np.zeros(L)
        for f, tau, a in [(1350, 0.030, 0.6), (2180, 0.018, 0.4), (3400, 0.011, 0.25)]:
            shell += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * (1 + R.normal(0, .01)) * t + R.uniform(0, 6))
        stick = _bp(R.standard_normal(L), 2500, 10000, 2) * np.exp(-t / 0.0020)
        return _ramp(np.tanh((head + shell * (1.4 if art == 'rim' else 0.5) + stick * 0.9) * vel * 1.3))

    def cascara(self, vel=1.0):
        """Stick on the side of the timbale shell."""
        R = self.rng
        L = int(0.12 * SR)
        t = np.arange(L) / SR
        x = np.zeros(L)
        for f, tau, a in [(1180, 0.014, 1.0), (2400, 0.008, 0.6), (4100, 0.004, 0.35)]:
            x += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * (1 + R.normal(0, .012)) * t + R.uniform(0, 6))
        x += _bp(R.standard_normal(L), 2500, 9000, 2) * np.exp(-t / 0.0016)
        return _ramp(np.tanh(x * vel * 1.1))

    def triangle(self, vel=1.0, open_=True):
        R = self.rng
        L = int((1.6 if open_ else 0.12) * SR)
        t = np.arange(L) / SR
        x = np.zeros(L)
        base = 4100.0
        for r, a in [(1.0, 1.0), (2.14, 0.7), (3.31, 0.55), (4.62, 0.4),
                     (5.9, 0.3), (7.4, 0.22), (9.1, 0.15)]:
            f = base * r * (1 + R.normal(0, 0.004))
            if f > SR / 2.2:
                continue
            tau = (0.9 if open_ else 0.030) / (r ** 0.35)
            x += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * t + R.uniform(0, 6))
        return _ramp(_hp(x, 2500, 2) * vel * 0.55)

    # ---------------------------------------------------------------- wood --
    def clave(self, vel=1.0):
        R = self.rng
        L = int(0.14 * SR)
        t = np.arange(L) / SR
        x = np.zeros(L)
        for f, tau, a in [(2400, 0.022, 1.0), (3760, 0.013, 0.5), (5400, 0.007, 0.25)]:
            x += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * (1 + R.normal(0, .008)) * t + R.uniform(0, 6))
        x += _bp(R.standard_normal(L), 3000, 9000, 2) * np.exp(-t / 0.0012) * 0.5
        return _ramp(np.tanh(x * vel * 1.2))

    def woodblock(self, vel=1.0, tune=1500.0):
        R = self.rng
        L = int(0.10 * SR)
        t = np.arange(L) / SR
        x = (np.exp(-t / 0.014) * np.sin(2 * np.pi * tune * t)
             + 0.4 * np.exp(-t / 0.007) * np.sin(2 * np.pi * tune * 2.7 * t))
        x += _bp(R.standard_normal(L), 2000, 8000, 2) * np.exp(-t / 0.0012) * 0.6
        return _ramp(x * vel * 0.9)

    # ------------------------------------------------------------ scrapers --
    def guiro(self, vel=1.0, long_=True, n=None):
        R = self.rng
        dur = 0.28 if long_ else 0.09
        L = int(dur * SR)
        t = np.arange(L) / SR
        n = n or (11 if long_ else 4)
        grains = np.zeros(L)
        for i in range(n):
            p = int((i / n) * L * 0.92)
            g = _bp(R.standard_normal(int(0.010 * SR)), 1800, 7000, 2)
            g *= np.exp(-np.arange(len(g)) / SR / 0.0025)
            m = min(len(g), L - p)
            grains[p:p + m] += g[:m] * R.uniform(0.6, 1.0)
        return _ramp(grains * vel * 1.6 * np.exp(-t / (dur * 0.9)))

    def cabasa(self, vel=1.0, turn=False):
        R = self.rng
        L = int((0.16 if turn else 0.07) * SR)
        t = np.arange(L) / SR
        beads = (R.random(L) < 0.42).astype(float) * R.uniform(0.4, 1.0, L)
        x = _bp(beads, 3500, 12000, 2)
        return _ramp(x * np.exp(-t / (0.05 if turn else 0.018)) * vel * 1.3)

    def chocalho(self, vel=1.0):
        """The big samba shaker -- a wall of small metal."""
        R = self.rng
        L = int(0.13 * SR)
        t = np.arange(L) / SR
        x = _bp(R.standard_normal(L), 3800, 14000, 2)
        x *= (0.6 + 0.8 * (R.random(L) < 0.5))
        return _ramp(x * np.exp(-t / 0.028) * vel * 0.7)

    def shekere(self, vel=1.0):
        R = self.rng
        L = int(0.20 * SR)
        t = np.arange(L) / SR
        beads = (R.random(L) < 0.30).astype(float) * R.uniform(0.3, 1.0, L)
        x = _bp(beads, 1800, 9000, 2) * np.exp(-t / 0.035)
        gourd = _bp(R.standard_normal(L), 180, 600, 2) * np.exp(-t / 0.020) * 0.5
        return _ramp((x + gourd) * vel * 1.2)

    # ---------------------------------------------------------------- cuica --
    def cuica(self, vel=1.0, note=None, up=True, dur=0.34):
        """A friction drum. The stick rubs the membrane and it *talks*.

        Modelled as a narrow resonance swept in pitch, driven by a rasping
        pulse train -- the squeak is the point.
        """
        R = self.rng
        L = int(dur * SR)
        t = np.arange(L) / SR
        f0 = 240.0 if note is None else float(note)
        sweep = np.linspace(0.72, 1.55, L) if up else np.linspace(1.55, 0.72, L)
        f = f0 * sweep
        ph = 2 * np.pi * np.cumsum(f) / SR
        rasp = sg.sawtooth(ph, 0.15) * 0.6 + np.sin(ph) * 0.5
        rasp += _bp(R.standard_normal(L), 400, 3000, 2) * 0.25
        out = np.zeros(L)
        step = 1024
        for i in range(0, L, step):
            fc = float(np.clip(f[min(i, L - 1)] * 3.1, 200, SR / 2 - 800))
            bq, aq = sg.iirpeak(fc / (SR / 2), 7.0)
            seg = sg.lfilter(bq, aq, rasp[i:i + step * 2])[:min(step, L - i)]
            out[i:i + len(seg)] += seg
        out = _bp(out + rasp * 0.35, 150, 5000, 2)
        e = np.minimum(1, t / 0.012) * np.exp(-np.maximum(t - dur * 0.55, 0) / 0.06)
        return _ramp(np.tanh(out * e * vel * 1.4))
