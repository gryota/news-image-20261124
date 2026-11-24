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

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

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


def font(size):
    """Pillow's bundled scalable font: identical on any machine with Pillow."""
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow without the size parameter
        return ImageFont.load_default()


def text_w(draw, text, fnt, stroke=0):
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    return box[2] - box[0]


def wrap(draw, text, fnt, max_w, stroke=0):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt, stroke) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def center(draw, cx, y, text, fnt, fill, stroke=0):
    w = text_w(draw, text, fnt, stroke)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill, stroke_width=stroke,
              stroke_fill=fill)


def starburst(draw, cx, cy, r_out, r_in, points, fill):
    """A simple spiky burst polygon (explosion / sun)."""
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


# ---- illustrations (all original, drawn from zero) -----------------------

def draw_chip_return(draw, x0, y0, x1, y1):
    """Nvidia: a chip with a golden return arrow -- Huang is back as CEO."""
    draw.rectangle([x0, y0, x1, y1], fill=(238, 240, 242))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 8
    # chip body with pins
    draw.rectangle([cx - 52, cy - 36, cx + 52, cy + 36], fill=INK,
                   outline=GOLD, width=3)
    for i in range(4):
        px = cx - 36 + i * 24
        draw.rectangle([px, cy - 48, px + 10, cy - 36], fill=INK)
        draw.rectangle([px, cy + 36, px + 10, cy + 48], fill=INK)
    for i in range(3):
        py = cy - 24 + i * 24
        draw.rectangle([cx - 64, py, cx - 52, py + 10], fill=INK)
        draw.rectangle([cx + 52, py, cx + 64, py + 10], fill=INK)
    # CEO plate on the chip
    center(draw, cx, cy - 13, "CEO", font(26), GOLD, stroke=1)
    # golden circular return arrow around the chip
    draw.arc([cx - 84, cy - 84, cx + 84, cy + 84], 250, 335, fill=GOLD, width=6)
    end_a = math.radians(335)
    tip = (cx + 84 * math.cos(end_a), cy + 84 * math.sin(end_a))
    tx, ty = -math.sin(end_a), math.cos(end_a)  # tangent, clockwise
    nx, ny = math.cos(end_a), math.sin(end_a)   # outward normal
    draw.polygon([(tip[0] + 16 * tx, tip[1] + 16 * ty),
                  (tip[0] - 8 * tx + 9 * nx, tip[1] - 8 * ty + 9 * ny),
                  (tip[0] - 8 * tx - 9 * nx, tip[1] - 8 * ty - 9 * ny)],
                 fill=GOLD)
    # small "back" label under the arrow
    center(draw, cx, y1 - 26, "HUANG RETURNS", font(17), GOLD, stroke=1)


def draw_blacklist(draw, x0, y0, x1, y1):
    """Megaspeed: a chip under a red prohibition stamp -- blacklisted."""
    draw.rectangle([x0, y0, x1, y1], fill=CARD)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 6
    # small chip
    draw.rectangle([cx - 46, cy - 30, cx + 46, cy + 30], fill=NAVY,
                   outline=INK, width=2)
    for i in range(3):
        px = cx - 30 + i * 24
        draw.rectangle([px, cy - 40, px + 10, cy - 30], fill=INK)
        draw.rectangle([px, cy + 30, px + 10, cy + 40], fill=INK)
    # (no label on the chip: the prohibition slash would strike through it)
    # red prohibition circle + slash over the chip
    draw.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], outline=RED, width=8)
    draw.line([(cx - 44, cy + 44), (cx + 44, cy - 44)], fill=RED, width=8)
    # BANNED stamp below
    sx0, sx1, sy = cx - 62, cx + 62, y1 - 40
    draw.rectangle([sx0, sy, sx1, sy + 26], outline=RED, width=3)
    center(draw, cx, sy + 3, "BANNED", font(20), RED, stroke=1)


def draw_demand_tanker(draw, x0, y0, x1, y1):
    """Hormuz: Tehran's $290bn demand banner over a tanker and a mine."""
    # demand banner across the top
    draw.rectangle([x0, y0, x1, y0 + 40], fill=RED)
    center(draw, (x0 + x1) // 2, y0 + 6, "$290 BILLION", font(26), CARD,
           stroke=1)
    # sea
    sea_y = y0 + 40
    draw.rectangle([x0, sea_y, x1, y1], fill=SEA)
    for wx in range(x0 + 6, x1 - 10, 34):
        draw.arc([wx, sea_y + 66, wx + 30, sea_y + 84], 200, 340, fill=CARD,
                 width=3)
    # tanker hull
    hx0, hx1, hy = x0 + 52, x1 - 52, sea_y + 26
    draw.polygon([(hx0, hy), (hx1, hy), (hx1 - 12, hy + 32), (hx0 + 12, hy + 32)],
                 fill=(52, 58, 68))
    draw.rectangle([hx0, hy - 20, hx0 + 140, hy], fill=RED)      # containers
    draw.rectangle([hx0 + 146, hy - 20, hx0 + 196, hy], fill=GOLD)
    draw.rectangle([hx0 + 202, hy - 20, hx1 - 36, hy], fill=TEAL)
    draw.rectangle([hx1 - 30, hy - 36, hx1 - 8, hy], fill=INK)   # funnel
    draw.rectangle([hx1 - 30, hy - 36, hx1 - 8, hy - 28], fill=YELLOW)
    # spiked mine in the water, right side
    mx, my = x1 - 34, sea_y + 92
    for dx, dy in [(0, -12), (0, 12), (-12, 0), (12, 0),
                   (-8, -8), (8, -8), (-8, 8), (8, 8)]:
        draw.line([mx, my, mx + dx, my + dy], fill=INK, width=3)
    draw.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=INK)
    # small explosion burst above the ship
    starburst(draw, (x0 + x1) // 2, sea_y + 12, 16, 7, 8, ORANGE)


def draw_jets_radar(draw, x0, y0, x1, y1):
    """Korea ADIZ: fighter jets cross the sky, radar tracks them."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT)
    # contrails
    draw.arc([x0 - 40, y0 + 6, x0 + 260, y0 + 90], 300, 30, fill=CARD, width=4)
    draw.arc([x0 - 20, y0 + 52, x0 + 300, y0 + 136], 300, 30, fill=CARD,
             width=4)

    def jet(jx, jy, s):
        pts = [(jx + 36 * s, jy), (jx + 8 * s, jy - 8 * s),
               (jx - 28 * s, jy - 26 * s), (jx - 20 * s, jy - 6 * s),
               (jx - 30 * s, jy - 2 * s), (jx - 30 * s, jy + 2 * s),
               (jx - 20 * s, jy + 6 * s), (jx - 28 * s, jy + 26 * s),
               (jx + 8 * s, jy + 8 * s)]
        draw.polygon(pts, fill=INK)

    jet(x0 + 210, y0 + 44, 1.0)
    jet(x0 + 260, y0 + 92, 0.8)
    # radar screen, lower left
    rx, ry, rr = x0 + 52, y1 - 40, 34
    draw.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(16, 60, 30),
                 outline=GREEN, width=2)
    draw.ellipse([rx - rr + 10, ry - rr + 10, rx + rr - 10, ry + rr - 10],
                 outline=GREEN, width=1)
    draw.line([(rx, ry), (rx + 24, ry - 22)], fill=GREEN, width=2)
    for bx, by in [(rx + 12, ry - 8), (rx - 8, ry + 12)]:
        draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=YELLOW)
    # warning triangle, lower right
    wx, wy = x1 - 52, y1 - 44
    draw.polygon([(wx, wy - 26), (wx - 26, wy + 18), (wx + 26, wy + 18)],
                 fill=YELLOW, outline=INK, width=2)
    center(draw, wx, wy - 14, "!", font(24), INK, stroke=1)


ILLUSTRATIONS = [draw_chip_return, draw_blacklist, draw_demand_tanker,
                 draw_jets_radar]

STORIES = [
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


def draw_story(draw, story, x0, y0, w, h):
    color = story["color"]
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=CARD, outline=INK, width=2)
    draw.rectangle([x0, y0, x0 + w, y0 + 8], fill=color)
    # illustration panel
    px0, py0, px1, py1 = x0 + 12, y0 + 20, x0 + w - 12, y0 + 188
    draw.rectangle([px0, py0, px1, py1], outline=(190, 192, 196), width=1)
    ILLUSTRATIONS[story["art"]](draw, px0, py0, px1, py1)
    # story number badge
    bx, by = px0 + 16, py0 + 16
    draw.ellipse([bx, by, bx + 30, by + 30], fill=color, outline=CARD, width=2)
    center(draw, bx + 15, by + 4, story["num"], font(18), CARD, stroke=1)
    # tag
    draw.text((x0 + 16, y0 + 200), story["tag"], font=font(17), fill=color,
              stroke_width=1, stroke_fill=color)
    # headline (up to 2 lines)
    hl = wrap(draw, story["headline"], font(29), w - 32, stroke=1)
    y = y0 + 226
    for line in hl[:2]:
        draw.text((x0 + 16, y), line, font=font(29), fill=INK,
                  stroke_width=1, stroke_fill=INK)
        y += 36
    # subtext (up to 3 lines)
    sub = wrap(draw, story["sub"], font(19), w - 32)
    y = y0 + 226 + 36 * len(hl[:2]) + 6
    for line in sub[:3]:
        draw.text((x0 + 16, y), line, font=font(19), fill=GREY)
        y += 25


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # outer double border
    draw.rectangle([10, 10, W - 11, H - 11], outline=INK, width=3)
    draw.rectangle([18, 18, W - 19, H - 19], outline=INK, width=1)

    # masthead: the day, named loud and clear
    center(draw, W // 2, 34, "THE WORLD IN ONE DAY", font(26), INK, stroke=1)
    center(draw, W // 2, 68, "TUESDAY, 24 NOVEMBER 2026", font(46), RED, stroke=2)
    draw.line([(60, 128), (W - 60, 128)], fill=INK, width=2)
    draw.line([(60, 134), (W - 60, 134)], fill=INK, width=1)
    center(draw, W // 2, 142, "Four stories that defined the day",
           font(20), GREY)

    # 2 x 2 grid of stories
    cell_w, cell_h, gap = 476, 384, 16
    x0, y0 = 28, 172
    for i, story in enumerate(STORIES):
        cx = x0 + (i % 2) * (cell_w + gap)
        cy = y0 + (i // 2) * (cell_h + gap)
        draw_story(draw, story, cx, cy, cell_w, cell_h)

    # footer repeats the date so the day is unmistakable
    center(draw, W // 2, 968, "News of Tuesday, 24 November 2026",
           font(18), GREY, stroke=1)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
