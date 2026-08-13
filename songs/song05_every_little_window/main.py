#!/usr/bin/env python3
"""Render Every Little Window — bai 5 cua Revolver Sessions (HTAE DNA)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from songs.song05_every_little_window.song import EveryLittleWindow

if __name__ == '__main__':
    outdir = os.path.join('output', EveryLittleWindow.name)
    s = EveryLittleWindow()
    mp3 = s.render(outdir)
    zp = s.zip_sources(outdir)
    print('OK:', mp3)
    print('OK:', zp)
