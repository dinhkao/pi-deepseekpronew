#!/usr/bin/env python3
"""Render Sunshower Sunday — bai 8 cua Revolver Sessions (GDS DNA)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from songs.song08_sunshower_sunday.song import SunshowerSunday

if __name__ == '__main__':
    outdir = os.path.join('output', SunshowerSunday.name)
    s = SunshowerSunday()
    mp3 = s.render(outdir)
    zp = s.zip_sources(outdir)
    print('OK:', mp3)
    print('OK:', zp)
