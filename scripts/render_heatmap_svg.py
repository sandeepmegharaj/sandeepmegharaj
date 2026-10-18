#!/usr/bin/env python3
"""
Render data/contributions.json as a GitHub contribution heatmap SVG:
A grid of 53 weeks x 7 days with terminal title bar, diagonal cascade animation,
stats footer, and Data Engineering aesthetic.
"""
import datetime
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

# Color palette: Dark slate terminal with vivid emerald/cyan greens
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 20
LEFT_LABEL_W = 32
TOP_LABEL_H = 22
TITLEBAR_H = 34
STATS_H = 50

BG = "#0d1117"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
CYAN = "#38bdf8"
GREEN = "#39d353"
GOLD = "#fbbf24"


def level_for(count):
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 10:
        return 3
    if count <= 20:
        return 4
    return 5


def build_grid(days):
    if not days:
        return []
    first = datetime.date.fromisoformat(days[0]["date"])
    lead_pad = (first.weekday() + 1) % 7  # Sunday=0
    grid = []
    col = [None] * lead_pad
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        while len(col) < weekday:
            col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"])))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        while len(col) < 7:
            col.append(None)
        grid.append(col)
    return grid


def render(data):
    days = data.get("days", [])
    grid = build_grid(days)
    n_cols = len(grid)
    art_w = n_cols * STEP
    art_h = 7 * STEP

    month_labels = []
    seen_months = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                month_labels.append((ci, date.strftime("%b")))
            break

    canvas_w = 860
    # adjust horizontal padding so grid is centered or nicely spaced
    grid_x0 = PAD + LEFT_LABEL_W
    canvas_h = TITLEBAR_H + TOP_LABEL_H + art_h + STATS_H + PAD

    # Animated keyframes (diagonal cascade reveal)
    css = """
      .term-bg { fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 8px; }
      .title-text { fill: #7d8590; font-size: 12px; font-weight: 500; }
      .lbl { fill: #7d8590; font-size: 10px; }
      .cell {
        transform-box: fill-box;
        transform-origin: center;
        animation: revealCell 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
      }
      @keyframes revealCell {
        0% { opacity: 0; transform: scale(0.3); }
        100% { opacity: 1; transform: scale(1); }
      }
    """

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w} {canvas_h}" width="{canvas_w}" height="{canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">')
    svg.append(f'<style>{css}</style>')

    # Window container
    svg.append(f'<rect x="0.5" y="0.5" width="{canvas_w - 1}" height="{canvas_h - 1}" class="term-bg" />')

    # Title bar
    svg.append(f'<circle cx="16" cy="17" r="4.5" fill="#ff5f56" />')
    svg.append(f'<circle cx="29" cy="17" r="4.5" fill="#ffbd2e" />')
    svg.append(f'<circle cx="42" cy="17" r="4.5" fill="#27c93f" />')
    svg.append(f'<text x="60" y="21" class="title-text">sandeep@data-platform: ~ /contributions.sh</text>')
    svg.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" stroke="#30363d" stroke-width="1" />')

    # Month labels
    grid_y0 = TITLEBAR_H + TOP_LABEL_H
    for ci, m_name in month_labels:
        mx = grid_x0 + ci * STEP
        svg.append(f'<text x="{mx}" y="{TITLEBAR_H + 15}" class="lbl">{m_name}</text>')

    # Day of week labels (Mon, Wed, Fri)
    day_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for r_idx, day_name in day_labels:
        dy = grid_y0 + r_idx * STEP + 9
        svg.append(f'<text x="{PAD}" y="{dy}" class="lbl">{day_name}</text>')

    # Cells
    for ci, column in enumerate(grid):
        for ri, cell in enumerate(column):
            if cell is None:
                continue
            date_str, count, level = cell
            cx = grid_x0 + ci * STEP
            cy = grid_y0 + ri * STEP
            color = PALETTE[level]
            # delay for diagonal cascade
            delay = round(0.05 + ci * 0.015 + ri * 0.035, 3)
            svg.append(
                f'<rect x="{cx}" y="{cy}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}" '
                f'class="cell" style="animation-delay: {delay}s;" />'
            )

    # Footer stats
    footer_y = grid_y0 + art_h + 30
    total = data.get("total_contributions", 0)
    cur_streak = data.get("current_streak", {}).get("length", 0)
    long_streak = data.get("longest_streak", {}).get("length", 0)

    stats_str = f'<tspan fill="{TEXT}" font-weight="600">{total} contributions</tspan><tspan fill="{MUTED}"> in the last year</tspan>'
    streak_str = f'<tspan fill="{MUTED}"> •  Current Streak: </tspan><tspan fill="{GREEN}" font-weight="600">{cur_streak} days</tspan>'
    max_streak_str = f'<tspan fill="{MUTED}"> •  Longest: </tspan><tspan fill="{CYAN}" font-weight="600">{long_streak} days</tspan>'

    svg.append(f'<text x="{grid_x0}" y="{footer_y}" font-size="11px">{stats_str}{streak_str}{max_streak_str}</text>')

    # Legend (Less -> More)
    legend_right = grid_x0 + art_w
    legend_x = legend_right - (len(PALETTE) * (CELL + 2) + 65)
    svg.append(f'<text x="{legend_x}" y="{footer_y}" class="lbl">Less</text>')
    for li, col in enumerate(PALETTE):
        lx = legend_x + 30 + li * (CELL + 2)
        svg.append(f'<rect x="{lx}" y="{footer_y - 9}" width="{CELL}" height="{CELL}" rx="2" fill="{col}" />')
    svg.append(f'<text x="{legend_x + 30 + len(PALETTE) * (CELL + 2) + 6}" y="{footer_y}" class="lbl">More</text>')

    svg.append('</svg>')
    return "".join(svg)


def main():
    if not os.path.exists(IN_PATH):
        print(f"File not found: {IN_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(IN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    svg_content = render(data)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {OUT_PATH}")


if __name__ == "__main__":
    main()
