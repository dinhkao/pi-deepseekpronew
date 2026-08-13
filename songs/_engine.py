"""Bo khung render chung cho 10 bai "Revolver Sessions".

Moi bai hat la mot lop con cua Song. Engine lo:
- tao tempo map + humanize
- mix stereo kieu 1966 (hard pan, vocal/drums giua, reverb aux)
- kiem tra khong lech tone TRUOC khi encode (scale/chord/bass/f0 audit)
- render 2 ban: vocal + instrumental
- encode mp3 (ffmpeg loudnorm) + zip source
"""
from __future__ import annotations

import os
import subprocess
import sys
import zipfile

import numpy as np

from nhaccu._core import configure_map, T, buf, set_hum, Hum, nn, hz
from nhaccu._dsp import SR, reverb, comp, _fadeout, _ramp

HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------- track bus --

class Track:
    """Mot stem mono + thong tin pan/gain/reverb."""

    def __init__(self, name, pan=0.0, gain=1.0, verb=0.0, vocal=False,
                 squash=False):
        self.name = name
        self.pan = float(pan)          # -1 (trai) .. +1 (phai)
        self.gain = float(gain)
        self.verb = float(verb)        # reverb send 0..1
        self.vocal = vocal             # True -> bi loai o ban instrumental
        self.squash = squash           # True -> nen nhe track (giong hat)
        self.b = buf()


def mix_tracks(tracks, out_wav, total_s, peak=0.93, verb_decay=1.5,
               verb_wet=0.30, master_drive=1.4, tail=1.5):
    """Trong tat ca track thanh stereo, master, ghi wav."""
    n = int(total_s * SR)
    L = np.zeros(n)
    R = np.zeros(n)
    A = np.zeros(n)   # reverb aux

    for t in tracks:
        x = t.b[:n] * t.gain
        if t.squash:
            x = comp(x, thr=0.09, ratio=3.0, atk=0.004, rel=0.08, mu=1.0)
        th = (t.pan + 1.0) * np.pi / 4.0
        gl = np.cos(th)
        gr = np.sin(th)
        L += x * gl
        R += x * gr
        if t.verb > 0:
            A += x * t.verb

    # reverb aux -> stereo
    wl, wr = reverb(A, A, decay=verb_decay, wet=1.0)
    L = L + wl * verb_wet
    R = R + wr * verb_wet

    # EQ master: them sub (duoi 120 Hz), giam dai choi 2.5-5k
    from nhaccu._dsp import _lp, _bp
    L = L + _lp(L, 120, 2) * 0.38
    R = R + _lp(R, 120, 2) * 0.38
    L = L - _bp(L, 2600, 5400, 2) * 0.26
    R = R - _bp(R, 2600, 5400, 2) * 0.26

    # master: nen nhe + sat + clip mem
    L = comp(L, thr=0.14, ratio=2.2, atk=0.006, rel=0.12, mu=1.0)
    R = comp(R, thr=0.14, ratio=2.2, atk=0.006, rel=0.12, mu=1.0)
    L = np.tanh(L * master_drive) / np.tanh(master_drive)
    R = np.tanh(R * master_drive) / np.tanh(master_drive)

    # fade out duoi
    fo = int(0.05 * SR)
    L[-fo:] *= np.linspace(1, 0, fo)
    R[-fo:] *= np.linspace(1, 0, fo)

    m = max(float(np.abs(L).max()), float(np.abs(R).max()), 1e-9)
    L *= peak / m
    R *= peak / m

    st = np.empty(n * 2, dtype='<i2')
    st[0::2] = (np.clip(L, -1, 1) * 32767).astype('<i2')
    st[1::2] = (np.clip(R, -1, 1) * 32767).astype('<i2')
    import wave
    with wave.open(out_wav, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())
    return out_wav


def encode_mp3(wav, mp3, lufs=-14.0):
    """ffmpeg loudnorm + mp3 192k."""
    if os.path.exists(mp3):
        os.remove(mp3)
    subprocess.run([
        'ffmpeg', '-y', '-i', wav,
        '-af', 'loudnorm=I=%.1f:TP=-1.0:LRA=11' % lufs,
        '-codec:a', 'libmp3lame', '-b:a', '192k', mp3
    ], check=True, capture_output=True)
    return mp3


# ------------------------------------------------------------ tone audit ----

_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def _parse_note(s):
    if isinstance(s, (int, np.integer)):
        return int(s)
    n = _PC[s[0].upper()]
    i = 1
    while i < len(s) and s[i] in '#b':
        n += 1 if s[i] == '#' else -1
        i += 1
    return 12 * (int(s[i:]) + 1) + n


def audit(cells, chord_events, scale_pcs, label, allow=(), bass=False,
          tensions=None):
    """Kiem tra moi note khong lech khoi hoa am.

    cells: [(off_beats, dur_beats, note, ...), ...]
    chord_events: [(start, end, [pcs], sym), ...] phu het doan cells
    scale_pcs: set cac pitch class duoc phep (cho passing tones)
    allow: set note-name duoc phep nam ngoai scale (chuyen nua cung co chu y)
    tensions: {root_pc: set(pcs)} — not mau cho phep tren downbeat
        (vd {2: {0, 4, 9}} = b7/sus4/6 tren D)
    bass=True: downbeat bat buoc phai la root cua chord (hoac trong allow)
    Tra ve list chuoi van de. Rong = sach.
    """
    probs = []
    sc = {int(p) % 12 for p in scale_pcs}
    al = {_parse_note(x) % 12 for x in allow}
    tn = tensions or {}
    for i, c in enumerate(cells):
        off, d, note = c[0], c[1], c[2]
        if note is None:
            continue
        m = _parse_note(note)
        pc = m % 12
        pcs = sc | al
        sym = '?'
        root = None
        for s, e, p, sy in chord_events:
            if s <= off < e:
                pcs = set(p) | al
                sym = sy
                root = p[0]
                break
        downbeat = abs(off - round(off)) < 1e-6
        if pc not in sc and pc not in al:
            probs.append('%s: note %s (beat %.2f) NGOAI scale' % (label, note, off))
        if downbeat and d >= 0.8 and root is not None:
            chord_only = {q % 12 for q in pcs}
            tens = tn.get(root % 12, set())
            if pc not in chord_only and pc not in tens:
                probs.append('%s: note %s tren downbeat beat %.0f khong thuoc %s'
                             % (label, note, off, sym))
        if bass and downbeat and root is not None \
                and pc != root % 12 and pc not in al:
            probs.append('%s: BASS %s o beat %.0f khong phai root cua %s'
                         % (label, note, off, sym))
    return probs


def audit_vocal_f0(cells, b, label, hum, tol=0.045):
    """Kiem tra khong lech tone: nang luong cua tung note da render phai
    tap trung tai DUNG tan so du kien (dung sai +-tol). Neu do duoc tan so
    cua NOT KE BEN (glide chong lan) thi coi nhu binh thuong."""
    probs = []
    n_ok = 0
    notes = [c[2] for c in cells]
    for i, c in enumerate(cells):
        off, d, note = c[0], c[1], c[2]
        if note is None:
            continue
        if d < 0.6:
            # not luot qua nhanh (passing 8th) — khong do duoc tin cay
            continue
        m = _parse_note(note)
        t0 = T(off)
        # do som hon giau note (tranh glide chong lan cua not ke tiep)
        a = int((t0 + min(0.38 * d, 0.16)) * SR)
        bb = int(min(a + 0.075 * SR, (t0 + d - 0.02) * SR))
        if bb - a < 3000 or bb >= len(b):
            continue
        seg = np.asarray(b[a:bb], dtype=np.float64)
        want = hz(m)
        ok, f0 = _f0_check(seg, want, tol)
        if not ok and f0 is not None:
            # glide (legato) giua 2 not la binh thuong: f0 nam giua
            # not hien tai va not ke ben (+-8%)
            lo_b, hi_b = want, want
            for j in (i - 1, i + 1):
                if 0 <= j < len(notes) and notes[j] is not None:
                    nw = hz(_parse_note(notes[j]))
                    lo_b = min(lo_b, nw)
                    hi_b = max(hi_b, nw)
            if lo_b * (1 - 0.08) <= f0 <= hi_b * (1 + 0.08):
                ok = True
        if ok:
            n_ok += 1
        else:
            probs.append('%s: hat note %s (beat %.2f) (%.1f Hz) nhung nang luong lech%s'
                         % (label, note, off, want,
                            (' (do duoc %.1f Hz)' % f0) if f0 else ''))
    return probs, n_ok


def _f0_check(seg, want, tol=0.045):
    """FFT check (zero-padded cho do phan giai cao): co peak trong dai
    [want*(1-tol), want*(1+tol)] khong. Tra ve (ok, f0_do_duoc)."""
    n = len(seg)
    if n < 2048:
        return False, None
    seg = seg - seg.mean()
    w = np.hanning(n)
    NFFT = 16384
    X = np.abs(np.fft.rfft(seg * w, NFFT))
    freqs = np.fft.rfftfreq(NFFT, 1.0 / SR)
    lo = want * (1 - tol)
    hi = want * (1 + tol)
    m = (freqs >= lo) & (freqs <= hi)
    if not m.any():
        return False, None
    k = int(np.argmax(X[m]))
    idx = int(np.where(m)[0][k])
    f0 = float(freqs[idx])
    if 0 < idx < len(X) - 1:
        a, b2, c = X[idx - 1], X[idx], X[idx + 1]
        den = a - 2 * b2 + c
        if abs(den) > 1e-12:
            f0 = (idx + 0.5 * (a - c) / den) * SR / NFFT
    ok = abs(f0 - want) <= tol * want
    return ok, f0 if not ok else None


# ---------------------------------------------------------------- song ------

class Song:
    """Lop co so cho mot bai. Lop con cai dat: meta + build()."""

    name = 'song'
    bpm = 120
    beats = 400          # tong so phach
    human = 1            # seed humanizer
    laid = 0.0           # + = sau beat (luoi)

    def setup(self):
        configure_map([(0, self.beats, self.bpm, self.bpm)], self.beats)
        h = Hum(seed=self.human, laid=self.laid)
        set_hum(h)

    def build(self, tracks, vocal=True):
        """Lop con dien tracks vao danh sach. Raise NotImplementedError."""
        raise NotImplementedError

    # ------------------------------------------------------------- render --
    def render(self, outdir):
        self.setup()
        tracks = []
        self.build(tracks, vocal=True)
        from nhaccu._core import TOTAL
        total = T(self.beats) + 0.5
        name = self.name
        os.makedirs(outdir, exist_ok=True)
        wav_v = os.path.join(outdir, name + '.wav')
        mix_tracks(tracks, wav_v, total)
        encode_mp3(wav_v, os.path.join(outdir, name + '.mp3'))

        # ban instrumental: bo track vocal
        inst = [t for t in tracks if not t.vocal]
        wav_i = os.path.join(outdir, name + '_instr.wav')
        mix_tracks(inst, wav_i, total)
        encode_mp3(wav_i, os.path.join(outdir, name + '_instr.mp3'))
        for w in (wav_v, wav_i):
            if os.path.exists(w):
                os.remove(w)
        return os.path.join(outdir, name + '.mp3')

    def zip_sources(self, outdir):
        """Zip cac file python cua bai nay + engine de chay doc lap."""
        import inspect
        song_file = inspect.getfile(self.__class__)
        song_dir = os.path.dirname(song_file)
        zp = os.path.join(outdir, self.name + '.zip')
        if os.path.exists(zp):
            os.remove(zp)
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
            for fn in sorted(os.listdir(song_dir)):
                if fn.endswith('.py'):
                    z.write(os.path.join(song_dir, fn), '%s/%s' % (self.name, fn))
            z.write(os.path.join(HERE, '_engine.py'), '%s/_engine.py' % self.name)
            z.write(os.path.join(HERE, '_sitar.py'), '%s/_sitar.py' % self.name)
            z.writestr('%s/README.txt' % self.name,
                       'Chay: PYTHONPATH=<repo> python3 %s/main.py\n'
                       'Can: numpy, scipy, ffmpeg va thu vien nhaccu/.\n'
                       'Ra file mp3 + mp3 instrumental vao output/%s/.\n'
                       % (self.name, self.name))
        return zp
