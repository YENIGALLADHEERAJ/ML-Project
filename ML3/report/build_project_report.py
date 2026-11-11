"""Build the OrthoTrace project report in the department template format.

Usage (from repo root):
    .venv\\Scripts\\python.exe -X utf8 ML3/report/build_project_report.py "<template.docx>" ML3/report/OrthoTrace_Project_Report.docx

Content comes from ML3/paper/manuscript.md (frozen, audited numbers); figures from
ML3/paper/figures. Formatting follows the template's guideline table: A4, Times New Roman,
chapter 16 pt bold caps centred, section 14 pt bold, sub-section 12 pt bold, body 12 pt justified,
1.5 spacing, 6 pt after, margins L 1.5" / R,T,B 1", captions 11 pt bold, tables 11 pt,
code Consolas 10 pt single, roman page numbers for preliminaries, arabic from Chapter 1.
"""
import os
import re
import sys

import docx
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ML3
PAPER = os.path.join(ROOT, "paper")
TEMPLATE, OUT = sys.argv[1], sys.argv[2]
FONT = "Times New Roman"
PROJECT_TITLE = "OrthoTrace: Source-Controlled Evaluation of Orthopaedic Joint Recognition and an Inspectable X-ray Model Workbench"

# ----------------------------------------------------------------------------- manuscript parsing
md = open(os.path.join(PAPER, "manuscript.md"), encoding="utf-8").read()
secs = {}
cur = None
for line in md.splitlines():
    m = re.match(r"^## (\d+)\. (.*)$", line)
    if m:
        cur = m.group(1)
        secs[cur] = {"title": m.group(2), "lines": []}
    elif re.match(r"^## ", line):
        cur = None  # Declarations etc.
    elif cur:
        secs[cur]["lines"].append(line)
decl = re.search(r"^## Declarations\n(.*?)(?=^## )", md, flags=re.S | re.M)

# references -> numbered list
refs = []
for ln in secs["23"]["lines"]:
    m = re.match(r"^(\d+)\. (.*)$", ln)
    if m:
        refs.append((int(m.group(1)), m.group(2)))
ref_note = next((l for l in secs["23"]["lines"] if l.startswith("Verification status")), "")
ref_index = []
for n, text in refs:
    sur = re.match(r"^([A-Za-z'’\-À-ſ]+)", text).group(1).lower()
    years = set(re.findall(r"\b((?:19|20)\d\d)\b", text[:400]))
    ref_index.append((n, sur, years))
unresolved = set()


def cite_sub(match):
    inner = match.group(1)
    nums = []
    for tok in inner.split(";"):
        tok = tok.strip()
        m = re.match(r"^([A-Za-z'’\-À-ſ]+)(?: et al\.?| and [A-Z][\w\-]+| & [A-Z][\w\-]+)?,? ((?:19|20)\d\d)[a-z]?(?: \([^)]*\))?$", tok)
        if not m:
            return match.group(0)
        sur, yr = m.group(1).lower(), m.group(2)
        hit = [n for n, s, ys in ref_index if s == sur and yr in ys]
        if len(hit) != 1:
            unresolved.add(tok + " -> " + str(hit))
            return match.group(0)
        nums.append(hit[0])
    return "[" + ", ".join(str(n) for n in sorted(set(nums))) + "]"


def cites(text):
    return re.sub(r"\[([A-Z][^\[\]]{2,160}?)\]", cite_sub, text)


# ----------------------------------------------------------------------------- block model
def md_blocks(lines):
    """Turn markdown lines into blocks: ('p',text) ('img',cap,path) ('tbl',rows) ('li',text) ('cap',text)."""
    blocks, i = [], 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        m = re.match(r"^!\[(.*)\]\((.*)\)\s*$", ln)
        if m:
            blocks.append(("img", m.group(1), m.group(2)))
            i += 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append(("tbl", rows))
            continue
        if re.match(r"^[-*] ", ln):
            blocks.append(("li", ln[2:]))
            i += 1
            continue
        if re.match(r"^\d+\. ", ln):
            blocks.append(("nli", ln))
            i += 1
            continue
        if re.match(r"^\*\*Table (P1|S\d|\d+b?)\.", ln):
            blocks.append(("cap", ln))
            i += 1
            continue
        if ln.startswith("#") or ln.startswith(">") or ln.startswith("```") or "<" in ln[:2]:
            print("UNHANDLED", ln[:80])
        blocks.append(("p", ln))
        i += 1
    return blocks


def sec_blocks(num):
    return md_blocks(secs[num]["lines"])


# pull figures out of their stored positions and re-home them
fig_store = {}
for num, s in secs.items():
    kept = []
    for b in sec_blocks(num):
        if b[0] == "img":
            fn = int(re.match(r"Figure (\d+)", b[1]).group(1))
            fig_store[fn] = b
        else:
            kept.append(b)
    s["blocks"] = kept


def prose(*paras):
    return [("p", t) for t in paras]


def bullets(*items):
    return [("li", t) for t in items]


FIG_AFTER = {1: ("9", "start"), 2: ("6", "end"), 3: ("8", "end")}
for fn, (sn, where) in FIG_AFTER.items():
    secs[sn]["blocks"] = ([fig_store.pop(fn)] + secs[sn]["blocks"]) if where == "start" else secs[sn]["blocks"] + [fig_store.pop(fn)]
# remaining figures (4-8) were stored without position; re-insert at the end of their results section
FIG_HOME = {4: "11", 5: "11", 6: "14", 7: "13", 8: "14"}
for fn, sn in FIG_HOME.items():
    if fn in fig_store:
        secs[sn]["blocks"].append(fig_store.pop(fn))

# ----------------------------------------------------------------------------- authored sections
INTRO_PROBLEM = prose(
    "Hip, knee and shoulder recognition on pooled public radiograph collections is reported with near-perfect accuracy, "
    "but almost every public collection supplies a single joint, so the joint label is confounded with the data source. "
    "A model can therefore score highly by recognising source-specific properties such as image size, borders, file "
    "metadata or implant appearance without learning anatomy. The problem addressed in this project is to measure how much "
    "pooled evaluation overstates anatomical generalisation, to test which anatomy-free properties explain the overstatement, "
    "and to make the resulting model behaviour inspectable on individual X-rays rather than only in aggregate tables.",
    "**Project objectives.** The study was derived from the research gap in Chapter 2 and has four measurable objectives:",
)
INTRO_OBJ = bullets(
    "**Objective 1.** Measure the difference in balanced accuracy between pooled and source-decoupled Hip, Knee and Shoulder evaluation, pre-specified as a gap larger than 0.10 for at least four of five primary models.",
    "**Objective 2.** Test simple shortcuts using dimensions-only and metadata-only models and paired border interventions.",
    "**Objective 3.** Compare classical classifiers and image models (EfficientNet-B3, ConvNeXt-T, Swin-T) under defined, frozen protocols.",
    "**Objective 4.** Make predictions, disagreements and label conflicts inspectable in a live workbench with saved evidence for offline use.",
)
INTRO_CONTRIB = prose(
    "The contributions of the project are: (i) a leakage-audited six-source benchmark with a sealed, hash-recorded test partition; "
    "(ii) a pre-specified source-controlled evaluation showing pooled-to-decoupled gaps of 0.31–0.50 balanced accuracy; "
    "(iii) anatomy-free baselines that reproduce pooled accuracy and fall to chance when decoupled; "
    "(iv) an automated audit of the frozen evaluation; and (v) the OrthoTrace workbench, a local web application that runs the "
    "checkpoints, a six-region classifier and Grad-CAM on the same image. Implant presence is treated as a plausible "
    "source-associated confound, not a demonstrated cause, and the models are evaluation tools, not diagnostic devices.",
)

IMPL = [
    ("Repository and Software Stack", prose(
        "The implementation is organised so that the research pipeline and the web workbench stay separate. "
        "The research pipeline lives in `ML3/scripts` (dataset manifests and grouped splits, random-forest and CNN experiments, "
        "fine-tuning, frozen-evaluation, statistics and audit scripts). The workbench lives in `ML3/site`: a FastAPI service "
        "(`site/api/app.py`, `site/api/infer.py`), a static site generated by `site/build_site.py`, and vanilla JavaScript front-end "
        "modules in `site/assets/js`. Python 3.11, PyTorch and torchvision, scikit-learn, NumPy, pandas, SciPy, Pillow and OpenCV "
        "are the main libraries; the pinned research environment is recorded in `ML3/requirements.txt`.",
        "A complete Python implementation of the essential scripts is given in Appendix A.")),
    ("Preprocessing and Model Inference", prose(
        "Every uploaded or sample image is validated and decoded in memory, converted to greyscale, resized to 160 × 160 and normalised "
        "with ImageNet statistics. The service loads four EfficientNet-B3 checkpoints on CPU: pooled, trained without FracAtlas, trained "
        "without the Kaggle hip-implant source (K) and trained without the UCI shoulder-implant source (U). The expanded workbench "
        "also scores a center crop with a six-region classifier (Hip, Knee, Shoulder, Hand, Leg, Elbow) and compares each region score "
        "with a development-set cutoff. A pooled Grad-CAM overlay is returned with the predictions. Request bodies are size-limited "
        "(12 MB), rate-limited (30 prediction requests per minute per IP) and static access to backend source and checkpoints is blocked.")),
    ("Working Demonstration", prose(
        "The workbench pipeline is: X-ray → image validation → preprocessing → six-region scores and four benchmark predictions → "
        "Grad-CAM → review record. The report displays each region cutoff and benchmark agreement, and the export omits image pixels and filenames. "
        "Saved specimens remain available when the inference service is offline and are explicitly labelled as saved outputs; uploaded files "
        "never use saved predictions. The service is started with `setup.ps1` followed by `start.ps1` and is opened at "
        "`http://127.0.0.1:8000/demo.html`.")),
    ("Anatomy-Free Shortcut Probe", prose(
        "To make the central finding visible on every image, the workbench adds a shortcut probe (`scripts/build_probe.py`, `site/api/probe.py`). "
        "The probe is a Random Forest that sees only six file-level properties (width, height, aspect, colour mode, PNG flag and file size), never pixels. "
        "It is trained on the development rows of the frozen manifest only, and the sealed test partition is never read. For each analysed image it reports the joint "
        "those properties alone would suggest, the training source the file most resembles, and a verdict on whether the pooled model's answer is shortcut-compatible, "
        "meaning it can be reproduced without looking at anatomy. On development data the probe reached 0.990 balanced accuracy pooled and 0.313 when trained without FracAtlas "
        "(chance 0.333), the same pattern as the frozen-test dimensions-only forests (0.971 falling to 0.333), and it identified the source from file properties alone with 0.996 balanced accuracy. "
        "A shortcut-compatible verdict is not proof that the deep model used a shortcut, and a disagreement does not prove it recognised anatomy; files whose properties fall outside the training range are marked unfamiliar. "
        "The probe is exported as JSON and evaluated in NumPy, so the service needs no extra dependencies.")),
    ("Testing and Verification", prose(
        "The workbench is covered by ten service regression tests (`site/qa/test_service.py`), a static audit of all pages "
        "(`site/qa/qa_audit.py`: link resolution, asset references, headings, image alternatives, external resources) and an API check "
        "(`site/qa/qa_api.py`). The research side is covered by `scripts/audit_results.py`, which verifies that the manifest hash matches the freeze, "
        "that 657 test rows exist, that no training set contains a test path, that the test partition was unsealed once, that 29 checkpoint hashes match "
        "and that recomputed balanced accuracy agrees with the saved summary to within 1.1 × 10⁻¹⁶. All checks passed at the time of writing.")),
    ("Industry Relevance, Deployment and Cost", prose(
        "The intended users are imaging-research and machine-learning evaluation teams that need to inspect model disagreement and "
        "questionable labels on de-identified evaluation images, for example before trusting a pooled score for radiograph routing or label cleaning. "
        "A local CPU check of 12 sequential requests over four bundled X-rays gave a median round-trip time of 305 ms (range 214–395 ms), including both "
        "prediction tracks and Grad-CAM; these timings describe one laptop and a running server. No GPU, database or login is required, so the main cost "
        "drivers are CPU time per request and storage of the checkpoints. A Dockerfile and deployment notes (`site/DEPLOY.md`) are provided for container "
        "deployment. No user study or clinical validation has been performed, and no adoption claim is made.")),
]

RESULTS_EXTRA = [
    ("Classical Source-Holdout Comparison and External Check", prose(
        "Two further experiments support the workbench. A development experiment compared six classical classifiers on the same PCA-reduced EfficientNet-B3 "
        "features with source holdout; the RBF support-vector machine led with 56.5% balanced accuracy on 47 FracAtlas validation images "
        "(`artifacts/retraining/algorithm-comparison.json`). This applies to the three-class development experiment only. An external check on 54 BTXRD images "
        "(`artifacts/retraining/btxrd-mirror-evaluation.json`) found that center-cropping raised Knee detections from 8 to 21 of 37 and reduced extra Elbow flags "
        "from 33 to 16 of 49 (`artifacts/retraining/center-crop-candidates.json`). The same 54 images were reused after inspecting the first run and the elbow subset is small, "
        "so this is an exploratory result and not a confirmatory test. Median local inference time was 305 ms per request (Section 5.6).")),
]

FUTURE = prose(
    "The following extensions are realistic next steps; none is claimed as completed work.",
)
FUTURE_B = bullets(
    "**Fresh external test set.** Evaluate on a source that was never inspected, with the protocol frozen first, to turn the exploratory BTXRD result into a confirmatory one.",
    "**Clinician review.** Run the prepared review protocol on the provisional FracAtlas knee and leg labels, which is the main remaining limitation.",
    "**Larger decoupled cohorts.** Add more sources so that confidence intervals no longer collapse at 0.00–0.00 and the knee-class error can be separated from view shift.",
    "**Shortcut audit tool.** Package the dimensions, metadata and border probes as a one-command shortcut-risk score for any labelled image folder, and show the anatomy-free probe's agreement next to Grad-CAM in the workbench.",
    "**Invariance training and calibration.** Test source-adversarial training and unknown-source detection so that the model can say when an input looks like a new source.",
)

ABSTRACT = (
    "Public orthopaedic radiograph collections usually supply one joint each, so the joint label is confounded with the data source and pooled evaluation may "
    "overstate recognition ability. This project, OrthoTrace, measures that overstatement and exposes it through an inspectable workbench. Six public sources "
    "(4,427 images, of which 657 form a sealed test partition) were organised into leakage-audited, group-aware splits, and the analysis plan was frozen before the "
    "test set was opened. Hip, knee and shoulder recognition was compared under pooled, source-decoupled and leave-one-source-out protocols using random-forest "
    "baselines on anatomy-free features, linear probes on frozen EfficientNet-B3, ConvNeXt-T and Swin-T features, and fine-tuned networks. Pooled balanced accuracy was "
    "0.993–1.000 for the five primary models but fell to 0.498–0.686 on the source-decoupled test (gap 0.31–0.50; adjusted p = 0.002; hypothesis supported for 5 of 5 models). "
    "Random forests using only image dimensions or file metadata reached 0.971 and 0.960 pooled and chance level (0.333) when decoupled, and holding out the implant-bearing "
    "sources produced balanced accuracy of 0.00–0.17 with confident, systematic joint swaps. A local web workbench returns six-region scores, four benchmark predictions and Grad-CAM "
    "overlays in a median of 305 ms on CPU. The results show that pooled scores in these collections reflect source properties as well as anatomy, so source-decoupled reporting "
    "and anatomy-free baselines are recommended. Clinical validity was not tested and the knee labels remain provisional."
)

ABBREVIATIONS = [
    ("AUPR", "Area Under the Precision–Recall curve"), ("AUROC", "Area Under the Receiver Operating Characteristic curve"),
    ("BA", "Balanced Accuracy"), ("BTXRD", "Bone Tumor X-ray Radiograph Dataset"), ("CI", "Confidence Interval"),
    ("CNN", "Convolutional Neural Network"), ("CPU", "Central Processing Unit"), ("ECE", "Expected Calibration Error"),
    ("Grad-CAM", "Gradient-weighted Class Activation Mapping"), ("HOG", "Histogram of Oriented Gradients"),
    ("LOSO", "Leave-One-Source-Out"), ("OOD", "Out-of-Distribution"), ("PCA", "Principal Component Analysis"),
    ("RF", "Random Forest"), ("SVM", "Support Vector Machine"),
]

# chapters: (title, [(section title, blocks)])
CHAPTERS = [
    ("Introduction", [
        ("Background, Motivation and Scope", secs["3"]["blocks"]),
        ("Problem Statement and Objectives", INTRO_PROBLEM + INTRO_OBJ),
        ("Contributions", INTRO_CONTRIB),
    ]),
    ("Literature Survey", [("Related Work", secs["4"]["blocks"]), ("Research Gap", secs["5"]["blocks"])]),
    ("Datasets and Data Analysis", [("Dataset Construction", secs["6"]["blocks"]), ("Data-Leakage Audit", secs["7"]["blocks"])]),
    ("Proposed Methodology and System Architecture", [
        ("Study Workflow and Experimental Protocol", secs["9"]["blocks"]),
        ("Models", secs["10"]["blocks"]),
        ("Statistical Analysis", secs["15"]["blocks"]),
    ]),
    ("Implementation and Demonstration", IMPL),
    ("Results and Performance Evaluation", [
        ("Shortcut Analysis", secs["8"]["blocks"]),
        ("Source-Controlled Evaluation", secs["11"]["blocks"]),
        ("Cross-Dataset Evaluation", secs["12"]["blocks"]),
        ("Out-of-Distribution and Reliability Analysis", secs["13"]["blocks"]),
        ("Error Analysis", secs["14"]["blocks"]),
        ("Summary of Confirmatory Outcomes", secs["16"]["blocks"]),
    ] + RESULTS_EXTRA),
    ("Integrated Discussion and Limitations", [
        ("Discussion", secs["17"]["blocks"]), ("Limitations", secs["18"]["blocks"]), ("Research Implications", secs["19"]["blocks"]),
    ]),
    ("Overall Conclusion and Future Scope", [
        ("Conclusion", secs["20"]["blocks"]), ("Future Scope", FUTURE + FUTURE_B),
        ("Data, Code and Ethics Statement", secs["21"]["blocks"] + secs["22"]["blocks"]),
    ]),
]
# implementation sections are (title, blocks) already; IMPL tuples fit the same shape
APPX_B_BLOCKS = secs["24"]["blocks"]

# ----------------------------------------------------------------------------- numbering of figures/tables
fig_no, tbl_no, label_map = {}, {}, {}


def label_of(block, chap, counters):
    if block[0] == "img":
        old = re.match(r"Figure (\w+)", block[1]).group(1)
        kind = "Figure"
    elif block[0] == "cap":
        m = re.match(r"\*\*Table (P1|S\d|\d+b?)\.", block[1])
        old, kind = m.group(1), "Table"
    else:
        return None
    key = (kind, chap)
    counters[key] = counters.get(key, 0) + 1
    new = f"{chap}.{counters[key]}"
    label_map[(kind, old)] = new
    return kind, old, new


counters = {}
numbered = []  # parallel structure to CHAPTERS with labels
for ci, (ctitle, sections) in enumerate(CHAPTERS, 1):
    for stitle, blocks in sections:
        for b in blocks:
            label_of(b, str(ci), counters)
for b in APPX_B_BLOCKS:
    label_of(b, "B", counters)


def renumber(text):
    def sub(m):
        kind, old = m.group(1), m.group(2)
        return f"{kind} {label_map.get((kind, old), m.group(0).split(' ', 1)[1])}"
    return re.sub(r"\b(Figure|Table)s? (P1|S\d|\d+b?)\b(?![.\d]*\d)", sub, text)


# ----------------------------------------------------------------------------- docx helpers
doc = docx.Document(TEMPLATE)
body = doc.element.body
children = list(body)
for el in children[35:-1]:
    body.remove(el)  # keep cover page (0-34, ends with section break) and the final sectPr

styles = doc.styles


def mkstyle(name, size, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, spacing=1.5, after=6, before=0, font=FONT,
            caps=False, outline=None, page_break=False, keep_next=False, italic=False):
    st = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    st.base_style = styles["Normal"]
    st.font.name = font
    st.font.size = Pt(size)
    st.font.bold = bold
    st.font.italic = italic
    st.font.all_caps = caps
    st.font.color.rgb = RGBColor(0, 0, 0)
    rpr = st.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), font)
    pf = st.paragraph_format
    pf.alignment = align
    pf.line_spacing = spacing
    pf.space_after = Pt(after)
    pf.space_before = Pt(before)
    pf.page_break_before = page_break
    pf.keep_with_next = keep_next
    pf.widow_control = True
    if outline is not None:
        ppr = st.element.get_or_add_pPr()
        ol = OxmlElement("w:outlineLvl")
        ol.set(qn("w:val"), str(outline))
        ppr.append(ol)
    return st


C = WD_ALIGN_PARAGRAPH.CENTER
L = WD_ALIGN_PARAGRAPH.LEFT
mkstyle("RptBody", 12)
mkstyle("RptChapterNo", 16, True, C, page_break=True, keep_next=True, caps=True, after=0)
mkstyle("RptChapter", 16, True, C, keep_next=True, caps=True, outline=0, after=12)
mkstyle("RptFront", 16, True, C, page_break=True, keep_next=True, caps=True, outline=0, after=12)
mkstyle("RptFrontNB", 16, True, C, keep_next=True, caps=True, outline=0, after=12)
mkstyle("RptSection", 14, True, L, keep_next=True, outline=1, before=6)
mkstyle("RptSub", 12, True, L, keep_next=True, outline=2)
mkstyle("RptFigCap", 11, True, C, spacing=1.15, after=10)
mkstyle("RptTblCap", 11, True, L, spacing=1.15, after=4, keep_next=True)
mkstyle("RptCode", 10, False, L, spacing=1.0, after=6, font="Consolas")
mkstyle("RptTbl", 11, False, L, spacing=1.0, after=0)
mkstyle("RptTocEntry", 12, False, L, spacing=1.15, after=3)
mkstyle("RptRef", 12, False, WD_ALIGN_PARAGRAPH.JUSTIFY, spacing=1.15, after=6)
styles["RptRef"].paragraph_format.left_indent = Inches(0.45)
styles["RptRef"].paragraph_format.first_line_indent = Inches(-0.45)
mkstyle("RptBullet", 12)
styles["RptBullet"].paragraph_format.left_indent = Inches(0.4)
styles["RptBullet"].paragraph_format.first_line_indent = Inches(-0.25)


def set_runfont(run, size=None, bold=None, italic=None, mono=False):
    name = "Consolas" if mono else FONT
    run.font.name = name
    rpr = run._r.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic


INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|(?<![\w*])\*[^*\s][^*]*?\*(?![\w*]))")


def add_inline(par, text, size=None, bold=None):
    text = renumber(cites(text))
    for tok in INLINE.split(text):
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            r = par.add_run(tok[2:-2])
            set_runfont(r, size, True)
        elif tok.startswith("`") and tok.endswith("`"):
            r = par.add_run(tok[1:-1])
            set_runfont(r, (size or 12) - 1, bold, mono=True)
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            r = par.add_run(tok[1:-1])
            set_runfont(r, size, bold, italic=True)
        else:
            r = par.add_run(tok)
            set_runfont(r, size, bold)


def para(text="", style="RptBody"):
    p = doc.add_paragraph(style=style)
    if text:
        add_inline(p, text)
    return p


def fld_runs(par, instr, cached, size=None):
    def fc(t):
        r = par.add_run()
        e = OxmlElement("w:fldChar")
        e.set(qn("w:fldCharType"), t)
        r._r.append(e)
        return r
    fc("begin")
    r = par.add_run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instr} "
    r._r.append(it)
    fc("separate")
    rr = par.add_run(cached)
    set_runfont(rr, size)
    fc("end")


def toc_field(instr, entries):
    """Multi-paragraph TOC field with cached entries (Word refreshes page numbers on open)."""
    for i, text in enumerate(entries):
        p = doc.add_paragraph(style="RptTocEntry")
        if i == 0:
            for t in ("begin",):
                r = p.add_run()
                e = OxmlElement("w:fldChar")
                e.set(qn("w:fldCharType"), t)
                r._r.append(e)
            r = p.add_run()
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = f" {instr} "
            r._r.append(it)
            r = p.add_run()
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), "separate")
            r._r.append(e)
        rr = p.add_run(text)
        set_runfont(rr, 12)
        if i == len(entries) - 1:
            r = p.add_run()
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), "end")
            r._r.append(e)


def shade(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), fill)
    tcpr.append(sh)


def add_table(rows):
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    size = 11 if ncol <= 5 else (9.5 if ncol <= 8 else 8.5)
    t = doc.add_table(rows=len(rows), cols=ncol)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblpr = t._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), "808080")
        borders.append(e)
    tblpr.append(borders)
    total = 8.27 - 2.5  # usable width in inches
    # width weights from content length, bounded so no column collapses
    wts = [max(6, min(40, max(len(re.sub(r"[*`]", "", r[c])) for r in rows))) for c in range(ncol)]
    s = sum(wts)
    widths = [max(0.45, total * w / s) for w in wts]
    k = total / sum(widths)
    widths = [w * k for w in widths]
    for ri, row in enumerate(rows):
        for ci, txt in enumerate(row):
            cell = t.cell(ri, ci)
            cell.width = Inches(widths[ci])
            p = cell.paragraphs[0]
            p.style = styles["RptTbl"]
            add_inline(p, txt, size=size, bold=True if ri == 0 else None)
            if ri == 0:
                shade(cell, "E7E6E6")
        if ri == 0:
            trpr = t.rows[0]._tr.get_or_add_trPr()
            h = OxmlElement("w:tblHeader")
            trpr.append(h)
        cant = OxmlElement("w:cantSplit")
        t.rows[ri]._tr.get_or_add_trPr().append(cant)
    sp = doc.add_paragraph(style="RptBody")
    sp.paragraph_format.space_after = Pt(6)
    return t


captions = {"Figure": [], "Table": []}


def emit(blocks, chap):
    for b in blocks:
        k = b[0]
        if k == "p":
            para(b[1])
        elif k == "li":
            p = doc.add_paragraph(style="RptBullet")
            add_inline(p, "•  " + b[1])
        elif k == "nli":
            p = doc.add_paragraph(style="RptBullet")
            add_inline(p, b[1])
        elif k == "cap":
            m = re.match(r"\*\*Table (P1|S\d|\d+b?)\.\s*(.*)$", b[1], flags=re.S)
            old, rest = m.group(1), m.group(2)
            if not rest.strip() and False:
                pass
            new = label_map[("Table", old)]
            # captions of the form "**Table 3. Title.** note" keep the title bold, rest too (11 pt bold per guideline)
            full = f"Table {new}. {rest}".strip()
            full = re.sub(r"\s+", " ", re.sub(r"\*\*", "", renumber(cites(full))))
            p = doc.add_paragraph(style="RptTblCap")
            r = p.add_run(full)
            set_runfont(r, 11, True)
            captions["Table"].append(full)
        elif k == "tbl":
            add_table(b[1])
        elif k == "img":
            old = re.match(r"Figure (\w+)\.?\s*(.*)$", b[1], flags=re.S)
            new = label_map[("Figure", old.group(1))]
            path = os.path.normpath(os.path.join(PAPER, b[2]))
            p = doc.add_paragraph(style="RptBody")
            p.alignment = C
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.line_spacing = 1.0
            p.add_run().add_picture(path, width=Inches(5.5))
            full = renumber(cites(f"Figure {new}. {old.group(2)}".strip()))
            full = re.sub(r"\*\*", "", full)
            cp = doc.add_paragraph(style="RptFigCap")
            r = cp.add_run(full)
            set_runfont(r, 11, True)
            captions["Figure"].append(full)


def section_footer(section, fmt, start):
    section.footer.is_linked_to_previous = False
    for p in list(section.footer.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    fp = section.footer.paragraphs[0]
    for r in list(fp.runs):
        r._r.getparent().remove(r._r)
    fp.alignment = C
    if fmt:
        fld_runs(fp, "PAGE", "1", 11)
    sp = section._sectPr
    for e in sp.findall(qn("w:pgNumType")):
        sp.remove(e)
    if fmt:
        pg = OxmlElement("w:pgNumType")
        pg.set(qn("w:fmt"), fmt)
        pg.set(qn("w:start"), str(start))
        # schema order: pgNumType precedes cols
        cols = sp.find(qn("w:cols"))
        (cols.addprevious(pg) if cols is not None else sp.append(pg))


def page_setup(section):
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)  # A4
    section.left_margin, section.right_margin = Inches(1.5), Inches(1)
    section.top_margin = section.bottom_margin = Inches(1)
    section.footer_distance = Inches(0.5)
    section.start_type = WD_SECTION.NEW_PAGE


# ----------------------------------------------------------------------------- cover page edits
cover = doc.paragraphs
for p in cover:
    if p.text.strip().startswith("Design, Implementation, and Performance Evaluation"):
        for r in p.runs[1:]:
            r._r.getparent().remove(r._r)
        p.runs[0].text = PROJECT_TITLE
        break
for p in cover:
    if p.text.strip().startswith("21CSC305P"):
        pass  # course code line is kept as printed in the template

# ----------------------------------------------------------------------------- preliminary pages
prelim = doc.sections[-1]
page_setup(prelim)
p = doc.add_paragraph("ABSTRACT", style="RptFrontNB")
para(ABSTRACT)
p = doc.add_paragraph("Keywords: shortcut learning; dataset shift; orthopaedic radiographs; joint recognition; leave-one-source-out; calibration; Grad-CAM.", style="RptBody")
for r in p.runs:
    set_runfont(r, 12, None, True)

# headings for the lists of contents; entries cached and refreshed by Word on open
heads = []
for ci, (ct, secs_) in enumerate(CHAPTERS, 1):
    heads.append((1, f"{ci}. {ct}"))
    for si, (st, _) in enumerate(secs_, 1):
        heads.append((2, f"{ci}.{si} {st}"))
heads += [(1, "References"), (1, "Appendix A: Coding"), (1, "Appendix B: Supplementary Methods and Tables")]
doc.add_paragraph("TABLE OF CONTENTS", style="RptFront")
toc_field('TOC \\o "1-3" \\h \\z \\u', [("    " if l == 2 else "") + t for l, t in heads])
# lists of figures and tables use cached entries made after the body is generated -> placeholders filled below
lof_anchor = doc.add_paragraph("LIST OF FIGURES", style="RptFront")
lot_anchor = None  # created after the body is known
abbr_anchor = None

# ----------------------------------------------------------------------------- body (new section, arabic)
# generate body into a temporary list to collect captions first
# (body is added after lists; we create lists later by inserting before body marker)
marker = doc.add_paragraph("", style="RptBody")
body_section = doc.add_section(WD_SECTION.NEW_PAGE)
prelim = doc.sections[-2]
body_section = doc.sections[-1]
page_setup(body_section)
section_footer(prelim, "lowerRoman", 1)
section_footer(body_section, "decimal", 1)
section_footer(doc.sections[0], None, 1)

for ci, (ctitle, sections) in enumerate(CHAPTERS, 1):
    doc.add_paragraph(f"CHAPTER {ci}", style="RptChapterNo")
    doc.add_paragraph(f"{ci}. {ctitle}", style="RptChapter")
    for si, (stitle, blocks) in enumerate(sections, 1):
        doc.add_paragraph(f"{ci}.{si} {stitle}", style="RptSection")
        emit(blocks, str(ci))

# references
doc.add_paragraph("REFERENCES", style="RptFront")
if ref_note:
    para(re.sub(r"`", "", ref_note.replace("**", "")))
for n, text in refs:
    p = doc.add_paragraph(style="RptRef")
    add_inline(p, f"[{n}]  " + text)

# appendix A: code
doc.add_paragraph("APPENDIX A", style="RptChapterNo")
doc.add_paragraph("A. Coding", style="RptChapter")
para("This appendix lists the essential Python implementation. The complete code is in the project repository (`ML3/scripts`, `ML3/site`). "
     "The Google Colab notebook used for the earlier joint-identification stage is stored in `notebooks/Orthopedic_Joint_Identification_Colab.ipynb` and opens in Colab at "
     "https://colab.research.google.com/github/YENIGALLADHEERAJ/ML-Project/blob/main/notebooks/Orthopedic_Joint_Identification_Colab.ipynb")
CODE = [
    ("A.1 Data utilities (scripts/data_utils.py)", "scripts/data_utils.py"),
    ("A.2 Grouped splits (scripts/make_splits.py)", "scripts/make_splits.py"),
    ("A.3 Anatomy-free random-forest experiments (scripts/benchmark_rf_experiments.py)", "scripts/benchmark_rf_experiments.py"),
    ("A.4 Shortcut probe (scripts/shortcut_probe.py)", "scripts/shortcut_probe.py"),
    ("A.5 Paired border audit (scripts/border_audit.py)", "scripts/border_audit.py"),
    ("A.6 Shared PyTorch utilities (scripts/torch_common.py)", "scripts/torch_common.py"),
    ("A.7 EfficientNet-B3 training (scripts/train_efficientnet.py)", "scripts/train_efficientnet.py"),
    ("A.8 Frozen-test statistics (scripts/final_stats.py)", "scripts/final_stats.py"),
    ("A.9 Inference service (site/api/infer.py)", "site/api/infer.py"),
    ("A.10 Web API (site/api/app.py)", "site/api/app.py"),
]
for title, rel in CODE:
    doc.add_paragraph(title, style="RptSection")
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read().replace("\t", "    ").rstrip().splitlines()
    cp = doc.add_paragraph(style="RptCode")
    for i, ln in enumerate(src):
        r = cp.add_run(ln)
        set_runfont(r, 10, None, None, mono=True)
        if i < len(src) - 1:
            r.add_break()

# appendix B: supplementary
doc.add_paragraph("APPENDIX B", style="RptChapterNo")
doc.add_paragraph("B. Supplementary Methods and Tables", style="RptChapter")
emit(APPX_B_BLOCKS, "B")
if decl:
    doc.add_paragraph("Declarations", style="RptSection")
    emit(md_blocks(decl.group(1).splitlines()), "B")

# ----------------------------------------------------------------------------- lists of figures / tables / abbreviations (inserted before the body section break)
# build into the end, then move to just before `marker`
def build_lists():
    start = len(list(body)) - 1  # final sectPr stays last
    doc.add_paragraph("LIST OF FIGURES", style="RptFront")
    toc_field('TOC \\h \\z \\c "Figure"', captions["Figure"] or ["(none)"])
    doc.add_paragraph("LIST OF TABLES", style="RptFront")
    toc_field('TOC \\h \\z \\c "Table"', captions["Table"] or ["(none)"])
    doc.add_paragraph("ABBREVIATIONS", style="RptFront")
    t = doc.add_table(rows=len(ABBREVIATIONS), cols=2)
    t.autofit = False
    for i, (a, b) in enumerate(ABBREVIATIONS):
        for j, txt in enumerate((a, b)):
            c = t.cell(i, j)
            c.width = Inches(1.3 if j == 0 else 4.4)
            p = c.paragraphs[0]
            p.style = styles["RptBody"]
            p.paragraph_format.alignment = L
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(txt)
            set_runfont(r, 12, j == 0)
    return start


lists_start = build_lists()
els = list(body)
new_els = els[lists_start:-1]  # everything appended by build_lists (excluding final sectPr)
# remove the original empty LIST OF FIGURES anchor created earlier (replaced by the richer block)
lof_anchor._p.getparent().remove(lof_anchor._p)
for el in new_els:
    marker._p.addprevious(el)

# captions must be recognised by the TOC \c switch: tag caption paragraphs with SEQ-less text, so use \t style fields instead
for fld in body.iter(qn("w:instrText")):
    if '\\c "Figure"' in (fld.text or ""):
        fld.text = ' TOC \\h \\z \\t "RptFigCap,1" '
    elif '\\c "Table"' in (fld.text or ""):
        fld.text = ' TOC \\h \\z \\t "RptTblCap,1" '

# refresh fields when opened in Word
settings = doc.settings.element
uf = OxmlElement("w:updateFields")
uf.set(qn("w:val"), "true")
settings.append(uf)

core = doc.core_properties
core.title = PROJECT_TITLE
core.subject = "Machine Learning Project Report"
core.author = ""
doc.save(OUT)
print("saved", OUT)
print("figures", len(captions["Figure"]), "tables", len(captions["Table"]), "refs", len(refs))
print("unresolved citations:", sorted(unresolved)[:20])
