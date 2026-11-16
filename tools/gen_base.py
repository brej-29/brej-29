"""Generates the profile README artwork. All text is converted to outlines so it
renders identically everywhere (GitHub serves SVGs as images, which cannot load web fonts)."""
import sys, os, math, random
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

FONTS_DIR, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

INK, PANEL, LINE = "#0B0E14", "#121722", "#252C3B"
PAPER, MUTED, DIM = "#ECE6D8", "#8E96A8", "#586074"
AMBER, GREEN, RED = "#F5B13D", "#5FD39A", "#FF6B5E"

FILES = {"serif": "InstrumentSerif-Regular.ttf", "ital": "InstrumentSerif-Italic.ttf",
         "mono": "IBMPlexMono-Regular.ttf", "monom": "IBMPlexMono-Medium.ttf",
         "monob": "IBMPlexMono-SemiBold.ttf"}


class F:
    def __init__(self, key):
        path = os.path.join(FONTS_DIR, FILES[key])
        self.key = key
        self.tt = TTFont(path)
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upm = self.tt["head"].unitsPerEm
        self.hb = hb.Font(hb.Face(open(path, "rb").read()))

    def shape(self, s):
        buf = hb.Buffer()
        buf.add_str(s)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": False})
        return [(self.order[i.codepoint], p.x_advance, p.x_offset) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


FONT = {k: F(k) for k in FILES}


class Doc:
    def __init__(self, w, h, rx=18, bg=INK, border=LINE):
        self.w, self.h = w, h
        self.defs, self.seen, self.body, self.css = [], set(), [], []
        self.body.append(f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{rx}" fill="{bg}" stroke="{border}"/>')

    def glyph(self, f, name):
        gid = f"{f.key}-{f.order.index(name)}"
        if gid not in self.seen:
            self.seen.add(gid)
            pen = SVGPathPen(f.gs, ntos=lambda v: str(int(round(v))))
            f.gs[name].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
            d = pen.getCommands()
            if d:
                self.defs.append(f'<path id="{gid}" d="{d}"/>')
            else:
                self.seen.discard(gid)
                return None
        return gid

    def width(self, s, font, size, ls=0):
        f = FONT[font]
        return sum(a for _, a, _ in f.shape(s)) * size / f.upm + ls * len(s)

    def text(self, x, y, s, font="mono", size=16, fill=PAPER, anchor="start", ls=0, op=None, cls=None, raw=False):
        f = FONT[font]
        sc = size / f.upm
        w = self.width(s, font, size, ls)
        if anchor == "middle": x -= w / 2
        elif anchor == "end": x -= w
        uses, cx = [], 0.0
        for name, adv, xo in f.shape(s):
            gid = self.glyph(f, name)
            if gid:
                uses.append(f'<use href="#{gid}" x="{round(cx + xo)}"/>')
            cx += adv + ls / sc
        attrs = f' opacity="{op}"' if op is not None else ""
        attrs += f' class="{cls}"' if cls else ""
        el = f'<g transform="translate({x:.1f} {y:.1f}) scale({sc:.5f})" fill="{fill}"{attrs}>{"".join(uses)}</g>'
        if raw: return el
        self.body.append(el)
        return w

    def wrap(self, x, y, s, maxw, font="mono", size=16, fill=MUTED, lh=1.5, **kw):
        words, lines, cur = s.split(), [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if self.width(t, font, size) > maxw and cur:
                lines.append(cur); cur = wd
            else:
                cur = t
        lines.append(cur)
        for i, l in enumerate(lines):
            self.text(x, y + i * size * lh, l, font, size, fill, **kw)
        return y + len(lines) * size * lh

    def add(self, s): self.body.append(s)

    def chip(self, x, y, s, size=14, fill=PAPER, stroke=LINE, pad=11, h=None, bg="none"):
        h = h or size + 14
        w = self.width(s, "mono", size) + pad * 2
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{bg}" stroke="{stroke}"/>')
        self.text(x + pad, y + h / 2 + size * 0.34, s, "mono", size, fill)
        return w

    def save(self, name, title):
        css = "".join(self.css)
        style = f"<style>{css}@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}</style>" if css else ""
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" role="img" aria-label="{title}">'
               f'<title>{title}</title>{style}<defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>')
        p = os.path.join(OUT, name)
        open(p, "w").write(svg)
        print(f"{name}: {len(svg)/1024:.0f} KB")


def grid(d, x0, y0, x1, y1, step=28, op=0.5):
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="1"/>' for y in range(y0, y1, step) for x in range(x0, x1, step))
    d.add(f'<g fill="{LINE}" opacity="{op}">{dots}</g>')


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1280, 516
    d = Doc(W, H, rx=22)
    d.add(f'<defs><radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{AMBER}" stop-opacity="0.22"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>'
          f'<linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient>'
          f'<linearGradient id="fadeR" x1="1" x2="0"><stop offset="0" stop-color="{INK}"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient>'
          f'<clipPath id="clip"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="21"/></clipPath></defs>')
    d.add('<g clip-path="url(#clip)">')
    grid(d, 28, 28, W, H, 28, 0.55)
    GX, Y0, Y1 = 852, 340, 484          # guard gate x, band top/bottom
    d.add(f'<ellipse cx="{GX}" cy="{(Y0+Y1)//2}" rx="330" ry="210" fill="url(#glow)"/>')

    # top meta row
    d.add(f'<circle cx="62" cy="62" r="5" fill="{GREEN}" class="pulse"/>')
    d.text(78, 68, "BREJ-29", "monob", 17, PAPER, ls=2.2)
    d.text(178, 68, "/  AI ENGINEER  /  AGENTIC AI + EVALUATION", "mono", 17, MUTED, ls=1.6)
    d.text(W - 56, 68, "github.com/brej-29", "mono", 17, DIM, anchor="end", ls=0.5)

    # name + tagline
    d.text(52, 178, "Brejesh Balakrishnan", "serif", 112, PAPER)
    w = d.text(56, 240, "AI that knows ", "ital", 46, MUTED)
    w2 = d.text(56 + w, 240, "when it's wrong.", "ital", 46, AMBER)
    d.add(f'<rect x="{56+w+w2+10:.0f}" y="204" width="4" height="42" fill="{AMBER}" class="blink"/>')
    d.text(56, 284, "I build tool-using agents, then measure what actually stops them from doing harm.", "mono", 18.5, MUTED)

    # guard band
    lanes = [Y0 + 18 + i * 27 for i in range(5)]
    for y in lanes:
        d.add(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="1" stroke-dasharray="2 7"/>')
    rnd = random.Random(29)
    DUR = 9.0
    gate_pct = (GX + 40) / (W + 80) * 100          # % of travel at which a dot meets the gate
    d.css.append(
        f".d{{animation:{DUR}s linear infinite}}"
        f"@keyframes pass{{0%{{transform:translateX(-40px);fill:{MUTED}}}{gate_pct:.1f}%{{fill:{MUTED}}}{gate_pct+1.5:.1f}%{{fill:{GREEN}}}100%{{transform:translateX({W+40}px);fill:{GREEN}}}}}"
        f"@keyframes stop{{0%{{transform:translateX(-40px);fill:{MUTED};opacity:1}}{gate_pct-1.2:.1f}%{{transform:translateX({GX-13}px);fill:{MUTED};opacity:1}}{gate_pct+1:.1f}%{{transform:translateX({GX-13}px);fill:{RED};opacity:1}}{gate_pct+9:.1f}%{{transform:translateX({GX-13}px);fill:{RED};opacity:1}}{gate_pct+15:.1f}%,100%{{transform:translateX({GX-13}px);fill:{RED};opacity:0}}}}"
        f"@keyframes ring{{0%,{gate_pct-1:.1f}%{{transform:translateX({GX-13}px) scale(1);opacity:0}}{gate_pct+1:.1f}%{{transform:translateX({GX-13}px) scale(1);opacity:.9}}{gate_pct+11:.1f}%,100%{{transform:translateX({GX-13}px) scale(3.2);opacity:0}}}}"
        f".p{{animation-name:pass}}.s{{animation-name:stop}}.r{{animation-name:ring;fill:none;stroke:{RED};stroke-width:1.4;transform-box:fill-box;transform-origin:center}}"
        f".blink{{animation:blink 1.1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}"
        f".pulse{{animation:pulse 2.4s ease-in-out infinite}}@keyframes pulse{{50%{{opacity:.35}}}}"
        f".scan{{animation:scan 3.2s ease-in-out infinite}}@keyframes scan{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY({Y1-Y0-26}px)}}}}")
    for li, y in enumerate(lanes):
        n = 6
        for k in range(n):
            delay = -(k * DUR / n + rnd.uniform(0, DUR / n * 0.7) + li * 0.37)
            blocked = rnd.random() < 0.34
            r = rnd.choice([4, 4.5, 5.5])
            if blocked:
                d.add(f'<circle class="d r" cx="0" cy="{y}" r="{r+2}" style="animation-delay:{delay:.2f}s"/>')
                d.add(f'<circle class="d s" cx="0" cy="{y}" r="{r}" style="animation-delay:{delay:.2f}s"/>')
            else:
                d.add(f'<circle class="d p" cx="0" cy="{y}" r="{r}" style="animation-delay:{delay:.2f}s"/>')
    d.add(f'<rect x="0" y="{Y0}" width="150" height="{Y1-Y0}" fill="url(#fadeL)"/><rect x="{W-150}" y="{Y0}" width="150" height="{Y1-Y0}" fill="url(#fadeR)"/>')
    # gate
    d.add(f'<line x1="{GX}" y1="{Y0-8}" x2="{GX}" y2="{Y1-8}" stroke="{AMBER}" stroke-width="2"/>')
    d.add(f'<path d="M{GX-9} {Y0-8}h18M{GX-9} {Y1-8}h18" stroke="{AMBER}" stroke-width="2"/>')
    d.add(f'<rect class="scan" x="{GX-5}" y="{Y0-2}" width="10" height="14" rx="2" fill="{AMBER}"/>')
    lw = d.width("GUARD", "monob", 14, 2.4)
    d.add(f'<rect x="{GX-lw/2-11:.0f}" y="{Y0-40}" width="{lw+22:.0f}" height="24" rx="12" fill="{AMBER}"/>')
    d.text(GX, Y0 - 23, "GUARD", "monob", 14, INK, anchor="middle", ls=2.4)
    d.text(56, Y1 + 14, "PROPOSED TOOL CALLS", "mono", 13.5, DIM, ls=2)
    d.text(GX - 22, Y1 + 14, "BLOCKED", "mono", 13.5, RED, anchor="end", ls=2)
    d.text(W - 56, Y1 + 14, "EXECUTED", "mono", 13.5, GREEN, anchor="end", ls=2)
    d.add('</g>')
    d.save("hero.svg", "Brejesh Balakrishnan. AI engineer, agentic AI and evaluation. AI that knows when it's wrong.")


# ---------------------------------------------------------------- section headers
def header(n, title, note, name):
    W, H = 1280, 92
    d = Doc(W, H, rx=16, bg=INK)
    d.text(36, 57, n, "monob", 20, AMBER, ls=1)
    d.add(f'<line x1="82" y1="28" x2="82" y2="64" stroke="{LINE}" stroke-width="1.5"/>')
    w = d.text(104, 62, title, "serif", 46, PAPER)
    nw = d.width(note, "mono", 15.5, 1.2)
    x0, x1 = 104 + w + 28, W - 36 - nw - 24
    if x1 > x0 + 40:
        d.add(f'<line x1="{x0:.0f}" y1="47" x2="{x1:.0f}" y2="47" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="1 9" stroke-linecap="round"/>')
    d.text(W - 36, 52, note, "mono", 15.5, MUTED, anchor="end", ls=1.2)
    d.save(name, title)


# ---------------------------------------------------------------- principles strip
def principles():
    W, H = 1280, 214
    d = Doc(W, H, rx=18)
    items = [("01", "Evaluation before claims", "The test plan and the thresholds get written first. Then the model gets built."),
             ("02", "Fail safe by structure", "A system that cannot answer should decline. Guardrails live in the pipeline, not in a prompt."),
             ("03", "Report the weak spot", "Every project says where it breaks, with the number, next to the headline result.")]
    cw = W / 3
    for i, (n, t, b) in enumerate(items):
        x = i * cw + 40
        if i: d.add(f'<line x1="{i*cw:.0f}" y1="34" x2="{i*cw:.0f}" y2="{H-34}" stroke="{LINE}"/>')
        d.text(x, 56, n, "monob", 15, AMBER, ls=1.5)
        d.text(x, 104, t, "serif", 37, PAPER)
        d.wrap(x, 138, b, cw - 80, "mono", 15.5, MUTED, lh=1.55)
    d.save("principles.svg", "How I work: evaluation before claims, fail safe by structure, report the weak spot.")


# ---------------------------------------------------------------- project cards
def card(name, kicker, title, big, big_sub, body, tags, weak=None, viz=None):
    W, H = 620, 440
    d = Doc(W, H, rx=18, bg=PANEL)
    d.add(f'<clipPath id="c"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17"/></clipPath><g clip-path="url(#c)"><rect x="0" y="0" width="{W}" height="4" fill="url(#tb)"/><rect class="sweep" x="-160" y="0" width="160" height="4" fill="url(#sw)"/></g>')
    d.add(f'<defs><linearGradient id="tb" x1="0" x2="1"><stop offset="0" stop-color="#22D3EE"/><stop offset=".5" stop-color="#A78BFA"/><stop offset="1" stop-color="{AMBER}"/></linearGradient><linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>')
    d.css.append(f".sweep{{animation:sweep 4.5s ease-in-out infinite}}@keyframes sweep{{0%{{transform:translateX(0)}}60%,100%{{transform:translateX({W+160}px)}}}}"
                 ".grow{animation:grow 6s cubic-bezier(.2,.8,.2,1) infinite;transform-box:fill-box;transform-origin:left center}@keyframes grow{0%{transform:scaleX(0)}25%,88%{transform:scaleX(1)}100%{transform:scaleX(1);opacity:.0}}"
                 ".live{animation:live 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}@keyframes live{0%{transform:scale(1);opacity:.8}100%{transform:scale(3.2);opacity:0}}")
    d.add(f'<circle class="live" cx="{W-82}" cy="45" r="4" fill="{GREEN}"/><circle cx="{W-82}" cy="45" r="4" fill="{GREEN}"/>')
    d.text(34, 50, kicker, "monom", 15, AMBER, ls=1.8)
    d.add(f'<path d="M{W-52} 54l14-14m-10 0h10v10" fill="none" stroke="{DIM}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    d.text(34, 98, title, "serif", 44, PAPER)
    if isinstance(big, tuple):
        w1 = d.text(34, 182, big[0], "serif", 78, MUTED)
        ax = 34 + w1 + 18
        d.add(f'<path d="M{ax:.0f} 158h44m-14-13l14 13-14 13" fill="none" stroke="{AMBER}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')
        bw = w1 + 18 + 44 + 18 + d.text(ax + 62, 182, big[1], "serif", 78, PAPER)
        big = f"{big[0]} to {big[1]}"
    else:
        bw = d.text(34, 182, big, "serif", 78, PAPER)
    if viz: viz(d, 34 + bw + 24, 126, W - 34 - (34 + bw + 24))
    d.text(34, 214, big_sub, "mono", 16.5, GREEN)
    y = d.wrap(34, 254, body, W - 68, "mono", 16.5, MUTED, lh=1.48)
    if weak:
        d.text(34, y + 4, "weak spot: " + weak, "mono", 15, AMBER, op=0.85)
    x = 34
    for t in tags:
        x += d.chip(x, H - 54, t, size=14.5, fill=MUTED, pad=11, h=30) + 8
    d.save(name, f"{title}: {big} {big_sub}")


def bars(vals, labels, colors):
    def f(d, x, y, w):
        if w < 120: return
        for i, (v, l, c) in enumerate(zip(vals, labels, colors)):
            yy = y + i * 23
            d.text(x, yy + 9, l, "mono", 11.5, MUTED, ls=0.6)
            bx = x + 132
            mw = w - 132
            d.add(f'<rect x="{bx}" y="{yy}" width="{mw:.0f}" height="10" rx="2" fill="{INK}"/>')
            d.add(f'<rect class="grow" style="animation-delay:{i*0.25}s" x="{bx}" y="{yy}" width="{max(mw*v,3):.0f}" height="10" rx="2" fill="{c}"/>')
    return f


def cards():
    card("card-govbench.svg", "BENCHMARK  /  AGENT SAFETY", "Agent GovBench",
         ("51.5%", "4.7%"), "attack success: no guard vs LLM guard, live agent runs",
         "Which guardrails actually stop a tool-using agent from making harmful calls on Google Cloud, and what do they cost in blocked legitimate work, latency and money?",
         ["Python", "Gemini", "Model Armor", "HF dataset"])
    card("card-toolcall.svg", "GUARD MODEL  /  LOCAL + FREE", "Toolcall Guard",
         "0.62", "of attacks blocked at 0.08 false-positive rate",
         "A LoRA-tuned Gemma 4 that checks one agent tool call before it runs and answers in JSON. The 8-bit build fits a 6 GB GPU. A pre-execution check, not a security boundary.",
         ["Gemma 4", "PEFT / LoRA", "MCP server", "Playground"],
         viz=bars([0.62, 0.61, 0.35], ["FULL PRECISION", "8-BIT", "4-BIT"], [AMBER, AMBER, DIM]))
    card("card-compliance.svg", "RAG  /  DECLINES INSTEAD OF GUESSING", "Compliance Workbench",
         "677", "tests passing, 5 MCP tools",
         "Which EU and US rules apply to your AI, data or cyber product? Cited answers from the official text of the EU AI Act, GDPR, NIS2, DORA, CRA and NIST. Uncovered rules get a plain decline.",
         ["LangGraph", "FastAPI", "Streamlit", "MCP"])
    card("card-mozhi.svg", "VOICE AGENT  /  TAMIL + MALAYALAM + ENGLISH", "Mozhi",
         "0.941", "action macro-F1 on 2,805 test requests",
         "A voice assistant that checks before it acts. I measured the LLM-picks-the-tool approach, found it slow and unreliable, and replaced it with a 23 MB trained router that takes 2 ms.",
         ["Fine-tuned router", "In-browser", "Speech"])
    card("card-feasible.svg", "PLANNING  /  PROVABLE CONSTRAINTS", "Feasible Day",
         "96 / 96", "feasible days, vs 2 of 576 for an LLM alone",
         "Day plans you can actually walk. Every stop is a real OpenStreetMap place, checked against opening hours and walking time. Pre-registered test, 27 cities.",
         ["TypeScript", "React", "MapLibre", "OSRM"], weak="59% on the routing re-check in 15 added cities")
    card("card-clearcut.svg", "FRAUD REVIEW  /  CAPACITY-AWARE", "Clearcut",
         "85.3%", "recall when you can only review 0.5%",
         "Turns risk scores into a review budget and an exportable queue. 64 of 75 confirmed frauds caught in 284 reviews on 56,962 held-out payments.",
         ["scikit-learn", "Browser-local", "Chronological split"],
         viz=bars([0.853, 0.467, 0.013], ["LOGISTIC", "ISOLATION FOREST", "LARGEST AMOUNT"], [AMBER, DIM, DIM]))


# ---------------------------------------------------------------- stack
def stack():
    rows = [("AGENTS + LLM", ["LangGraph", "LangChain", "RAG", "MCP", "Amazon Bedrock", "AgentCore", "Gemini", "Groq", "Pinecone"]),
            ("ML + EVAL", ["PyTorch", "TensorFlow", "scikit-learn", "XGBoost", "Optuna", "SHAP", "MLflow", "Evidently", "Feast"]),
            ("BACKEND", ["Python", "FastAPI", "Java", "Spring Boot", "PostgreSQL", "Redis", "Kafka", "SQL"]),
            ("FRONTEND", ["TypeScript", "React", "Vite", "Angular", "Streamlit", "MapLibre"]),
            ("CLOUD + OPS", ["AWS", "Google Cloud", "Docker", "GitHub Actions", "Cloudflare Workers", "Hugging Face", "Prometheus"])]
    W, RH = 1280, 96
    H = 30 + RH * len(rows) + 10
    d = Doc(W, H, rx=18)
    for i, (lab, chips) in enumerate(rows):
        y = 30 + i * RH
        if i: d.add(f'<line x1="36" y1="{y-8}" x2="{W-36}" y2="{y-8}" stroke="{LINE}" stroke-dasharray="1 8" stroke-linecap="round"/>')
        d.text(36, y + 22, lab, "monom", 16, AMBER, ls=2)
        x = 36
        for j, c in enumerate(chips):
            assert x < W - 140, (lab, c)
            x += d.chip(x, y + 36, c, size=19, fill=PAPER if (j < 4 or (i == 0 and j < 6)) else MUTED, stroke="#3A4356" if (j < 4 or (i == 0 and j < 6)) else LINE, pad=15, h=42) + 10
        assert x < W - 26, (lab, x)
    d.save("stack.svg", "Tech stack: " + "; ".join(f"{l}: {', '.join(c)}" for l, c in rows))


# ---------------------------------------------------------------- footer
def footer():
    W, H = 1280, 190
    d = Doc(W, H, rx=22)
    d.add(f'<clipPath id="fc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="21"/></clipPath><g clip-path="url(#fc)">')
    grid(d, 28, 22, W, H, 28, 0.5)
    d.css.append(f".w{{animation:w 5s ease-in-out infinite}}@keyframes w{{50%{{opacity:.25}}}}")
    rnd = random.Random(7)
    for k in range(46):
        x, y = rnd.randrange(28, W, 28), rnd.randrange(22, H, 28)
        c = rnd.choice([AMBER, GREEN, AMBER, MUTED])
        d.add(f'<circle class="w" cx="{x}" cy="{y}" r="2" fill="{c}" style="animation-delay:{-rnd.uniform(0,5):.1f}s"/>')
    d.add(f'<rect x="250" y="44" width="780" height="104" rx="52" fill="{INK}" opacity=".94"/></g>')
    w1 = d.width("Evidence first. ", "serif", 54); w2 = d.width("Then the claim.", "ital", 54)
    x = (W - w1 - w2) / 2
    d.text(x, 104, "Evidence first. ", "serif", 54, PAPER)
    d.text(x + w1, 104, "Then the claim.", "ital", 54, AMBER)
    d.text(W / 2, 134, "THANKS FOR READING  /  BREJ-29", "mono", 13, DIM, anchor="middle", ls=2.4)
    d.save("footer.svg", "Evidence first. Then the claim.")


if __name__ == "__main__":
    hero()
    header("01", "Now", "WHAT I AM WORKING ON", "h-now.svg")
    header("02", "Measured work", "EVERY NUMBER LINKS TO ITS EVIDENCE", "h-work.svg")
    header("03", "Also shipped", "LIVE, FREE TO USE", "h-more.svg")
    header("04", "Stack", "WHAT I REACH FOR", "h-stack.svg")
    header("05", "Telemetry", "GITHUB ACTIVITY", "h-telemetry.svg")
    header("06", "Contact", "SAY HELLO", "h-contact.svg")
    principles(); cards(); stack(); footer()
