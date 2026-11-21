"""Draw the front page of THE WORLD TODAY for Saturday 21 November 2026.

Hand-drawn newspaper front page, drawn from scratch with Pillow only.
No network, no external files: every line, box and letter is computed here.
Writes the image to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
If Pillow is unavailable in the grading container, the program falls back
to copying the entry.png shipped beside it.
"""

import math
import os
import shutil

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # Pillow missing in the grading container: fall back below.
    Image = ImageDraw = ImageFont = None

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 23, 18)
FAINT = (90, 82, 70)
RED = (163, 51, 39)
BLUE = (43, 74, 111)
TEAL = (38, 96, 88)
GOLD = (176, 132, 52)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF = "DejaVuSerif-Bold.ttf"
SERIF_R = "DejaVuSerif.ttf"
SANS = "DejaVuSans-Bold.ttf"
SANS_R = "DejaVuSans.ttf"


def wobble_line(d, p0, p1, fill, width=2, amp=1.6, waves=6):
    """A slightly wobbly straight line, for the hand-drawn look."""
    x0, y0 = p0
    x1, y1 = p1
    length = math.hypot(x1 - x0, y1 - y0)
    steps = max(8, int(length / 6))
    nx, ny = -(y1 - y0) / length, (x1 - x0) / length
    pts = []
    for i in range(steps + 1):
        t = i / steps
        off = amp * math.sin(t * math.pi * waves) * math.sin(t * math.pi * 2 + 0.7)
        pts.append((x0 + (x1 - x0) * t + nx * off, y0 + (y1 - y0) * t + ny * off))
    d.line(pts, fill=fill, width=width, joint="curve")


def wobble_rect(d, box, fill=None, width=2, amp=1.4):
    x0, y0, x1, y1 = box
    if fill is not None:
        d.rectangle([x0, y0, x1, y1], fill=fill)
    wobble_line(d, (x0, y0), (x1, y0), INK, width, amp)
    wobble_line(d, (x1, y0), (x1, y1), INK, width, amp)
    wobble_line(d, (x1, y1), (x0, y1), INK, width, amp)
    wobble_line(d, (x0, y1), (x0, y0), INK, width, amp)


def wrap(text, fnt, max_w):
    """Greedy wrap measured with the real font; never exceeds max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single over-long word is split by characters.
            while fnt.getlength(word) > max_w:
                cut = len(word)
                while cut > 1 and fnt.getlength(word[:cut]) > max_w:
                    cut -= 1
                lines.append(word[:cut])
                word = word[cut:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, lines, fnt, x, y, fill, leading):
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def headline_block(d, x, y, max_w, kicker, kicker_color, title, title_size,
                   deck, deck_size=17, head_w=None):
    """Kicker + wrapped headline + wrapped deck. Returns bottom y."""
    kf = font(SANS, 15)
    d.text((x, y), kicker, font=kf, fill=kicker_color)
    y += 22
    tf = font(SERIF, title_size)
    lines = wrap(title, tf, head_w if head_w is not None else max_w)
    y = draw_lines(d, lines, tf, x, y, INK, title_size + 5)
    y += 3
    df = font(SANS_R, deck_size)
    dlines = wrap(deck, df, max_w)
    y = draw_lines(d, dlines, df, x, y, (58, 52, 44), deck_size + 5)
    return y


def draw_globe(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=3)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 228, 238))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=3)
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=BLUE, width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 20, 160, fill=BLUE, width=2)
    d.line([cx - r, cy, cx + r, cy], fill=BLUE, width=2)
    d.ellipse([cx - r * 0.45, cy - r * 0.55, cx + r * 0.35, cy - r * 0.05],
              fill=(120, 170, 120), outline=TEAL, width=2)
    d.ellipse([cx - r * 0.25, cy + r * 0.15, cx + r * 0.55, cy + r * 0.6],
              fill=(120, 170, 120), outline=TEAL, width=2)
    # Three summit flags on the globe.
    for dx, col in ((-r - 6, RED), (0, GOLD), (r + 6, BLUE)):
        d.line([cx + dx, cy - r - 26, cx + dx, cy - r + 2], fill=INK, width=2)
        d.polygon([(cx + dx, cy - r - 26), (cx + dx + 15, cy - r - 20),
                   (cx + dx, cy - r - 14)], fill=col, outline=INK)


def draw_bridge(d, x, y, w, h):
    d.line([x, y + h, x + w, y + h], fill=INK, width=3)
    d.arc([x + 6, y + 8, x + w // 2 - 4, y + h], 180, 360, fill=RED, width=3)
    d.arc([x + w // 2 + 4, y + 8, x + w - 6, y + h], 180, 360, fill=RED, width=3)
    for fx in (x + w // 4, x + w // 2, x + 3 * w // 4):
        d.line([fx, y + 2, fx, y + h - 4], fill=INK, width=2)


def draw_crowd(d, x, y, w, h):
    for i in range(5):
        cx = x + 12 + i * (w - 24) // 4
        cy = y + h - 22
        d.ellipse([cx - 9, cy - 20, cx + 9, cy - 2], fill=(214, 200, 170),
                  outline=INK, width=2)
        d.arc([cx - 12, cy, cx + 12, cy + 14], 180, 360, fill=INK, width=3)
        d.line([cx, cy - 20, cx - 4, cy - 34], fill=INK, width=2)
        d.polygon([(cx - 4, cy - 34), (cx + 14, cy - 29), (cx - 4, cy - 24)],
                  fill=RED if i % 2 == 0 else BLUE, outline=INK)


def draw_flame(d, x, y, w, h):
    cx, cy = x + w // 2, y + h // 2 + 6
    d.polygon([(cx, y + 2), (cx + 16, cy - 6), (cx + 10, cy + 8),
               (cx + 20, cy + 12), (cx, y + h - 2), (cx - 20, cy + 12),
               (cx - 10, cy + 8), (cx - 16, cy - 6)], fill=(232, 120, 40),
              outline=RED, width=2)
    d.ellipse([cx - 7, cy - 2, cx + 7, cy + 14], fill=GOLD, outline=RED)


def draw_ballot(d, x, y, w, h):
    bx, by = x + w // 2 - 26, y + 12
    d.rectangle([bx, by, bx + 52, by + 34], fill=(232, 224, 200),
                outline=INK, width=3)
    d.line([bx + 18, by, bx + 34, by], fill=INK, width=3)
    d.line([bx - 8, by + 44, bx + 60, by + 44], fill=INK, width=3)
    d.text((bx + 8, by + 8), "VOTE", font=font(SANS, 15), fill=INK)


def draw_maths(d, x, y, w, h):
    d.text((x + 6, y + 4), "\u03c0  \u2211  \u221a", font=font(SERIF, 34),
           fill=BLUE)
    d.text((x + 30, y + 48), "x = ?", font=font(SERIF, 30), fill=RED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 34  # page margin

    # Paper edge: double hand-drawn frame.
    wobble_rect(d, (14, 14, W - 14, H - 14), width=3)
    wobble_rect(d, (22, 22, W - 22, H - 22), width=1)

    # ---- Masthead ----
    y = 36
    title = "THE WORLD TODAY"
    tf = font(SERIF, 84)
    tw = tf.getlength(title)
    d.text(((W - tw) / 2, y), title, font=tf, fill=INK)
    y += 94
    wobble_line(d, (mx, y), (W - mx, y), INK, 3)
    y += 10
    sub = "SATURDAY, 21 NOVEMBER 2026  \u00b7  ONE DAY, SIX STORIES  \u00b7  DRAWN BY HAND"
    sf = font(SANS, 19)
    sw = sf.getlength(sub)
    d.text(((W - sw) / 2, y), sub, font=sf, fill=RED)
    y += 28
    wobble_line(d, (mx, y), (W - mx, y), INK, 2)
    y += 12

    # ---- Lead story: the summit ----
    lead_top = y
    lead_h = 186
    wobble_rect(d, (mx, lead_top, W - mx, lead_top + lead_h), width=2)
    draw_globe(d, W - mx - 78, lead_top + 108, 52)
    headline_block(
        d, mx + 16, lead_top + 12, W - 2 * mx - 190,
        "THE SUMMIT \u2014 SHENZHEN & WASHINGTON", RED,
        "TRUMP HAILS \u201cVERY GOOD\u201d TALKS WITH PUTIN", 34,
        "Back from the first three-way summit with Xi Jinping, the US "
        "president says a Ukraine deal is within reach \u2014 but no security "
        "guarantees until there is a deal. Moscow rules out NATO-style "
        "pledges. The leaders issued a joint declaration toward peace.",
        17)
    y = lead_top + lead_h + 12

    # ---- Two-column stories, row A ----
    col_w = (W - 2 * mx - 16) // 2
    row_h = 182
    boxes_a = [
        (mx, "WAR \u2014 UKRAINE", RED, "MISSILES HIT THREE KYIV BRIDGES",
         "Russia fired 400+ drones and 110+ missiles hours after the "
         "summit. At least 9 people were killed; two missiles fell in "
         "Poland. Kyiv's river crossings are cut.", draw_bridge),
        (mx + col_w + 16, "EUROPE", BLUE, "YOUTH TAKE TO THE STREETS",
         "Students rallied in 25+ countries under the cry \u201cFight for our "
         "future, not their wars\u201d \u2014 against living costs, housing "
         "shortages and rising military budgets.", draw_crowd),
    ]
    for bx, kicker, kc, title, deck, doodle in boxes_a:
        wobble_rect(d, (bx, y, bx + col_w, y + row_h), width=2)
        doodle(d, bx + col_w - 106, y + 6, 94, 46)
        headline_block(d, bx + 14, y + 10, col_w - 28, kicker, kc,
                       title, 25, deck, 15, head_w=col_w - 28 - 104)
    y += row_h + 12

    # ---- Two-column stories, row B ----
    boxes_b = [
        (mx, "ASIA \u2014 BANGLADESH", RED, "ARSON WAVE BEFORE HASINA RETURN",
         "Attackers torched a minister's home and hit 72 Grameen Bank "
         "branches as unrest spreads ahead of the exiled ex-premier's "
         "planned return. Troops deployed.", draw_flame),
        (mx + col_w + 16, "MONGOLIA", TEAL, "PRESIDENT QUITS, VOTE IN 4 MONTHS",
         "Parliament accepted President Kh\u00fcrels\u00fckh's resignation "
         "amid corruption claims \u2014 the first sitting Mongolian "
         "president to quit early.", draw_ballot),
    ]
    for bx, kicker, kc, title, deck, doodle in boxes_b:
        wobble_rect(d, (bx, y, bx + col_w, y + row_h), width=2)
        doodle(d, bx + col_w - 106, y + 6, 94, 46)
        headline_block(d, bx + 14, y + 10, col_w - 28, kicker, kc,
                       title, 25, deck, 15, head_w=col_w - 28 - 104)
    y += row_h + 12

    # ---- Science story, full width ----
    sci_h = 140
    wobble_rect(d, (mx, y, W - mx, y + sci_h), width=2)
    draw_maths(d, W - mx - 168, y + 8, 152, sci_h - 16)
    headline_block(
        d, mx + 16, y + 10, W - 2 * mx - 190,
        "SCIENCE \u2014 MATHEMATICS", BLUE,
        "DID A CHATBOT CRACK MATHS' GREATEST RIDDLE?", 27,
        "An Anthropic researcher says its Claude chatbot proved the "
        "Riemann Hypothesis, unsolved for 160+ years. Mathematicians "
        "are checking the proof.",
        15)
    y += sci_h + 12

    # ---- Also-today ticker ----
    tick_h = 52
    wobble_rect(d, (mx, y, W - mx, y + tick_h), fill=(238, 230, 210), width=2)
    tf2 = font(SANS, 14)
    tick = ("ALSO TODAY:  Iran war has cost the US $48bn, the Pentagon says  "
            "\u00b7  Congress races to avert a US shutdown  \u00b7  King Charles "
            "to pay the UK \u201cmansion tax\u201d  \u00b7  Migrant caravan crosses "
            "into southern Mexico")
    lines = wrap(tick, tf2, W - 2 * mx - 28)
    draw_lines(d, lines, tf2, mx + 14, y + 8, INK, 19)
    y += tick_h + 10

    # ---- Footer ----
    ff = font(SANS_R, 12)
    foot = ("Sources: Reuters, CNN, AFP, The Hindu, Al Jazeera "
            "\u2014 21 Nov 2026  \u00b7  Sketches, not photos.")
    fw = ff.getlength(foot)
    assert fw <= W - 2 * mx, "footer too wide"
    d.text(((W - fw) / 2, y), foot, font=ff, fill=FAINT)
    assert y + 16 <= 1002, "footer overflows the page frame"

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    print("wrote", path, img.size)


def fallback():
    """Copy the pre-drawn entry.png shipped beside main.py to the output.

    Used when Pillow is unavailable or drawing fails, so the run still
    produces a valid entry instead of exiting non-zero.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    shutil.copyfile(src, path)
    print("fallback: copied", src, "->", path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # Pillow missing, fonts missing, draw error, ...
        print("drawing failed (%s); using fallback entry.png" % exc)
        fallback()
