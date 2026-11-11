# FROZEN analysis plan (protocol v3), written before any sealed test image was opened

Status at freeze: the 657 sealed test rows (manifest v2, `split == "test"`) have **never been opened** by any script. Development results are in `docs/Research_Validation_Report.md`. This plan fixes what will be run on the test rows, how it is analysed and how it is interpreted. Any later deviation will be listed in the manuscript as a deviation.

## 1. Question and design
Question: *Can conventional pooled evaluation of public orthopaedic radiograph datasets substantially overestimate anatomical (joint) generalisation because joint labels are confounded with data source / acquisition?*
Task: 3-class Hip / Knee / Shoulder. Sources: F FracAtlas (all three joints; knee labels provisional), K Kaggle hip, U UCI shoulder, A AV-DDH hip, G Gornale knee, O OAI-derived knee. Unit of clustering: `group` column (patient / literature reference / near-duplicate cluster / FracAtlas id neighbourhood).

**Models are retrained from the frozen recipes** because earlier development runs did not store checkpoints. Training data = development partitions only (`rows.csv`, split ∈ {train,val}); recipes are identical to development (capped draw of 300 images per source×label per seed, 80/20 group-wise calibration split for temperature scaling, same hyper-parameters). Only the evaluation rows change (development rows → sealed test rows of the same sources).

| Protocol | Training data (dev only) | Test evaluation set (sealed rows) |
|---|---|---|
| E0 pooled random | all sources, train partition | all 657 test rows |
| E1 pooled, source-balanced weights | same, cell-balanced weights | all 657 |
| **E2 decoupled external** | all sources except F | F test rows (n=55: 26 hip, 14 knee, 15 shoulder) |
| E3 leave-one-source-out (K,U,A,G,O) | all sources except X | X test rows (24, 89, 60, 247, 182) |
| E6 F only → others | F dev rows | each other source's test rows |
| E7 native-only (no K,U) pooled and hold A/G/O | native sources | native test rows / X test rows |

Model families (all reported): handcrafted baselines with random forest (dimensions, metadata, border frame, 8×8 low-frequency, 32-bin histogram, HOG full, HOG centre; 5 seeds); frozen-backbone linear probes (EfficientNet-B3, ConvNeXt-T, Swin-T × 6 input variants; 5 seeds); fine-tuned (3 epochs, 160 px): EfficientNet-B3 (E0, E2, K, U, A, G, O; 3 seeds), Swin-T (E0, E2, K, U; 3 seeds), ConvNeXt-T (E0, E2; **1 seed**). **Primary models** (≥3 seeds, full image): FT EfficientNet-B3, FT Swin-T, probe EfficientNet-B3, probe ConvNeXt-T, probe Swin-T.
OOD "unknown joints" = the same unknown pool as in development (FracAtlas hand, n=400, and 101 visually verified non-knee leg images); these images are not test rows and are only used as the OOD comparison set.

## 2. Primary hypothesis and endpoint
**H1.** For deep models, balanced accuracy under pooled evaluation (E0, all test rows) exceeds balanced accuracy under source-decoupled evaluation (E2, F test rows) by more than 0.10.
Primary endpoint per model: Δ = BA(E0, pooled test) − BA(E2, F test), BA = mean over seeds of per-seed balanced accuracy (macro-average of per-class recall over classes present).
H1 is **supported** if the Holm-adjusted one-sided p-value for H0: Δ ≤ 0.10 is < 0.05 **and** the lower bound of the 95% CI exceeds 0.10 for **at least 4 of the 5 primary models**. Otherwise H1 is reported as not supported/partially supported; the hypothesis will not be re-defined.

## 3. Secondary endpoints / hypotheses
- **H2.** Anatomy-free baselines (RF on metadata; RF on dimensions) have pooled BA ≥ 0.90 and decoupled BA ≤ 0.40 (chance = 0.333).
- **H3.** Holding out an implant-bearing source (K, U) gives BA < 0.25 for every primary model (point estimate; CI upper bounds reported).
- **H4.** On K and U holdouts, confidence is not positively informative about correctness (AUROC of max-softmax for correctness, seed-averaged, CI reported; "anti-informative" if the CI upper bound is < 0.5).
- **H5 (descriptive).** Confidence-based unknown-joint detection (AUROC of MSP) is lower under decoupled evaluation (E2) than under pooled evaluation (E0); feature-space Mahalanobis (probes only) is reported alongside MSP, energy, negative entropy, and temperature-scaled MSP. No OOD method is claimed as novel.
- Descriptive: per-class recall and specificity, macro-F1, confusion matrices (seed-averaged), ECE (15 bins; raw and temperature-scaled), AURC and accuracy at 50% coverage, seed SD / range, native-only (E7) and cross-source (E6) results, input-variant results for probes, dev-versus-test comparison.

## 4. Statistical methods (and why)
- **Cluster bootstrap (2,000 resamples, seed 20261004) over `group`**: images from the same patient / source article / near-duplicate set are not independent; resampling whole clusters gives CIs that respect this. Point estimate = mean over seeds; the bootstrap holds the trained models fixed, so CIs reflect evaluation-set sampling. Seed variability is reported separately (SD, range, individual seeds; t-intervals are *not* used for inference because seeds are not independent samples of the source population).
- **Primary gap test**: E0 predictions are available for all pooled test rows, E2 predictions only for F rows, and F rows belong to the pooled set. The bootstrap therefore draws clusters from the *pooled* test set once and computes both balanced accuracies on the same draw (clustered, correlation-aware, paired by construction); the one-sided p-value is (#{Δ_b ≤ 0.10} + 1)/(B + 1).
- **Multiplicity**: Holm–Bonferroni across the 5 primary models for H1. All other analyses are descriptive/exploratory and unadjusted; they are labelled as such.
- **Paired model comparisons** on the same decoupled F test rows use a paired cluster bootstrap of the BA difference (same cluster draws for both models) — appropriate because the same images are scored by every model; McNemar's test is not used because predictions are clustered and averaged over seeds.
- **OOD metrics**: AUROC, AUPR (unknown = positive), FPR at 95% TPR of known images, per seed then averaged; CIs by independent cluster bootstrap of the known and unknown sets.
- **H4 AUROC CI**: cluster bootstrap with per-seed AUROC averaged (resamples with a single outcome class are discarded and counted).
- Class-wise sensitivity = recall; specificity = one-vs-rest from the seed-averaged confusion matrix.
- Power caveat (pre-stated): the decoupled test set has 55 images (26/14/15), so intervals will be wide; the dev-set decoupled evaluation (n=319) is reported as supporting, non-confirmatory evidence.

## 5. Planned tables and figures
Tables: T1 dataset inventory; T2 prior-art comparison; T3 pooled vs decoupled performance (all models, test); T4 leave-one-source-out and cross-source results; T5 primary-endpoint gap statistics (with Holm); T6 OOD / calibration / selective prediction; T7 paired comparisons and dev-vs-test; Supplementary: per-seed results, input variants, native-only, confusion matrices.
Figures: F1 workflow; F2 dataset/source composition; F3 evidence of source shortcuts (feature groups pooled vs decoupled; source decodability); F4 pooled vs source-controlled performance; F5 leave-one-source-out; F6 confusion matrices; F7 OOD/confidence behaviour; F8 representative failure cases.

## 6. Interpretation rules fixed in advance
1. Implant presence will be described only as **a plausible source-associated confound**; no causal claim. The implant-masking proxy is weak (flags 93% K, 83% U, 69% F-shoulder, 33% A, 7% G, 0.6% O) and will be described as such.
2. OOD/selective prediction is a **secondary reliability finding**, not a novel method.
3. Novelty wording: "To our knowledge, we found no study specifically evaluating whether pooled public orthopaedic radiograph joint recognition is inflated by joint–source confounding using source-decoupled and leave-source-out evaluation, although shortcut learning and cross-dataset failures have been reported in other medical-imaging and orthopaedic tasks" — used only if the final literature check supports it (it does as of the freeze: closest precedents are Hill 2024, Ly 2024, Badgeley 2019, Kutbi 2026).
4. No tuning of models, thresholds, preprocessing, hyper-parameters or analysis choices after seeing test results. If results weaken a claim, the claim is weakened in the paper.
5. Each unit (classical model set, probe set, checkpoint) is evaluated on the test rows **once**, enforced by a touch-log (`artifacts/final/test_touch_log.json`). Unsealing itself (opening test images) is guarded to happen once.

## 7. Known limitations accepted at freeze
Few independent sources; FracAtlas knee labels provisional and not clinician-verified; scraped/web-collected provenance for K and U; implant presence confounded with source; weak implant proxy; limited compute (3-epoch fine-tuning, ConvNeXt fine-tuning 1 seed); no hospital-level external validation; MRKR/MURA/LERA not accessed (require user-side agreements); decoupled test n=55.

## Amendment A1 (made BEFORE unsealing; test images still unopened)
Fine-tuning ran about twice as slowly as budgeted (GPU thermal/clock limits, ~8 min per checkpoint). To finish the frozen evaluation, the fine-tuned **A, G and O holdouts are trained for seed 0 only** (they are secondary/descriptive); EfficientNet seeds 1-2 and all Swin seeds run E0, E2, K, U (the protocols that carry H1, H3, H4). Primary endpoint, models, thresholds and statistics are unchanged. The amended `final_eval.py` hash is recorded in `artifacts/final/freeze_addendum.json` together with all checkpoint hashes before Phase B.

## Deviation D1 (code bug, before any test image was read)
The first unsealing attempt (2026-10-03 17:00) failed with `NameError: name 'Image' is not defined` in `final_eval.py` before the first `Image.open` call; **no test image was read and no test output was produced**. The missing `PIL` import was added, the one-time BUILD assertion was replaced by an attempts log (so a crash cannot block a deterministic rebuild), and the Phase B code paths (variant/feature construction, classical/probe evaluation, checkpoint loading) were smoke-tested on development rows only: variants and handcrafted features reproduce the stored development arrays exactly. No analysis choice changed. The updated `final_eval.py` hash is in `freeze_addendum.json` (key `final_eval.py`, field `_meta.deviation_D1`).

## Deviation D2 (process management, no analytic effect)
During the one-time evaluation, the process evaluating classical/probe units was terminated by the analyst (a mis-targeted stop of a launcher process) after five units (`dims_only`, `meta_all`, `lowfreq_only`, `hist_only`, `border_only`) had been written and logged. The remaining units had produced no output and no results had been inspected; they were relaunched with the identical frozen code and recipe hashes, and the touch-log skips completed units. No unit was evaluated twice with outputs retained.
