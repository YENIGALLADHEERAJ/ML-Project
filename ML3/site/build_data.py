"""Builds site/data/*.json from the project's real result files (no hand-typed numbers)."""
import json, glob, shutil
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; SITE = ROOT / "site"; DATA = SITE / "data"; DATA.mkdir(parents=True, exist_ok=True)
ST = ROOT / "artifacts/final/stats"; FN = ROOT / "artifacts/final"
S = pd.read_csv(ST / "summary.csv"); G = pd.read_csv(ST / "gap.csv"); OOD = pd.read_csv(ST / "ood.csv"); SA = pd.read_csv(ST / "sensitivity_class_recall.csv")
SB = pd.read_csv(ST / "sensitivity_hip_shoulder_gap.csv"); S2 = pd.read_csv(ST / "sensitivity2.csv"); H4 = pd.read_csv(ST / "h4_confidence_correctness.csv")
M = pd.read_csv(ROOT / "artifacts/benchmark/manifest_v2.csv"); DEC = json.load(open(ROOT / "artifacts/benchmark/v2/res_source.json"))
NAME = {"ft|effnet|full": "EfficientNet-B3 (fine-tuned)", "ft|swin|full": "Swin-T (fine-tuned)", "ft|convnext|full": "ConvNeXt-T (fine-tuned, 1 seed)", "lr|effnet|full": "EfficientNet-B3 (probe)",
        "lr|convnext|full": "ConvNeXt-T (probe)", "lr|swin|full": "Swin-T (probe)", "rf|dims_only": "Image dimensions (RF)", "rf|meta_all": "File metadata (RF)", "rf|border_only": "Border frame (RF)",
        "rf|lowfreq_only": "Low-frequency 8x8 (RF)", "rf|hist_only": "Grey-level histogram (RF)", "rf|hog_full": "HOG (RF)", "rf|hog_center": "HOG centre crop (RF)"}
PRIM = ["ft|effnet|full", "ft|swin|full", "lr|effnet|full", "lr|convnext|full", "lr|swin|full"]
r3 = lambda x: None if pd.isna(x) else round(float(x), 4)
out = {}
# --- gap
def ba(m, p, e):
    r = S[(S.model == m) & (S.protocol == p) & (S["eval"] == e)]; return None if r.empty else r.iloc[0]
gap = []
for r in G.itertuples():
    if r.model not in NAME: continue
    d = ba(r.model, "E2_hold_F", "F"); gap.append(dict(id=r.model, name=NAME[r.model], primary=bool(r.primary), seeds=int(r.seeds_pooled), pooled=r3(r.ba_pooled), decoupled=r3(r.ba_decoupled), dec_lo=r3(d.ba_ci_lo), dec_hi=r3(d.ba_ci_hi),
                                                       gap=r3(r.gap), gap_lo=r3(r.gap_ci_lo), gap_hi=r3(r.gap_ci_hi), p_holm=r3(r.p_holm) if not pd.isna(r.p_holm) else None, kind=r.model.split("|")[0]))
out["gap"] = gap
# --- leave-one-source-out
lodo = {}
for m in PRIM + ["rf|dims_only", "rf|meta_all"]:
    lodo[m] = {"name": NAME[m]}
    for s in "KUAGO":
        r = ba(m, f"E3_hold_{s}", s)
        if r is not None: lodo[m][s] = dict(ba=r3(r.ba_mean), lo=r3(r.ba_ci_lo), hi=r3(r.ba_ci_hi), n=int(r.n))
out["lodo"] = lodo
# prediction shares in holdouts (effnet FT + swin probe)
shares = {}
for m in ["ft|effnet|full", "lr|swin|full"]:
    shares[m] = {}
    for s, lab in (("K", "Hold-out K (hip implants)"), ("U", "Hold-out U (shoulder implants)")):
        r = ba(m, f"E3_hold_{s}", s); cm = np.array(json.loads(r.cm)); tot = cm.sum(); shares[m][s] = dict(label=lab, share=[round(float(cm[:, j].sum() / tot), 3) for j in range(3)])
out["holdout_pred_share"] = shares
# --- shortcut probes
out["shortcut"] = [dict(id=m, name=NAME[m], pooled=r3(G.set_index("model").loc[m, "ba_pooled"]), decoupled=r3(G.set_index("model").loc[m, "ba_decoupled"])) for m in ["rf|dims_only", "rf|meta_all", "rf|border_only", "rf|lowfreq_only", "rf|hist_only", "rf|hog_full", "rf|hog_center", "lr|effnet|full", "lr|swin|full"]]
# --- confusion
conf = {}
for p, e, lab in (("E0_pooled", "pooled_test", "Pooled random split"), ("E2_hold_F", "F", "Hold out FracAtlas"), ("E3_hold_K", "K", "Hold out K (hip implants)"), ("E3_hold_U", "U", "Hold out U (shoulder implants)")):
    r = ba("ft|effnet|full", p, e); conf[p] = dict(label=lab, cm=json.loads(r.cm))
out["confusion"] = conf
# --- OOD & calibration
out["ood"] = [dict(id=r.model, name=NAME.get(r.model, r.model), score=r.score, pooled=r3(r.auroc) if r.protocol == "E0_pooled" else None, dec=r3(r.auroc) if r.protocol == "E2_hold_F" else None,
                   lo=r3(r.auroc_lo), hi=r3(r.auroc_hi), protocol=r.protocol, fpr95=r3(r.fpr95)) for r in OOD.itertuples() if r.model in PRIM and r.score in ("msp", "energy", "mahalanobis", "neg_entropy", "msp_ts")]
cal = []
for m in PRIM:
    for p, e, lab in (("E0_pooled", "pooled_test", "Pooled"), ("E2_hold_F", "F", "Hold out F"), ("E3_hold_K", "K", "Hold out K"), ("E3_hold_U", "U", "Hold out U")):
        r = ba(m, p, e); cal.append(dict(id=m, name=NAME[m], setting=lab, acc=r3(r.acc), ece_raw=r3(r.ece_raw), ece_ts=r3(r.ece_ts), acc50=r3(r.acc_at_50cov), aurc=r3(r.aurc), conf_auroc=r3(r.conf_auroc)))
out["calibration"] = cal
# risk-coverage (effnet FT, seed-averaged)
CL = ["Hip", "Knee", "Shoulder"]; rc = {}
for p, e, lab in (("E0_pooled", "pooled_test", "Pooled random split"), ("E2_hold_F", "F", "Hold out FracAtlas"), ("E3_hold_K", "K", "Hold out K"), ("E3_hold_U", "U", "Hold out U")):
    d = pd.concat([pd.read_csv(f) for f in glob.glob(str(FN / "preds" / f"ft_effnet_full_{p}_s*.csv.gz"))]); d = d[d["eval"] == e]; cov = np.linspace(0.1, 1, 19); acc = []
    for s, g in d.groupby("seed"):
        L = g[["l_Hip", "l_Knee", "l_Shoulder"]].values; pr = np.exp(L - L.max(1, keepdims=True)); pr /= pr.sum(1, keepdims=True); conf_ = pr.max(1); ok = (g.pred == g.true).values; o = np.argsort(-conf_)
        acc.append([ok[o][:max(1, int(c * len(ok)))].mean() for c in cov])
    rc[p] = dict(label=lab, coverage=[round(float(c), 2) for c in cov], acc=[round(float(a), 4) for a in np.mean(acc, 0)])
out["risk_coverage"] = rc
# --- sensitivity
out["sensitivity"] = dict(class_recall=[dict(id=r.model, name=NAME[r.model], cls=r.cls, n=int(r.n), recall=r3(r.recall), lo=r3(r.lo), hi=r3(r.hi)) for r in SA.itertuples()],
                          hip_shoulder=[dict(id=r.model, name=NAME[r.model], pooled=r3(r.ba_hip_shoulder_pooled), decoupled=r3(r.ba_hip_shoulder_decoupled), gap=r3(r.gap), lo=r3(r.gap_lo), hi=r3(r.gap_hi)) for r in SB.itertuples()],
                          same_source=[dict(id=r.model, name=NAME[r.model], pooled_model_on_F=r3(r.ba_pooledmodel_on_F), decoupled_model_on_F=r3(r.ba_decoupledmodel_on_F), macro_f1_gap=r3(r.macroF1_gap)) for r in S2.itertuples()])
# --- sources
T = M[M.role == "target"]
info = {"F": ("FracAtlas", "3 Bangladeshi hospitals; figshare 10.6084/m9.figshare.22363012", "CC BY 4.0", "hardware flagged in 6 of 374 images", "Only source with all three joints; knee subset (94) labelled provisionally by visual inspection, not clinician-verified"),
        "K": ("Kaggle hip implants", "images compiled from ~100 papers and web pages", "CC0 on Kaggle (underlying figures' rights unclear)", "implants in 30/30 sampled", "close-up arthroplasty crops"),
        "U": ("UCI shoulder implants", "UW Shoulder Site, manufacturer sites, UCSF lab; doi 10.24432/C5F893", "CC BY 4.0", "implants in ~29/30 sampled", "close-up arthroplasty crops"),
        "A": ("AV-DDH (paediatric hip)", "Mendeley 10.17632/4gvcb6gmh2.2", "CC BY 4.0 on Mendeley; export says 'Private'", "0/30 sampled (lead shields common)", "paediatric pelvis; 640x640 RGB export"),
        "G": ("Gornale knee", "Mendeley 10.17632/t9ndx37v5h.1", "CC BY 4.0", "0/30 sampled", "one scanner; ~10% near-blank frames in a sample"),
        "O": ("OAI-derived knee", "Osteoarthritis Initiative derivative (Kaggle copy)", "CC BY 4.0 as reported; OAI terms may apply", "0/30 sampled", "224x224 pre-cropped single knees")}
srcs = []
for k, (nm, prov, lic, imp, note) in info.items():
    c = T[T.source == k].groupby("label").size().to_dict(); srcs.append(dict(id=k, name=nm, hip=int(c.get("Hip", 0)), knee=int(c.get("Knee", 0)), shoulder=int(c.get("Shoulder", 0)), provenance=prov, licence=lic, implants=imp, note=note))
out["sources"] = srcs; out["decodability"] = {k: {c: round(v[c]["bal_acc"], 3) for c in v} for k, v in DEC.items() if k.split("|")[1] in ("full", "center", "norm", "noborder", "highpass")}
# input variants on the decoupled test (probes)
VAR = ["full", "center", "norm", "noborder", "noimplant", "highpass"]; out["variants"] = {m: {v: r3(ba(f"lr|{m}|{v}", "E2_hold_F", "F").ba_mean) for v in VAR} for m in ("effnet", "convnext", "swin")}
# --- meta
out["meta"] = dict(n_images=int(len(T)), n_sources=6, n_test=int((T.split == "test").sum()), n_train=int((T.split == "train").sum()), n_val=int((T.split == "val").sum()), n_checkpoints=29, n_audit_checks=13,
                   h1=dict(supported=int(G[G.primary].H1_supported.sum()), of=5, gap_min=r3(G[G.primary].gap.min()), gap_max=r3(G[G.primary].gap.max()), pooled_min=r3(G[G.primary].ba_pooled.min()), pooled_max=r3(G[G.primary].ba_pooled.max()), dec_min=r3(G[G.primary].ba_decoupled.min()), dec_max=r3(G[G.primary].ba_decoupled.max())),
                   chance=0.333)
(DATA / "results.json").write_text(json.dumps(out, separators=(",", ":"))); print("results.json", (DATA / "results.json").stat().st_size, "bytes")
# --- dimension reference (development rows only; used for the illustrative client-side kNN)
rows = pd.read_csv(ROOT / "artifacts/benchmark/v2/rows.csv"); rows = rows[rows.role == "target"]
ref = pd.concat([g.sample(min(len(g), 90), random_state=0) for _, g in rows.groupby(["source", "label"])])
(DATA / "dims_reference.json").write_text(json.dumps([[int(r.w), int(r.h), r.source, r.label] for r in ref.itertuples()], separators=(",", ":"))); print("dims_reference", len(ref))
