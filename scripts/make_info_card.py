#!/usr/bin/env python3
"""
Generate an animated neofetch-style terminal info card SVG (420 x 500)
highlighting Data Engineering expertise (Databricks, Microsoft Fabric, Delta Lake, PySpark)
and core projects (Apex F1, Sterling Financial Analytics, Deep Agent).
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")

W = 420
H = 500
TITLEBAR_H = 34
PAD = 20

BG = "#0d1117"
FRAME = "#30363d"
INK = "#e6edf3"
MUTED = "#7d8590"

# Tech accents
CYAN = "#38bdf8"
GREEN = "#39d353"
GOLD = "#fbbf24"
PURPLE = "#c084fc"
ORANGE = "#fb923c"
BLUE = "#60a5fa"

ENTRIES = [
    ("OS", "Lakehouse Architecture & Azure Cloud", MUTED),
    ("Role", "Data Engineer & AI Systems Architect", GREEN),
    ("Location", "Hyderabad, India", INK),
    ("Cloud / Lakehouse", "Microsoft Fabric  •  Databricks", CYAN),
    ("Storage Layer", "Delta Lake  •  Parquet  •  DuckDB", GOLD),
    ("Pipeline / ETL", "PySpark  •  Apache Airflow  •  SQL", ORANGE),
    ("AI & Agentic", "Azure AI Foundry  •  LangGraph  •  RAG", PURPLE),
    ("", "", ""),  # blank line separator
    ("Featured 01", "Apex F1 (Databricks + Delta Lake + RAG)", CYAN),
    ("Featured 02", "Sterling Analytics (Fabric + Azure AI)", GREEN),
    ("Featured 03", "Deep-Agent Data Lab (Streamlit + LLM)", BLUE),
]


def generate_info_card_svg():
    css = """
      .term-bg { fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 8px; }
      .title-text { fill: #7d8590; font-size: 11px; font-weight: 500; }
      .row {
        transform-box: fill-box;
        transform-origin: left;
        animation: slideIn 0.35s ease-out both;
      }
      .cursor {
        animation: blink 1s step-start infinite;
      }
      @keyframes slideIn {
        0% { opacity: 0; transform: translateY(6px); }
        100% { opacity: 1; transform: translateY(0); }
      }
      @keyframes blink {
        50% { opacity: 0; }
      }
    """

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">')
    svg.append(f'<style>{css}</style>')

    # Window background & border
    svg.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" class="term-bg" />')

    # Title bar
    svg.append('<circle cx="16" cy="17" r="4.5" fill="#ff5f56" />')
    svg.append('<circle cx="29" cy="17" r="4.5" fill="#ffbd2e" />')
    svg.append('<circle cx="42" cy="17" r="4.5" fill="#27c93f" />')
    svg.append(f'<text x="60" y="21" class="title-text">sandeep@data-platform: ~ /neofetch</text>')
    svg.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-width="1" />')

    # Header section
    content_y = TITLEBAR_H + 30
    svg.append(f'<g class="row" style="animation-delay: 0.1s;">')
    svg.append(f'<text x="{PAD}" y="{content_y}" font-size="14px" font-weight="700">')
    svg.append(f'<tspan fill="{CYAN}">sandeep</tspan><tspan fill="{MUTED}">@</tspan><tspan fill="{GREEN}">data-platform</tspan>')
    svg.append(f'</text>')
    svg.append(f'<text x="{PAD}" y="{content_y + 14}" fill="{FRAME}" font-size="12px">-----------------------------------------</text>')
    svg.append('</g>')

    # Key / value rows
    row_y = content_y + 36
    line_h = 24
    for i, (key, val, val_color) in enumerate(ENTRIES):
        delay = round(0.2 + i * 0.08, 2)
        if not key:  # spacer
            row_y += 8
            continue

        svg.append(f'<g class="row" style="animation-delay: {delay}s;">')
        escaped_key = html.escape(key)
        escaped_val = html.escape(val)
        svg.append(
            f'<text x="{PAD}" y="{row_y}" font-size="11px">'
            f'<tspan fill="{CYAN}" font-weight="600">{escaped_key:17}</tspan>'
            f'<tspan fill="{val_color}">{escaped_val}</tspan>'
            f'</text>'
        )
        svg.append('</g>')
        row_y += line_h

    # Color palette blocks (classic neofetch badge blocks)
    palette_colors = ["#0d1117", "#ff5f56", "#27c93f", "#ffbd2e", "#38bdf8", "#c084fc", "#e6edf3"]
    palette_y = H - 36
    svg.append(f'<g class="row" style="animation-delay: 1.3s;">')
    for ci, col in enumerate(palette_colors):
        px = PAD + ci * 24
        svg.append(f'<rect x="{px}" y="{palette_y}" width="18" height="12" rx="2" fill="{col}" stroke="{FRAME}" stroke-width="1" />')
    svg.append(f'<text x="{PAD + len(palette_colors) * 24 + 10}" y="{palette_y + 10}" fill="{GREEN}" font-size="12px" class="cursor">_</text>')
    svg.append('</g>')

    svg.append('</svg>')
    return "".join(svg)


def main():
    svg = generate_info_card_svg()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUT_PATH}")


if __name__ == "__main__":
    main()
