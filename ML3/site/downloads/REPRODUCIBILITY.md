# Reproducibility guide

Study: source-controlled evaluation of hip/knee/shoulder radiograph recognition (6 public sources, 4,427 target images, 657 sealed test rows).
Environment: Windows 11, Python 3.11.14, `requirements.txt` (torch 2.4.1+cu121, scikit-learn 1.9.0, pandas 3.0.5), GPU GeForce MX250 (2 GB). Seeds: 0-4 (RF/probes), 0-2 (fine-tuning); bootstrap seed 20261004, B = 2000.

## 0. What is and is not in the repository
Included: code (`scripts/`, `paper/build_manuscript.py`), frozen plan and hashes (`docs/FROZEN_analysis_plan.md`, `artifacts/final/freeze_v3.json`, `freeze_addendum.json`), manifests and split definitions (`artifacts/benchmark/manifest_v2.csv`, `fracatlas_leg_visual_labels.csv`), per-image predictions (`artifacts/final/preds/`), statistics (`artifacts/final/stats/`), figures and manuscript (`paper/`). **Images are not redistributed**; obtain them from the original providers (URLs/DOIs in Table 1 of the manuscript and `docs/dataset_access_status.md`) and place them as described below.

## 1. Data layout expected by the scripts (`E:\ML3\data\...`)
`fracatlas/FracAtlas` (figshare 10.6084/m9.figshare.22363012, CC BY 4.0) | `hip/Data` (Kaggle `tawsifurrahman/aseptic-loose-hip-implant-xray-database`) | `data/` (Kaggle `yasserhessein/shoulder-implant-xray`; = UCI 10.24432/C5F893) | `knee_real/MedicalExpert-I` (Gornale, Mendeley 10.17632/t9ndx37v5h.1) | `avddh/sample` (400 unique originals from the `valid`/`test` folders of Mendeley 10.17632/4gvcb6gmh2.2, seed 7) | `oai_knee` (Kaggle `shashwatwork/knee-osteoarthritis-dataset-with-severity`). Paths are absolute (`E:/ML3/...`) inside the scripts.

## 2. Pipeline (each step is deterministic given the seeds)
1. `python scripts/bench2_manifest.py` - builds `manifest_v2.csv` (group-aware splits; v1 sealed split preserved). Check SHA-256 against `freeze_v3.json`.
2. `python scripts/bench2_variants.py`, `bench2_embed.py` - input variants (160 px) and frozen-backbone embeddings for **non-test rows only**.
3. Development study (validation partitions only): `bench2_probes.py hand|probes ...`, `bench2_finetune.py ...`, `bench2_analysis.py`, `bench2_boot.py`, `bench2_report.py`, `bench2_ood_summary.py`, `bench2_final_table.py`, `bench2_build_report.py` -> `artifacts/benchmark/v2/`, `docs/Research_Validation_Report.md`.
4. Freeze: `docs/FROZEN_analysis_plan.md`, `artifacts/final/freeze_v3.json` (written before any test image was opened).
5. Phase A (dev data only): `python scripts/final_eval.py recipes` and `python scripts/final_eval.py train` (29 checkpoints, hashes in `artifacts/final/ft_registry.json`; fine-tuning is not bit-reproducible across GPUs, so retrained checkpoints will differ slightly; the stored hashes identify the exact weights evaluated).
6. Phase B (unseals the test set; refuses to repeat): `final_eval.py build`, `eval_cls all`, `eval_ft` -> `artifacts/final/preds/`, `test_touch_log.json`.
7. `python scripts/final_stats.py` (frozen statistics, ~1-1.5 h) -> `artifacts/final/stats/`; post-hoc: `final_sensitivity.py`, `final_sensitivity2.py`.
8. `python scripts/audit_results.py` (13 independent checks, all PASS: manifest hash, test/training disjointness, single unsealing, prediction coverage, checkpoint hashes, recomputed metrics) and `python scripts/check_dataset_integrity_v2.py all` (leakage audit) and `python scripts/verify_references.py`.
9. `python scripts/make_figures.py`, `python paper/build_manuscript.py`, `python scripts/md_to_docx.py paper/manuscript.md paper/manuscript.docx`.

## 3. Expected key outputs (to check a reproduction)
Pooled balanced accuracy 0.993-1.000 and decoupled (hold out FracAtlas) 0.498-0.686 for the five primary models; H1 supported 5/5; RF on metadata/dimensions 0.960/0.971 -> 0.333; hold out K 0.00-0.04, hold out U 0.00-0.17 (`artifacts/final/stats/gap.csv`, `summary.csv`). Seed-level results in `summary.csv` column `ba_seeds`.

## 4. Known non-determinism and deviations
GPU fine-tuning (cuDNN) and thread scheduling can change third decimals; probes and random forests are deterministic given seeds. Amendment A1 and Deviations D1, D2 are documented in the frozen plan. `make_figures.py` changed layout code after the freeze record (no analysis effect). Operational notes: launch long jobs detached; the laptop may sleep (wall-clock times in logs can be inflated).
