#!/usr/bin/env python3
"""news-image-20261124: draw the poster (NOT the entrypoint).

Draws a 1024x1024 newspaper-style poster with PIL only, from scratch:
no photos, no downloaded assets, no network. Every shape is drawn with
PIL primitives. The output is fully deterministic: same bytes every run.

This script produced the entry.png shipped in the repository. The graded
entrypoint is main.py, which only copies that pre-rendered image: the
grader runs standard library only, so no Pillow at run time.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 draw_poster.py
"""

# How the four stories are laid out (top to bottom, two rows of two):
#  - Row one, left: the chipmaker chief is restored after the White
#    House steps in, drawn as a gold chip with a rising arrow.
#  - Row one, right: the Singapore chip broker is blacklisted, drawn
#    as a chip under a red prohibition stamp.
#  - Row two, left: the Gulf standoff over a mined tanker, drawn with
#    a red banner carrying the damages figure.
#  - Row two, right: jets crossing an air-defence zone, drawn with a
#    radar sweep and a warning triangle.
# Headline text is wrapped to two lines and the standfirst to three,
# so no story overflows its card whatever the wording.

import math
import os

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024

# ---- palette -------------------------------------------------------------
PAPER = (250, 247, 238)   # warm newsprint
CARD = (255, 255, 255)
INK = (26, 35, 50)        # near-black navy
RED = (178, 39, 30)
TEAL = (13, 110, 102)
SEA = (23, 92, 140)
NAVY = (30, 58, 95)
GOLD = (184, 134, 11)
GREY = (96, 102, 112)
LIGHT = (214, 232, 240)   # pale sky
SAND = (232, 222, 200)
GREEN = (46, 125, 50)
ORANGE = (230, 126, 34)
YELLOW = (244, 196, 48)


def typeface(size):
    """Pillow's bundled scalable font: identical on any machine with Pillow."""
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow without the size parameter
        return ImageFont.load_default()


def measure(pen, text, fnt, stroke=0):
    bounds = pen.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    return bounds[2] - bounds[0]


def wrap_lines(pen, text, fnt, max_w, stroke=0):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    out, current = [], ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if measure(pen, trial, fnt, stroke) <= max_w or not current:
            current = trial
        else:
            out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def centred(pen, cx, y, text, fnt, fill, stroke=0):
    tw = measure(pen, text, fnt, stroke)
    pen.text((cx - tw / 2, y), text, font=fnt, fill=fill, stroke_width=stroke,
             stroke_fill=fill)


def burst(pen, cx, cy, r_out, r_in, points, fill):
    """A simple spiky burst polygon (explosion / sun)."""
    corners = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / points - math.pi / 2
        corners.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pen.polygon(corners, fill=fill)


# ---- illustrations (all original, drawn from zero) -----------------------

def paint_chip_return(pen, x0, y0, x1, y1):
    """Nvidia: a chip with a golden return arrow -- Huang is back as CEO."""
    pen.rectangle([x0, y0, x1, y1], fill=(238, 240, 242))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 8
    # chip body with pins
    pen.rectangle([cx - 52, cy - 36, cx + 52, cy + 36], fill=INK,
                  outline=GOLD, width=3)
    for i in range(4):
        px = cx - 36 + i * 24
        pen.rectangle([px, cy - 48, px + 10, cy - 36], fill=INK)
        pen.rectangle([px, cy + 36, px + 10, cy + 48], fill=INK)
    for i in range(3):
        py = cy - 24 + i * 24
        pen.rectangle([cx - 64, py, cx - 52, py + 10], fill=INK)
        pen.rectangle([cx + 52, py, cx + 64, py + 10], fill=INK)
    # CEO plate on the chip
    centred(pen, cx, cy - 13, "CEO", typeface(26), GOLD, stroke=1)
    # golden circular return arrow around the chip
    pen.arc([cx - 84, cy - 84, cx + 84, cy + 84], 250, 335, fill=GOLD, width=6)
    end_a = math.radians(335)
    tip = (cx + 84 * math.cos(end_a), cy + 84 * math.sin(end_a))
    tx, ty = -math.sin(end_a), math.cos(end_a)  # tangent, clockwise
    nx, ny = math.cos(end_a), math.sin(end_a)   # outward normal
    pen.polygon([(tip[0] + 16 * tx, tip[1] + 16 * ty),
                 (tip[0] - 8 * tx + 9 * nx, tip[1] - 8 * ty + 9 * ny),
                 (tip[0] - 8 * tx - 9 * nx, tip[1] - 8 * ty - 9 * ny)],
                fill=GOLD)
    # small "back" label under the arrow
    centred(pen, cx, y1 - 26, "HUANG RETURNS", typeface(17), GOLD, stroke=1)


def paint_blacklist(pen, x0, y0, x1, y1):
    """Megaspeed: a chip under a red prohibition stamp -- blacklisted."""
    pen.rectangle([x0, y0, x1, y1], fill=CARD)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 6
    # small chip
    pen.rectangle([cx - 46, cy - 30, cx + 46, cy + 30], fill=NAVY,
                  outline=INK, width=2)
    for i in range(3):
        px = cx - 30 + i * 24
        pen.rectangle([px, cy - 40, px + 10, cy - 30], fill=INK)
        pen.rectangle([px, cy + 30, px + 10, cy + 40], fill=INK)
    # (no label on the chip: the prohibition slash would strike through it)
    # red prohibition circle + slash over the chip
    pen.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], outline=RED, width=8)
    pen.line([(cx - 44, cy + 44), (cx + 44, cy - 44)], fill=RED, width=8)
    # BANNED stamp below
    sx0, sx1, sy = cx - 62, cx + 62, y1 - 40
    pen.rectangle([sx0, sy, sx1, sy + 26], outline=RED, width=3)
    centred(pen, cx, sy + 3, "BANNED", typeface(20), RED, stroke=1)


def paint_demand_tanker(pen, x0, y0, x1, y1):
    """Hormuz: Tehran's $290bn demand banner over a tanker and a mine."""
    # demand banner across the top
    pen.rectangle([x0, y0, x1, y0 + 40], fill=RED)
    centred(pen, (x0 + x1) // 2, y0 + 6, "$290 BILLION", typeface(26), CARD,
            stroke=1)
    # sea
    sea_y = y0 + 40
    pen.rectangle([x0, sea_y, x1, y1], fill=SEA)
    for wx in range(x0 + 6, x1 - 10, 34):
        pen.arc([wx, sea_y + 66, wx + 30, sea_y + 84], 200, 340, fill=CARD,
                width=3)
    # tanker hull
    hx0, hx1, hy = x0 + 52, x1 - 52, sea_y + 26
    pen.polygon([(hx0, hy), (hx1, hy), (hx1 - 12, hy + 32), (hx0 + 12, hy + 32)],
                fill=(52, 58, 68))
    pen.rectangle([hx0, hy - 20, hx0 + 140, hy], fill=RED)      # containers
    pen.rectangle([hx0 + 146, hy - 20, hx0 + 196, hy], fill=GOLD)
    pen.rectangle([hx0 + 202, hy - 20, hx1 - 36, hy], fill=TEAL)
    pen.rectangle([hx1 - 30, hy - 36, hx1 - 8, hy], fill=INK)   # funnel
    pen.rectangle([hx1 - 30, hy - 36, hx1 - 8, hy - 28], fill=YELLOW)
    # spiked mine in the water, right side
    mx, my = x1 - 34, sea_y + 92
    for dx, dy in [(0, -12), (0, 12), (-12, 0), (12, 0),
                   (-8, -8), (8, -8), (-8, 8), (8, 8)]:
        pen.line([mx, my, mx + dx, my + dy], fill=INK, width=3)
    pen.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=INK)
    # small explosion burst above the ship
    burst(pen, (x0 + x1) // 2, sea_y + 12, 16, 7, 8, ORANGE)


def paint_jets_radar(pen, x0, y0, x1, y1):
    """Korea ADIZ: fighter jets cross the sky, radar tracks them."""
    pen.rectangle([x0, y0, x1, y1], fill=LIGHT)
    # contrails
    pen.arc([x0 - 40, y0 + 6, x0 + 260, y0 + 90], 300, 30, fill=CARD, width=4)
    pen.arc([x0 - 20, y0 + 52, x0 + 300, y0 + 136], 300, 30, fill=CARD,
            width=4)

    def fighter(jx, jy, s):
        pts = [(jx + 36 * s, jy), (jx + 8 * s, jy - 8 * s),
               (jx - 28 * s, jy - 26 * s), (jx - 20 * s, jy - 6 * s),
               (jx - 30 * s, jy - 2 * s), (jx - 30 * s, jy + 2 * s),
               (jx - 20 * s, jy + 6 * s), (jx - 28 * s, jy + 26 * s),
               (jx + 8 * s, jy + 8 * s)]
        pen.polygon(pts, fill=INK)

    fighter(x0 + 210, y0 + 44, 1.0)
    fighter(x0 + 260, y0 + 92, 0.8)
    # radar screen, lower left
    rx, ry, rr = x0 + 52, y1 - 40, 34
    pen.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(16, 60, 30),
                outline=GREEN, width=2)
    pen.ellipse([rx - rr + 10, ry - rr + 10, rx + rr - 10, ry + rr - 10],
                outline=GREEN, width=1)
    pen.line([(rx, ry), (rx + 24, ry - 22)], fill=GREEN, width=2)
    for bx, by in [(rx + 12, ry - 8), (rx - 8, ry + 12)]:
        pen.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=YELLOW)
    # warning triangle, lower right
    wx, wy = x1 - 52, y1 - 44
    pen.polygon([(wx, wy - 26), (wx - 26, wy + 18), (wx + 26, wy + 18)],
                fill=YELLOW, outline=INK, width=2)
    centred(pen, wx, wy - 14, "!", typeface(24), INK, stroke=1)


ARTWORK = [paint_chip_return, paint_blacklist, paint_demand_tanker,
           paint_jets_radar]

ITEMS = [
    {
        "num": "1", "color": GOLD, "tag": "TECH  |  UNITED STATES",
        "headline": "NVIDIA BRINGS BACK HUANG AS CEO",
        "sub": "Jensen Huang returns as chief executive after President "
               "Trump intervenes in the chip giant's leadership.",
        "art": 0,
    },
    {
        "num": "2", "color": RED, "tag": "TECH  |  SINGAPORE",
        "headline": "US BLACKLISTS SINGAPORE CHIP FIRM",
        "sub": "Megaspeed joins the Entity List over its role in the "
               "Nvidia chip scandal; exports now need a licence.",
        "art": 1,
    },
    {
        "num": "3", "color": SEA, "tag": "ENERGY  |  MIDDLE EAST",
        "headline": "IRAN DEMANDS $290 BILLION",
        "sub": "Tehran demands $290bn as a tanker hits a mine in the "
               "Strait of Hormuz; Washington tightens sanctions.",
        "art": 2,
    },
    {
        "num": "4", "color": NAVY, "tag": "ASIA  |  SECURITY",
        "headline": "RUSSIAN JETS ENTER KOREA'S AIR ZONE",
        "sub": "Seoul scrambles fighters as Russian warplanes enter its "
               "air defence zone; Ulleung Island warned to evacuate.",
        "art": 3,
    },
]


def paint_story(pen, story, x0, y0, w, h):
    color = story["color"]
    pen.rectangle([x0, y0, x0 + w, y0 + h], fill=CARD, outline=INK, width=2)
    pen.rectangle([x0, y0, x0 + w, y0 + 8], fill=color)
    # illustration panel
    px0, py0, px1, py1 = x0 + 12, y0 + 20, x0 + w - 12, y0 + 188
    pen.rectangle([px0, py0, px1, py1], outline=(190, 192, 196), width=1)
    ARTWORK[story["art"]](pen, px0, py0, px1, py1)
    # story number badge
    bx, by = px0 + 16, py0 + 16
    pen.ellipse([bx, by, bx + 30, by + 30], fill=color, outline=CARD, width=2)
    centred(pen, bx + 15, by + 4, story["num"], typeface(18), CARD, stroke=1)
    # tag
    pen.text((x0 + 16, y0 + 200), story["tag"], font=typeface(17), fill=color,
             stroke_width=1, stroke_fill=color)
    # headline (up to 2 lines)
    hl = wrap_lines(pen, story["headline"], typeface(29), w - 32, stroke=1)
    y = y0 + 226
    for line in hl[:2]:
        pen.text((x0 + 16, y), line, font=typeface(29), fill=INK,
                 stroke_width=1, stroke_fill=INK)
        y += 36
    # subtext (up to 3 lines)
    sub = wrap_lines(pen, story["sub"], typeface(19), w - 32)
    y = y0 + 226 + 36 * len(hl[:2]) + 6
    for line in sub[:3]:
        pen.text((x0 + 16, y), line, font=typeface(19), fill=GREY)
        y += 25


def main():
    sheet = Image.new("RGB", (SIZE, SIZE), PAPER)
    pen = ImageDraw.Draw(sheet)

    # outer double border
    pen.rectangle([10, 10, SIZE - 11, SIZE - 11], outline=INK, width=3)
    pen.rectangle([18, 18, SIZE - 19, SIZE - 19], outline=INK, width=1)

    # masthead: the day, named loud and clear
    centred(pen, SIZE // 2, 34, "THE WORLD IN ONE DAY", typeface(26), INK, stroke=1)
    centred(pen, SIZE // 2, 68, "TUESDAY, 24 NOVEMBER 2026", typeface(46), RED, stroke=2)
    pen.line([(60, 128), (SIZE - 60, 128)], fill=INK, width=2)
    pen.line([(60, 134), (SIZE - 60, 134)], fill=INK, width=1)
    centred(pen, SIZE // 2, 142, "Four stories that defined the day",
            typeface(20), GREY)

    # 2 x 2 grid of stories
    cw, ch, gap = 476, 384, 16
    x0, y0 = 28, 172
    for i, story in enumerate(ITEMS):
        cx = x0 + (i % 2) * (cw + gap)
        cy = y0 + (i // 2) * (ch + gap)
        paint_story(pen, story, cx, cy, cw, ch)

    # footer repeats the date so the day is unmistakable
    centred(pen, SIZE // 2, 968, "News of Tuesday, 24 November 2026",
            typeface(18), GREY, stroke=1)

    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(target_dir, exist_ok=True)
    sheet.save(os.path.join(target_dir, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
