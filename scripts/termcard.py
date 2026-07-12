"""
termcard.py -- shared helpers to render terminal-window SVG cards that match the
ASCII portrait / neofetch / heatmap aesthetic (same BG gradient, frame, traffic
dots, monospace title). Each card is a self-hosted SVG so nothing 404s on GitHub.

Palette + chrome are identical across every card so the whole README reads as one
cohesive terminal desktop.
"""
import html
import os

# ---- shared palette (matches make_ascii_svg.py / make_info_card.py) --------
BG      = "#0d1117"
BG2     = "#111722"
FRAME   = "#30363d"
MUTED   = "#7d8590"
INK     = "#c9d1d9"
KEY     = "#ffa657"   # orange keys
SECTION = "#58a6ff"   # blue section headers / accents
GREEN   = "#3fb950"
CYAN    = "#22d3ee"
GOLD    = "#f2cc60"
RED     = "#ff7b72"

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
TITLEBAR_H = 30
PAD = 20

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
STATIC = bool(os.environ.get("STATIC"))


def esc(s):
    return html.escape(str(s))


def chrome(w, h, prompt):
    """Return the opening SVG + window chrome (title bar, dots, prompt text)."""
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}">',
        '<defs>'
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        f'</linearGradient></defs>',
        f'<rect width="{w}" height="{h}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="none" '
        f'stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{w}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
    p.append(f'<text x="{w/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">{esc(prompt)}</text>')
    return p


def rise(inner, i, base=0.12, step=0.05):
    """fade + small upward slide, staggered by row index; freezes visible."""
    if STATIC:
        return f"<g>{inner}</g>"
    d = base + i * step
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{d:.2f}s" '
            f'dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" '
            f'to="0 0" begin="{d:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" '
            f'keySplines="0.2 0.8 0.2 1"/></g>')


def wrap(text, width):
    """naive monospace word-wrap to `width` characters."""
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        if len(cur) + len(wd) + (1 if cur else 0) <= width:
            cur = f"{cur} {wd}".strip()
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def save(parts, name, w, h, extra=""):
    parts.append("</svg>")
    svg = "".join(parts)
    out = os.path.join(OUTDIR, name)
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {name} ({len(svg)} bytes) {w}x{h}{extra}")
    return out
