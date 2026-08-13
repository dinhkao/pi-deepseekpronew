#!/usr/bin/env python3
"""Render mot doan demo cho tung nhac cu ra file .wav.

    python3 -m nhaccu.demo                # tat ca, ra demo_out/
    python3 -m nhaccu.demo fuzz mellotron # chi vai cai
    python3 -m nhaccu.demo --list         # liet ke ten

Moi file la mot cau ngan (mono, 44.1 kHz) o 120 BPM.
Nhac cu nao khong hop chu ky mac dinh se bi bo qua va bao ro.
"""
from __future__ import annotations

import inspect
import os
import sys
import wave

import numpy as np

from ._core import configure, buf, set_hum, Hum
from ._dsp import SR

FAMILIES = ['bass', 'guitar', 'keys', 'mallet', 'string_section', 'folk',
            'horns', 'voice', 'drums', 'percussion', 'fx']

PHRASE = [(0.0, 0.9, 'E3'), (1.0, 0.9, 'G3'), (2.0, 0.9, 'B3'), (3.0, 1.4, 'E4')]
CHORD = ['E3', 'G3', 'B3']
CELLS = [(0.0, 1.0, 'E3', 'oh', 1.0), (1.0, 1.0, 'G3', 'oh', 1.0),
         (2.0, 1.0, 'B3', 'oh', 1.0), (3.0, 1.0, 'E4', 'oh', 1.0)]
# cells cua ken: (offset, dur, [notes], vel)
HORN_CELLS = [(0.0, 0.5, ['E3', 'G3', 'B3'], 1.0),
              (1.5, 0.5, ['E3', 'A3', 'C4'], 0.9),
              (2.5, 1.0, ['E3', 'G3', 'B3'], 1.0)]
HORN_UNI = [(0.0, 0.5, 'E3', 1.0), (1.0, 0.5, 'G3', 0.9),
            (2.0, 1.5, 'B3', 1.0)]


def _catalogue():
    """[(family, name, callable)] — doc thang tu cac package con."""
    import importlib
    out = []
    for fam in FAMILIES:
        mod = importlib.import_module('%s.%s' % (__package__, fam))
        for name in mod.__all__:
            out.append((fam, name, getattr(mod, name)))
    return out


def _render(fn, name):
    """Goi `fn` theo dung chu ky cua no. Tra ve buffer stereo hoac None."""
    b = buf()
    p = list(inspect.signature(fn).parameters)
    if p[:4] == ['b_', 't0', 'm', 'dur']:
        for t, d, m in PHRASE:
            fn(b, 1.0 + t, m, d)
    elif p[:4] == ['b_', 't0', 'notes', 'dur']:
        for t, d, _ in PHRASE:
            fn(b, 1.0 + t, CHORD, d)
    elif p[:3] == ['b_', 't0', 'm']:
        for t, _, m in PHRASE:
            fn(b, 1.0 + t, m)
    elif p[:4] == ['b_', 't0', 'm_from', 'm_to']:
        fn(b, 1.0, 'E3', 'B3', 2.0)
    elif p[:2] == ['b_', 't0']:
        for t, _, _m in PHRASE:
            fn(b, 1.0 + t)
    elif p[:4] == ['b_', 'bar0', 'cells', 'chords']:
        fn(b, 1.0, CELLS, ['E', 'E', 'E', 'E'])
    elif p[:3] == ['b_', 'bar0', 'cells'] and name == 'stabs':
        fn(b, 1.0, HORN_CELLS)
    elif p[:3] == ['b_', 'bar0', 'cells'] and name == 'unison':
        fn(b, 1.0, HORN_UNI)
    elif p[:3] == ['b_', 'bar0', 'cells']:
        fn(b, 1.0, CELLS)
    elif p[:3] == ['b_', 'bar0', 'notes']:
        fn(b, 1.0, CHORD, 2.0)
    elif p[:3] == ['b_', 'beat0', 'beats']:
        fn(b, 1.0, 4.0)
    elif p[:2] == ['b_', 'beats']:
        fn(b, [1.0, 2.0, 3.0, 4.0])
    elif p[:3] == ['P', 'bar_beat', 'pat']:
        from .drums import Kit, Performer
        P = Performer(Kit(seed=7), 12.0, seed=11)
        fn(P, 1.0, {'K': 'K..K..K...K.K...', 'S': '....S..g....S.g.',
                    'H': 'H.hHh.hHh.hHh.hH'})
        fn(P, 5.0, {'K': 'K..K..K...K.K...', 'S': '....S..g....S.g.',
                    'H': 'H.hHh.hHh.hHh.hH'})
        return _from_bus(P)
    elif p[:2] == ['P', 'kit']:
        from .drums import Kit, Performer
        from .percussion import LatinKit
        P = Performer(Kit(seed=7), 12.0, seed=11)
        for bar in (1.0, 5.0):
            fn(P, LatinKit(seed=23), bar)
        return _from_bus(P)
    elif name in ('Kit', 'LatinKit'):
        return _kit_sampler(fn)
    else:
        return None
    return b


def _from_bus(P):
    b = buf()
    for v in P.bus.values():
        v = np.asarray(v).ravel()
        n = min(len(b), len(v))
        b[:n] += v[:n]
    return b


def _kit_sampler(cls):
    """Danh lan luot moi mon cua bo trong, cach nhau 0.4 s."""
    obj = cls(seed=7)
    b = buf()
    t = int(0.3 * SR)
    for meth in sorted(m for m in dir(obj) if not m.startswith('_')):
        f = getattr(obj, meth)
        if not callable(f):
            continue
        try:
            x = np.asarray(f()).ravel()
        except Exception:
            continue
        n = min(len(x), len(b) - t)
        if n <= 0:
            break
        b[t:t + n] += x[:n]
        t += int(0.4 * SR)
    return b


def write_wav(path, b, peak=0.89):
    x = np.asarray(b).ravel()
    m = float(np.max(np.abs(x)))
    if m > 1e-9:
        x = x * (peak / m)
    d = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(d.tobytes())


def main(argv):
    if '--list' in argv:
        for fam, name, _ in _catalogue():
            print('%-15s %s' % (fam, name))
        return 0
    want = set(a for a in argv if not a.startswith('-'))
    outdir = os.path.join(os.getcwd(), 'demo_out')
    os.makedirs(outdir, exist_ok=True)
    ok, skipped, failed = 0, [], []
    for fam, name, fn in _catalogue():
        if want and name not in want:
            continue
        configure(120, 120, end=24)
        set_hum(Hum(seed=1))
        try:
            b = _render(fn, name)
        except Exception as e:
            failed.append('%s (%s: %s)' % (name, type(e).__name__, e))
            continue
        if b is None:
            skipped.append(name)
            continue
        if float(np.max(np.abs(np.asarray(b)))) < 1e-9:
            skipped.append(name + ' (im lang)')
            continue
        write_wav(os.path.join(outdir, '%s-%s.wav' % (fam, name)), b)
        ok += 1
    print('viet %d file vao %s' % (ok, outdir))
    if skipped:
        print('bo qua %d: %s' % (len(skipped), ', '.join(skipped)))
    if failed:
        print('loi %d:' % len(failed))
        for f in failed:
            print('   ', f)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
