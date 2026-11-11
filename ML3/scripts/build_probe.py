"""Train the anatomy-free "shortcut probe" used by the OrthoTrace workbench and export it as JSON.

The probe never looks at image content. Its only inputs are the six file-level properties that the study's
`meta_all` Random Forest used: width, height, aspect, RGB flag, PNG flag and file size (kB). It is trained on the
DEVELOPMENT rows (train + val) of the frozen v2 manifest only; the sealed test partition is never read.

It produces two forests, exported as plain arrays so the API needs no scikit-learn at inference time:
  * joint  - guesses Hip / Knee / Shoulder from the properties alone
  * source - guesses which of the six public sources the file came from

Usage (repo root):  .venv\\Scripts\\python.exe -X utf8 ML3/scripts/build_probe.py
Output: ML3/site/api/models/probe.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "artifacts" / "benchmark" / "manifest_v2.csv"
OUT = ROOT / "site" / "api" / "models" / "probe.json"
FEATURES = ["width", "height", "aspect", "is_rgb", "is_png", "file_kb"]
SOURCE_NAMES = {"A": "AV-DDH (paediatric pelvis)", "F": "FracAtlas", "G": "Gornale knee", "K": "Kaggle hip implants",
                "O": "OAI-derived knee", "U": "UCI shoulder implants"}
RF = dict(n_estimators=50, max_depth=10, min_samples_leaf=4, class_weight="balanced_subsample", random_state=0, n_jobs=-1)

df = pd.read_csv(MANIFEST)
dev = df[(df.role == "target") & df.split.isin(["train", "val"])].reset_index(drop=True)
assert not (dev.split == "test").any() and len(dev) == 3770, len(dev)
X = np.column_stack([dev.w, dev.h, dev.w / dev.h, (dev["mode"] == "RGB").astype(int), (dev.ext == ".png").astype(int), dev.kb]).astype(np.float64)


def fit(Xm, y):
    return RandomForestClassifier(**RF).fit(Xm, y)


def ba(y, p):
    return float(balanced_accuracy_score(y, p))


# honest development-set evidence --------------------------------------------------------------------------------
tr, va = (dev.split == "train").values, (dev.split == "val").values
pooled_ba = ba(dev.label[va], fit(X[tr], dev.label[tr]).predict(X[va]))
nf = (dev.source != "F").values
isf = (dev.source == "F").values
decoupled = fit(X[nf], dev.label[nf])
decoupled_ba = ba(dev.label[isf], decoupled.predict(X[isf]))
source_ba = ba(dev.source[va], fit(X[tr], dev.source[tr]).predict(X[va]))
print(f"dev pooled BA {pooled_ba:.3f} | decoupled (train w/o FracAtlas -> FracAtlas) BA {decoupled_ba:.3f} | source BA {source_ba:.3f}")


# export ---------------------------------------------------------------------------------------------------------
def export(clf):
    trees = []
    for est in clf.estimators_:
        t = est.tree_
        val = t.value[:, 0, :]
        val = val / val.sum(1, keepdims=True)
        trees.append(dict(l=t.children_left.tolist(), r=t.children_right.tolist(), f=t.feature.tolist(),
                          t=[round(float(v), 4) for v in t.threshold], v=[[round(float(p), 3) for p in row] for row in val]))
    return dict(classes=[str(c) for c in clf.classes_], trees=trees)


joint, source = fit(X, dev.label), fit(X, dev.source)
src_stats = {}
for s, g in dev.groupby("source"):
    src_stats[s] = dict(name=SOURCE_NAMES[s], n=int(len(g)), label_mix={k: round(float(v), 3) for k, v in g.label.value_counts(normalize=True).items()},
                        median_width=float(g.w.median()), median_height=float(g.h.median()), median_kb=round(float(g.kb.median()), 1))
rng = {name: [float(np.percentile(X[:, i], 1)), float(np.percentile(X[:, i], 99))] for i, name in enumerate(FEATURES) if name in ("width", "height", "file_kb")}
payload = dict(
    features=FEATURES, joint=export(joint), source=export(source), sources=src_stats, range_p1_p99=rng,
    evidence=dict(n_dev_rows=int(len(dev)), trained_on="development rows only (train + val); sealed test never read", manifest_sha256=json.loads(
        (ROOT / "artifacts" / "benchmark" / "manifest_v2_summary.json").read_text())["sha256"],
        dev_pooled_balanced_accuracy=round(pooled_ba, 3), dev_decoupled_balanced_accuracy=round(decoupled_ba, 3),
        dev_source_balanced_accuracy=round(source_ba, 3),
        frozen_test_reference=dict(meta_pooled=0.960, meta_decoupled=0.333, dims_pooled=0.971, dims_decoupled=0.333,
                                   note="Frozen sealed-test results of the study's metadata and dimensions-only random forests (manuscript Table 3 (H2)).")),
)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
print("wrote", OUT, f"{OUT.stat().st_size / 1024:.0f} kB")

# self-check: exported forests must reproduce scikit-learn --------------------------------------------------------
def walk(tree, x):
    n = 0
    while tree["l"][n] != -1:
        n = tree["l"][n] if x[tree["f"][n]] <= tree["t"][n] else tree["r"][n]
    return tree["v"][n]


for name, clf in (("joint", joint), ("source", source)):
    exp = payload[name]
    idx = np.random.default_rng(0).choice(len(X), 300, replace=False)
    mine = np.array([np.mean([walk(t, X[i]) for t in exp["trees"]], axis=0) for i in idx])
    ref = clf.predict_proba(X[idx])
    print(name, "max |export - sklearn| =", float(np.abs(mine - ref).max()))
    assert np.abs(mine - ref).max() < 0.01
