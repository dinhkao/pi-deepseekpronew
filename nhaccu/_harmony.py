"""Chords, voicings and comping patterns.

The harmonic vocabulary here is deliberately wide: this record slides between
bossa ii-V chains, altered dominants, maj7#11 lydian pools and blunt triads
inside the same eight bars, and the voicing code has to survive all of it.
"""
from __future__ import annotations

import numpy as np

from ._core import nn, T, HUM
from ._dsp import SR

PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

QUAL = {
    '': [0, 4, 7], 'M': [0, 4, 7], 'maj': [0, 4, 7],
    'm': [0, 3, 7], 'min': [0, 3, 7],
    '5': [0, 7], 'no3': [0, 7],
    'sus2': [0, 2, 7], 'sus4': [0, 5, 7], 'sus': [0, 5, 7],
    'dim': [0, 3, 6], 'aug': [0, 4, 8], '+': [0, 4, 8],
    '6': [0, 4, 7, 9], 'm6': [0, 3, 7, 9],
    '69': [0, 4, 7, 9, 14], '6/9': [0, 4, 7, 9, 14],
    'm69': [0, 3, 7, 9, 14], 'm6/9': [0, 3, 7, 9, 14],
    '7': [0, 4, 7, 10], 'maj7': [0, 4, 7, 11], 'M7': [0, 4, 7, 11],
    'm7': [0, 3, 7, 10], 'mmaj7': [0, 3, 7, 11], 'm(maj7)': [0, 3, 7, 11],
    'dim7': [0, 3, 6, 9], 'm7b5': [0, 3, 6, 10], 'm7-5': [0, 3, 6, 10],
    '7sus4': [0, 5, 7, 10], '7sus': [0, 5, 7, 10], '9sus4': [0, 5, 7, 10, 14],
    'add9': [0, 4, 7, 14], 'madd9': [0, 3, 7, 14], 'add11': [0, 4, 7, 17],
    '9': [0, 4, 7, 10, 14], 'maj9': [0, 4, 7, 11, 14], 'M9': [0, 4, 7, 11, 14],
    'm9': [0, 3, 7, 10, 14], 'm11': [0, 3, 7, 10, 14, 17],
    '11': [0, 4, 7, 10, 14, 17], '13': [0, 4, 7, 10, 14, 21],
    'm13': [0, 3, 7, 10, 14, 21], 'maj13': [0, 4, 7, 11, 14, 21],
    'maj7#11': [0, 4, 7, 11, 18], 'M7#11': [0, 4, 7, 11, 18],
    'maj9#11': [0, 4, 7, 11, 14, 18],
    '7#11': [0, 4, 7, 10, 18], '9#11': [0, 4, 7, 10, 14, 18],
    '7b9': [0, 4, 7, 10, 13], '7#9': [0, 4, 7, 10, 15],
    '7b5': [0, 4, 6, 10], '7#5': [0, 4, 8, 10], 'aug7': [0, 4, 8, 10],
    '7b13': [0, 4, 7, 10, 20], '13b9': [0, 4, 10, 13, 21],
    '7alt': [0, 4, 10, 13, 20], '7b9#11': [0, 4, 10, 13, 18],
    'm7add11': [0, 3, 7, 10, 17], 'mmaj9': [0, 3, 7, 11, 14],
}


def _root(s):
    """Read a note name off the front. Returns (pitch_class, chars_consumed)."""
    r = PC[s[0].upper()]
    i = 1
    while i < len(s) and s[i] in '#b':
        r += 1 if s[i] == '#' else -1
        i += 1
    return r % 12, i


def split_sym(sym):
    """'Gb6/9' -> ('Gb6/9', None) but 'F/G' -> ('F', 'G').

    A '/' only means a slash bass if what follows is a note name AND the
    whole tail isn't already a legal quality -- otherwise 6/9 chords break.
    """
    s = sym.strip()
    r, i = _root(s)
    q = s[i:]
    if q in QUAL or q.replace(' ', '') in QUAL:
        return s, None
    if '/' in q:
        head, tail = q.rsplit('/', 1)
        if tail and tail[0].upper() in PC and (head in QUAL or head.replace(' ', '') in QUAL):
            return s[:i] + head, tail
    return s, None


def parse(sym):
    """'Fmaj9#11/G' -> (root_pc, [pitch classes], bass_pc, [intervals])"""
    body, bs = split_sym(sym)
    bass = None
    if bs is not None:
        bass = _root(bs)[0]
    r, i = _root(body)
    q = body[i:]
    if q not in QUAL:
        q2 = q.replace(' ', '')
        if q2 in QUAL:
            q = q2
        else:
            raise ValueError('unknown chord quality %r in %r' % (q, sym))
    pcs = [(r + x) % 12 for x in QUAL[q]]
    return r % 12, pcs, (bass if bass is not None else r % 12), [r + x for x in QUAL[q]]


def pcs_of(sym):
    return parse(sym)[1]


def voicelead(pcs, prev, lo=52, hi=76):
    """Pick octaves for a set of pitch classes so the voicing moves as little
    as possible from `prev`."""
    cands = []
    for pc in pcs:
        opts = [m for m in range(lo, hi + 1) if m % 12 == pc]
        if not opts:
            opts = [lo + ((pc - lo) % 12)]
        cands.append(opts)
    if prev is None:
        out = []
        cur = lo
        for opts in cands:
            o = [m for m in opts if m >= cur] or opts
            out.append(o[0])
            cur = out[-1] + 1
        return sorted(out)
    out = []
    used = set()
    for opts in cands:
        best = min(opts, key=lambda m: (min(abs(m - p) for p in prev), m in used,
                                        abs(m - int(np.mean(prev)))))
        out.append(best)
        used.add(best)
    out = sorted(set(out))
    if len(out) < len(pcs):
        for pc in pcs:
            if not any(m % 12 == pc for m in out):
                o = [m for m in range(lo, hi + 1) if m % 12 == pc]
                if o:
                    out.append(min(o, key=lambda m: abs(m - int(np.mean(out)))))
        out = sorted(set(out))
    return out


def stack_below(top, pcs, n=3, lo=40):
    """`n` actual chord tones, descending from `top`.

    Written because the obvious shortcut -- take the top voice and add a fixed
    interval below it, say a minor third -- puts a note that is not in the
    chord under every single chord. On a major-key hymn that lands a minor
    third below the 9th, which is the major 7th's neighbour, and the whole
    band sounds a semitone wrong on every bar.
    """
    want = {int(p) % 12 for p in pcs}
    pool = [m for m in range(int(lo), int(top) + 1) if m % 12 in want]
    if not pool:
        return [int(top)] * n
    out = [pool[-1]]
    i = len(pool) - 1
    while len(out) < n and i > 0:
        i -= 1
        if out[-1] - pool[i] >= 2:          # no unisons, no semitone doubles
            out.append(pool[i])
    while len(out) < n:
        out.append(out[-1] - 12)
    return out


def snap(note, pcs, direction=0, lo=24, hi=108):
    """Move `note` to the nearest chord tone. direction +1 up, -1 down, 0 either."""
    want = {int(p) % 12 for p in pcs}
    note = int(note)
    if note % 12 in want:
        return note
    for d in range(1, 13):
        if direction >= 0 and lo <= note + d <= hi and (note + d) % 12 in want:
            return note + d
        if direction <= 0 and lo <= note - d <= hi and (note - d) % 12 in want:
            return note - d
    return note


def rootless(sym, lo=55, hi=76, prev=None):
    """Drop the root (and often the 5th) -- the standard jazz keyboard voicing.
    The bass has the root; doubling it just makes mud."""
    r, pcs, b, ext = parse(sym)
    keep = [p for p in pcs if p != r]
    if len(keep) >= 4:
        fifth = (r + 7) % 12
        if fifth in keep and len(keep) > 3:
            keep = [p for p in keep if p != fifth]
    return voicelead(keep or pcs, prev, lo, hi)


def shell(sym, lo=48, hi=68, prev=None):
    """Root + 3rd + 7th. Enough to state the chord and nothing more."""
    r, pcs, b, ext = parse(sym)
    third = next((p for p in pcs if (p - r) % 12 in (3, 4, 2, 5)), pcs[1 % len(pcs)])
    sev = next((p for p in pcs if (p - r) % 12 in (10, 11, 9)), None)
    keep = [r, third] + ([sev] if sev is not None else [])
    return voicelead(keep, prev, lo, hi)


class Prog:
    """A chord progression with pre-computed voicings and bass notes."""

    def __init__(self, items, lo=55, hi=76, bass_oct=2, voicing='rootless'):
        self.items = items
        self._lo, self._hi, self._bo, self._voicing = lo, hi, bass_oct, voicing
        self.voicings = []
        self.basses = []
        self.syms = []
        self.spans = []
        self.pcs = []
        prev = None
        b = 0.0
        for sym, d in items:
            r, pcs, bs, ext = parse(sym)
            if voicing == 'rootless':
                v = rootless(sym, lo, hi, prev)
            elif voicing == 'shell':
                v = shell(sym, lo - 6, hi - 8, prev)
            else:
                v = voicelead(pcs, prev, lo, hi)
            prev = v
            self.voicings.append(v)
            self.basses.append(12 * (bass_oct + 1) + bs)
            self.syms.append(sym)
            self.pcs.append(pcs)
            self.spans.append((b, b + d))
            b += d
        self.length = b

    def idx_at(self, rel):
        rel = rel % self.length
        for i, (s, e) in enumerate(self.spans):
            if s <= rel < e:
                return i
        return len(self.spans) - 1

    def at(self, rel):
        i = self.idx_at(rel)
        return self.voicings[i], self.basses[i], self.syms[i]

    def events(self, start=0.0, reps=1):
        reps = max(int(round(reps)), 1)
        out = []
        for r in range(reps):
            for i, (s, e) in enumerate(self.spans):
                out.append((start + r * self.length + s, e - s,
                            self.voicings[i], self.basses[i], self.syms[i], self.pcs[i]))
        return out

    def transpose(self, semis):
        names = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

        def tr(sym):
            body, bs = split_sym(sym)
            r, i = _root(body)
            new = names[(r + semis) % 12] + body[i:]
            if bs is not None:
                new += '/' + names[(_root(bs)[0] + semis) % 12]
            return new
        return Prog([(tr(s), d) for s, d in self.items],
                    lo=self._lo, hi=self._hi, bass_oct=self._bo,
                    voicing=self._voicing)


# ============================================================== comp rhythms =
# Each returns [(offset_beats, dur_beats, velocity), ...] for ONE chord span.

def rhy_bossa(span):
    """Classic bossa comp: 1, 1a(&of2-ish), 3, 4& over two beats-per-half."""
    hits = [(0.0, 1.4, 1.00), (1.5, 0.9, 0.72), (2.5, 1.4, 0.85), (3.75, 0.6, 0.66)]
    return [(o, d, v) for o, d, v in hits if o < span]


def rhy_samba(span):
    hits = [(0.0, 0.45, 0.95), (0.75, 0.45, 0.70), (1.5, 0.45, 0.85),
            (2.25, 0.45, 0.68), (2.75, 0.6, 0.90), (3.5, 0.5, 0.72)]
    return [(o, d, v) for o, d, v in hits if o < span]


def rhy_charleston(span):
    hits = [(0.0, 1.4, 1.00), (1.5, 1.2, 0.80)]
    return [(o, d, v) for o, d, v in hits if o < span]


def rhy_cabaret(span):
    """Lounge/torch: a soft chord on 1 and a lift on 3."""
    hits = [(0.0, 2.6, 1.00), (2.0, 1.8, 0.62)]
    return [(o, d, v) for o, d, v in hits if o < span]


def rhy_waltz(span):
    hits = [(0.0, 0.9, 1.0), (1.0, 0.8, 0.62), (2.0, 0.8, 0.68)]
    return [(o, d, v) for o, d, v in hits if o < span]


def rhy_push(span):
    """Anticipated: everything arrives an eighth early."""
    hits = [(0.0, 1.4, 1.0), (1.5, 0.9, 0.75), (3.5, 1.2, 0.9)]
    return [(o, d, v) for o, d, v in hits if o < span]


def rhy_stab(span):
    hits = [(0.0, 0.28, 1.0), (1.0, 0.28, 0.7), (2.5, 0.28, 0.95), (3.0, 0.28, 0.7)]
    return [(o, d, v) for o, d, v in hits if o < span]


def rhy_hold(span):
    return [(0.0, span * 0.97, 1.0)]


RHY = {'bossa': rhy_bossa, 'samba': rhy_samba, 'charleston': rhy_charleston,
       'cabaret': rhy_cabaret, 'waltz': rhy_waltz, 'push': rhy_push,
       'stab': rhy_stab, 'hold': rhy_hold}


def comp(fn, b_, beat0, prog, reps=1, g=0.07, rhythm='bossa', spread=0.006,
         hum=None, bar_beats=4, chordwise=True, **kw):
    """Comp a progression with a rhythm pattern.

    `chordwise=True` means the instrument takes a list of notes (organ,
    accordion); False means one call per note (piano, guitar, Rhodes).
    """
    H = hum or HUM
    pat = RHY[rhythm] if isinstance(rhythm, str) else rhythm
    for bt, d, vo, bs, sym, pcs in prog.events(beat0, reps):
        for off, hd, hv in pat(d):
            b2 = bt + off
            t0 = H.t(b2, bar_beats)
            dd = max(T(b2 + min(hd, d - off)) - T(b2), 0.06)
            gg = H.g(g, b2, bar_beats=bar_beats) * hv
            if chordwise:
                fn(b_, t0, vo, dd, g=gg, **kw)
            else:
                for j, m in enumerate(vo):
                    fn(b_, t0 + j * spread, m, dd, g=gg * (1 - 0.05 * j), **kw)


def bassline(fn, b_, beat0, prog, reps=1, g=0.28, style='root', hum=None,
             bar_beats=4, octave=0, **kw):
    """style: root / two_feel / walk / bossa / samba / tumbao / pedal"""
    H = hum or HUM
    ev = prog.events(beat0, reps)
    for i, (bt, d, vo, bs, sym, pcs) in enumerate(ev):
        r = bs + 12 * octave
        nxt = ev[(i + 1) % len(ev)][3] + 12 * octave
        fifth = r + 7
        if style == 'root':
            hits = [(0.0, d * 0.9, r, 1.0)]
        elif style == 'two_feel':
            hits = [(0.0, 1.7, r, 1.0)] + ([(2.0, 1.7, fifth, 0.78)] if d > 2 else [])
        elif style == 'bossa':
            hits = [(0.0, 1.4, r, 1.0), (1.5, 0.9, fifth, 0.72)]
            if d > 2:
                hits += [(2.0, 1.4, r, 0.92), (3.5, 0.6, fifth, 0.68)]
        elif style == 'samba':
            hits = [(0.0, 0.45, r, 1.0), (1.5, 0.45, r, 0.75), (2.0, 0.45, fifth, 0.9),
                    (3.5, 0.45, r, 0.8)]
            hits = [h for h in hits if h[0] < d]
        elif style == 'tumbao':
            # the Cuban bass figure: nothing on 1, the 'and of 2', then 4
            hits = [(1.5, 0.9, r, 0.95), (3.0, 1.2, fifth, 0.85)]
            if d > 3.5:
                hits += [(3.5, 0.5, nxt, 0.7)]
            hits = [h for h in hits if h[0] < d]
        elif style == 'walk':
            steps = [r, r + 4 if 4 in [(p - bs % 12) % 12 for p in pcs] else r + 3,
                     fifth, nxt - 1 if nxt > r else nxt + 1]
            hits = [(k * 1.0, 0.95, steps[k % 4], 1.0 if k == 0 else 0.8)
                    for k in range(int(d))]
        elif style == 'pedal':
            hits = [(k * 0.5, 0.45, r, 1.0 if k % 2 == 0 else 0.7)
                    for k in range(int(d * 2))]
        else:
            hits = [(0.0, d * 0.9, r, 1.0)]
        for off, hd, m, hv in hits:
            b2 = bt + off
            t0 = H.t(b2, bar_beats)
            dd = max(T(b2 + min(hd, d - off)) - T(b2), 0.07)
            fn(b_, t0, int(m), dd, g=H.g(g, b2, bar_beats=bar_beats) * hv, **kw)


def montuno(fn, b_, beat0, prog, reps=1, g=0.07, hum=None, octave=0, **kw):
    """Cuban piano montuno: a fixed rhythmic cell, guide tones only, the
    right hand playing the same shape while the harmony moves underneath."""
    H = hum or HUM
    cell = [(0.0, 0.9), (0.75, 0.8), (1.5, 0.9), (2.5, 0.85), (3.0, 0.8), (3.5, 0.7)]
    for bt, d, vo, bs, sym, pcs in prog.events(beat0, reps):
        v = sorted(vo)[:3] + [sorted(vo)[0] + 12]
        for k, (off, hv) in enumerate(cell):
            if off >= d:
                continue
            b2 = bt + off
            t0 = H.t(b2)
            dd = max(T(b2 + 0.45) - T(b2), 0.06)
            m = v[[0, 2, 1, 3, 2, 1][k % 6] % len(v)] + 12 * octave
            fn(b_, t0, m, dd, g=H.g(g, b2) * hv, **kw)


def arp(fn, b_, beat0, prog, reps=1, g=0.08, sub=0.25, shape=(0, 1, 2, 1),
        hum=None, octave=0, **kw):
    H = hum or HUM
    for bt, d, vo, bs, sym, pcs in prog.events(beat0, reps):
        n = int(round(d / sub))
        for k in range(n):
            b2 = bt + k * sub
            t0 = H.t(b2)
            dd = max(T(b2 + sub) - T(b2), 0.05) * 0.92
            m = vo[shape[k % len(shape)] % len(vo)] + 12 * octave
            fn(b_, t0, m, dd, g=H.g(g, b2), **kw)
