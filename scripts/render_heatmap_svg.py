#!/usr/bin/env python3
"""
Render data/contributions.json (produced by fetch_contributions.py) as a proper
GitHub-style contribution heatmap SVG: a grid of rounded, colored BOXES in the
classic 53-week x 7-day calendar, revealed once with a diagonal line-after-line
slide-down (CSS keyframes, plays on load then freezes -- no looping "glow"), a
Less->More legend, and a real stats footer.

Run by .github/workflows/update-profile-art.yml after fetch_contributions.py.
"""
import datetime
import json
import os

HERE = os.path.dirname(__file__)
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

# GitHub-ish green ramp: empty -> brightest. Level 5 is a brighter neon top end.
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 22
LEFT_LABEL_W = 30
TOP_LABEL_H = 20
TITLEBAR_H = 30

BG = "#0a0e14"
BG2 = "#0d1420"
FRAME = "#1f6feb"
MUTED = "#7d8590"
TEXT = "#e6edf3"
ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"

# reveal timing (one-shot)
COL_T = 0.018   # per-column delay contribution (left -> right sweep)
ROW_T = 0.045   # per-row delay contribution (top -> bottom cascade)
CELL_DUR = 0.42


def level_for(count):
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5


def build_grid(days):
    first = datetime.date.fromisoformat(days[0]["date"])
    lead_pad = (first.weekday() + 1) % 7  # sunday=0
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
    days = data["days"]
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

    canvas_w = PAD + LEFT_LABEL_W + art_w + PAD
    stats_h = 88
    canvas_h = TITLEBAR_H + TOP_LABEL_H + art_h + stats_h + PAD

    css = f"""
@keyframes cell {{
  0%   {{ opacity: 0; transform: translateY(-6px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}
.c {{ opacity: 0; animation: cell {CELL_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both; }}
""".strip()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<style>{css}</style>',
        '<defs>'
        f'<linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
        '</defs>',
        f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#hbg)"/>',
        f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" '
        f'fill="none" stroke="{FRAME}" stroke-width="1" stroke-opacity="0.55"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.35"/>',
    ]
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{canvas_w/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">gabriel@github: ~/contributions --graph</text>')

    grid_top = TITLEBAR_H + TOP_LABEL_H
    grid_left = PAD + LEFT_LABEL_W

    for ci, label in month_labels:
        x = grid_left + ci * STEP
        parts.append(f'<text x="{x}" y="{TITLEBAR_H + 14}" fill="{MUTED}" font-size="10">{label}</text>')

    for wi, wname in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = grid_top + wi * STEP + CELL * 0.78
        parts.append(f'<text x="{PAD}" y="{y:.1f}" fill="{MUTED}" font-size="9">{wname}</text>')

    # snake path: seeded RANDOM WALK over the grid (seed = data end date, so the
    # route changes every refresh). The whole animation LOOPS: cells the snake
    # eats are restored just before each new lap.
    import random
    SNAKE_STEP = 0.055          # seconds the head spends per cell
    SNAKE_LEN = 5               # body segments trailing the head
    WALK_STEPS = 420            # steps per lap
    rng = random.Random(data["range"]["end"])

    def neighbors(c, r):
        out = []
        if c > 0: out.append((c - 1, r))
        if c < n_cols - 1: out.append((c + 1, r))
        if r > 0: out.append((c, r - 1))
        if r < 6: out.append((c, r + 1))
        return out

    pos = (rng.randrange(n_cols), rng.randrange(7))
    prev = None
    visited = set([pos])
    order = []                  # (ci, ri, gx, gy) per step
    for _ in range(WALK_STEPS):
        ci, ri = pos
        order.append((ci, ri, grid_left + ci * STEP, grid_top + ri * STEP))
        opts = neighbors(ci, ri)
        fresh = [p for p in opts if p not in visited]
        no_back = [p for p in opts if p != prev]
        pool = fresh if fresh and rng.random() < 0.8 else (no_back or opts)
        prev = pos
        pos = rng.choice(pool)
        visited.add(pos)

    total_steps = len(order)
    lap = total_steps * SNAKE_STEP
    RESTORE_PAUSE = 0.8
    total_time = lap + RESTORE_PAUSE     # full loop duration

    first_visit = {}            # (ci,ri) -> first time the head arrives
    for step, (ci, ri, gx, gy) in enumerate(order):
        first_visit.setdefault((ci, ri), step * SNAKE_STEP)

    # the boxes -- rounded rects. A cell the snake reaches turns empty at that
    # moment and is restored at the end of the lap; loops forever.
    for ci, column in enumerate(grid):
        gx = grid_left + ci * STEP
        for ri, cell in enumerate(column):
            if cell is None:
                continue
            date_s, count, lvl = cell
            gy = grid_top + ri * STEP
            plural = "s" if count != 1 else ""
            eaten = ""
            t = first_visit.get((ci, ri))
            if lvl > 0 and t is not None:
                kt_eat = max(0.0001, t / total_time)
                kt_back = (lap + RESTORE_PAUSE * 0.5) / total_time
                eaten = (f'<animate attributeName="fill" '
                         f'values="{PALETTE[lvl]};{PALETTE[0]};{PALETTE[0]};{PALETTE[lvl]}" '
                         f'keyTimes="0;{kt_eat:.4f};{kt_back:.4f};1" calcMode="discrete" '
                         f'dur="{total_time:.2f}s" repeatCount="indefinite"/>')
            parts.append(
                f'<rect x="{gx}" y="{gy}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{PALETTE[lvl]}">'
                f'<title>{date_s}: {count} contribution{plural}</title>{eaten}</rect>'
            )

    # ---- the snake itself: head + trailing body, looping forever --------------
    def values_for(offset):
        """'x,y; ...' translate values for a segment `offset` cells behind head."""
        pts = []
        for step in range(total_steps):
            idx = max(0, step - offset)
            _, _, gx, gy = order[idx]
            pts.append(f"{gx + CELL/2:.1f},{gy + CELL/2:.1f}")
        pts.append(pts[-1])      # hold position during the restore pause
        return ";".join(pts)

    kts = [i * SNAKE_STEP / total_time for i in range(total_steps)] + [1.0]
    key_times = ";".join(f"{k:.4f}" for k in kts)
    snake_cols = ["#39d353", "#2eaa47", "#22803a", "#186a2f", "#125425"]
    for seg in range(SNAKE_LEN, -1, -1):     # tail first, head last (drawn on top)
        vals = values_for(seg)
        if seg == 0:
            col = "#e6ffec"; r = CELL/2 + 1     # bright head
        else:
            col = snake_cols[min(seg - 1, len(snake_cols) - 1)]
            r = max(2.5, CELL/2 - (seg - 1) * 0.9)
        parts.append(
            f'<rect x="{-r:.1f}" y="{-r:.1f}" width="{2*r:.1f}" height="{2*r:.1f}" '
            f'rx="{r*0.5:.1f}" fill="{col}">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="{vals}" keyTimes="{key_times}" dur="{total_time:.2f}s" '
            f'calcMode="linear" repeatCount="indefinite"/></rect>'
        )


    # legend: Less [][][][][] More (bottom-right of the grid)
    leg_y = grid_top + art_h + 6
    leg_x = canvas_w - PAD - (len(PALETTE) * (CELL - 1) + 70)
    parts.append(f'<text x="{leg_x}" y="{leg_y + CELL*0.8:.1f}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>')
    lx = leg_x + 8
    for lvl, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx}" y="{leg_y}" width="{CELL-1}" height="{CELL-1}" rx="2.2" fill="{color}"/>')
        lx += CELL
    parts.append(f'<text x="{lx + 4}" y="{leg_y + CELL*0.8:.1f}" fill="{MUTED}" font-size="10">More</text>')

    sep_y = leg_y + CELL + 14
    parts.append(f'<line x1="0" y1="{sep_y}" x2="{canvas_w}" y2="{sep_y}" stroke="{FRAME}" stroke-opacity="0.25"/>')

    cs = data["current_streak"]["length"]
    ls = data["longest_streak"]["length"]
    total = data["total_contributions"]
    best = data["best_day"]
    rng = data["range"]

    ly = sep_y + 24
    # left column: big highlighted numbers; right column: context in muted
    parts.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{GREEN}">'
                 f'<tspan font-weight="700">{total:,}</tspan>'
                 f'<tspan fill="{MUTED}"> contributions in the last year</tspan></text>')
    parts.append(f'<text x="{canvas_w - PAD}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">'
                 f'{rng["start"]} &#8594; {rng["end"]}</text>')
    ly += 24
    parts.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{MUTED}">current streak '
                 f'<tspan fill="{ACCENT}" font-weight="700">{cs} days</tspan>'
                 f'<tspan fill="{MUTED}">   &#183;   longest </tspan>'
                 f'<tspan fill="{ACCENT}" font-weight="700">{ls} days</tspan></text>')
    parts.append(f'<text x="{canvas_w - PAD}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">'
                 f'best day <tspan fill="{GOLD}" font-weight="700">{best["count"]}</tspan> on {best["date"]}</text>')

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    data = json.load(open(IN_PATH))
    svg = render(data)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH} ({len(svg)} bytes)")
