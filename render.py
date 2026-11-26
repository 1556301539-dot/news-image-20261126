#!/usr/bin/env python3
"""Draw the front page for news-image-20261126: one day of world news.

Deterministic Pillow program. Run it twice and the bytes are
identical: no randomness, no time, no network, fixed fonts.
Writes entry.png (1024x1024, under 1 MiB) next to this file.

Design: "Broadsheet Dusk" — deep navy, amber and signal red on warm
paper, serif masthead. 30 stories: 3 big scenes, 10 small scenes,
17 numbered briefs, a world map with numbered dots, a six-number
strip, a UTC timeline of real clock times only, and a boxed DATE
CHECK. Every story carries OFFICIAL / REPORTED / CLAIM.
"""

import hashlib
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = Path(__file__).resolve().parent / "entry.png"

# --- palette ---------------------------------------------------------
PAPER = (244, 234, 216)
PAPER_LT = (250, 246, 238)
INK = (27, 42, 74)
INK_SOFT = (58, 68, 96)
AMBER = (217, 164, 65)
AMBER_DK = (176, 124, 32)
RED = (179, 35, 27)
RED_DK = (140, 24, 18)
TEAL = (46, 111, 106)
GREEN = (74, 122, 58)
OCHRE = (192, 138, 45)
SLATE = (90, 107, 138)
SAGE = (201, 194, 168)
GREY = (120, 118, 110)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
LIB_DIR = Path("/usr/share/fonts/truetype/liberation")


def font(size, bold=False, serif=True, italic=False):
    if italic:
        p = LIB_DIR / "LiberationSerif-Italic.ttf"
        return ImageFont.truetype(str(p), size)
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
        return ImageFont.truetype(str(FONT_DIR / name), size)
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, cx, y, s, f, fill):
    w = draw.textlength(s, font=f)
    draw.text((cx - w / 2, y), s, font=f, fill=fill)


def vgrad(base, top, bottom, height):
    """Vertical gradient image, height tall, 1 px wide scaled up."""
    img = Image.new("RGB", (1, height))
    px = img.load()
    for y in range(height):
        t = y / max(1, height - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return img.resize((base, height))


def chip(draw, x, y, label, fill=RED):
    """Small credibility label chip; returns its width."""
    f = font(10, bold=True, serif=False)
    w = int(draw.textlength(label, font=f)) + 12
    draw.rounded_rectangle([x, y, x + w, y + 16], radius=3, fill=fill)
    draw.text((x + 6, y + 3), label, font=f, fill=WHITE)
    return w


def label_color(label):
    return {"OFFICIAL": TEAL, "REPORTED": INK, "CLAIM": RED}.get(label, INK)


def draw_star(draw, cx, cy, r_out, r_in, fill):
    """Five-pointed star polygon (the ★ glyph is missing in these fonts)."""
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        ang = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def rule(draw, x0, y, x1, color=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)

# --- masthead --------------------------------------------------------
def masthead(img, draw):
    # top double rule
    rule(draw, 24, 10, 1000, INK, 3)
    rule(draw, 24, 15, 1000, INK, 1)
    draw_centered(draw, 512, 22, "THE WORLD IN ONE PAGE",
                  font(30, bold=True), INK)
    draw_centered(draw, 512, 58, "THURSDAY  26  NOVEMBER  2026",
                  font(34, bold=True), RED)
    # red italic headline strip
    draw_centered(
        draw, 512, 100,
        "Five more tankers hit  ·  Parade off in the storm  ·  Kim vows more bombs",
        font(16, italic=True), RED_DK)
    rule(draw, 24, 126, 1000, INK, 2)


def count_bar(img, draw):
    y = 132
    draw.rectangle([24, y, 1000, y + 26], fill=AMBER)
    draw_centered(draw, 512, y + 5,
                  "30 STORIES  ·  6 REGIONS  ·  12 FIELDS",
                  font(15, bold=True, serif=False), INK)
    # legend, right-aligned inside the same band is too crowded;
    # put it on the next thin line instead
    y2 = y + 30
    lx = 24
    draw.text((lx, y2), "HOW SURE:", font=font(11, bold=True, serif=False),
              fill=INK_SOFT)
    lx += 78
    for label, col in (("OFFICIAL", TEAL), ("REPORTED", INK),
                       ("CLAIM", RED)):
        chip(draw, lx, y2, label, fill=col)
        lx += int(text_w(draw, label, font(10, bold=True, serif=False))) + 26


def region_bar(img, draw):
    y = 184
    regions = [
        ("MIDDLE EAST", 4, RED),
        ("ASIA-PACIFIC", 7, TEAL),
        ("AMERICAS", 11, INK),
        ("EUROPE", 4, OCHRE),
        ("AFRICA", 3, GREEN),
        ("OCEANIA", 1, SLATE),
    ]
    x = 24
    bw = (1000 - 24) // 6
    for name, n, col in regions:
        draw.rectangle([x, y, x + bw - 3, y + 30], fill=col)
        draw_centered(draw, x + (bw - 3) // 2, y + 4,
                      f"{name} · {n}", font(11, bold=True, serif=False),
                      WHITE)
        x += bw
    return y + 30


def number_strip(img, draw, y):
    nums = [
        ("5", "TANKERS HIT"),
        ("100", "YEARS OF PARADE"),
        ("1M", "SATELLITES"),
        ("~2,000", "MIGRANTS IN A DAY"),
        ("168", "REMEMBERED"),
        ("60", "MPH GUSTS"),
    ]
    x = 24
    bw = (1000 - 24) // 6
    for big, small in nums:
        draw.rectangle([x, y, x + bw - 3, y + 52], outline=INK, width=1)
        draw_centered(draw, x + (bw - 3) // 2, y + 4, big,
                      font(24, bold=True), RED)
        draw_centered(draw, x + (bw - 3) // 2, y + 32, small,
                      font(10, bold=True, serif=False), INK)
        x += bw
    return y + 52


def timeline(img, draw, y):
    draw.text((24, y), "THE DAY IN UTC — REAL TIMES ONLY",
              font=font(11, bold=True, serif=False), fill=INK_SOFT)
    y += 18
    draw.line([(40, y + 6), (984, y + 6)], fill=GREY, width=2)
    nodes = [
        ("01:37", "Brent $94.71 as Hormuz claims lift oil"),
        ("02:05", "Macy's parade moved to Saturday"),
        ("03:58", "Iran: five more tankers hit mines"),
    ]
    xs = [180, 512, 844]
    for (t, txt), cx in zip(nodes, xs):
        draw.ellipse([cx - 6, y, cx + 6, y + 12], fill=RED)
        draw_centered(draw, cx, y + 16, t, font(13, bold=True), RED)
        draw_centered(draw, cx, y + 34, txt, font(11, serif=False), INK)
    return y + 52

# --- big scenes ------------------------------------------------------
def big_scene_frame(img, draw, x, y, w, h, label):
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    chip(draw, x + 6, y + 6, label, fill=label_color(label))


def scene_hormuz(img, draw, x, y, w, h):
    # dusk sky + dark sea
    sky = vgrad(w, (232, 148, 74), (64, 52, 96), int(h * 0.62))
    img.paste(sky, (x, y))
    draw.ellipse([x + w // 2 - 26, y + 18, x + w // 2 + 26, y + 70],
                 fill=(240, 196, 90))
    sea_y = y + int(h * 0.62)
    draw.rectangle([x, sea_y, x + w, y + h], fill=(24, 38, 66))
    for i, wy in enumerate((sea_y + 12, sea_y + 26, sea_y + 40)):
        draw.line([(x + 8 + i * 30, wy), (x + w - 8 - i * 20, wy)],
                  fill=(90, 120, 160), width=2)
    # tanker silhouette
    hx, hy = x + 30, sea_y - 6
    draw.rectangle([hx, hy - 26, hx + 210, hy + 14], fill=BLACK)
    draw.rectangle([hx + 150, hy - 52, hx + 196, hy - 26], fill=BLACK)
    draw.rectangle([hx + 158, hy - 64, hx + 166, hy - 52], fill=BLACK)
    draw.line([(hx + 210, hy - 26), (hx + 236, hy + 2)], fill=BLACK, width=6)
    # fire glow on deck (stacked, flame-like) + smoke (kept inside frame)
    for (fx, fy, r, c) in ((hx + 96, hy - 22, 24, (240, 120, 30)),
                           (hx + 96, hy - 30, 16, (250, 190, 60)),
                           (hx + 96, hy - 35, 9, (255, 230, 120))):
        draw.ellipse([fx - r, fy - r, fx + r, fy + r], fill=c)
    for cx, cy, r in ((hx + 70, hy - 40, 10), (hx + 88, hy - 54, 12),
                      (hx + 108, hy - 66, 10)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 108, 104))
    # naval mine
    mx, my = x + w - 52, sea_y + 34
    draw.ellipse([mx - 10, my - 10, mx + 10, my + 10], fill=(40, 40, 40))
    for ang in range(0, 360, 45):
        import math
        dx = int(13 * math.cos(math.radians(ang)))
        dy = int(13 * math.sin(math.radians(ang)))
        draw.line([(mx, my), (mx + dx, my + dy)], fill=(40, 40, 40),
                  width=2)
    big_scene_frame(img, draw, x, y, w, h, "CLAIM")


def scene_parade(img, draw, x, y, w, h):
    # storm-grey sky, rain, skyline, drooping balloon
    sky = vgrad(w, (176, 188, 202), (120, 134, 158), int(h * 0.7))
    img.paste(sky, (x, y))
    for i in range(26):
        rx = x + (i * 37) % w
        ry = y + (i * 29) % int(h * 0.7)
        draw.line([(rx, ry), (rx - 8, ry + 16)], fill=(230, 236, 242),
                  width=1)
    base = y + int(h * 0.7)
    draw.rectangle([x, base, x + w, y + h], fill=(70, 78, 96))
    # skyline
    heights = [46, 70, 38, 88, 56, 78, 44, 66]
    bx = x + 8
    for hh in heights:
        bw = (w - 16) // 8
        draw.rectangle([bx, base - hh, bx + bw - 4, base], fill=INK)
        for wy in range(base - hh + 8, base - 6, 12):
            draw.rectangle([bx + 4, wy, bx + 8, wy + 5], fill=AMBER)
        bx += bw
    # big drooping balloon, low over the rooftops
    cx, cy = x + w // 2, y + 52
    draw.ellipse([cx - 58, cy - 26, cx + 58, cy + 26], fill=AMBER)
    draw.ellipse([cx - 58, cy - 26, cx - 8, cy + 26], fill=(226, 178, 92))
    draw.polygon([(cx - 58, cy + 10), (cx - 30, cy + 44), (cx - 18, cy + 12)],
                 fill=AMBER)
    draw.line([(cx - 30, cy + 44), (cx - 44, base - 46)], fill=BLACK, width=2)
    draw.line([(cx + 20, cy + 40), (cx + 34, base - 46)], fill=BLACK, width=2)
    draw.text((cx - 34, cy - 12), "100", font=font(26, bold=True), fill=RED_DK)
    big_scene_frame(img, draw, x, y, w, h, "OFFICIAL")


def scene_kim(img, draw, x, y, w, h):
    # pale dawn, mountains, missile on launcher
    sky = vgrad(w, (238, 222, 180), (168, 178, 196), int(h * 0.66))
    img.paste(sky, (x, y))
    draw.ellipse([x + w - 66, y + 14, x + w - 22, y + 58],
                 fill=(245, 220, 140))
    base = y + int(h * 0.66)
    draw.polygon([(x, base), (x + 70, base - 52), (x + 150, base),
                  (x + 210, base - 70), (x + 280, base - 20), (x + w, base),
                  (x + w, y + h), (x, y + h)], fill=(88, 96, 110))
    draw.rectangle([x, base, x + w, y + h], fill=(58, 64, 78))
    # launcher + missile
    lx = x + w // 2 - 70
    draw.rectangle([lx, base - 18, lx + 140, base - 8], fill=(30, 30, 34))
    draw.rectangle([lx + 8, base - 8, lx + 20, base], fill=(30, 30, 34))
    draw.rectangle([lx + 120, base - 8, lx + 132, base], fill=(30, 30, 34))
    mx = lx + 62
    draw.rectangle([mx, base - 78, mx + 16, base - 18], fill=(225, 225, 225))
    draw.polygon([(mx, base - 78), (mx + 8, base - 92), (mx + 16, base - 78)],
                 fill=RED)
    draw.rectangle([mx, base - 66, mx + 16, base - 58], fill=RED)
    # red star in the sky
    draw_star(draw, x + 36, y + 30, 14, 6, RED)
    big_scene_frame(img, draw, x, y, w, h, "REPORTED")


BIG_SCENES = [
    (scene_hormuz, "FIVE MORE TANKERS HIT",
     "Iran claims five tankers hit mines in a day; oil $94.71"),
    (scene_parade, "PARADE OFF IN THE STORM",
     "Macy's 100th parade put off to Saturday — a first in 100 years"),
    (scene_kim, "KIM VOWS MORE BOMBS",
     "North Korea to expand its nuclear weapons, ignoring Trump"),
]


def big_scenes(img, draw, y):
    w, gap = 318, 11
    x = 24
    img_h = 140
    for fn, head, sub in BIG_SCENES:
        fn(img, draw, x, y, w, img_h)
        hy = y + img_h + 8
        for line in wrap(draw, head, font(17, bold=True), w):
            draw.text((x, hy), line, font=font(17, bold=True), fill=INK)
            hy += 21
        draw.text((x, hy), sub, font=font(11, serif=False), fill=INK_SOFT)
        x += w + gap
    return y + img_h + 8 + 21 + 14

# --- small scenes ----------------------------------------------------
def small_frame(img, draw, x, y, w, h, keyword, kcolor, label):
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    draw.rectangle([x, y, x + w, y + 16], fill=kcolor)
    draw.text((x + 5, y + 3), keyword, font=font(10, bold=True, serif=False),
              fill=WHITE)
    lf = font(10, bold=True, serif=False)
    lw = int(draw.textlength(label, font=lf)) + 12
    chip(draw, x + w - lw - 3, y + h - 19, label, fill=label_color(label))


def sc_tariffs(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    draw.rectangle([x + 18, y + 34, x + 80, y + h - 6], fill=RED)
    draw.rectangle([x + 84, y + 34, x + 146, y + h - 6], fill=INK)
    draw.rectangle([x + 48, y + 18, x + 116, y + 34], fill=AMBER)
    draw.text((x + 30, y + 38), "25%", font=font(12, bold=True), fill=WHITE)
    draw.text((x + 88, y + 38), "15%", font=font(12, bold=True), fill=WHITE)
    draw.line([(x + 150, y + 18), (x + 178, y + 18)], fill=INK, width=3)


def sc_spacex(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(210, 226, 236))
    draw.ellipse([x - 30, y + h - 28, x + w + 30, y + h],
                 fill=(52, 98, 150))
    for cx, cy in ((x + 40, y + 26), (x + 96, y + 20), (x + 150, y + 30)):
        draw.rectangle([cx - 5, cy - 4, cx + 5, cy + 4], fill=(90, 90, 96))
        draw.rectangle([cx - 16, cy - 2, cx - 5, cy + 2], fill=(140, 150, 160))
        draw.rectangle([cx + 5, cy - 2, cx + 16, cy + 2], fill=(140, 150, 160))
    draw.arc([x + 10, y - 6, x + w - 10, y + 44], 200, 340,
             fill=(120, 130, 140), width=1)


def sc_shares(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(245, 240, 224))
    cx, cy = x + 56, y + 36
    draw_star(draw, cx, cy, 18, 8, AMBER)
    for ox in (118, 152):
        draw.ellipse([x + ox, y + 26, x + ox + 30, y + 56], fill=AMBER_DK)
        draw.text((x + ox + 10, y + 33), "$", font=font(14, bold=True), fill=WHITE)


def sc_canary(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(214, 228, 236))
    draw.ellipse([x + 140, y + 8, x + 168, y + 36], fill=(245, 220, 140))
    draw.rectangle([x, y + 38, x + w, y + h], fill=(120, 168, 196))
    draw.polygon([(x + 58, y + 40), (x + 130, y + 40), (x + 118, y + 52),
                  (x + 70, y + 52)], fill=(30, 34, 44))
    draw.line([(x + 94, y + 40), (x + 94, y + 22)], fill=(30, 34, 44), width=2)
    draw.polygon([(x + 96, y + 22), (x + 118, y + 38), (x + 96, y + 38)],
                 fill=WHITE)
    for dx in (76, 90, 104, 116):
        draw.ellipse([x + dx, y + 32, x + dx + 5, y + 37], fill=(20, 20, 20))


def sc_hongkong(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 236, 228))
    draw.rectangle([x, y + h - 14, x + w, y + h], fill=(120, 100, 84))
    for i, cx in enumerate((44, 84, 124, 160)):
        draw.rectangle([x + cx - 5, y + 30, x + cx + 5, y + h - 14],
                       fill=WHITE)
        draw.ellipse([x + cx - 4, y + 20, x + cx + 4, y + 30],
                     fill=(250, 190, 60))
    for cx, cy, c in ((30, 46, RED), (64, 50, (200, 120, 160)),
                      (104, 46, AMBER), (144, 50, (150, 120, 180)),
                      (172, 44, RED)):
        draw.ellipse([x + cx - 4, y + cy - 4, x + cx + 4, y + cy + 4], fill=c)


def sc_tides(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(220, 230, 236))
    draw.ellipse([x + 20, y + 16, x + 168, y + h], fill=(64, 130, 150))
    draw.ellipse([x + 20, y + 34, x + 168, y + h], fill=(214, 228, 236))
    draw.rectangle([x + 24, y + 40, x + w - 24, y + 48], fill=(120, 88, 56))
    for px in (40, 80, 120, 160):
        draw.rectangle([x + px, y + 48, x + px + 5, y + h - 4],
                       fill=(96, 70, 44))


def sc_fedex(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(224, 230, 236))
    draw.rectangle([x, y + 40, x + w, y + h], fill=(150, 152, 154))
    draw.rectangle([x, y + 40, x + w, y + 44], fill=WHITE)
    # plane silhouette, nose down the runway
    draw.ellipse([x + 30, y + 22, x + 150, y + 40], fill=WHITE)
    draw.polygon([(x + 140, y + 22), (x + 168, y + 30), (x + 140, y + 34)],
                 fill=INK)
    draw.rectangle([x + 96, y + 16, x + 116, y + 24], fill=INK)
    draw.rectangle([x + 60, y + 40, x + 66, y + 46], fill=BLACK)
    draw.rectangle([x + 120, y + 40, x + 126, y + 46], fill=BLACK)
    for cx, cy, r in ((28, 44, 7), (16, 48, 5), (40, 50, 4)):
        draw.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                     fill=(200, 196, 188))


def sc_crash(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(206, 224, 234))
    for wy in (30, 44):
        draw.arc([x + 10, y + wy - 8, x + w - 10, y + wy + 8], 0, 180,
                 fill=(90, 140, 170), width=2)
    draw.ellipse([x + 70, y + 24, x + 116, y + 52], outline=(230, 90, 20),
                 width=5)
    draw.ellipse([x + 82, y + 30, x + 104, y + 46], outline=(230, 90, 20),
                 width=5)
    draw.polygon([(x + 130, y + 44), (x + 170, y + 44), (x + 160, y + 52),
                  (x + 140, y + 52)], fill=(230, 90, 20))


def sc_guitar(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    draw.ellipse([x + 34, y + 26, x + 86, y + 58], fill=(122, 74, 36))
    draw.ellipse([x + 52, y + 36, x + 68, y + 48], fill=(30, 20, 12))
    draw.rectangle([x + 82, y + 30, x + 158, y + 40], fill=(90, 56, 26))
    draw.rectangle([x + 152, y + 26, x + 172, y + 44], fill=(60, 38, 18))
    draw.text((x + 130, y + 40), "♪", font=font(18, serif=False), fill=INK)
    draw.text((x + 152, y + 22), "♫", font=font(16, serif=False), fill=RED)


def sc_swiss(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(228, 232, 238))
    draw.rectangle([x + 44, y + 22, x + 144, y + h - 6], fill=WHITE)
    draw.polygon([(x + 36, y + 22), (x + 94, y + 12), (x + 152, y + 22)],
                 fill=(150, 150, 152))
    for cx in (58, 80, 102, 124):
        draw.rectangle([x + cx, y + 30, x + cx + 5, y + h - 6], fill=INK)
    draw.rectangle([x + 156, y + 22, x + 178, y + 44], fill=RED)
    draw.rectangle([x + 164, y + 26, x + 170, y + 40], fill=WHITE)
    draw.rectangle([x + 159, y + 31, x + 175, y + 35], fill=WHITE)


SMALL_SCENES = [
    (sc_tariffs, "TARIFFS 25%", RED, "REPORTED",
     "Trump doubles down on tariffs"),
    (sc_spacex, "1M SATELLITES", TEAL, "OFFICIAL",
     "FCC clears 1m SpaceX satellites"),
    (sc_shares, "2 SHARES", AMBER_DK, "REPORTED",
     "Musk: 2 shares for every child"),
    (sc_canary, "2,000 ARRIVE", INK, "REPORTED",
     "Nearly 2,000 reach Canary Isles"),
    (sc_hongkong, "168 REMEMBERED", SLATE, "REPORTED",
     "Hong Kong remembers 168 victims"),
    (sc_tides, "KING TIDES", TEAL, "REPORTED",
     "King tides flood California coast"),
    (sc_fedex, "RUNWAY", INK, "REPORTED",
     "FedEx plane off Miami runway"),
    (sc_crash, "6 DEAD", RED, "OFFICIAL",
     "Six dead in US coast plane crash"),
    (sc_guitar, "ANDY TAYLOR 65", OCHRE, "REPORTED",
     "Duran Duran's Andy Taylor dies, 65"),
    (sc_swiss, "OFFICE SHUT", SLATE, "REPORTED",
     "N. Korea shuts Swiss office"),
]


def small_scenes(img, draw, y):
    w, gap = 188, 9
    img_h = 56
    row_h = 90
    for row in range(2):
        x = 24
        for col in range(5):
            fn, kw, kc, lab, head = SMALL_SCENES[row * 5 + col]
            fn(img, draw, x, y, w, img_h)
            small_frame(img, draw, x, y, w, img_h, kw, kc, lab)
            hy = y + img_h + 4
            for line in wrap(draw, head, font(10, bold=True, serif=False), w):
                draw.text((x, hy), line, font=font(10, bold=True, serif=False),
                          fill=INK)
                hy += 12
            x += w + gap
        y += row_h
    return y

# --- map + DATE CHECK -----------------------------------------------
CONTINENTS = [
    # North America
    [(58, 18), (96, 12), (128, 22), (158, 28), (186, 24), (198, 42),
     (188, 64), (162, 74), (140, 70), (112, 56), (82, 42), (58, 32)],
    # South America
    [(188, 74), (208, 72), (222, 88), (212, 112), (194, 118), (184, 94)],
    # Europe
    [(282, 22), (308, 14), (328, 22), (318, 36), (296, 34), (282, 28)],
    # Africa
    [(284, 48), (312, 44), (338, 54), (334, 78), (314, 98), (294, 88),
     (280, 64)],
    # Asia
    [(338, 18), (418, 10), (496, 16), (538, 28), (520, 50), (472, 64),
     (420, 68), (380, 54), (350, 36)],
    # Australia
    [(478, 98), (518, 94), (532, 106), (504, 116), (480, 110)],
]

# (number, x, y) in map-area coords
MAP_DOTS = [
    (1, 393, 50), (2, 185, 35), (3, 508, 40), (4, 170, 54), (5, 148, 80),
    (6, 125, 45), (7, 273, 50), (8, 488, 56), (9, 97, 44), (10, 182, 82),
    (11, 138, 66), (12, 300, 32), (13, 526, 60),
]


def map_panel(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    draw.text((x + 8, y + 5), "WHERE IT HAPPENED — STORIES 1–13",
              font=font(11, bold=True, serif=False), fill=INK)
    my = y + 22
    mh = h - 22
    for poly in CONTINENTS:
        pts = [(x + px, my + int(py * mh / 126)) for px, py in poly]
        draw.polygon(pts, fill=SAGE, outline=(150, 146, 128))
    for n, dx, dy in MAP_DOTS:
        cx, cy = x + dx, my + int(dy * mh / 126)
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED,
                     outline=WHITE, width=1)
        nf = font(9, bold=True, serif=False)
        tw = draw.textlength(str(n), font=nf)
        draw.text((cx - tw / 2, cy - 6), str(n), font=nf, fill=WHITE)


DATE_CHECK_LEFT = [
    "Shenzhou-24 launch — Wed 25",
    "Cairo tanker fire, 31 dead — Wed 25",
    "Savasleyka airbase hit — Wed 25",
    "Miss Universe crowned — Tue 24",
    "Huawei verdict — Tue 24",
    "Murmansk governor sacked — Wed 25",
    "Gaza security chief killed — Wed 25",
    "COP31 collapsed — Sun 22",
]
DATE_CHECK_NOT_YET = [
    "Macy's parade — Sat 28",
    "Spain votes — Sun 29",
]


def date_check_panel(img, draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], outline=RED, width=2)
    draw.rectangle([x, y, x + w, y + 22], fill=RED)
    draw.text((x + 8, y + 4), "DATE CHECK — LEFT OUT",
              font=font(12, bold=True, serif=False), fill=WHITE)
    ly = y + 28
    f = font(9, serif=False)
    for line in DATE_CHECK_LEFT:
        draw.text((x + 8, ly), "×  " + line, font=f, fill=INK)
        ly += 12
    draw.text((x + 8, ly + 2), "NOT YET — MUST NOT BE SHOWN AS DONE:",
              font=font(9, bold=True, serif=False), fill=RED_DK)
    ly += 16
    for line in DATE_CHECK_NOT_YET:
        draw.text((x + 8, ly), "○  " + line, font=f, fill=INK)
        ly += 12
    return ly


# --- briefs + footer --------------------------------------------------
BRIEFS = [
    (14, "Coalition intercepts Houthi attacks", "REPORTED"),
    (15, "Iran shrugs off US naval blockade", "OFFICIAL"),
    (16, "Birthright order blocked by 2nd judge", "OFFICIAL"),
    (17, "OPEC blames EU for COP31 collapse", "REPORTED"),
    (18, "Solomons sign deal with Australia", "OFFICIAL"),
    (19, "RSF kills 19 in Blue Nile strikes", "REPORTED"),
    (20, "20+ trapped in flooded Indonesia mine", "REPORTED"),
    (21, "Ramaphosa report ruled unlawful", "OFFICIAL"),
    (22, "WHO: end US fuel blockade on Cuba", "OFFICIAL"),
    (23, "Lebanon to open 2nd airport", "REPORTED"),
    (24, "Nations urge Russia: halt riot agent", "OFFICIAL"),
    (25, "Kenyan cult leader convicted again", "OFFICIAL"),
    (26, "Steelers cut Aaron Rodgers", "OFFICIAL"),
    (27, "Nvidia: China chip access; Vance backs Huang", "REPORTED"),
    (28, "US approves $621.9M for Ukraine F-16s", "OFFICIAL"),
    (29, "Russia approves 50T-ruble war budget", "OFFICIAL"),
    (30, "JAXA unveils Moon rover with India", "OFFICIAL"),
]


def briefs(img, draw, y):
    draw.text((24, y), "THE DAY IN BRIEF — 14–30",
              font=font(12, bold=True, serif=False), fill=INK)
    rule(draw, 24, y + 16, 1000, INK, 1)
    by = y + 22
    bf = font(11, serif=False)
    lf = font(9, bold=True, serif=False)
    cols = [24, 352, 680]
    col_w = 320
    for i, (n, text, lab) in enumerate(BRIEFS):
        col, row = divmod(i, 6)
        bx, byy = cols[col], by + row * 15
        draw.text((bx, byy), f"{n}.", font=font(11, bold=True), fill=RED)
        # fit the text: shrink until it fits the column minus label
        tf = bf
        max_tw = col_w - 24 - int(draw.textlength(lab, font=lf)) - 8
        while draw.textlength(text, font=tf) > max_tw and tf.size > 9:
            tf = font(tf.size - 1, serif=False)
        draw.text((bx + 22, byy), text, font=tf, fill=INK)
        tw = draw.textlength(text, font=tf)
        draw.text((bx + 22 + tw + 6, byy + 1), lab, font=lf,
                  fill=label_color(lab))
    return by + 6 * 15


def footer(img, draw, y):
    rule(draw, 24, y, 1000, INK, 2)
    draw.text(
        (24, y + 5),
        "Sources: Reuters · AP · AFP · BBC · CGTN · Times Now · USA Today · "
        "Japan Times · HKFP · One Turn — full list in SOURCES.md",
        font=font(9, serif=False), fill=INK_SOFT)
    draw_centered(draw, 512, y + 18,
                  "THE WORLD IN ONE PAGE · THURSDAY 26 NOVEMBER 2026",
                  font(9, bold=True, serif=False), INK_SOFT)
    return y + 30


# --- compose ----------------------------------------------------------
def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    masthead(img, draw)
    count_bar(img, draw)
    region_bar(img, draw)
    y = number_strip(img, draw, 218)
    y = timeline(img, draw, y + 6)
    y = big_scenes(img, draw, y + 6)
    y = small_scenes(img, draw, y + 6)
    y += 6
    map_panel(img, draw, 24, y, 600, 140)
    date_check_panel(img, draw, 636, y, 364, 140)
    y += 140 + 6
    y = briefs(img, draw, y)
    y = footer(img, draw, y + 4)
    assert y <= 1024, f"layout overflow: {y}"
    img.save(OUT, format="PNG", optimize=True)
    data = OUT.read_bytes()
    print(f"wrote {OUT} ({len(data)} bytes, "
          f"sha256 {hashlib.sha256(data).hexdigest()})")
    return len(data)


if __name__ == "__main__":
    build()
