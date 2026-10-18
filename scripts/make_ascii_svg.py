#!/usr/bin/env python3
"""
Convert source-photo.jpg into a monochrome animated ASCII SVG portrait
that types in row-by-row like a terminal scan and freezes.
"""
import html
import os
import sys
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "sandeep-ascii.svg")

COLS = 75
RAMP = " .`:-=+*cs#%@"

# Visual canvas settings
W = 420
H = 500
PAD = 16
TITLEBAR_H = 34

ART_W = W - PAD * 2
CELL_W = ART_W / COLS
CELL_H = CELL_W * 1.8
ROWS = int((H - TITLEBAR_H - PAD * 2) / CELL_H)

BG = "#0d1117"
FRAME = "#30363d"
INK = "#e6edf3"      # Clean crisp terminal text
DIM = "#484f58"
MUTED = "#7d8590"

TOTAL_DUR = 3.5      # Total typing duration in seconds
ROW_DUR = TOTAL_DUR / ROWS


def generate_ascii_svg():
    im = Image.open(SRC).convert("L")  # Convert to grayscale
    # Auto contrast and brightness boost for sharp ASCII rendering
    im = ImageOps.autocontrast(im, cutoff=2)
    im = ImageEnhance.Contrast(im).enhance(1.25)
    im = ImageEnhance.Sharpness(im).enhance(1.4)
    im = im.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    px = im.load()

    lines = []
    for y in range(ROWS):
        row_chars = []
        for x in range(COLS):
            lum = px[x, y] / 255.0
            # Higher lum = brighter -> space or sparse chars
            idx = int((1.0 - lum) * (len(RAMP) - 1))
            idx = max(0, min(len(RAMP) - 1, idx))
            row_chars.append(RAMP[idx])
        lines.append("".join(row_chars))

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">')

    # Styling and SMIL
    svg.append('<defs>')
    for y in range(ROWS):
        start_t = round(y * (ROW_DUR * 0.9), 3)
        svg.append(
            f'<clipPath id="cp_{y}">'
            f'<rect x="{PAD}" y="{TITLEBAR_H + PAD + y * CELL_H}" width="0" height="{CELL_H + 2}">'
            f'<animate attributeName="width" from="0" to="{ART_W}" dur="{round(ROW_DUR, 3)}s" begin="{start_t}s" fill="freeze" calcMode="linear" />'
            f'</rect>'
            f'</clipPath>'
        )
    svg.append('</defs>')

    # Terminal background & frame
    svg.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{BG}" stroke="{FRAME}" stroke-width="1" />')

    # Title bar
    svg.append('<circle cx="16" cy="17" r="4.5" fill="#ff5f56" />')
    svg.append('<circle cx="29" cy="17" r="4.5" fill="#ffbd2e" />')
    svg.append('<circle cx="42" cy="17" r="4.5" fill="#27c93f" />')
    svg.append(f'<text x="60" y="21" fill="{MUTED}" font-size="11px" font-weight="500">sandeep@profile: ~ /whoami.ascii</text>')
    svg.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-width="1" />')

    # Draw ASCII rows with clipPath animation
    font_size = round(CELL_W * 1.5, 2)
    for y, text_line in enumerate(lines):
        y_pos = round(TITLEBAR_H + PAD + y * CELL_H + CELL_H * 0.75, 2)
        escaped_line = html.escape(text_line)
        svg.append(
            f'<text x="{PAD}" y="{y_pos}" fill="{INK}" font-size="{font_size}px" xml:space="preserve" '
            f'clip-path="url(#cp_{y})" letter-spacing="0.5px">{escaped_line}</text>'
        )

    svg.append('</svg>')
    return "".join(svg)


def main():
    if not os.path.exists(SRC):
        print(f"Source photo not found: {SRC}", file=sys.stderr)
        sys.exit(1)
    svg = generate_ascii_svg()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUT_PATH}")


if __name__ == "__main__":
    main()
