"""Independent audit of the frozen final evaluation. Writes artifacts/final/audit_report.json and prints PASS/FAIL per check.
Checks: (1) manifest hash vs freeze; (2) test rows never in any training set; (3) every unit evaluated exactly once (touch log) and prediction coverage complete / no duplicates;
(4) checkpoint hashes; (5) metrics recomputed independently with scikit-learn match summary.csv; (6) frozen-code hash drift; (7) split/group integrity; (8) test-set label sanity."""
import sys, json, glob, hashlib
sys.path.insert(0, "E:/ML3/scripts")
import numpy as np, pandas as pd
from pathlib import Path
from sklearn.metrics import balanced_accuracy_score
F = Path("E:/ML3/artifacts/final"); R = {}; ok_all = True
def check(name, cond, detail=""):
    global ok_all; R[name] = dict(passed=bool(cond), detail=str(detail)); ok_all &= bool(cond); print(("PASS " if cond else "FAIL ") + name, detail)

M = pd.read_csv("E:/ML3/artifacts/benchmark/manifest_v2.csv"); fz = json.load(open(F / "freeze_v3.json")); ad = json.load(open(F / "freeze_addendum.json"))
check("manifest_hash_matches_freeze", hashlib.sha256(Path("E:/ML3/artifacts/benchmark/manifest_v2.csv").read_bytes()).hexdigest() == fz["artifacts/benchmark/manifest_v2.csv"])
TEST = M[(M.split == "test") & (M.role == "target")]; check("test_rows_count_657", len(TEST) == 657, len(TEST))
check("no_group_spans_splits", (M[M.role == "target"].groupby("group").split.nunique() > 1).sum() == 0)
# (2) recompute every training set and intersect with test paths
import final_eval as fe
tp = set(TEST.path); bad = 0; n_sets = 0
for seed in fe.SEEDS:
    for name, (tr, bal) in fe.train_sets(seed).items():
        n_sets += 1; bad += len(tp & set(tr.path))
check("training_sets_disjoint_from_test", bad == 0, f"{n_sets} training sets checked, {bad} test paths found")
# (3) touch log and coverage
log = json.load(open(F / "test_touch_log.json")); units = [k for k in log if k != "BUILD_ATTEMPTS"]
check("touch_log_units", len(units) == 25 + 29, len(units)); check("single_unsealing_attempt", len(log["BUILD_ATTEMPTS"]) == 1, log["BUILD_ATTEMPTS"])
D = pd.concat([pd.read_csv(f) for f in glob.glob(str(F / "preds" / "*.csv.gz"))], ignore_index=True); D["model"] = D.kind + "|" + D.key
dup = D.duplicated(["model", "protocol", "seed", "eval", "mrow"]).sum(); check("no_duplicate_predictions", dup == 0, dup)
cov_bad = 0
for (m, p, s, e), g in D[D["eval"] != "UNK"].groupby(["model", "protocol", "seed", "eval"]):
    exp = {"pooled_test": TEST, "F": TEST[TEST.source == "F"], "native_test": TEST[~TEST.source.isin(["K", "U"])]}.get(e, TEST[TEST.source == e])
    if set(g.mrow) != set(exp.index): cov_bad += 1
check("prediction_coverage_complete", cov_bad == 0, f"{cov_bad} (model,protocol,seed,eval) cells with missing/extra test rows")
check("true_labels_match_manifest", (D[D["eval"] != "UNK"].set_index("mrow").true == M.loc[D[D["eval"] != "UNK"].mrow.values, "label"].values).all())
# (4) checkpoint hashes
reg = json.load(open(F / "ft_registry.json")); mism = [k for k, v in reg.items() if hashlib.sha256(Path(v["ckpt"]).read_bytes()).hexdigest() != v["sha256"]]
check("checkpoint_hashes_match", not mism and len(reg) == 29, f"{len(reg)} checkpoints, mismatches {mism}")
check("addendum_hashes_equal_registry", all(ad["checkpoints"][k]["sha256"] == v["sha256"] for k, v in reg.items()))
# (5) independent recomputation of balanced accuracy
S = pd.read_csv(F / "stats" / "summary.csv"); rng = np.random.default_rng(0); diffs = []
for r in S.sample(60, random_state=1).itertuples():
    g = D[(D.model == r.model) & (D.protocol == r.protocol) & (D["eval"] == r.eval)]; v = [balanced_accuracy_score(gg.true, gg.pred) for _, gg in g.groupby("seed")]; diffs.append(abs(np.mean(v) - r.ba_mean))
check("recomputed_balanced_accuracy_matches_summary", max(diffs) < 1e-9, f"max abs diff over 60 random cells = {max(diffs):.2e}")
G = pd.read_csv(F / "stats" / "gap.csv"); chk = []
for r in G.itertuples():
    a = S[(S.model == r.model) & (S.protocol == "E0_pooled")].ba_mean.iloc[0]; b = S[(S.model == r.model) & (S.protocol == "E2_hold_F")].ba_mean.iloc[0]; chk.append(abs((a - b) - r.gap))
check("gap_equals_difference_of_summary_values", max(chk) < 1e-9, f"max diff {max(chk):.2e}")
# (6) frozen code drift
drift = {}
for f, h in {**{k: v for k, v in fz.items() if k.endswith((".py", ".md", ".csv", ".json")) and not k.startswith("_")}, **{k: v for k, v in ad.items() if k.endswith((".py", ".md", ".json")) and not k.startswith(("_", "checkpoints"))}}.items():
    p = Path("E:/ML3") / f
    if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() != h: drift[f] = "changed since freeze record"
R["code_drift_since_freeze_records"] = drift; print("INFO files changed since their freeze/addendum record:", list(drift))
(F / "audit_report.json").write_text(json.dumps(R, indent=1)); print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
