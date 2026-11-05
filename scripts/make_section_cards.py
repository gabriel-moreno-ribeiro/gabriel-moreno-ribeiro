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
        "HIBEEX is a fintech startup with full AI back-office services for Brazil's "
        "small businesses. Our AI agents connect to the old software a business "
        "already pays for, then do the manual work on top: taxes, forms, insurance "
        "claims, whatever they need.",
        "It began inside my father's dental clinic. At 14, after he had to let his "
        "staff go, I took over its accounting and finances and built tools to save "
        "my parents time. After four years of that and 96 conversations with owners "
        "in the same situation, my co-founder Teodoro and I made it a company "
        "(February 2026).",
        "As co-founder I do code and business: sales, fundraising, finance and law. "
        "So far: 42 clients, 73% less manual work, and a $100K offer. We moved to "
        "Sao Paulo in April, worked inside a client's office from July, and since "
        "October build out of Ithaca, Taqtile's house, where co-founder Edmar "
        "Miyake mentors us and backs HIBEEX.",
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
        ("LLM Product Building", 95, "Claude API integration, narrative generation in prod"),
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
    ("Projeto Candela", "Registered NGO with the Federal University of Bahia", "2023 - Present", GOLD,
     ["Founder & lead engineer: kit design, fundraising & partners",
      "140 low-cost physics lab kits in 28 public schools with no lab | 3K+ students",
      "Physics failure rate fell from 30% to 10%"]),
    ("Steady-State Hypothesis", "Research Fellow, Instituto Principia", "2023 - 2026", RED,
     ["137-page thesis advised by 2 USP/JHU PhDs | US$3K scholarship",
      "Python models of ozone depletion (CFCs) & Haber-Bosch ammonia reactors",
      "Off by up to 37%, 'total' version within 14% | held in ~92% of 1,938 enzyme measurements"]),
    ("Science Olympiad Club", "President, Colegio Militar de Salvador", "2022 - 2024", CYAN,
     ["400+ members (57% of the school) | VP, Math Division Head, Army liaison",
      "Coached 215 students: ~60 won national gold or silver"]),
    ("Anisio Teixeira Initiative", "Free olympiad prep for low-income students", "2023 - Present", GREEN,
     ["Founder & president, team of 9 volunteers | 8 schools, 678 students",
      "25 national medals (4 gold)"]),
    ("National Physics Competition", "Co-creator, free olympiad open to all of Brazil", "2024 - 2025", SECTION,
     ["4-stage mock olympiad for students with no school lab: 26 states, 2K students",
      "40 simulated-experiment problems"]),
    ("Principia Alumni Association", "Vice President", "2023 - Present", SECTION,
     ["94 members | founded the Hackathon Club | hosted 7 PhD talks",
      "Co-led fundraising: ~US$60K | interviewed 32 applicants"]),
    ("FinTech Savings RCT", "Behavioral economics research, Fundacao Estudar", "2025", SECTION,
     ["Randomized controlled trial, n=208 public-school students: +130% savings",
      "Mentored by Aaron Litvin, Ph.D. (Harvard)"]),
    ("GSAT Education", "Test-prep platform built from scratch", "Nov 2025 - May 2026", GREEN,
     ["Product, engineering and go-to-market"]),
    ("Refurbished Laptops", "Online store, self-taught repair since 7th grade", "2022 - 2026", MUTED,
     ["121 laptops fixed for clients & resale, shipped to 21 of Brazil's 26 states",
      "US$7K earned to pay olympiad courses, fund Candela & help at home"]),
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
                 + text(BODY_X + 16 + name_w, y, "- " + esc(sub), MUTED, size=12)
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
    ("28 Olympiad Medals (18 Gold, 5 Silver, 5 Bronze)", "37 olympiads, ~7,000 training hours since grade 5 | finalist, Brazil's IChO team selection | IMPA fellow", GOLD),
    ("SAT 1570/1600", "Reading & Writing 770, Math 800", GREEN),
    ("Gold, Brazilian Public Schools Physics Olympiad", "1st in Bahia; led to a research grant", GOLD),
    ("National Silver, Brazilian Public Schools Math Olympiad", "2nd in my school, 5th in Bahia", CYAN),
    ("Research presentations, IIP & IFT-UNESP", "Top 2% of 700+; the only one from my region", GREEN),
    ("Finalist, Behring Founders", "Fellowship that funds young tech founders; top 5% of 1,200+ applicants", RED),
    ("Youngest founders, Canastra AI Residence", "Top 1% of 1K+ | WOW Accelerator finalist, top 4% of 276", RED),
    ("~US$172K Merit Scholarships & Research Funding", "Full scholarships at Ari de Sa & Farias Brito + Poliedro & Estrategia Militares", CYAN),
    ("LALA & Fundacao Estudar", "Latin American Leadership Academy | Fundacao Estudar fellow", SECTION),
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
    prompt = "gabriel@github: ~$ cat certifications.yaml"
    rows = [
        ("AWS", "AWS Activate, USD 10,000 active credits", GOLD),
        ("Calculus", "AP-equivalent, Schoolhouse (recognized by MIT, CalTech, Columbia)", CYAN),
        ("Chemistry", "AP-equivalent, Schoolhouse by Khan Academy", GREEN),
    ]
    h = 30 + 30 + len(rows) * LH + 18
    parts = chrome(W, h, prompt)
    y = 30 + 34
    for i, (k, v, col) in enumerate(rows):
        inner = (f'<rect x="{BODY_X}" y="{y-13:.1f}" width="4" height="16" rx="2" fill="{col}"/>'
                 + text(BODY_X + 14, y, esc(k), col, size=12.5, weight=700)
                 + text(BODY_X + 130, y, esc(v), INK, size=12.5))
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
        ("open_to", GOLD, ["Builder Roles | AI/ML Roles",
                           "Open Source collaboration | Founder & investor conversations"]),
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
