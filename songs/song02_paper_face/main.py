#!/usr/bin/env python3
"""Render Paper Face — bai 2 cua Revolver Sessions (Eleanor Rigby DNA)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from songs.song02_paper_face.song import PaperFace

if __name__ == '__main__':
    outdir = os.path.join('output', PaperFace.name)
    s = PaperFace()
    mp3 = s.render(outdir)
    zp = s.zip_sources(outdir)
    print('OK:', mp3)
    print('OK:', zp)
