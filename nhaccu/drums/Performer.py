"""Performer — nguoi danh trong

Trich nguyen van tu `greeplib/drums.py` cua geese-3d-country.
Chua: `SIGMA`, `ACC16`, `Performer`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _fadeout
from .._core import T


SIGMA = {'kick': 0.0055, 'snare': 0.0026, 'hat': 0.0031, 'tom': 0.0035,
         'cym': 0.0040, 'perc': 0.0045, 'lperc': 0.0040}


ACC16 = [1.00, 0.45, 0.70, 0.45, 0.85, 0.45, 0.68, 0.45,
         0.95, 0.45, 0.70, 0.45, 0.85, 0.48, 0.68, 0.52]


class Performer:
    """Places kit hits on a beat grid with human timing and velocity.

    Half the timing error is a FIXED per-position offset that repeats every
    bar (a player's physical habit); the other half is Gaussian noise.  On-beat
    notes land slightly late, off-16ths slightly early.
    """

    def __init__(self, kit, total_s, seed=11, laid=0.008):
        self.k = kit
        self.rng = np.random.default_rng(seed)
        N = int(total_s * SR) + SR
        self.bus = {n: np.zeros(N) for n in ['kick', 'snare', 'hat', 'tom', 'cym', 'perc', 'lperc']}
        R = np.random.default_rng(seed + 1)
        self.sysoff = {}
        for inst in SIGMA:
            for p in range(16):
                self.sysoff[(inst, p)] = R.normal(0, 0.0034)
        self.laid = {'kick': 0.0, 'snare': laid, 'hat': -0.002, 'tom': 0.006,
                     'cym': 0.0, 'perc': 0.003, 'lperc': 0.002}
        self.openhats = []
        self.hum = 1.0
        self.flatacc = False

    def _t(self, beat, inst, pos16):
        p = int(round(pos16)) % 16
        metric = 0.004 if p % 4 == 0 else -0.0032
        h = self.hum
        return (T(beat) + self.sysoff[(inst, p)] * h
                + self.rng.normal(0, SIGMA[inst] * h) + metric * h + self.laid[inst] * h)

    def _add(self, name, t0, x, g=1.0):
        b = self.bus[name]
        i = int(t0 * SR)
        if i < 0:
            x = x[-i:]
            i = 0
        n = min(len(x), len(b) - i)
        if n > 0:
            b[i:i + n] += x[:n] * g
        return i

    def _v(self, base, pos16, arc=1.0):
        if self.flatacc:
            return base * arc * (1 + self.rng.normal(0, 0.030))
        return base * ACC16[int(pos16) % 16] * arc * (1 + self.rng.normal(0, 0.042 * self.hum))

    # --- kit voices ---
    def K(self, beat, pos16, v=1.0, arc=1.0, mode='acoustic', tune=48.0):
        self._add('kick', self._t(beat, 'kick', pos16), self.k.kick(self._v(v, pos16, arc), tune, mode=mode))

    def S(self, beat, pos16, v=1.0, art='center', arc=1.0, tune=205.0):
        vv = self._v(v, pos16, arc)
        x = self.k.flam(vv, tune, art) if art == 'flam' else self.k.snare(vv, tune, art)
        self._add('snare', self._t(beat, 'snare', pos16), x)

    def H(self, beat, pos16, v=1.0, o=0.0, art='tip', arc=1.0, choke_beat=None):
        x = self.k.hat(self._v(v, pos16, arc), o, art)
        i = self._add('hat', self._t(beat, 'hat', pos16), x)
        if o > 0.25 and choke_beat is not None:
            self.openhats.append((i, int(T(choke_beat) * SR)))

    def TM(self, beat, pos16, v=1.0, tune=120.0, arc=1.0):
        self._add('tom', self._t(beat, 'tom', pos16), self.k.tom(self._v(v, pos16, arc), tune))

    def CT(self, beat, pos16, v=1.0, tune=150.0, arc=1.0):
        self._add('tom', self._t(beat, 'tom', pos16), self.k.ctom(self._v(v, pos16, arc), tune))

    def CR(self, beat, pos16, v=1.0, size=1.0):
        self._add('cym', self._t(beat, 'cym', pos16), self.k.crash(v * (1 + self.rng.normal(0, .04)), size))

    def SPL(self, beat, pos16, v=1.0):
        self._add('cym', self._t(beat, 'cym', pos16), self.k.splash(v))

    def RD(self, beat, pos16, v=1.0, bell=False, arc=1.0):
        self._add('cym', self._t(beat, 'cym', pos16), self.k.ride(self._v(v, pos16, arc), bell))

    def CL(self, beat, pos16, v=1.0, arc=1.0):
        self._add('perc', self._t(beat, 'perc', pos16), self.k.clap(self._v(v, pos16, arc)))

    def TB(self, beat, pos16, v=1.0, arc=1.0):
        self._add('perc', self._t(beat, 'perc', pos16), self.k.tamb(self._v(v, pos16, arc)))

    def SH(self, beat, pos16, v=1.0, arc=1.0):
        self._add('perc', self._t(beat, 'perc', pos16), self.k.shaker(self._v(v, pos16, arc)))

    def ST(self, beat, pos16, v=1.0, tune=330.0, damp=1.0, arc=1.0):
        self._add('perc', self._t(beat, 'perc', pos16), self.k.steel(self._v(v, pos16, arc), tune, damp))

    def hit(self, bus, beat, pos16, sample, v=1.0, arc=1.0):
        """Generic: drop any one-shot on any bus with the performer's feel."""
        self._add(bus, self._t(beat, bus if bus in SIGMA else 'perc', pos16),
                  sample, self._v(v, pos16, arc))

    # --- gestures ---
    def REV(self, beat, dur_beats=0.5, v=0.7, kind='crash'):
        """A reversed hit whose TAIL ends exactly on `beat`."""
        x = self.k.crash(v, 0.8) if kind == 'crash' else self.k.snare(v, 215, 'edge')
        n = max(int((T(beat) - T(beat - dur_beats)) * SR), 64)
        if len(x) > n:
            x = x[:n]
        y = x[::-1].copy() * (np.linspace(0, 1, len(x)) ** 1.6)
        y = _fadeout(y, 6.0)
        self._add('cym' if kind == 'crash' else 'snare', T(beat) - len(y) / SR, y)

    def roll(self, beat0, beats=1.0, step=0.25, v0=0.30, v1=0.55, tune=205.0,
             art='ghost', jitter=0.0):
        hum0 = self.hum
        self.hum = jitter
        n = int(round(beats / step))
        for i in range(n):
            v = v0 + (v1 - v0) * (i / max(n - 1, 1))
            self.S(beat0 + i * step, int(i * (16 * step / 4)) % 16, v, art=art, tune=tune)
        self.hum = hum0

    def apply_chokes(self):
        h = self.bus['hat']
        for start, cut in self.openhats:
            if start < cut < len(h):
                n = min(int(0.005 * SR), len(h) - cut)
                h[cut:cut + n] *= np.linspace(1, 0.25, n)
