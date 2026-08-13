#!/usr/bin/env python3
"""Render Half-Dream Morning — bai 3 cua Revolver Sessions (I'm Only Sleeping DNA)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from songs.song03_half_dream_morning.song import HalfDreamMorning

if __name__ == '__main__':
    outdir = os.path.join('output', HalfDreamMorning.name)
    s = HalfDreamMorning()
    mp3 = s.render(outdir)
    zp = s.zip_sources(outdir)
    print('OK:', mp3)
    print('OK:', zp)
