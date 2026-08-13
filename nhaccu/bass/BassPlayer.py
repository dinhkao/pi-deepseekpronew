"""BassPlayer — nguoi choi bass (chon day, the bam)

Trich nguyen van tu `greeplib/bassgtr.py` cua geese-3d-country.
Chua: `STRINGS`, `MAX_FRET`, `BassPlayer`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR
from .._core import HUM, T, nn, put
from ..bass.pluck import pluck


# Standard tuning. Fret 0 is the open string.
STRINGS = [28, 33, 38, 43]           # E1 A1 D2 G2


MAX_FRET = 20


class BassPlayer:
    """Decides which string each note goes on, and stops the last one.

    Notes are collected first and rendered afterwards, because how long a
    note rings is not a property of the note -- it is a property of what the
    player does next on the same string.
    """

    def __init__(self, seed=0, style='finger', pluck_pos=0.19,
                 pickup_pos=0.115, prefer_low=True, max_pos=9):
        self.notes = []
        self.rng = np.random.default_rng(4000 + seed)
        self.style = style
        self.pluck_pos = pluck_pos
        self.pickup_pos = pickup_pos
        self.prefer_low = prefer_low
        self.max_pos = max_pos
        self.hand = 5                   # where the left hand currently is
        self._seed = seed

    # ---- choosing a string, the way a hand does ----
    def _choose(self, midi, force=None):
        if force is not None:
            return force, midi - STRINGS[force]
        best, best_cost = None, 1e9
        for si, open_m in enumerate(STRINGS):
            fret = midi - open_m
            if fret < 0 or fret > MAX_FRET:
                continue
            cost = abs(fret - self.hand) * 1.0          # don't move far
            if fret == 0:
                cost -= 2.5                              # open strings are free
            if fret > self.max_pos:
                cost += 6.0                              # stay out of the dusty end
            if self.prefer_low:
                cost += si * 1.2                         # fat strings first
            if cost < best_cost:
                best, best_cost = (si, fret), cost
        if best is None:
            si = int(np.clip((midi - 28) // 5, 0, 3))
            best = (si, max(midi - STRINGS[si], 0))
        return best

    def note(self, beat, dur_beats, midi, vel=1.0, art='finger', slide=0.0,
             string=None, ghost=False):
        """art: finger / pick / thumb / ghost / harmonic"""
        midi = nn(midi)
        si, fret = self._choose(midi, string)
        self.hand = int(0.7 * self.hand + 0.3 * fret)
        self.notes.append(dict(beat=float(beat), dur=float(dur_beats), midi=midi,
                               vel=float(vel), art=art, slide=float(slide),
                               string=si, fret=int(fret), ghost=bool(ghost)))
        return si, fret

    def line(self, cells, base_vel=1.0):
        """cells = [(beat, dur_beats, midi[, vel[, art]]), ...]"""
        for c in cells:
            beat, dur, midi = c[0], c[1], c[2]
            vel = c[3] if len(c) > 3 else 1.0
            art = c[4] if len(c) > 4 else 'finger'
            self.note(beat, dur, midi, vel * base_vel, art)

    # ---- rendering ----
    def render(self, b_, g=0.30, hum=None, bar_beats=4, humanize=True):
        H = hum or HUM
        ns = sorted(self.notes, key=lambda n: n['beat'])
        # when does each string next get used?
        nxt = {}
        for i, n in enumerate(ns):
            for j in range(i + 1, len(ns)):
                if ns[j]['string'] == n['string']:
                    nxt[i] = ns[j]['beat']
                    break
            else:
                nxt[i] = n['beat'] + n['dur'] + 8.0
        for i, n in enumerate(ns):
            b = n['beat']
            t0 = H.t(b, bar_beats) if humanize else T(b)
            # the string rings until the hand needs it again, or until the
            # player lifts a finger at the end of the written note -- whichever
            # comes first, plus a little, because hands are not gates
            held = T(b + n['dur'] * 1.12) - T(b)
            until_reuse = T(nxt[i]) - T(b)
            ring = max(min(held, until_reuse), 0.06)
            hard = {'finger': 0.30, 'pick': 0.85, 'thumb': 0.10,
                    'ghost': 0.55, 'harmonic': 0.20}[n['art']]
            vel = n['vel'] * (0.22 if n['ghost'] or n['art'] == 'ghost' else 1.0)
            damp = 0.85 if (n['ghost'] or n['art'] == 'ghost') else 0.0
            x = pluck(n['midi'], ring, vel, n['string'], n['fret'],
                      pluck_pos=self.pluck_pos, pickup_pos=self.pickup_pos,
                      hardness=hard, seed=self._seed + i, damp_extra=damp)
            x = x.astype(np.float64)
            if n['slide']:
                L = len(x)
                tt = np.arange(L) / SR
                d = (2 ** ((n['slide'] * np.exp(-tt / 0.055)) / 12) - 1)
                idx = np.clip(np.cumsum(1 + d), 0, L - 1)
                i0 = idx.astype(int)
                fr = idx - i0
                x = x[i0] * (1 - fr) + x[np.minimum(i0 + 1, L - 1)] * fr
            gg = H.g(g, b, bar_beats=bar_beats) if humanize else g
            put(b_, t0, x, gg)
        return len(ns)
