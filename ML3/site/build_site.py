"""Generates the static pages of the OrthoTrace research site. Numbers on pages come from data/results.json (real study artifacts);
copies manuscript, figures and key docs into site/downloads and site/assets/figures. Run: python site/build_site.py"""
import json, shutil, hashlib, re
from html import escape
from pathlib import Path

SITE = Path(__file__).resolve().parent; ROOT = SITE.parent
D = json.loads((SITE / "data/results.json").read_text(encoding="utf-8")); M = D["meta"]
G = {g["id"]: g for g in D["gap"]}
PR = [g for g in D["gap"] if g["primary"]]
gmin, gmax = min(g["gap"] for g in PR), max(g["gap"] for g in PR)
dmin, dmax = min(g["decoupled"] for g in PR), max(g["decoupled"] for g in PR)
pmin, pmax = min(g["pooled"] for g in PR), max(g["pooled"] for g in PR)

# ---------- assets / downloads ----------
(SITE / "downloads").mkdir(exist_ok=True); (SITE / "assets/figures").mkdir(parents=True, exist_ok=True)
DL = {"manuscript.pdf": ROOT / "paper/manuscript.pdf", "manuscript.docx": ROOT / "paper/manuscript.docx", "manuscript.md": ROOT / "paper/manuscript.md",
      "FROZEN_analysis_plan.md": ROOT / "docs/FROZEN_analysis_plan.md", "Peer_Review_Simulation.md": ROOT / "docs/Peer_Review_Simulation.md",
      "Pre_submission_fix_list.md": ROOT / "docs/Pre_submission_fix_list.md", "External_data_necessity_memo.md": ROOT / "docs/External_data_necessity_memo.md",
      "Submission_readiness_checklist.md": ROOT / "docs/Submission_readiness_checklist.md", "dataset_licences.md": ROOT / "docs/submission/dataset_licences.md",
      "clinician_review_PROTOCOL.md": ROOT / "clinician_review/PROTOCOL.md", "REPRODUCIBILITY.md": ROOT / "REPRODUCIBILITY.md", "requirements.txt": ROOT / "requirements.txt",
      "audit_results.py": ROOT / "scripts/audit_results.py"}
for name in ['DELIVERY.md', 'TEAM_CHECKLIST.md', 'DEMO_AND_VIVA.md', 'LITERATURE_MATRIX.md']:
    DL[name] = ROOT / 'docs' / name
for name in ['context.md', 'literaturesurvey.md']:
    DL[name] = ROOT.parent / name
for n, p in DL.items():
    if p.exists(): shutil.copy2(p, SITE / "downloads" / n)
from PIL import Image
FIGDIM = {}
for f in ["F1_workflow", "F2_dataset_composition", "F3_shortcut_evidence", "F4_pooled_vs_decoupled", "F5_leave_one_source_out", "F6_confusion_matrices", "F7_ood_reliability"]:
    s = ROOT / "paper/figures" / (f + ".png")
    if s.exists():  # optimised WebP for the web; the full-resolution PNGs stay in the manuscript
        im = Image.open(s).convert("RGB")
        if im.width > 1800: im = im.resize((1800, round(im.height * 1800 / im.width)), Image.LANCZOS)
        im.save(SITE / "assets/figures" / (f + ".webp"), "WEBP", quality=86, method=6); FIGDIM[f] = im.size
        (SITE / "assets/figures" / (f + ".png")).unlink(missing_ok=True)
_smp = json.loads((SITE / "data/samples.json").read_text(encoding="utf-8"))
(SITE / "data/hero.json").write_text(json.dumps([{k: v for k, v in x.items() if k != "gradcam"} for x in _smp if x["id"] in ("sample2", "sample5", "sample8")], separators=(",", ":")), encoding="utf-8")
have = lambda n: (SITE / "downloads" / n).exists()
sha = lambda n: hashlib.sha256((SITE / "downloads" / n).read_bytes()).hexdigest()[:16] if have(n) else "n/a"

import clarity
LOGO = '<img class="logo" src="assets/logo.svg" alt="" width="40" height="40">'   # standalone SVG (gradients/ids live in the file, so the page keeps unique ids)
NAV = [("index.html", "Home"), ("demo.html", "AI Demo"), ("robustness.html", "Robustness"), ("results.html", "Results")]
STUDY = [("literature.html", "Literature survey", "Prior research, themes and the focused gap."), ("results.html", "Results", "Measured outcomes, baselines and intervals."), ("robustness.html", "Source shift", "Switch between pooled and source-controlled tests."), ("research.html", "Research question", "Hypotheses and what is not claimed."), ("datasets.html", "Datasets", "Six public sources and their provenance."), ("methodology.html", "Methodology", "Freeze, single unsealing, clustered bootstrap."), ("limitations.html", "Limitations", "What the study cannot show.")]
PROJ = [("evaluation.html", "Evidence hub", "Where each part is documented, and what remains open."), ("paper.html", "Manuscript & artifacts", "Study figures and supporting downloads."), ("reproducibility.html", "Reproducibility", "Code, frozen plan, audit and artifacts."), ("about.html", "About", "Status, authorship and responsible use.")]


def menu(cur):
    AC = ' aria-current="page"'
    def a(h, t, cta=False):
        c = AC if h == cur else ""; k = ' class="cta"' if cta else ""
        return f'<li><a href="{h}"{c}{k}>{t}</a></li>'
    def dd(label, items): return f'<li><details><summary>{label} ▾</summary><div class="drop">' + "".join('<a href="%s"%s>%s<small>%s</small></a>' % (h, AC if h == cur else "", t, d) for h, t, d in items) + '</div></details></li>'
    project_links = [('context.html','Implants & imaging','Orthopaedic implants and what the model scores.'), ('timeline.html','Implant timeline','Explore four historical implant designs.'), ('contribution.html','Project contribution','Methods, experiments and the comparison tool.')] + STUDY + PROJ
    return ('<ul class="menu" id="menu">' + a('guide.html','Start here') + a('results.html','Results') + a('methodology.html','How it was tested') + dd('More',project_links) + a('demo.html','Try the demo',cta=True) + '</ul>')


ORDER = [("index.html", "Home"), ("guide.html", "Start here"), ("demo.html", "X-ray demo"), ("robustness.html", "Robustness"), ("results.html", "Results"), ("research.html", "Research"), ("datasets.html", "Datasets"), ("methodology.html", "Methodology"), ("limitations.html", "Limitations"), ("paper.html", "Paper"), ("reproducibility.html", "Reproducibility"), ("about.html", "About")]
ORDER += [('context.html', 'Implants & imaging'), ('contribution.html', 'Our contribution'), ('literature.html', 'Literature survey'), ('evaluation.html', 'Evidence hub')]
ORDER += [('timeline.html', 'Implant history'), ('border-audit.html', 'X-ray border audit')]
STUDY.insert(0, ('border-audit.html', 'X-ray border audit', 'Compare paired border changes on the same joint image.'))
STUDY.insert(0, ('timeline.html', 'Interactive implant history', 'Explore four periods and virtual artifact reconstructions.'))


def nextlink(fn):
    if fn == "index.html": return ""
    i = [o[0] for o in ORDER].index(fn); h, t = ORDER[(i + 1) % len(ORDER)]
    return f'<section class="nextp"><div class="wrap"><a class="rowlink" href="{h}"><i>Next</i><b>{t}</b><span>continue →</span></a></div></section>'


def fix_headings(html):
    """Keep a valid outline (no skipped levels); original visual size is preserved through .hNs classes."""
    stack = []; prev = [0]
    def rep(m):
        close, lvl, rest = m.group(1), int(m.group(2)), m.group(3)
        if close:
            return f"</h{stack.pop()}>" if stack else m.group(0)
        new = min(lvl, prev[0] + 1) if prev[0] else lvl
        prev[0] = new; stack.append(new)
        if new != lvl:
            if 'class="' in rest: rest = rest.replace('class="', f'class="h{lvl}s ', 1)
            else: rest += f' class="h{lvl}s"'
        return f"<h{new}{rest}>"
    html = re.sub(r'<h[1-6]\b[^>]*>.*?</h[1-6]>', lambda m: re.sub(r'<br\s*/?>\s*', '<br> ', m.group()), html, flags=re.S)
    return re.sub(r"<(/?)h([1-6])([^>]*)>", rep, html)


def page(fn, title, desc, body, scripts=(), hero=False, bodycls="", css=()):
    cs = "".join(f'<link rel="stylesheet" href="assets/css/{c}">' for c in css)
    hb = '' if bodycls == "demo-page" else ""
    js = "".join(f'<script src="assets/js/{s}"></script>' for s in scripts)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title} · OrthoTrace</title><meta name="description" content="{desc}"><meta name="theme-color" content="#F4F0E6">
<meta property="og:title" content="{title} · OrthoTrace"><meta property="og:description" content="{desc}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css"><link rel="stylesheet" href="assets/css/cinema.css">{cs}{hb}
<script>(function(){{var d=document.documentElement;d.classList.add("js");d.setAttribute("data-theme","light");if(!matchMedia("(prefers-reduced-motion: reduce)").matches){{d.classList.add("js-motion","is-entering")}}}})()</script></head><body class="{bodycls}">
<a class="skip" href="#main">Skip to content</a><div class="progress" aria-hidden="true"></div><div class="glow" aria-hidden="true"></div>
<div class="curtain" aria-hidden="true">{LOGO}</div>
<div class="research-banner"><b>Research demonstration</b><span class="bn"> · not a medical device · not clinically validated</span> · not for diagnosis</div>
<header class="site"><div class="wrap nav"><a class="brand" href="index.html">{LOGO}<span>OrthoTrace</span></a>
<button class="burger" aria-expanded="false" aria-controls="menu">Menu</button>{menu(fn)}</div></header>
<main id="main">{body}{nextlink(fn)}</main>
<footer class="site"><div class="wrap"><p class="footbig" data-split>Test the source, <em>not just the score.</em></p><div class="cols">
<div><a class="brand" href="index.html">{LOGO}<span>OrthoTrace</span></a>
<p style="margin-top:14px;max-width:46ch">An independent research website for a pre-specified, source-controlled evaluation of hip, knee and shoulder radiograph recognition. A research demonstration — not a medical device and not clinically validated.</p>
<p class="small muted">An academic software project combining model inference, source-aware evaluation and traceable evidence.</p></div>
<div><p class="fh">Explore</p><ul><li><a href="demo.html">AI Demo</a></li><li><a href="robustness.html">Robustness</a></li><li><a href="results.html">Results</a></li><li><a href="paper.html">Paper</a></li></ul></div>
<div><p class="fh">Study</p><ul><li><a href="research.html">Research</a></li><li><a href="datasets.html">Datasets</a></li><li><a href="methodology.html">Methodology</a></li><li><a href="limitations.html">Limitations</a></li><li><a href="reproducibility.html">Reproducibility</a></li><li><a href="about.html">About</a></li></ul></div></div></div></footer>
<script src="assets/vendor/gsap.min.js"></script><script src="assets/vendor/ScrollTrigger.min.js"></script><script src="assets/vendor/lenis.min.js"></script>
<script src="assets/js/charts.js"></script><script src="assets/js/app.js"></script>{js}<script src="assets/js/motion.js"></script></body></html>'''


def head(eyebrow, h, lead, extra=""):
    return f'<section class="phead"><div class="wrap"><span class="eyebrow">{eyebrow}</span><h1 data-split>{h}</h1><p class="lead">{lead}</p>{extra}</div></section>'


def sec(inner, cls="", id_=""):
    i = ' id="%s"' % id_ if id_ else ""
    return f'<section class="{cls}"{i}><div class="wrap">{inner}</div></section>'


def chart(id_, title, sub="", legend=None, h=""):
    lg = ""
    if legend: lg = '<div class="legend">' + "".join(f'<span><i style="background:{c}"></i>{t}</span>' for c, t in legend) + '</div>'
    return f'<div class="card reveal"><h3>{title}</h3><p class="small muted">{sub}</p>{lg}{h}<div class="chart" id="{id_}"></div></div>'


DISC = '<div class="callout warn"><b>Project scope</b>The models classify Hip, Knee or Shoulder. This project evaluates <i>how joint-recognition models are tested</i>; disease prediction and implant-brand identification are outside the implemented task.</div>'
P = {}

# ---------------- HOME ----------------
HB = D["holdout_pred_share"]["ft|effnet|full"]


def sbar(sh):
    cols = ["var(--c1)", "var(--c2)", "var(--c3)"]; names = ["Hip", "Knee", "Shoulder"]
    lab = ", ".join(f"{n} {s*100:.0f}%" for n, s in zip(names, sh))
    segs = "".join(f'<span style="width:{s*100:.1f}%;background:{c}">{(n + " " + format(s*100, ".0f") + "%") if s > .07 else ""}</span>' for s, c, n in zip(sh, cols, names) if s > 0)
    return f'<div class="sbar" role="img" aria-label="{lab}">{segs}</div>'


dm, dd = G["rf|dims_only"], G["rf|meta_all"]; ee = G["ft|effnet|full"]
SRC = "".join(f"<span>{s['name']}</span>" for s in D["sources"] * 2)
P["index.html"] = page("index.html", "High pooled accuracy does not mean robust generalization", "A pre-specified, source-controlled evaluation of hip, knee and shoulder radiograph recognition.", f'''
<section class="hero"><canvas id="fx" aria-hidden="true"></canvas><div class="wrap grid"><div>
<span class="eyebrow">Orthopaedic imaging AI · source-controlled evaluation</span>
<h1 data-split>High pooled accuracy does <em>not necessarily</em> mean robust anatomical generalization.</h1>
<p class="lead">On six public radiograph collections, networks name the joint with {pmin:.2f}–{pmax:.2f} balanced accuracy. Test them on a source they have not learned and it falls to {dmin:.2f}–{dmax:.2f} — against a chance level of 0.33.</p>
<div class="cta-row"><a class="btn primary" href="demo.html">Try the X-ray demo →</a><a class="btn" href="results.html">Explore the results</a><a class="btn ghost" href="paper.html">Read the paper</a></div></div>
<figure id="frame" class="frame" style="margin-bottom:0" aria-label="Held-out radiographs with the study checkpoints' outputs"><span class="tag">Held-out sample · research demo</span><div class="scanline"></div><i class="br a"></i><i class="br b"></i><i class="br c"></i><i class="br d"></i><div class="meta"></div></figure></div>
<div class="scrollcue" aria-hidden="true"><span>Scroll</span><i></i></div></section>
<div class="marquee" aria-hidden="true"><div class="track">{SRC}{SRC}</div></div>

<section id="scene" class="scene"><div class="wrap scene-pin"><div>
<span class="eyebrow">The core finding</span>
<div class="stack"><h2 id="st-a">The same networks, scored the usual way.</h2><h2 id="st-b" style="opacity:0">The same networks, on a source they never saw.</h2></div>
<div class="bigval" id="bigval">{(sum(g["pooled"] for g in PR)/5):.2f}<small id="bigcap">mean balanced accuracy · pooled random split</small></div>
<p class="muted" style="max-width:44ch;margin-top:26px">Scroll to switch the test. Five primary models, sealed test set, FracAtlas held out of training (n = 55). All five gaps exceed the pre-specified 0.10 threshold (Holm-adjusted p = 0.0025).</p>
<p id="scene-static" class="small muted" hidden>Pooled random split: {pmin:.3f}–{pmax:.3f}. Source-controlled: {dmin:.3f}–{dmax:.3f}.</p></div>
<div id="scene-bars"></div></div></section>

<section class="tint"><div class="wrap"><span class="eyebrow">Why it happens</span><h2 data-split style="max-width:18ch">The label can be read from <em>where the image came from.</em></h2>
<p class="lead" style="margin:26px 0 56px">Most public collections supply one joint each, so joint is confounded with source. Models that see nothing of the anatomy recover the pooled score — and fall to chance when the confound is removed.</p>
<div class="stat"><div class="n"><span data-count data-from="{dm['pooled']}" data-to="{dm['decoupled']}" data-dec="3">{dm['decoupled']}</span></div><p><b>Image width, height and aspect ratio</b> alone, random forest. Pooled {dm['pooled']:.3f} → source-controlled {dm['decoupled']:.3f}: exactly chance.</p></div>
<div class="stat"><div class="n"><span data-count data-from="{dd['pooled']}" data-to="{dd['decoupled']}" data-dec="3">{dd['decoupled']}</span></div><p><b>File metadata</b> alone. Pooled {dd['pooled']:.3f} → {dd['decoupled']:.3f}. No pixel of anatomy was used.</p></div>
<div class="stat"><div class="n"><span data-count data-from="{ee['pooled']}" data-to="{ee['decoupled']}" data-dec="3">{ee['decoupled']}</span></div><p><b>Fine-tuned EfficientNet-B3</b>: {ee['pooled']:.3f} pooled to {ee['decoupled']:.3f} (95% CI {ee['dec_lo']:.2f}–{ee['dec_hi']:.2f}) when FracAtlas is held out.</p></div></div></section>

<section><div class="wrap two" style="align-items:center;gap:clamp(2rem,6vw,7rem)"><div><span class="eyebrow">When a whole source is held out</span><h2 data-split>Confidently wrong, in a pattern.</h2>
<p class="lead" style="margin-top:24px">Hold out the only source of hip-implant radiographs and the fine-tuned EfficientNet-B3 calls them <b style="color:var(--c3);font-weight:500">shoulder</b>. Hold out the only shoulder-implant source and most become <b style="color:var(--c1);font-weight:500">hip</b>.</p>
<p class="small muted">Implant presence is a plausible source-associated confound; the study does not show it is the cause.</p></div>
<div><p class="small muted" style="margin:0">{HB['K']['label']} — predicted joint</p>{sbar(HB['K']['share'])}<p class="small muted" style="margin:26px 0 0">{HB['U']['label']} — predicted joint</p>{sbar(HB['U']['share'])}
<div class="collage" style="margin-top:34px"><figure><img src="assets/samples/sample2.jpg" width="454" height="373" alt="Held-out hip radiograph" loading="lazy" decoding="async"><figcaption>Hip</figcaption></figure><figure><img src="assets/samples/sample4.jpg" width="454" height="373" alt="Held-out knee radiograph" loading="lazy" decoding="async"><figcaption>Knee*</figcaption></figure><figure><img src="assets/samples/sample8.jpg" width="454" height="373" alt="Held-out shoulder radiograph" loading="lazy" decoding="async"><figcaption>Shoulder</figcaption></figure></div>
<p class="small muted" style="margin-top:10px">Held-out FracAtlas images (CC BY 4.0). *Knee labels provisional, pending clinician review.</p></div></div></section>

<section class="tint"><div class="wrap"><span class="eyebrow">How the study was run</span><h2 data-split style="max-width:20ch">Constrained so that the result could not be tuned.</h2>
<div class="steps" style="margin-top:56px"><div><b>01</b><h3>Audit</h3><p>Duplicate and leakage checks, group-aware splits, {M["n_test"]} images sealed.</p></div><div><b>02</b><h3>Freeze</h3><p>Plan, code and recipes hashed before any test image was opened.</p></div><div><b>03</b><h3>Unseal once</h3><p>{M["n_checkpoints"]} checkpoints scored once; the test set refuses a second opening.</p></div><div><b>04</b><h3>Verify</h3><p>{M["n_audit_checks"]} independent checks recompute every reported metric.</p></div></div></div></section>

<section><div class="wrap"><span class="eyebrow">Explore</span><h2 data-split style="margin-bottom:48px">Four ways in.</h2>
<a class="rowlink" href="demo.html"><i>01</i><b>X-ray demo</b><span>upload or pick a sample · four checkpoints</span></a>
<a class="rowlink" href="robustness.html"><i>02</i><b>Robustness</b><span>pooled vs source-controlled</span></a>
<a class="rowlink" href="results.html"><i>03</i><b>Results</b><span>interactive charts with CIs</span></a>
<a class="rowlink" href="paper.html"><i>04</i><b>Paper</b><span>manuscript and figures</span></a></div></section>
<section class="tight"><div class="wrap">{DISC}</div></section>
''', ["hero.js"])

# ---------------- DEMO ----------------
P["demo.html"] = page("demo.html", "X-ray Demo", "Drop a radiograph, or pick a held-out specimen, and watch four checkpoints name the joint — and disagree.", head("Instrument 01 · Joint recognition", "One X-ray. <em>Two ways to read it.</em>", "Pick an X-ray or upload your own. Four models name the joint, a heat map shows what they looked at, and a shortcut probe checks whether the answer could be a trick.") + f'''
<section style="padding-top:clamp(2rem,4vw,4rem)"><div class="wrap">
<div id="backend" class="statusline"><i class="dot"></i><span class="msg">Checking inference server…</span></div>
<div class="dm"><div class="dm-left">
<div class="plate"><div class="cap"><span>Film plate · 01</span><span>Expanded anatomy + benchmark</span></div>
<div id="dz" class="drop-zone film" tabindex="0" role="button" aria-label="Upload a radiograph image: drop a file or press Enter to browse">
<i class="ticks-x"></i><i class="ticks-y"></i><div class="reticle"><i></i><i></i><i></i><i></i></div><div id="laser" class="laser"></div>
<div class="prompt"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M12 16V4m0 0L7 9m5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3"/></svg><b>Drop a radiograph</b><span id="drop-sub">JPEG, PNG, WebP, BMP or TIFF · up to 12 MB · processed in memory, never stored</span><button type="button" id="browse" class="btn">Browse files</button></div></div>
<input id="file" type="file" accept="image/jpeg,image/png,image/webp,image/bmp,image/tiff" hidden>
<div class="strip"><h4>Specimen library · held-out FracAtlas (CC BY 4.0)</h4><div id="samples" class="samples" role="group" aria-label="Sample radiographs"></div></div>
<p class="plate-note">Do not upload images that could identify a patient. The bundled specimens were visually reviewed. The project’s recorded knee labels await clinician verification. Specimen 06 appears to show an elbow.</p></div></div>
<div id="report-anchor"><div id="out" aria-live="polite"><div class="report"><div class="idle"><span class="rp-kicker" style="font:500 .68rem var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--brass-ink)">Awaiting specimen</span><h2 style="margin-top:14px">How to read the <em>report.</em></h2><p style="margin:10px 0 0;max-width:46ch;color:var(--muted)">Choose a sample or drop an X-ray on the left. This is what the report will show.</p>
<ol><li><span><b>Main answer</b> The joint our main model thinks it sees, with a score. The score is how the model splits 100% between Hip, Knee and Shoulder, not the chance of being right.</span></li><li><span><b>Four models</b> The same type of network trained on different data: one saw everything, the others each missed one dataset. If they disagree, the training data is changing the answer.</span></li><li><span><b>Six-region flags</b> A second model that flags Hip, Knee, Shoulder, Hand, Leg and Elbow independently, each with its own cutoff.</span></li><li><span><b>Heat map</b> Drag the slider. Bright areas pushed the model towards its answer. It shows sensitivity, not proof the model understands anatomy.</span></li><li><span><b>Image properties</b> Size, shape, format and file size. These are the clues a shortcut could use.</span></li><li><span><b>Shortcut probe</b> A blind model that sees only those properties also guesses. If it agrees with the main answer, the answer could be a shortcut.</span></li></ol>
<div class="skel" style="width:70%;margin-top:26px"></div><div class="skel" style="width:52%"></div></div></div></div></div></div></div></section>
<section class="tight"><div class="wrap">{DISC}</div></section>
''', ["demo.js"], bodycls="demo-page", css=("demo.css",))

# ---------------- ROBUSTNESS ----------------
P["robustness.html"] = page("robustness.html", "Robustness Demo", "Pooled versus source-controlled evaluation, side by side.", head("Robustness demo", "The same models, two ways of testing them", "Choose a scenario and a model. The numbers are the study's sealed-test results.") + f'''
{sec(f"""<div class="two"><div class="card reveal"><div class="toolbar"><div class="seg" id="rb-seg"><button data-k="pooled" aria-pressed="true">Pooled</button><button data-k="dec" aria-pressed="false">Source-controlled</button></div></div>
<h3 id="rb-title"></h3><p id="rb-desc" class="muted"></p><div id="rb-scen"></div></div>
<div class="card reveal"><h3>Inspect one model</h3><div class="toolbar"><label for="rb-model" class="small muted">Model</label><select id="rb-model"></select></div>
<div class="kpis" style="grid-template-columns:repeat(3,1fr);margin-top:0"><div class="kpi"><b id="rb-pooled">–</b><span>Pooled balanced accuracy</span></div><div class="kpi"><b id="rb-dec">–</b><span>Source-controlled balanced accuracy</span></div><div class="kpi"><b id="rb-gap">–</b><span>Drop in percentage points</span></div></div>
<div class="pbar" style="grid-template-columns:90px 1fr 0"><span class="small">Pooled</span><span class="t"><span class="f" id="rb-bar1" style="background:var(--c1)"></span></span><span></span></div>
<div class="pbar" style="grid-template-columns:90px 1fr 0"><span class="small">Controlled</span><span class="t"><span class="f" id="rb-bar2" style="background:var(--c2)"></span></span><span></span></div>
<p class="small muted" id="rb-note"></p></div></div>""")}
{sec(f"""<span class="eyebrow">What the failure looks like</span><h2>When the only hip-implant (or shoulder-implant) source is held out</h2>
<p class="lead">In these held-out sources, hip implant images were usually classified as shoulder and shoulder implant images as hip.</p><div class="cards" id="rb-hold"></div>
<div class="callout" style="margin-top:22px"><b>How to read this</b>Pooled accuracy is not wrong — it answers a different question ("can the model separate these sources' images?"). Source-controlled testing asks whether the model recognises anatomy when the source stops telling it the answer. Implant presence is a plausible source-associated confound; the study does not show it is the cause.</div>""", "")}
{sec(DISC, "tight")}''', ["robust.js"])

# ---------------- RESULTS ----------------
mdl_opts = "".join(f'<option value="{g["id"]}">{g["name"]}</option>' for g in PR if g["id"] != "x")
P["results.html"] = page("results.html", "Results", "Interactive charts of every headline result: pooled vs source-controlled, holdouts, shortcut probes, OOD and calibration.", head("Results", "Interactive results", "All values are read from the study's frozen artifacts. Hover for confidence intervals; every chart has a text-table alternative below it.", '<div class="tabs" role="tablist" data-tabs style="margin-top:22px"><button class="tab" role="tab" aria-controls="t-gap">Pooled vs controlled</button><button class="tab" role="tab" aria-controls="t-lodo">Source holdouts</button><button class="tab" role="tab" aria-controls="t-short">Shortcut probes</button><button class="tab" role="tab" aria-controls="t-rel">OOD &amp; calibration</button></div>') + f'''
<section class="tight" style="padding-top:0"><div class="wrap">
<div id="t-gap" class="panel" role="tabpanel">
<div class="toolbar"><div class="seg" id="toggle-prim"><button data-v="prim" aria-pressed="true">Primary models</button><button data-v="all" aria-pressed="false">All models incl. baselines</button></div></div>
{chart("chart-gap", "Balanced accuracy: pooled vs source-decoupled", f"Train without FracAtlas, test on FracAtlas (n = 55). Primary gap 0.31–0.50, Holm-adjusted p = 0.0025 for all five primary models (clustered paired bootstrap, B = 2000). Dashed line: chance (0.333).", [("var(--c1)", "Pooled random split"), ("var(--c2)", "Source-decoupled (95% CI)")])}
<div class="two" style="margin-top:18px">{chart("chart-hs", "Sensitivity: hip and shoulder only", "Post-hoc, exploratory. Dropping the provisionally-labelled knee class narrows the gap (0.10–0.34).", [("var(--c1)", "Pooled"), ("var(--c2)", "Decoupled")])}
{chart("chart-same", "Same-source control: identical FracAtlas images", "Checkpoints trained with FracAtlas score about 1.00 balanced accuracy. Checkpoints trained without FracAtlas score 0.50–0.69 on the same test images.", [("var(--c1)", "FracAtlas in training"), ("var(--c2)", "FracAtlas excluded")])}</div>
<div style="margin-top:18px">{chart("chart-recall", "Per-class recall on the decoupled test", "Recall is generally higher for hip and shoulder than for the provisional knee class. The test contains 26 hip, 14 knee and 15 shoulder images.", [("var(--c1)", "Hip"), ("var(--c2)", "Knee"), ("var(--c3)", "Shoulder")])}</div>
<div style="margin-top:18px"><h3>Where the errors go</h3><div class="two" id="chart-conf"></div></div></div>

<div id="t-lodo" class="panel" role="tabpanel" hidden>
{chart("chart-lodo", "Leave-one-source-out", "Each group: the source held out of training. Bars: recall of that source's (single) joint. Knee sources transfer to each other; the only hip-implant and shoulder-implant sources do not.", [("var(--c1)", "EfficientNet-B3 FT"), ("var(--c2)", "Swin-T FT"), ("var(--c3)", "Swin-T probe"), ("var(--c4)", "EfficientNet-B3 probe"), ("var(--c5)", "ConvNeXt-T probe")])}
<div style="margin-top:18px">{chart("chart-share", "What the model predicts for the held-out implant sources", "Fine-tuned EfficientNet-B3. Hip implants → called shoulder; shoulder implants → called hip.", [("var(--c1)", "Hip"), ("var(--c2)", "Knee"), ("var(--c3)", "Shoulder")])}</div>
<div class="callout warn"><b>Interpretation limit</b>Implant presence is perfectly aligned with source here (hip and shoulder sources are implant images; no knee source is). It is a plausible confound, not a demonstrated cause.</div></div>

<div id="t-short" class="panel" role="tabpanel" hidden>
<span id="shortcut"></span>{chart("chart-shortcut", "Shortcut controls and image-feature baselines", "Random forests use the listed features (pooled 0.88–0.97; decoupled 0.33–0.61). Dimensions and metadata contain no anatomy; image-derived features such as HOG can contain anatomical information. Frozen probes with image content: pooled ≈0.99, decoupled 0.50–0.66.", [("var(--c1)", "Pooled random test"), ("var(--c2)", "Source-decoupled test")])}
<div class="two" style="margin-top:18px">{chart("chart-decode", "Is the source still decodable after pre-processing?", "Within each joint, can a linear classifier on frozen embeddings tell which source an image came from? Mean balanced accuracy over hip, knee and shoulder (chance 0.33–0.50), development data, 5-fold group CV.")}
{chart("chart-variants", "Does removing cues rescue the decoupled score?", "No variant restores strong transfer; border removal and implant-blob inpainting are only partial controls.", [("var(--c1)", "EfficientNet-B3"), ("var(--c2)", "ConvNeXt-T"), ("var(--c3)", "Swin-T")])}</div></div>

<div id="t-rel" class="panel" role="tabpanel" hidden>
<div class="toolbar"><label class="small muted" for="ood-score">Unknown-joint score</label><select id="ood-score"><option value="msp">Max softmax probability</option><option value="energy">Energy</option><option value="mahalanobis">Mahalanobis (probes)</option></select></div>
{chart("chart-ood", "Unknown-joint detection (AUROC)", "Detecting hand and non-knee leg images. Good when pooled, weaker or uninformative under source shift. Secondary analysis.", [("var(--c1)", "Pooled evaluation"), ("var(--c2)", "Source-decoupled evaluation")])}
<div class="two" style="margin-top:18px"><div><div class="toolbar"><label class="small muted" for="cal-model">Model</label><select id="cal-model"><option value="ft|effnet|full">EfficientNet-B3 (fine-tuned)</option><option value="ft|swin|full">Swin-T (fine-tuned)</option></select></div>{chart("chart-cal", "Calibration (ECE)", "Temperature scaling fitted on in-distribution data does not rescue held-out sources.", [("var(--c1)", "Raw"), ("var(--c3)", "Temperature-scaled")])}</div>
{chart("chart-rc", "Selective prediction", "Keeping only the most-confident predictions helps on pooled data; under source shift the confident half stays wrong (accuracy ≤ 0.10 in the implant holdouts).")}</div></div>
</div></section>
{sec(DISC, "tight")}''', ["home-results.js"])

# ---------------- RESEARCH ----------------
P["research.html"] = page("research.html", "Research", "Question, hypotheses, contributions and what the study does not claim.", head("Research", "A narrow question, tested before looking", "Can conventional pooled evaluation of public orthopaedic radiograph datasets substantially overestimate anatomical generalisation because joint labels are confounded with source and acquisition characteristics?") + f'''
{sec(f"""<div class="two"><div><h2>Pre-specified primary hypothesis</h2><p><b>H1.</b> Pooled-minus-decoupled balanced accuracy exceeds 0.10 for the primary models (clustered paired bootstrap, Holm correction over five primary models).</p>
<p>Result: supported for {M["h1"]["supported"]} of {M["h1"]["of"]}; gaps {gmin:.2f}–{gmax:.2f}; Holm-adjusted p = 0.0025. Further secondary hypotheses (H2–H5) and all deviations are recorded in the <a href="downloads/FROZEN_analysis_plan.md">frozen analysis plan</a>.</p>
<h3>Contributions</h3><ol><li>A quantified gap between pooled and source-decoupled evaluation across handcrafted baselines, three frozen backbones and three fine-tuned networks.</li><li>Evidence that features with no anatomy (dimensions, file metadata) reproduce pooled performance and fall to chance when decoupled.</li><li>Characterisation of leave-one-source-out failure for implant-only sources, with explicit causal caveats.</li><li>A reliability analysis: unknown-joint detection, calibration and selective prediction degrade under source shift.</li></ol></div>
<div><h2>What this study does not claim</h2><ul><li>No new classifier and no clinical tool.</li><li>No claim that these models fail in hospitals — there is no hospital-level external validation.</li><li>No causal claim about implants; they are a plausible source-associated confound.</li><li>No claim of being the first to describe shortcut learning in medical imaging; related work includes Badgeley 2019, DeGrave 2021 and Hill 2024 (knee). Our search was targeted, not systematic.</li></ul>
<div class="callout"><b>Strongest, safest sentence</b>In these public collections, pooled evaluation overstated anatomical generalisation by 0.31–0.50 balanced accuracy on the three-class endpoint; part of the pooled performance is attributable to image properties unrelated to anatomy.</div></div></div>""")}
{sec(DISC, "tight")}''')

# ---------------- DATASETS ----------------
rows = "".join(f'<tr><td><b>{s["id"]}</b> · {s["name"]}</td><td class="mono">{s["hip"]}/{s["knee"]}/{s["shoulder"]}</td><td>{s["provenance"]}</td><td>{s["licence"]}</td><td>{s["implants"]}</td><td>{s["note"]}</td></tr>' for s in D["sources"])
P["datasets.html"] = page("datasets.html", "Datasets", "Six public sources, how they relate to joints, and what is and is not known about them.", head("Datasets", "Six public sources, one with all three joints", f"{M['n_images']:,} target images. FracAtlas is the only source that contains hip, knee and shoulder together, which makes the source-decoupled test possible. Counts are hip/knee/shoulder images.") + f'''
{sec(f"""<div class="tablewrap"><table class="data"><thead><tr><th>Source</th><th>Hip/Knee/Shoulder</th><th>Provenance</th><th>Licence (as reported)</th><th>Implants</th><th>Notes</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="callout warn"><b>Provisional knee labels</b>The 94 FracAtlas knee images were labelled by visual inspection by an AI model, not by a clinician. A clinician review protocol and blinded review tool are prepared; results will be reported alongside the original-label analysis. Licences are as reported by the hosts and some need rights clarification (see <a href="downloads/dataset_licences.md">dataset licence notes</a>).</div>
<figure class="card" style="margin:22px 0 0"><img src="assets/figures/F2_dataset_composition.png" alt="Dataset composition by source and joint" loading="lazy" decoding="async"><figcaption class="small muted">Figure 2. Dataset composition (study figure).</figcaption></figure>
<h3 style="margin-top:28px">Not used</h3><p>MURA, LERA and MRKR require data-use agreements and were not accessed. They are discussed as <i>useful extensions</i> (LERA as an independent replication), not as necessary for the central claim — see the <a href="downloads/External_data_necessity_memo.md">necessity memo</a>. No data were added to strengthen the results.</p>""")}
{sec(DISC, "tight")}''')

# ---------------- METHODOLOGY ----------------
def algorithm_comparison():
    artifact = ROOT / "artifacts/retraining/algorithm-comparison.json"
    if not artifact.is_file():
        return ""
    comparison = json.loads(artifact.read_text(encoding="utf-8"))
    pooled = comparison["protocols"]["pooled"]
    held = comparison["protocols"]["without_fracatlas"]
    held_scores = {row["model"]: row for row in held["scores"]}
    rows = "".join(
        f'<tr><th scope="row">{escape(row["model"])}</th>'
        f'<td>{row["balanced_accuracy"]:.1%}</td>'
        f'<td>{held_scores[row["model"]]["balanced_accuracy"]:.1%}</td>'
        f'<td>{held_scores[row["model"]]["macro_f1"]:.3f}</td></tr>'
        for row in pooled["scores"]
    )
    clusters = "".join(
        f'<tr><th scope="row">{escape(row["method"])}</th><td>{row["anatomy_ari"]:.3f}</td>'
        f'<td>{row["source_ari"]:.3f}</td><td>{row["silhouette"]:.3f}</td></tr>'
        for row in comparison["clustering"]
    )
    shutil.copy2(artifact, SITE / "downloads" / artifact.name)
    return sec(f"""
<div id="algorithm-comparison">
<h2>Which algorithms work best?</h2>
<p>We compared six supervised methods on frozen EfficientNet-B3 image features reduced to 64 components with PCA. Scaling and PCA were fitted on training data for each setting.</p>
<p>The pooled comparison used {pooled["n_val"]} validation images. The source-holdout comparison trained without FracAtlas and evaluated {held["n_val"]} FracAtlas validation images. These are exploratory three-class development comparisons. The cohorts differ in composition and size.</p>
<div class="tablewrap"><table><caption>Hip, Knee and Shoulder classifier comparison</caption>
<thead><tr><th scope="col">Algorithm</th><th scope="col">Pooled balanced accuracy</th><th scope="col">FracAtlas holdout balanced accuracy</th><th scope="col">Holdout macro-F1</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p>The highest held-source balanced accuracy in this comparison came from <strong>{escape(held["best"])}</strong>. The live workbench uses a separately trained six-region model.</p>
<h3>Do the images cluster by joint or source?</h3>
<p>K-means, Gaussian mixtures fitted with EM, and hierarchical clustering grouped the image features without using joint labels. Adjusted Rand index measures agreement with joint or dataset labels. A value near zero indicates chance-level agreement.</p>
<div class="tablewrap"><table><caption>Clustering on the pooled validation cohort</caption><thead>
<tr><th scope="col">Method</th><th scope="col">Joint agreement (ARI)</th><th scope="col">Source agreement (ARI)</th><th scope="col">Silhouette</th></tr>
</thead><tbody>{clusters}</tbody></table></div>
<p class="small">Hierarchical clustering groups the validation cohort directly. K-means and the Gaussian mixture assign validation images to groups learned from training images.</p>
<p>Linear regression targets continuous values, while this task predicts discrete joint labels. Hidden Markov models use ordered observations, while the workbench scores individual X-rays.</p>
<p><a href="downloads/{artifact.name}">Download the comparison results</a></p>
</div>""")



P["methodology.html"] = page("methodology.html", "Methodology", "Group-aware splits, freeze-before-test, sealed test partition, clustered bootstrap, and the pre-registered evaluation protocols.", head("Methodology", "Freeze first, open the test once", "A short tour of how the evaluation was constrained to limit analyst degrees of freedom.") + f'''
{sec(f"""<div class="two"><ol class="timeline"><li><b>Leakage audit &amp; benchmark</b><br><span class="muted">Hash-based duplicate and near-duplicate checks; group-aware splits; {M["n_train"]:,} train / {M["n_val"]} validation / {M["n_test"]} sealed test images.</span></li>
<li><b>Development study</b><br><span class="muted">All model selection on training/validation partitions only.</span></li><li><b>Freeze</b><br><span class="muted">Analysis plan, statistics, code and recipes recorded with SHA-256 hashes before any test image was opened.</span></li>
<li><b>Single unsealing</b><br><span class="muted">{M["n_checkpoints"]} checkpoints evaluated once; the test set refuses to be re-opened; a touch-log records the access.</span></li><li><b>Frozen statistics</b><br><span class="muted">Clustered paired bootstrap (B = 2000, seed 20261004), Holm over five primary models.</span></li><li><b>Independent audit</b><br><span class="muted">{M["n_audit_checks"]} automated checks recompute metrics, verify hashes and disjointness.</span></li></ol>
<div><h3>Evaluation protocols</h3><ul><li><b>Pooled random split</b> — the conventional setting.</li><li><b>Source-decoupled</b> — train without FracAtlas, test on FracAtlas (n = 55).</li><li><b>Leave-one-source-out</b> — hold out each of K, U, A, G, O.</li><li><b>Same-source control</b> — identical images scored by models with and without FracAtlas in training.</li></ul>
<h3>Models</h3><p>Random forests on anatomy-free features; frozen ImageNet backbones with linear probes (EfficientNet-B3, ConvNeXt-T, Swin-T); fine-tuned networks (3 seeds for EfficientNet-B3 and Swin-T, one for ConvNeXt-T). Input: greyscale, resized to 160 px.</p>
<h3>Metrics</h3><p>Balanced accuracy (chance 0.333), macro-F1, ECE with temperature scaling, AUROC for unknown-joint detection, risk–coverage curves.</p>
<div class="callout"><b>Disclosed deviations</b>Amendment A1 (fewer seeds for secondary holdouts) and deviations D1 (a missing import fixed before any test image was opened) and D2 (an evaluation process restarted before outputs existed). The post-hoc sensitivity analyses are labelled exploratory.</div></div></div>
<figure class="card" style="margin:22px 0 0"><img src="assets/figures/F1_workflow.png" alt="Study workflow" loading="lazy" decoding="async"><figcaption class="small muted">Figure 1. Study workflow.</figcaption></figure>""")}{algorithm_comparison()}{sec(DISC, "tight")}''')

# ---------------- LIMITATIONS ----------------
P["limitations.html"] = page("limitations.html", "Limitations", "What this study can and cannot support.", head("Limitations", "What this study cannot show", "Stated plainly, because the headline result is easy to over-read.") + f'''
{sec(f"""<div class="cards">
<div class="card reveal"><h3>One decoupled source</h3><p>The decoupled test rests on FracAtlas (three hospitals; 55 test images). It cannot separate general source effects from FracAtlas-specific ones.</p></div>
<div class="card reveal"><h3>Provisional knee labels</h3><p>94 FracAtlas knee images were labelled by an AI model and are not clinician-verified. A hip/shoulder-only sensitivity analysis shows the gap narrows to 0.10–0.34 without the knee class.</p></div>
<div class="card reveal"><h3>Implants are a confound, not a cause</h3><p>Hip and shoulder sources are implant images; no knee source is. We cannot attribute failure to implants. The inpainting proxy is weak.</p></div>
<div class="card reveal"><h3>Public-data provenance</h3><p>Some images were compiled from publications or web pages; patient-level leakage within a source cannot be excluded; licences are heterogeneous.</p></div>
<div class="card reveal"><h3>Limited compute</h3><p>Three epochs at 160 px on a 2 GB GPU; ConvNeXt-T has one seed. The study did not test whether longer training or higher-resolution inputs change the gap.</p></div>
<div class="card reveal"><h3>No clinical validation</h3><p>The study concerns evaluation of joint recognition on public data — not deployment, fracture detection or implant identification.</p></div>
<div class="card reveal"><h3>Targeted literature search</h3><p>Not systematic; the absence of a directly comparable study is a statement about our search only.</p></div>
<div class="card reveal"><h3>Self-recorded freeze</h3><p>Pre-registration was hash-recorded locally, not deposited in an independent registry.</p></div></div>
<p style="margin-top:22px">The full list (14 items) is in the <a href="paper.html">manuscript</a>. Demo outputs here inherit all of these limits.</p>""")}{sec(DISC, "tight")}''')

# ---------------- PAPER ----------------
P["paper.html"] = page("paper.html", "Paper", "The manuscript, figures and supporting documents.", head("Paper", "Manuscript", "Draft manuscript generated from the frozen, hash-recorded analyses. Not peer-reviewed; authors and affiliations to be added before submission.") + f'''
{sec(f"""<div class="two"><div class="card"><h3>Pooled public data overstate orthopaedic joint recognition: a pre-specified, source-controlled evaluation of shortcut learning in hip, knee and shoulder radiographs</h3>
<p class="muted">25 pages · draft</p><div class="cta-row" style="display:flex;gap:10px;flex-wrap:wrap">{'<a class="btn primary" href="downloads/manuscript.pdf">PDF</a>' if have("manuscript.pdf") else ''}{'<a class="btn" href="downloads/manuscript.docx">Word</a>' if have("manuscript.docx") else ''}{'<a class="btn" href="downloads/manuscript.md">Markdown</a>' if have("manuscript.md") else ''}</div></div>
<div class="card"><h4>Supporting documents</h4><ul>
<li><a href="downloads/FROZEN_analysis_plan.md">Frozen analysis plan</a></li><li><a href="downloads/Peer_Review_Simulation.md">Simulated peer review</a></li><li><a href="downloads/Pre_submission_fix_list.md">Pre-submission fix list</a></li>
<li><a href="downloads/External_data_necessity_memo.md">External data necessity memo</a></li><li><a href="downloads/clinician_review_PROTOCOL.md">Clinician review protocol</a></li>{'<li><a href="downloads/Submission_readiness_checklist.md">Submission readiness checklist</a></li>' if have("Submission_readiness_checklist.md") else ''}</ul></div></div>
<h3 style="margin-top:30px">Figures</h3><div class="cards">""" + "".join(f'<figure class="card" style="margin:0"><img src="assets/figures/{f}.png" alt="{t}" loading="lazy" decoding="async"><figcaption class="small muted">{t} <a href="assets/figures/{f}.webp" aria-label="Open full-size {t.lower()}">Full size</a></figcaption></figure>' for f, t in [("F3_shortcut_evidence", "Figure 3. Shortcut evidence"), ("F4_pooled_vs_decoupled", "Figure 4. Pooled vs decoupled"), ("F5_leave_one_source_out", "Figure 5. Leave-one-source-out"), ("F6_confusion_matrices", "Figure 6. Confusion matrices"), ("F7_ood_reliability", "Figure 7. OOD and reliability")]) + "</div>")}{sec(DISC, "tight")}''')

# ---------------- REPRODUCIBILITY ----------------
P["reproducibility.html"] = page("reproducibility.html", "Reproducibility", "Code, frozen plan, audit and artifacts.", head("Reproducibility", "Check it yourself", "Everything needed to re-derive the reported numbers from the frozen artifacts, apart from the third-party image data, which must be downloaded from the original hosts.") + f'''
{sec(f"""<div class="two"><div><h3>What is included</h3><ul><li>Pipeline scripts and the step-by-step guide (<a href="downloads/REPRODUCIBILITY.md">REPRODUCIBILITY.md</a>)</li><li>Frozen analysis plan with SHA-256 hashes (<a href="downloads/FROZEN_analysis_plan.md">plan</a>)</li><li>Independent audit script with {M["n_audit_checks"]} checks (<a href="downloads/audit_results.py">audit_results.py</a>)</li><li>Pinned environment (<a href="downloads/requirements.txt">requirements.txt</a>: Python 3.11, torch 2.4.1, scikit-learn 1.9.0)</li><li>Per-checkpoint hashes; this site's API reports the SHA-256 prefix of the four demo checkpoints at <code>/api/health</code></li></ul>
<div class="callout warn"><b>Not included</b>Source images (licences differ; download from the original hosts) and the full set of 29 checkpoints. Fine-tuning is not bit-reproducible on GPU; third decimals may vary.</div></div>
<div><h3>Expected key outputs</h3><div class="tablewrap"><table class="data"><tbody><tr><th>Pooled BA, 5 primary models</th><td>0.993–1.000</td></tr><tr><th>Decoupled BA</th><td>0.498–0.686</td></tr><tr><th>H1 supported</th><td>5 / 5 (Holm p = 0.0025)</td></tr><tr><th>RF on metadata / dimensions, pooled → decoupled</th><td>0.960 / 0.971 → 0.333</td></tr><tr><th>Audit checks</th><td>{M["n_audit_checks"]} / {M["n_audit_checks"]} pass</td></tr></tbody></table></div>
<h3 style="margin-top:22px">Run this site</h3><pre class="mono small" style="background:var(--surface-2);padding:14px;border-radius:12px;overflow:auto">pip install -r site/api/requirements.txt
cd site/api &amp;&amp; uvicorn app:app --port 8000
# open http://localhost:8000</pre><p class="small muted">Without the API, the demo falls back to precomputed sample outputs and labels itself accordingly.</p></div></div>""")}{sec(DISC, "tight")}''')

# ---------------- ABOUT ----------------
P["about.html"] = page("about.html", "About", "About this research demonstration.", head("About", "About this project", "OrthoTrace is an independent research website built to present a source-controlled evaluation of orthopaedic joint recognition. It was designed from scratch; it is not affiliated with, or derived from, any commercial product.") + f'''
{sec(f"""<div class="two"><div><h3>Authors &amp; affiliations</h3><p>To be completed before submission (see the author and declarations template in the project). Until then, no authorship, funding or conflict-of-interest statement is made on this site.</p>
<h3>Status</h3><ul><li>Manuscript: draft, not peer-reviewed.</li><li>Clinician verification of the 94 FracAtlas knee labels: pending.</li><li>Ethics: public, de-identified datasets only; no new patient data.</li></ul></div>
<div><h3>Responsible use</h3><p>This site demonstrates evaluation methodology. The models name a joint and nothing else. They must not be used for diagnosis, triage, implant identification or any patient-facing purpose. Please do not upload identifiable images.</p>
<h3>Acknowledgements &amp; data</h3><p>Dataset creators are credited on the <a href="datasets.html">Datasets</a> page; licences as reported by the hosts.</p></div></div>""")}{sec(DISC, "tight")}''')

def webp_imgs(html):
    def rep(m):
        f = m.group(1); w, h = FIGDIM.get(f, (None, None))
        return f'<img src="assets/figures/{f}.webp"' + (f' width="{w}" height="{h}"' if w else "")
    return re.sub(r'<img src="assets/figures/([^".]+)\.png"', rep, html)


def versioned(html):
    def rep(m):
        p = SITE / m.group(1)
        return f'{m.group(1)}?v={hashlib.sha256(p.read_bytes()).hexdigest()[:10]}"' if p.exists() else m.group(0)
    return re.sub(r'(assets/(?:css|js|vendor)/[^"?]+\.(?:css|js))"', rep, html)


# Product entry point is generated from the same real sample and result artifacts.
example = next((s for s in _smp if not s['all_agree']), _smp[0])
main, shifted = example['models'][0], next(m for m in example['models'] if m['id'] == 'no_fracatlas')
from showcase import pages as showcase_pages
P.update(showcase_pages(page, head, sec, DISC, ROOT, D))
from border_page import make_page as border_page
P['border-audit.html'] = border_page(page, head, sec)
from implant_history import make_page as history_page
P['timeline.html'] = history_page(page, head, sec, DISC)
from presentation import intro as presentation_intro
for name in ['robustness', 'results']:
    P[name+'.html'] = P[name+'.html'].replace('</section>', '</section>'+presentation_intro(name), 1)
P['guide.html'] = clarity.guide_page(page, head, sec)
(SITE / 'assets/js/terms.js').write_text(clarity.terms_js(), encoding='utf-8')
home = clarity.tune_home((SITE / 'reference_home.html.template').read_text(encoding='utf-8'))
lab_samples = [{k:v for k,v in s.items() if k != 'gradcam'} for s in _smp if s['id'] in ['sample2','sample5','sample8']]
(SITE / 'data/lab_samples.json').write_text(json.dumps(lab_samples, separators=(',',':')),encoding='utf-8')
checkpoint_receipts = ''.join(f'<article class="compact-receipt"><span>0{i+2}</span><div><h3>{escape(model["name"])}</h3><p>{escape(model["description"])}</p></div><div class="compact-output"><b>{escape(model["pred"])}</b><span>{model["confidence"]*100:.1f}%</span></div></article>' for i,model in enumerate(example['models'][1:]))
values = dict(sample_file=example['file'], sample_width=example['image']['width'], sample_height=example['image']['height'],
              sample_note='Saved predictions. The recorded knee label is provisional.' if example['true_label'] == 'Knee' else 'Saved predictions for this FracAtlas specimen.',
              prediction=main['pred'], confidence=f"{main['confidence']*100:.1f}",
              shift_prediction=shifted['pred'], shift_confidence=f"{shifted['confidence']*100:.1f}",
              sample_number=example['id'].replace('sample',''), n_images=f"{M['n_images']:,}", n_test=M['n_test'],
              pooled=f"{ee['pooled']:.3f}", decoupled=f"{ee['decoupled']:.3f}",
              pooled_percent=ee['pooled']*100, decoupled_percent=ee['decoupled']*100, disclaimer=DISC,
              checkpoint_receipts=checkpoint_receipts,dimension_gap=f"{(G['rf|dims_only']['pooled']-G['rf|dims_only']['decoupled'])*100:.1f}")
for key, value in values.items(): home = home.replace('{{' + key + '}}', str(value))
P['index.html'] = page('index.html', 'Radiograph evaluation workbench',
    'Explore implants, compare real X-ray checkpoints and investigate source bias with live inference and reproducible evidence.', home, bodycls='experience-page')
for fn, html in P.items():
    html = html.replace('</head>', '<link rel="stylesheet" href="assets/css/product.css"><link rel="stylesheet" href="assets/css/experience.css"></head>')
    html = html.replace('</head>', '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@96,82,400..800&amp;family=Geist:wght@400;500;600&amp;family=Geist+Mono:wght@400;500&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="assets/css/studio.css"></head>')
    if fn == 'timeline.html': html = html.replace('</head>', '<link rel="stylesheet" href="assets/css/timeline.css"></head>')
    if fn == 'timeline.html': html = html.replace('<link rel="stylesheet" href="assets/css/studio.css">', '').replace('</head>', '<link rel="stylesheet" href="assets/css/studio.css"></head>')
    html = html.replace('</head>', '<link rel="stylesheet" href="assets/css/reference.css"></head>')
    html = html.replace('</head>', '<link rel="stylesheet" href="assets/css/readability.css"></head>')
    html = html.replace('</head>', '<link rel="stylesheet" href="assets/css/clarity.css"></head>')
    html = clarity.add_plain(fn, html)
    if fn in ['results.html','robustness.html']:
        html = html.replace('<body class="">','<body class="data-page">')
    html = html.replace('<script src="assets/js/app.js"></script>', '<script src="assets/js/app.js"></script><script src="assets/js/film.js"></script>')
    html = html.replace('</body>', '<script src="assets/js/experience.js"></script><script src="assets/js/terms.js"></script></body>')
    if fn == 'index.html': html = html.replace('</body>', '<script src="assets/js/studio.js"></script></body>')
    if fn == 'index.html': html = html.replace('</body>', '<script src="assets/js/reference.js"></script></body>')
    html = html.replace('#F4F0E6', '#091724')
    html = html.replace('<div><p class="fh">Explore</p><ul>', '<div><p class="fh">Explore</p><ul><li><a href="context.html">Implants & imaging</a></li><li><a href="contribution.html">Our contribution</a></li><li><a href="literature.html">Literature survey</a></li><li><a href="evaluation.html">Evidence hub</a></li>')
    html = re.sub(r'<div class="curtain" aria-hidden="true">.*?</div>', '', html)
    html = re.sub(r'<div class="research-banner">.*?</div>', '', html)
    html = html.replace('research demonstration','academic project').replace('Research demonstration','Academic project').replace('Research Demonstration','Academic Project')
    html = html.replace('A academic project — not a medical device and not clinically validated.', 'Built as an academic project in source-aware orthopaedic AI.')
    html = html.replace('<div><p class="fh">Explore</p><ul>', '<div><p class="fh">Explore</p><ul><li><a href="guide.html">Start here</a></li>', 1)
    html = html.replace('AI Demo', 'Workbench').replace('Study ▾', 'Evidence ▾')
    html = html.replace('An independent research website for a pre-specified, source-controlled evaluation of hip, knee and shoulder radiograph recognition.', 'A model evaluation workbench for hip, knee and shoulder radiographs. Compare checkpoints and investigate source sensitivity.')
    (SITE / fn).write_text(versioned(webp_imgs(fix_headings(html))), encoding="utf-8")
(SITE / "assets/favicon.svg").write_text((SITE / "assets/logo.svg").read_text(encoding="utf-8"), encoding="utf-8")
print("built", len(P), "pages")
