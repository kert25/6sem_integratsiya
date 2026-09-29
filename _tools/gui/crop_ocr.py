# -*- coding: utf-8 -*-
"""crop_ocr.py - crop screenshot region, upscale, save for OCR.
usage: py crop_ocr.py <in.png> <out.png> L T R B [scale]"""
import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
l, t, r, b = map(int, sys.argv[3:7])
scale = int(sys.argv[7]) if len(sys.argv) > 7 else 2
img = Image.open(src)
crop = img.crop((l, t, r, b))
crop = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
crop.save(dst)
print("saved %s (%dx%d)" % (dst, crop.width, crop.height))
