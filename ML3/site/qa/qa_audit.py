"""Static QA for the built site: data-consistency of hard-coded narrative numbers, disclaimers, links, ids, alt text, heading order, asset weights.
Run: python site/qa/qa_audit.py   (exit code 1 if any check fails)"""
import json, re, glob, os, sys
from html.parser import HTMLParser
from pathlib import Path
S = Path(__file__).resolve().parent.parent; os.chdir(S)
D = json.loads(Path("data/results.json").read_text(encoding="utf-8")); fails = []
def chk(name, ok, extra=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{extra}]" if extra else "")); ok or fails.append(name)
G = {g["id"]: g for g in D["gap"]}; PR = [g for g in D["gap"] if g["primary"]]
r = lambda v: f"{v:.2f}"
chk("primary gaps 0.31-0.50", (r(min(g["gap"] for g in PR)), r(max(g["gap"] for g in PR))) == ("0.31", "0.50"))
chk("pooled 0.99-1.00 / decoupled 0.50-0.69", (r(min(g["pooled"] for g in PR)), r(max(g["pooled"] for g in PR)), r(min(g["decoupled"] for g in PR)), r(max(g["decoupled"] for g in PR))) == ("0.99", "1.00", "0.50", "0.69"))
chk("Holm p=0.0025 for all primary", all(g["p_holm"] == 0.0025 for g in PR), str({g["p_holm"] for g in PR}))
hs = D["sensitivity"]["hip_shoulder"]; chk("hip/shoulder-only gap 0.10-0.34", (r(min(x["gap"] for x in hs)), r(max(x["gap"] for x in hs))) == ("0.10", "0.34"))
rf = [G[k] for k in G if k.startswith("rf|")]; chk("RF pooled 0.88-0.97 / decoupled 0.33-0.61", (r(min(g["pooled"] for g in rf)), r(max(g["pooled"] for g in rf)), r(min(g["decoupled"] for g in rf)), r(max(g["decoupled"] for g in rf))) == ("0.88", "0.97", "0.33", "0.61"))
pr = [G[k] for k in G if k.startswith("lr|")]; chk("probes decoupled 0.50-0.66", (r(min(g["decoupled"] for g in pr)), r(max(g["decoupled"] for g in pr))) == ("0.50", "0.66"))
chk("dims 0.971->0.333, meta 0.960->0.333", (G["rf|dims_only"]["pooled"], G["rf|dims_only"]["decoupled"], G["rf|meta_all"]["pooled"], G["rf|meta_all"]["decoupled"]) == (0.9713, 0.3333, 0.9605, 0.3333))
cr = {(x["id"], x["cls"]): x["n"] for x in D["sensitivity"]["class_recall"]}; chk("decoupled test n: hip26 knee14 shoulder15 (=55)", (cr[("ft|effnet|full", "Hip")], cr[("ft|effnet|full", "Knee")], cr[("ft|effnet|full", "Shoulder")]) == (26, 14, 15))
sh = D["holdout_pred_share"]["ft|effnet|full"]; chk("EffNet FT: held-out K -> shoulder 100%, U -> hip 83%", (round(sh["K"]["share"][2] * 100), round(sh["U"]["share"][0] * 100)) == (100, 83))
chk("meta: 4427 images, 657 test, 13 audit checks, 29 checkpoints, H1 5/5", (D["meta"]["n_images"], D["meta"]["n_test"], D["meta"]["n_audit_checks"], D["meta"]["n_checkpoints"], D["meta"]["h1"]["supported"]) == (4427, 657, 13, 29, 5))
smp = json.loads(Path("data/samples.json").read_text(encoding="utf-8")); chk("samples.json: 9 samples x 4 models, probs sum to 1", len(smp) == 9 and all(len(s["models"]) == 4 and all(abs(sum(m["probs"].values()) - 1) < .01 for m in s["models"]) for s in smp))

class P(HTMLParser):
    def __init__(s): super().__init__(); s.ids = []; s.imgs = []; s.heads = []; s.links = []; s.btn = []; s.cur = None; s.text = ""; s.title = ""; s.intitle = False; s.h1 = 0; s.main = 0; s.lang = None
    def handle_starttag(s, t, a):
        a = dict(a)
        if "id" in a: s.ids.append(a["id"])
        if t == "html": s.lang = a.get("lang")
        if t == "main": s.main += 1
        if t == "img": s.imgs.append(a)
        if t in "h1 h2 h3 h4".split(): s.heads.append(int(t[1])); s.h1 += t == "h1"
        if t == "a" and "href" in a: s.links.append(a["href"])
        if t == "button": s.cur = ["button", a.get("aria-label"), ""]
        if t == "title": s.intitle = True
    def handle_endtag(s, t):
        if t == "button" and s.cur: s.btn.append(s.cur); s.cur = None
        if t == "title": s.intitle = False
    def handle_data(s, d):
        s.text += d
        if s.cur: s.cur[2] += d
        if s.intitle: s.title += d
for f in sorted(glob.glob("*.html")):
    p = P(); t = Path(f).read_text(encoding="utf-8"); p.feed(t)
    chk(f"{f}: project identity and scope present", 'OrthoTrace' in t and ('joint' in t.lower() or 'checkpoint' in t.lower()) and 'class="research-banner"' not in t)
    chk(f"{f}: lang, title, one h1, one main", bool(p.lang) and bool(p.title.strip()) and p.h1 == 1 and p.main == 1, f"h1={p.h1}")
    chk(f"{f}: unique ids", len(p.ids) == len(set(p.ids)), str({i for i in p.ids if p.ids.count(i) > 1}))
    chk(f"{f}: images have alt", all("alt" in i for i in p.imgs))
    chk(f"{f}: no heading level skips >1", all(b - a <= 1 for a, b in zip(p.heads, p.heads[1:])), str(p.heads))
    chk(f"{f}: buttons have names", all((b[1] or b[2].strip()) for b in p.btn), str([b for b in p.btn if not (b[1] or b[2].strip())]))
    bad = [l for l in p.links if not l.startswith(("http", "mailto:", "#", "data:")) and not os.path.exists(l.split("#")[0].split("?")[0])]
    chk(f"{f}: internal links resolve", not bad, str(bad))
    refs = re.findall(r'(?:src|href)="((?:assets|downloads|data)/[^"#?]+)"', t); chk(f"{f}: asset refs exist", all(os.path.exists(x) for x in refs), str([x for x in refs if not os.path.exists(x)]))
    ext = re.findall(r'<(?:script|img|link)\b[^>]*(?:src|href)="(https?://[^"]+)"', t); chk(f"{f}: external resources only Google Fonts", all("fonts.g" in x for x in ext), str(ext))
sz = lambda g: sum(os.path.getsize(x) for x in glob.glob(g, recursive=True))
print(f"INFO css {sz('assets/css/*.css')/1024:.0f} kB, js(own) {sz('assets/js/*.js')/1024:.0f} kB, vendor {sz('assets/vendor/*.js')/1024:.0f} kB, html {sz('*.html')/1024:.0f} kB, samples {sz('assets/samples/*.jpg')/1024:.0f} kB, figures {sz('assets/figures/*')/1024:.0f} kB, data {sz('data/*.json')/1024:.0f} kB")
print("\nFAILED: " + ", ".join(fails) if fails else "\nALL CHECKS PASSED"); sys.exit(1 if fails else 0)
