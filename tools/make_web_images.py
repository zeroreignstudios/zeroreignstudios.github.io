#!/usr/bin/env python3
"""Rebuild the site's product shots from the Unity store renders.

WHY THIS EXISTS
---------------
On 2026-08-11 every product shot on the site turned almost pure white.
The renders were fine; the web conversion was not.

The Unity screenshots are captured with a TRANSPARENT background, so the
PNGs are RGBA. Whatever produced the web JPEGs composited them onto a
white canvas using that alpha as a mask. Alpha on the night shots averages
about 12/255, so ~95% of every pixel became white paper:

    02_lineup_night.png   composited over white -> mean 248.6, stdev 7.2
                          alpha simply dropped  -> mean  42.0, stdev 41.3

props_og and gear_sheet survived only because their alpha is fully opaque.

THE RULE
--------
JPEG has no alpha. Discard it with .convert("RGB") -- never composite the
render onto a background. The RGB channels already hold the finished image.

Run:  python3 tools/make_web_images.py [path/to/screenshots]
"""
import os, sys
from PIL import Image, ImageStat

DEFAULT_SRC = ("/Volumes/GABRIEL_VAULT/GVAULT/asset_creation/LanternTail"
               "/store_20260810/screenshots")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
W, H, QUALITY = 1600, 1066, 88

MAP = {
    "01_lineup_day.png":         "og2_lineup_day.jpg",
    "02_lineup_night.png":       "og2_lineup_night.jpg",
    "03_demo_day.png":           "og2_demo_day.jpg",
    "04_demo_night.png":         "og2_demo_night.jpg",
    "05_zombie_lineup_day.png":  "zombie_lineup_day.jpg",
    "06_zombie_lineup_night.png":"zombie_lineup_night.jpg",
    "07_zombie_demo.png":        "zombie_demo.jpg",
    "08_props_og.png":           "props_og.jpg",
    "09_props_zombie.png":       "props_zombie.jpg",
    "10_gear_sheet.png":         "gear_sheet.jpg",
}

def main(src=DEFAULT_SRC):
    if not os.path.isdir(src):
        sys.exit(f"Source folder not found: {src}\n"
                 "Mount GABRIEL_VAULT, or pass the screenshots folder as an argument.")
    print(f"{'output':26} {'mean':>7} {'min':>5} {'sd':>6}  check")
    for s, d in MAP.items():
        p = os.path.join(src, s)
        if not os.path.exists(p):
            print(f"{d:26}  MISSING SOURCE {s}"); continue
        rgb = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
        rgb.save(os.path.join(OUT, d), "JPEG",
                 quality=QUALITY, optimize=True, progressive=True)
        g = rgb.convert("L"); st = ImageStat.Stat(g); lo = g.getextrema()[0]
        # A correctly converted shot keeps real shadows and real spread.
        bad = lo > 150 and st.stddev[0] < 20
        print(f"{d:26} {st.mean[0]:7.1f} {lo:5} {st.stddev[0]:6.1f}  "
              f"{'*** WASHED OUT — alpha was composited ***' if bad else 'ok'}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC)
