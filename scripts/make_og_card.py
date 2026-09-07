#!/usr/bin/env python
"""Social link-preview card for the project page (static/images/og_card.png).

The card is the og:image / twitter:image that messaging apps and social sites show next to
the site link. It restates the teaser video's end card in the site's own look: Google Sans
and the poster's Google palette (blue #4285F4, red #EA4335, green #34A853, ink #202124).

Fonts: Google Sans 400/500/700 TrueType from the Google Fonts CSS API v1
(`curl -A curl "https://fonts.googleapis.com/css?family=Google+Sans:400,500,700"` lists the
.ttf URLs), cached in FONT_DIR. Set OG_FONT_DIR to point elsewhere.

Numbers: the paper's Table 1 headline pair per benchmark (baseline Gemini 3.1 Pro -> SPLIT),
the same six numbers as the teaser video's end card and the site's benchmark chart.

Output: 1200 x 630 (the Open Graph aspect), rendered at 2x and downsampled, PNG under 300 KB
so WhatsApp and Twitter accept it as a large preview.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "static", "images", "og_card.png")
FONT_DIR = os.environ.get("OG_FONT_DIR", "/data2/jjyeung/tools/fonts/google_sans")

BLUE, RED, GREEN = "#4285F4", "#EA4335", "#34A853"
INK, GRAY, LIGHT = "#202124", "#5F6368", "#9AA0A6"
WHITE = "#FFFFFF"

W, H, S = 1200, 630, 2                      # og size, supersampling factor
TITLE = ["Perception, Not Reasoning,", "Limits Video Spatial Understanding"]
SUBTITLE = "SPLIT: Separating Perception from LLM Inference with Tools"
BENCH = [("VSIBench", "60.4", "66.9"), ("VSTIBench", "57.7", "78.3"), ("ReVSI", "63.8", "71.5")]
LEGEND = [(RED, "Baseline (Gemini 3.1 Pro)"), (GREEN, "SPLIT (Ours)")]
CLAIM = "up to 1.9x less error than the same VLM without tools"


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"GoogleSans-{weight}.ttf"), int(size * S))


def text_w(draw, s, f):
    l, _, r, _ = draw.textbbox((0, 0), s, font=f)
    return r - l


def arrow(draw, x0, x1, y, color, lw):
    """Right-pointing arrow from x0 to x1 (page units), centred on y."""
    x0, x1, y, lw = x0 * S, x1 * S, y * S, lw * S
    head = 3.2 * lw
    draw.line([(x0, y), (x1 - head * 0.6, y)], fill=color, width=int(lw))
    draw.polygon([(x1, y), (x1 - head, y - head * 0.62), (x1 - head, y + head * 0.62)], fill=color)


def main():
    im = Image.new("RGB", (W * S, H * S), WHITE)
    d = ImageDraw.Draw(im)

    # Poster header colours as a thin band across the top: blue, red, green.
    band = 8 * S
    for i, c in enumerate((BLUE, RED, GREEN)):
        d.rectangle([i * W * S / 3, 0, (i + 1) * W * S / 3, band], fill=c)

    cx = W / 2
    f_title, f_sub = font(700, 52), font(500, 25)
    d.text((cx * S, 118 * S), TITLE[0], font=f_title, fill=INK, anchor="ms")
    d.text((cx * S, 178 * S), TITLE[1], font=f_title, fill=INK, anchor="ms")
    d.text((cx * S, 232 * S), SUBTITLE, font=f_sub, fill=GRAY, anchor="ms")

    # Three benchmark columns: name, then "baseline -> SPLIT" in red -> green.
    f_name, f_num = font(500, 23), font(700, 58)
    gap = 38                                   # half-width reserved for the arrow
    for k, (name, base, ours) in enumerate(BENCH):
        col = W * (2 * k + 1) / 6
        d.text((col * S, 322 * S), name, font=f_name, fill=INK, anchor="ms")
        d.text(((col - gap) * S, 396 * S), base, font=f_num, fill=RED, anchor="rs")
        d.text(((col + gap) * S, 396 * S), ours, font=f_num, fill=GREEN, anchor="ls")
        arrow(d, col - gap + 12, col + gap - 12, 376, LIGHT, 4)

    # One legend row under the columns.
    f_leg = font(400, 21)
    dot, pad, sep = 8, 10, 44
    widths = [dot * 2 + pad + text_w(d, t, f_leg) / S for _, t in LEGEND]
    x = cx - (sum(widths) + sep * (len(LEGEND) - 1)) / 2
    for (c, t), w in zip(LEGEND, widths):
        cy = 462
        d.ellipse([(x) * S, (cy - dot) * S, (x + 2 * dot) * S, (cy + dot) * S], fill=c)
        d.text(((x + 2 * dot + pad) * S, (cy + 7.5) * S), t, font=f_leg, fill=GRAY, anchor="ls")
        x += w + sep

    f_claim = font(500, 26)
    d.text((cx * S, 556 * S), CLAIM, font=f_claim, fill=INK, anchor="ms")

    im = im.resize((W, H), Image.LANCZOS)
    im.save(OUT, optimize=True)
    kb = os.path.getsize(OUT) / 1024
    print(f"wrote {os.path.abspath(OUT)}  {W}x{H}  {kb:.0f} KB")
    if kb > 300:
        raise SystemExit("og image over 300 KB; WhatsApp may skip the large preview")


if __name__ == "__main__":
    main()
