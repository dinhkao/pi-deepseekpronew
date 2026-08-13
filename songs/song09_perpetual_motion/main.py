#!/usr/bin/env python3
"""Render Perpetual Motion — bai 9 cua Revolver Sessions (AYBCS + FNO DNA)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from songs.song09_perpetual_motion.song import PerpetualMotion

if __name__ == '__main__':
    outdir = os.path.join('output', PerpetualMotion.name)
    s = PerpetualMotion()
    mp3 = s.render(outdir)
    zp = s.zip_sources(outdir)
    print('OK:', mp3)
    print('OK:', zp)
