"""
Generate every README section as a terminal-window SVG card (same chrome as the
ASCII portrait / neofetch / heatmap). Zero information overlap between cards:
each fact lives in exactly one place.

  card-hibeex.svg          what HIBEEX is + what Gabriel built (narrative)
  card-skills.svg          AI/ML proficiency bars (no project numbers)
  card-ventures.svg        other ventures & research, with date ranges
  card-honors.svg          awards / selective programs / scores
  card-certifications.svg  certifications
  card-now.svg             learning / exploring / open_to
"""
from termcard import (chrome, rise, wrap, save, esc,
                      INK, MUTED, KEY, SECTION, GREEN, CYAN, GOLD, RED, FRAME, PAD)

W = 900
LH = 22
BODY_X = PAD
CHARW = 7.5


def text(x, y, s, fill=INK, size=13, weight=None, anchor=None):
    w = f' font-weight="{weight}"' if weight else ""
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y:.1f}" fill="{fill}" font-size="{size}"{w}{a}>{s}</text>'


# ============================================================ HIBEEX (about)
def card_hibeex():
    prompt = "gabriel@github: ~$ cat hibeex.md"
    paras = [
        "HIBEEX is a B2B financial intelligence platform: it connects to the ERPs "
        "Brazilian SMBs already use (Omie, Conta Azul, Nibo, VHSYS), syncs their "
        "financial data automatically, and turns it into AI-powered cash-flow "
        "analysis and executive insight — replacing manual spreadsheets.",
        "As founding engineer I architected and shipped the full-stack MVP "
        "end-to-end: ERP-to-database sync pipelines, transaction reconciliation "
        "and categorization engines, multi-tenant auth with RBAC, REST API "
        "layers, automated ingestion jobs, Claude-powered executive narrative "
        "generation, and interactive KPI dashboards.",
        "Today HIBEEX serves major accounting operations — clients managing 600+ "
        "accounting bases, including the 6th largest Sistema Dominio user in "
        "Brazil — under a 12% revenue-share partnership with VHSYS (~20,000 "
        "clients).",
    ]
    lines = []
    for p in paras:
        for wl in wrap(p, 112):
            lines.append(wl)
        lines.append(None)  # gap
    lines = lines[:-1]
    h = 30 + 30 + sum(LH if l else int(LH*0.45) for l in lines) + 18
    parts = chrome(W, h, prompt)
    y = 30 + 32
    i = 0
    for l in lines:
        if l is None:
            y += LH * 0.45
            continue
        parts.append(rise(text(BODY_X, y, esc(l), INK, size=12.8), i))
        i += 1
        y += LH
    save(parts, "card-hibeex.svg", W, h)


# ============================================================ SKILLS (AI/ML)
def card_skills():
    prompt = "gabriel@github: ~$ ./skills --ai"
    rows = [
        ("LLM Product Engineering", 95, "Claude API integration, narrative generation in prod"),
        ("AI Data Pipelines", 90, "Real-time ERP ingestion with AI classification at scale"),
        ("Personalization Algorithms", 85, "Adaptive learning-path engines"),
        ("Scientific Computing", 85, "SciPy differential equations, MATLAB modeling"),
        ("Applied Econometrics", 75, "Experimental design, behavioral economics"),
    ]
    h = 30 + 28 + len(rows) * (LH + 14) + 14
    parts = chrome(W, h, prompt)
    y = 30 + 34
    BAR_X = 270
    BAR_W = 220
    SEG = 20
    seg_w = (BAR_W - (SEG - 1) * 2) / SEG
    for idx, (name, pct, desc) in enumerate(rows):
        filled = int(round(pct / 100 * SEG))
        segs = []
        for s in range(SEG):
            col = GREEN if s < filled else "#20262e"
            sx = BAR_X + s * (seg_w + 2)
            segs.append(f'<rect x="{sx:.1f}" y="{y-11:.1f}" width="{seg_w:.1f}" '
                        f'height="12" rx="2" fill="{col}"/>')
        inner = (text(BODY_X, y, esc(name), INK, size=12.5, weight=700)
                 + "".join(segs)
                 + text(BAR_X + BAR_W + 10, y, f"{pct}%", GOLD, size=12.5, weight=700)
                 + text(BODY_X, y + 15, esc(desc), MUTED, size=11.5))
        parts.append(rise(inner, idx))
        y += LH + 14
    save(parts, "card-skills.svg", W, h)


# ============================================================ VENTURES
VENTURES = [
    ("GSAT Education", "Adaptive SAT prep EdTech", "Oct 2025 — Present", GREEN,
     ["3,200+ annotated-solutions DB + proprietary personalization algorithm",
      "71 students mentored; 53 improved from ~900 to 1300+ SAT",
      "R$50K+ revenue bootstrapped, 100% reinvested",
      "Intl partnerships: Uzbek tech firm, CT Nicolas Santos, CSA Authority"]),
    ("Projeto Candela", "Physics lab kits for public schools", "Jun 2022 — Present", GOLD,
     ["Kits + QR video lessons in 28 schools · 3,392 students (BA & CE)",
      "Grades up 40%; physics failure rate cut 30% -> 10% in 6 months",
      "Funded by PIBIC Jr/UFBA grant + R$8K crowdfunding · pitched at 60+ schools"]),
    ("FinTech Savings RCT", "Behavioral economics research", "Jan 2025 — Apr 2026", SECTION,
     ["Randomized Controlled Trial, n=208 public-school students",
      "+130% total savings in treatment group",
      "Supervised by Dr. Aaron Litvin (Ph.D., Harvard) · policy recs for BNCC"]),
    ("Chemical Kinetics", "Computational modeling — Instituto Principia", "Jun 2023 — Jun 2025", RED,
     ["Steady-State Approximation of complex mechanisms · 59-page thesis",
      "97% simulation accuracy (Haber-Bosch, stratospheric ozone)",
      "Under Dr. Juliano Bonacin (Ph.D., USP)"]),
    ("Refurbished Electronics", "E-commerce venture", "Jan 2021 — Dec 2024", MUTED,
     ["Imported, repaired & shipped hardware to 150+ clients in 21 BR states",
      "~USD 7,000 revenue; 75% reinvested in education"]),
]


def card_ventures():
    prompt = "gabriel@github: ~/ventures$ ls --all"
    line_h = 17
    block_gap = 14
    heights = [1 + len(b[4]) for b in VENTURES]
    h = 30 + 26 + sum(hh * line_h + block_gap for hh in heights) + 8
    parts = chrome(W, h, prompt)
    y = 30 + 30
    i = 0
    for name, sub, when, col, bullets in VENTURES:
        name_w = len(name) * 8.6 + 24
        inner = (text(BODY_X, y, "$ ", MUTED, size=13)
                 + text(BODY_X + 16, y, esc(name), col, size=13.5, weight=700)
                 + text(BODY_X + 16 + name_w, y, "— " + esc(sub), MUTED, size=12)
                 + text(W - PAD, y, esc(when), MUTED, size=11.5, anchor="end"))
        parts.append(rise(inner, i)); i += 1
        y += line_h
        for b in bullets:
            inner = (f'<circle cx="{BODY_X+20}" cy="{y-4:.1f}" r="2.4" fill="{col}"/>'
                     + text(BODY_X + 32, y, esc(b), INK, size=12))
            parts.append(rise(inner, i)); i += 1
            y += line_h
        y += block_gap
    save(parts, "card-ventures.svg", W, h)


# ============================================================ HONORS
HONORS = [
    ("39 Olympiad Medals (19 Gold)", "49 science olympiads · 7,000+ study hours · 2 international awards", GOLD),
    ("IChO National Finalist", "International Chemistry Olympiad — Brazilian selection", GREEN),
    ("Gold — National Science Olympiad", "+ Gold: ONNEQ, OBB, OMEM, OQJ, 2x ONEE, 2x Math Sans Frontieres Intl", GOLD),
    ("SAT 1510/1600", "Math 780 (98th percentile global) · Top 1% in Brazil", GREEN),
    ("R$1.5M+ Merit Scholarships", "Full rides at Brazil's top 4 prep schools", CYAN),
    ("PREP Program — Fundacao Estudar", "1 of ~70 fellows from 10,000+ candidates (0.7% acceptance)", SECTION),
    ("Canastra Ventures AI Residency", "R$800K pre-seed · 1 of 6 startups (2.5%) · youngest founding team ever", RED),
    ("Colegio Militar de Salvador", "Admitted at age 10 (1 of 30 / 2,000+) · 'Alamar' 5 consecutive years", CYAN),
    ("IIP Selection", "1 of 14 among 700+ candidates — International Institute of Physics", GREEN),
]


def card_honors():
    prompt = "gabriel@github: ~$ ./honors.sh"
    line_h = 30
    h = 30 + 28 + len(HONORS) * line_h + 12
    parts = chrome(W, h, prompt)
    y = 30 + 34
    for i, (title, desc, col) in enumerate(HONORS):
        inner = (f'<rect x="{BODY_X}" y="{y-13:.1f}" width="4" height="20" rx="2" fill="{col}"/>'
                 + text(BODY_X + 14, y, esc(title), INK, size=13, weight=700)
                 + text(BODY_X + 14, y + 14, esc(desc), MUTED, size=11.5))
        parts.append(rise(inner, i))
        y += line_h
    save(parts, "card-honors.svg", W, h)


# ============================================================ CERTIFICATIONS
def card_certifications():
    prompt = "gabriel@github: ~$ ls certifications/"
    rows = [
        ("AWS", "AWS Activate — USD 10,000 active credits", GOLD),
        ("Calculus", "AP-equivalent — Schoolhouse (recognized by MIT, CalTech, Columbia)", CYAN),
        ("Chemistry", "AP-equivalent — Schoolhouse by Khan Academy", GREEN),
        ("English", "Duolingo English Test 125/160 (CEFR B2)", SECTION),
    ]
    h = 30 + 30 + len(rows) * LH + 18
    parts = chrome(W, h, prompt)
    y = 30 + 34
    for i, (k, v, col) in enumerate(rows):
        inner = (text(BODY_X, y, "-rw-r--r--", MUTED, size=12)
                 + text(BODY_X + 100, y, esc(k), col, size=12.5, weight=700)
                 + text(BODY_X + 200, y, esc(v), INK, size=12.5))
        parts.append(rise(inner, i))
        y += LH
    save(parts, "card-certifications.svg", W, h)


# ============================================================ NOW (focus)
def card_now():
    prompt = "gabriel@github: ~$ cat now.yaml"
    blocks = [
        ("learning", GREEN, ["Advanced LLM orchestration & agentic workflows",
                             "Distributed systems & scalable data pipelines",
                             "Leadership & entrepreneurship"]),
        ("exploring", SECTION, ["AI applications in accounting automation",
                                "Behavioral economics x product design"]),
        ("open_to", GOLD, ["Software Engineering Internships · AI/ML Roles",
                           "Open Source collaboration · Founder & investor conversations"]),
    ]
    line_h = 18
    total = sum(1 + len(b[2]) for b in blocks)
    h = 30 + 30 + total * line_h + 20
    parts = chrome(W, h, prompt)
    y = 30 + 32
    i = 0
    for key, col, items in blocks:
        parts.append(rise(text(BODY_X, y, esc(key) + ":", col, size=13, weight=700), i)); i += 1
        y += line_h
        for it in items:
            inner = (text(BODY_X + 20, y, "-", MUTED, size=12.5)
                     + text(BODY_X + 34, y, esc(it), INK, size=12.5))
            parts.append(rise(inner, i)); i += 1
            y += line_h
    save(parts, "card-now.svg", W, h)


if __name__ == "__main__":
    card_hibeex()
    card_skills()
    card_ventures()
    card_honors()
    card_certifications()
    card_now()
