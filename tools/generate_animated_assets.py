"""Animated pieces for the profile README: about-me terminal, AI workbench routing diagram,
plus the project cards and guard hero from gen.py. Usage: python gen2.py FONTS_DIR OUT_DIR"""
import sys, math
import gen_base as gen
from gen_base import Doc, FONT, PAPER, MUTED, DIM, AMBER, GREEN, RED, LINE, PANEL, INK

CYAN, VIOLET = "#22D3EE", "#A78BFA"
TBG = "#0B0F17"
OUT = sys.argv[2]


# ------------------------------------------------------------------ about-me terminal
def terminal():
    W = 1280
    SIZE, LH, X0 = 20, 33, 48
    CW = gen.FONT["mono"].shape("m")[0][1] * SIZE / gen.FONT["mono"].upm
    P = [("brejesh", GREEN), ("@", MUTED), ("cloud202", CYAN), (" ~ ", VIOLET), ("$ ", PAPER)]

    def kv(k, v, vc=PAPER):
        return [(f"{k:<11}", VIOLET), (v, vc)]

    def metric(label, val, ok=False):
        dots = "." * (46 - len(label))
        seg = [("  " + label + " ", PAPER), (dots, DIM), (" " + val, AMBER)]
        if ok: seg += [("   PASS", GREEN)]
        return seg

    script = [
        ("cmd", "whoami"),
        ("out", [("Brejesh Balakrishnan", PAPER), ("  ·  ", DIM), ("AI Engineer @ Cloud202", AMBER)]),
        ("out", [("governance + safety for agentic AI on Amazon Bedrock and AgentCore", MUTED)]),
        ("gap", None),
        ("cmd", "cat about.yml"),
        ("out", kv("focus:", "tool-using agents, guard models, RAG that declines, evals")),
        ("out", kv("before:", "~2 yrs full-stack at Accenture (Java, Spring Boot, Angular)")),
        ("out", kv("studied:", "B.E. ECE, College of Engineering Guindy (CGPA 8.54)")),
        ("out", kv("speaks:", "Tamil · Malayalam · English · Python")),
        ("out", kv("believes:", "a model that can't answer should decline, not guess", GREEN)),
        ("gap", None),
        ("cmd", "./agent-govbench --summary"),
        ("out", metric("attack success, no guard", "51.5%")),
        ("out", metric("attack success, LLM guard G6", " 4.7%", True)),
        ("out", metric("legit calls blocked by G6", " 0.4%", True)),
        ("gap", None),
        ("cmd", "ls ~/now"),
        ("out", [("agent-governance/  ", CYAN), ("gemma4-dev-agent/  ", CYAN), ("toolcall-guard/  ", CYAN), ("mozhi/", CYAN)]),
        ("cmd", ""),
    ]
    y, rows = 112, []
    for kind, val in script:
        if kind == "gap":
            y += 14; continue
        rows.append((kind, val, y)); y += LH
    H = y + 26
    d = Doc(W, H, rx=16, bg=TBG, border="#2A3142")
    # title bar
    d.add(f'<path d="M1 17a16 16 0 0 1 16-16h{W-34}a16 16 0 0 1 16 16v37H1z" fill="#151B27"/><line x1="1" y1="54" x2="{W-1}" y2="54" stroke="#2A3142"/>')
    for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        d.add(f'<circle cx="{30+i*24}" cy="28" r="7" fill="{c}"/>')
    d.text(W / 2, 34, "brejesh@cloud202: ~  (zsh)", "mono", 15, MUTED, anchor="middle")
    d.text(W - 28, 34, "about_me.sh", "mono", 14, DIM, anchor="end")

    TYPE, PRE, POST, OUTGAP, BLOCK = 0.075, 0.6, 0.45, 0.2, 0.8
    t, events = 0.6, []
    for kind, val, yy in rows:
        if kind == "cmd":
            n = len(val)
            events.append(("cmd", val, yy, t, t + PRE, t + PRE + n * TYPE))
            t += PRE + n * TYPE + POST
        else:
            events.append(("out", val, yy, t))
            t += OUTGAP
    t_end_last = t
    T = t_end_last + 5.0
    pct = lambda s: f"{min(s / T * 100, 100):.3f}%"
    FADE = (T - 0.5)
    css = d.css
    cid = 0

    def show_kf(on):
        nonlocal cid
        cid += 1
        css.append(f"@keyframes v{cid}{{0%,{pct(on - 0.001)}{{opacity:0}}{pct(on)},{pct(FADE)}{{opacity:1}}100%{{opacity:0}}}}.v{cid}{{animation:v{cid} {T:.2f}s steps(1) infinite}}")
        return f"v{cid}"

    prompt_w = sum(d.width(s, "mono", SIZE) for s, _ in P)
    for i, ev in enumerate(events):
        if ev[0] == "out":
            _, segs, yy, on = ev
            cls = show_kf(on)
            x, parts = X0, []
            for s, c in segs:
                parts.append(d.text(x, yy, s, "mono", SIZE, c, raw=True))
                x += d.width(s, "mono", SIZE)
            d.add(f'<g class="{cls}">{"".join(parts)}</g>')
        else:
            _, cmd, yy, on, ts, te = ev
            cls = show_kf(on)
            x, parts = X0, []
            for s, c in P:
                parts.append(d.text(x, yy, s, "mono", SIZE, c, raw=True))
                x += d.width(s, "mono", SIZE)
            if cmd:
                parts.append(d.text(x, yy, cmd, "monom", SIZE, PAPER, raw=True))
            d.add(f'<g class="{cls}">{"".join(parts)}</g>')
            # cover + cursor slide across the command, one character per step
            n = len(cmd)
            cid += 1
            last = i == len(events) - 1
            hide = FADE if last else (te + POST + 0.02)
            kf = (f"@keyframes c{cid}{{0%{{transform:translateX(0);opacity:0}}"
                  f"{pct(on)}{{transform:translateX(0);opacity:1}}"
                  f"{pct(ts)}{{transform:translateX(0);opacity:1;animation-timing-function:steps({max(n,1)},end)}}"
                  f"{pct(te)}{{transform:translateX({n*CW:.2f}px);opacity:1}}"
                  f"{pct(hide)}{{transform:translateX({n*CW:.2f}px);opacity:{1 if last else 0}}}"
                  f"100%{{transform:translateX({n*CW:.2f}px);opacity:0}}}}"
                  f".c{cid}{{animation:c{cid} {T:.2f}s steps(1,end) infinite}}")
            css.append(kf)
            css.append(".blk{animation:blk 1s steps(1) infinite}@keyframes blk{50%{opacity:0}}")
            top = yy - SIZE * 0.95
            d.add(f'<g transform="translate({x:.1f} 0)"><g class="c{cid}">'
                  f'<rect x="0" y="{top:.1f}" width="{n*CW+CW+4:.1f}" height="{LH}" fill="{TBG}"/>'
                  f'<rect class="blk" x="0" y="{top+3:.1f}" width="{CW:.1f}" height="{SIZE*1.2:.1f}" fill="{GREEN}"/></g></g>')
            # the cover must hide uncovered characters before typing begins: shift text under cover
    d.save("terminal.svg", "Animated terminal: whoami prints Brejesh Balakrishnan, AI Engineer at Cloud202, working on governance and safety for agentic AI on Amazon Bedrock and AgentCore. about.yml lists his focus on tool-using agents, guard models, RAG and evals; about two years full-stack at Accenture; B.E. ECE from College of Engineering Guindy; languages Tamil, Malayalam, English and Python. agent-govbench summary: attack success 51.5% with no guard, 4.7% with the LLM guard, 0.4% of legitimate calls blocked.")


# ------------------------------------------------------------------ AI workbench routing diagram
def workbench():
    W, H = 1280, 660
    d = Doc(W, H, rx=20, bg=INK)
    d.add(f'<defs><radialGradient id="hub" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".28"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>'
          f'<linearGradient id="gw" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>'
          f'<clipPath id="mq"><rect x="40" y="{H-74}" width="{W-80}" height="50"/></clipPath>'
          f'<linearGradient id="mf" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset=".08" stop-color="{INK}" stop-opacity="0"/><stop offset=".92" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}"/></linearGradient></defs>')
    gen.grid(d, 28, 28, W, H - 90, 28, 0.45)
    d.text(44, 56, "AI WORKBENCH", "monob", 15, AMBER, ls=2.4)
    d.text(W - 44, 56, "how my prompts get routed", "ital", 26, MUTED, anchor="end")

    CX, CY = 640, 300
    d.add(f'<ellipse cx="{CX}" cy="{CY}" rx="260" ry="200" fill="url(#hub)"/>')
    # left: agents
    LX, LWID = 48, 284
    agents = [("Claude Code", "terminal · desktop · cloud", CYAN), ("Codex", "CLI agent", GREEN), ("Claude app", "research · docs · design", CYAN)]
    d.text(LX, 118, "CODING AGENTS", "monom", 13, DIM, ls=2)
    ly = [168, 268, 368]
    # right: models
    RX, RWID = 1000, 216
    models = [("Claude", CYAN), ("GPT", GREEN), ("Gemini", VIOLET), ("Gemma 4", VIOLET), ("Llama 3.3", AMBER), ("Mistral", AMBER), ("Nemotron", GREEN)]
    d.text(RX, 118, "MODELS", "monom", 13, DIM, ls=2)
    ry = [146 + i * 54 for i in range(len(models))]

    paths = []
    for i, y in enumerate(ly):
        p = f"M{LX+LWID} {y} C{LX+LWID+110} {y} {CX-260} {CY} {CX-150} {CY}"
        paths.append((p, agents[i][2], 2.2, i * 0.7, None))
    for i, y in enumerate(ry):
        p = f"M{CX+150} {CY} C{CX+260} {CY} {RX-120} {y} {RX} {y}"
        paths.append((p, models[i][1], 2.0, 1.1 + i * 0.43, i))
    css = d.css
    css.append(".flow{stroke-dasharray:4 10;animation:flow 1.2s linear infinite}@keyframes flow{to{stroke-dashoffset:-28}}")
    for j, (p, c, dur, beg, mi) in enumerate(paths):
        d.add(f'<path d="{p}" fill="none" stroke="{LINE}" stroke-width="2"/>')
        d.add(f'<path class="flow" d="{p}" fill="none" stroke="{c}" stroke-opacity=".35" stroke-width="2"/>')
        period = 3.0
        d.add(f'<circle r="5" fill="{c}" opacity="0"><animateMotion dur="{dur}s" begin="{beg:.2f}s" repeatCount="indefinite" path="{p}" keyPoints="0;1;1" keyTimes="0;{dur/ (dur+0.8):.3f};1" calcMode="linear"/>'
              f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.05;{dur/(dur+0.8)-0.02:.3f};{dur/(dur+0.8):.3f};1" dur="{dur}s" begin="{beg:.2f}s" repeatCount="indefinite"/></circle>')
    # agent nodes
    for (name, sub, c), y in zip(agents, ly):
        d.add(f'<rect x="{LX}" y="{y-32}" width="{LWID}" height="64" rx="14" fill="{PANEL}" stroke="{c}" stroke-opacity=".55" stroke-width="1.5"/>')
        d.add(f'<circle cx="{LX+24}" cy="{y}" r="5" fill="{c}"><animate attributeName="opacity" values="1;.3;1" dur="2s" repeatCount="indefinite" begin="{y/300:.2f}s"/></circle>')
        d.text(LX + 42, y - 2, name, "monob", 19, PAPER)
        d.text(LX + 42, y + 20, sub, "mono", 13, DIM)
    # model nodes, flash when a packet lands
    for i, ((name, c), y) in enumerate(zip(models, ry)):
        _, _, dur, beg, _ = paths[len(agents) + i]
        land = dur / (dur + 0.8)
        d.add(f'<rect x="{RX}" y="{y-21}" width="{RWID}" height="42" rx="21" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5">'
              f'<animate attributeName="stroke" values="{LINE};{LINE};{c};{LINE}" keyTimes="0;{land-0.01:.3f};{land+0.02:.3f};1" dur="{dur}s" begin="{beg:.2f}s" repeatCount="indefinite"/></rect>')
        d.add(f'<circle cx="{RX+22}" cy="{y}" r="4.5" fill="{c}"/>')
        d.text(RX + 38, y + 6, name, "monom", 17, PAPER)
    # gateway
    css.append(f".spin{{animation:spin 18s linear infinite;transform-origin:{CX}px {CY}px}}.spin2{{animation:spin 30s linear infinite reverse;transform-origin:{CX}px {CY}px}}@keyframes spin{{to{{transform:rotate(360deg)}}}}"
               f".pulse2{{animation:p2 2.6s ease-out infinite;transform-box:fill-box;transform-origin:center}}@keyframes p2{{0%{{transform:scale(1);opacity:.7}}100%{{transform:scale(1.5);opacity:0}}}}")
    d.add(f'<circle class="spin" cx="{CX}" cy="{CY}" r="168" fill="none" stroke="url(#gw)" stroke-width="1.5" stroke-dasharray="2 12" stroke-linecap="round"/>')
    d.add(f'<circle class="spin2" cx="{CX}" cy="{CY}" r="186" fill="none" stroke="{LINE}" stroke-width="1" stroke-dasharray="40 18"/>')
    d.add(f'<rect class="pulse2" x="{CX-150}" y="{CY-96}" width="300" height="192" rx="26" fill="none" stroke="{VIOLET}" stroke-width="2"/>')
    d.add(f'<rect x="{CX-150}" y="{CY-96}" width="300" height="192" rx="26" fill="#121626" stroke="url(#gw)" stroke-width="2"/>')
    d.text(CX, CY - 52, "AI GATEWAY", "monom", 12.5, DIM, anchor="middle", ls=2.4)
    d.text(CX, CY + 2, "OmniRoute", "serif", 54, PAPER, anchor="middle")
    cw = d.width("routed by Nemotron", "monom", 15) + 40
    d.add(f'<rect x="{CX-cw/2:.0f}" y="{CY+24}" width="{cw:.0f}" height="34" rx="17" fill="{GREEN}" fill-opacity=".12" stroke="{GREEN}" stroke-opacity=".6"/>')
    d.add(f'<circle cx="{CX-cw/2+18:.0f}" cy="{CY+41}" r="4" fill="{GREEN}"><animate attributeName="opacity" values="1;.2;1" dur="1.2s" repeatCount="indefinite"/></circle>')
    d.text(CX + 8, CY + 46, "routed by Nemotron", "monom", 15, GREEN, anchor="middle")
    d.text(CX, CY + 82, "one endpoint · auto-fallback", "mono", 13, DIM, anchor="middle")

    # marquee of where things ship
    ship = ["Amazon Bedrock", "Bedrock AgentCore", "Hugging Face", "Kaggle", "Groq", "Google Cloud", "GitHub Pages", "Cloudflare Workers", "Streamlit Cloud", "MCP servers"]
    d.add(f'<line x1="40" y1="{H-96}" x2="{W-40}" y2="{H-96}" stroke="{LINE}"/>')
    d.text(44, H - 108, "WHERE IT SHIPS", "monom", 12.5, DIM, ls=2)
    row, x = [], 0
    for rep in range(2):
        for s in ship:
            w = d.width(s, "mono", 16) + 28
            row.append(f'<rect x="{x:.0f}" y="{H-68}" width="{w:.0f}" height="36" rx="18" fill="none" stroke="#3A4356"/>' + d.text(x + 14, H - 44, s, "mono", 16, MUTED, raw=True))
            x += w + 14
    span = x / 2
    css.append(f".mq{{animation:mq 28s linear infinite}}@keyframes mq{{to{{transform:translateX(-{span:.0f}px)}}}}")
    d.add(f'<g clip-path="url(#mq)"><g transform="translate(40 0)"><g class="mq">{"".join(row)}</g></g></g><rect x="40" y="{H-74}" width="{W-80}" height="50" fill="url(#mf)"/>')
    d.save("ai-workbench.svg", "AI workbench: Claude Code, Codex and the Claude app route through the OmniRoute AI gateway, routed by Nemotron, to Claude, GPT, Gemini, Gemma 4, Llama 3.3, Mistral and Nemotron. Work ships to Amazon Bedrock, Bedrock AgentCore, Hugging Face, Kaggle, Groq, Google Cloud, GitHub Pages, Cloudflare Workers, Streamlit Cloud and MCP servers.")


if __name__ == "__main__":
    gen.OUT = OUT
    import os; os.makedirs(OUT, exist_ok=True)
    gen.hero()
    gen.cards()
    terminal()
    workbench()
