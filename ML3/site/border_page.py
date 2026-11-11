"""Interactive page for the paired border intervention."""
import json
from pathlib import Path

SITE = Path(__file__).resolve().parent


def pct(value):
    return f"{100 * value:.1f}%"


def make_page(page, head, sec):
    report = json.loads((SITE / "data/border-audit.json").read_text(encoding="utf-8"))
    body = head("Source sensitivity", "What changes when only<br>the <em>border</em> changes?",
                "On held-out hip and shoulder X-rays, compare borders derived from images of the same joint. The center pixels stay identical in every comparison.")
    body += sec('''<h2>Compare the same image three ways</h2>
<p>These are saved model outputs from the paired experiment. Choose an example and a checkpoint. The two synthetic frames use four median edge intensities measured on donor images. Each replaces the outer 12 pixels on a 160 × 160 input.</p>
<div class="audit-controls"><label>Example <select id="audit-case"></select></label><label>Checkpoint <select id="audit-model"></select></label></div>
<div id="audit-views" class="audit-views" aria-live="polite"></div>''')
    rows = []
    for result in report["results"].values():
        lower, upper = result["interval"]
        rows.append(f'<tr><th scope="row">{result["name"]}</th><td>{pct(result["within"])}</td>'
                    f'<td>{pct(result["cross"])}</td><td>{100 * result["difference"]:+.1f} pp</td>'
                    f'<td>{100 * lower:+.1f} to {100 * upper:+.1f} pp</td></tr>')
    body += sec(f'''<h2>Prediction changes across the holdout</h2>
<p>{report["n"]} FracAtlas images in {report["groups"]} recorded groups. Each image was compared with {report["repeats"]} within-source and {report["repeats"]} cross-source frames. The outcome is a change in the top-scoring joint from the original input. The paired interval resamples recorded groups.</p>
<div class="tablewrap"><table class="data"><thead><tr><th scope="col">Checkpoint</th><th scope="col">Within-source flip rate</th><th scope="col">Cross-source flip rate</th><th scope="col">Difference</th><th scope="col">95% bootstrap interval</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<p>Cross-source minus within-source is the paired effect. The interval describes variation across the available image groups. The two rows use one checkpoint each.</p>
<p><a href="data/border-audit.json" download>Download aggregate results</a> · <a href="downloads/BORDER_AUDIT.md">Read the methods and publication draft</a></p>''', "tint")
    body += sec('''<h2>How this builds on prior work</h2>
<p>SAM-X established radiograph sorting across many anatomical categories. DeGrave and colleagues intervened on chest X-ray markers to test shortcuts. Here the experimental question is whether changing edge intensities with a same-joint donor from a different source shifts predictions more than applying the same operation with a donor from the original source.</p>
<p>The intervention can remove peripheral anatomy and introduce seams. The within-source control applies the same operation, and center pixels are identical in both conditions. This pilot estimates sensitivity to these synthetic frames. It cannot isolate hospital, acquisition equipment or implant effects. The provisional knee labels were excluded from this analysis.</p>
<p><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC9935683/">SAM-X</a> · <a href="https://www.nature.com/articles/s42256-021-00338-7">DeGrave et al.</a> · <a href="https://www.nature.com/articles/s41597-023-02432-4">FracAtlas</a></p>''')
    return page("border-audit.html", "Paired X-ray border audit",
                "A paired test of same-source and cross-source image framing for joint recognition.",
                body, ["border-audit.js"], css=("border-audit.css",))
