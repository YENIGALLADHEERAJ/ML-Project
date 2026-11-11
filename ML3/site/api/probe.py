"""Anatomy-free shortcut probe (pure NumPy, no scikit-learn needed at serving time).

Given only an image's file-level properties (size, aspect, colour mode, format, file size) it answers two questions:
  1. What joint would a model guess WITHOUT looking at the anatomy?
  2. Which training source does the file look like?

If the probe reproduces the deep model's answer with high confidence, that answer is *compatible with a shortcut*:
it can be explained by file properties alone. This does not prove the deep model used a shortcut, and a disagreement
does not prove it recognised anatomy. See manuscript Chapter 6 and `scripts/build_probe.py` for the evidence."""
import json
from pathlib import Path

import numpy as np

_FILE = Path(__file__).parent / "models" / "probe.json"
_P = None
CONFIDENT = 0.80


def available():
    return _FILE.is_file()


def _load():
    global _P
    if _P is None:
        _P = json.loads(_FILE.read_text(encoding="utf-8"))
        for key in ("joint", "source"):  # tuples of arrays for fast traversal
            _P[key]["_t"] = [(t["l"], t["r"], t["f"], t["t"], np.asarray(t["v"], np.float64)) for t in _P[key]["trees"]]
    return _P


def _forest(model, x):
    acc = np.zeros(len(model["classes"]))
    for left, right, feat, thr, val in model["_t"]:
        n = 0
        while left[n] != -1:
            n = left[n] if x[feat[n]] <= thr[n] else right[n]
        acc += val[n]
    return acc / len(model["_t"])


def features(facts):
    w, h = float(facts["width"]), float(facts["height"])
    return np.array([w, h, w / h, 1.0 if facts.get("mode") == "RGB" else 0.0,
                     1.0 if str(facts.get("format", "")).upper() == "PNG" else 0.0, float(facts["file_kb"])])


def _out_of_range(p, facts):
    notes = []
    for name, key, unit in (("width", "width", "px"), ("height", "height", "px"), ("file size", "file_kb", "kB")):
        lo, hi = p["range_p1_p99"]["file_kb" if key == "file_kb" else key]
        v = float(facts[key])
        if v < lo or v > hi:
            notes.append(f"{name} {v:g} {unit} is outside the 1st–99th percentile of the training files ({lo:g}–{hi:g} {unit})")
    return notes


def run(facts, results):
    """facts: infer.image_facts(); results: infer.predict() output. Returns a JSON-serialisable dict."""
    if not available():
        return dict(available=False)
    p = _load()
    x = features(facts)
    jp = _forest(p["joint"], x)
    sp = _forest(p["source"], x)
    jc, sc = p["joint"]["classes"], p["source"]["classes"]
    joint_pred = jc[int(jp.argmax())]
    joint_conf = float(jp.max())
    src = sc[int(sp.argmax())]
    src_info = p["sources"][src]
    pooled = results["models"][0]["pred"]
    others = {m["id"]: m["pred"] for m in results["models"][1:]}
    notes = _out_of_range(p, facts)
    agrees = joint_pred == pooled
    if notes:
        level = "unfamiliar"
        headline = "Unfamiliar file properties"
        text = ("This file looks unlike most training files, so the probe's answer is not reliable. Resized or re-encoded copies "
                "(including the bundled sample thumbnails) fall here. Use the original file for a meaningful probe.")
    elif agrees and joint_conf >= CONFIDENT:
        level = "shortcut"
        headline = "Shortcut-compatible"
        text = (f"A model that never looks at the picture guesses {joint_pred} with {joint_conf * 100:.0f}% confidence from file properties alone, "
                f"the same answer as the pooled model. This prediction can be explained without anatomy, so it is weak evidence of anatomical recognition.")
    elif agrees:
        level = "weak"
        headline = "Agrees, but weakly"
        text = (f"The probe also guesses {joint_pred}, but with only {joint_conf * 100:.0f}% confidence. File properties give a partial hint, "
                f"not a decisive one.")
    else:
        level = "independent"
        headline = "Not reproducible from file properties"
        text = (f"The probe guesses {joint_pred} ({joint_conf * 100:.0f}%) while the pooled model says {pooled}. This answer is not simply "
                f"explained by file properties. That does not show the model recognised anatomy, only that this shortcut did not produce it.")
    return dict(
        available=True,
        features=dict(zip(p["features"], [round(float(v), 3) for v in x])),
        joint=dict(pred=joint_pred, confidence=round(joint_conf, 3), probs={c: round(float(v), 3) for c, v in zip(jc, jp)},
                   agrees_with_pooled=agrees, agrees_with_all=all(joint_pred == v for v in [pooled, *others.values()])),
        source=dict(id=src, name=src_info["name"], confidence=round(float(sp.max()), 3), label_mix=src_info["label_mix"], n_train=src_info["n"],
                    typical=dict(width=src_info["median_width"], height=src_info["median_height"], file_kb=src_info["median_kb"])),
        in_range=not notes, range_notes=notes,
        verdict=dict(level=level, headline=headline, text=text),
        evidence=p["evidence"],
        caveat="Compatible with a shortcut is not proof of one. The probe uses only file properties, never pixels.",
    )
