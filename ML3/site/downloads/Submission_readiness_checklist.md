# Final submission-readiness checklist

Status legend: ✅ done and verified · 🟡 done, residual caveat disclosed · ⛔ blocked on a human action (listed in "Actions only you can take").
Overall: **scientifically ready to submit as a pre-specified, evaluation-methodology paper once the four ⛔ items below are closed.** No main experiment was rerun and the frozen analysis is unchanged.

## 1. Methodology
| Item | Status | Evidence |
|---|---|---|
| Question, hypotheses and endpoints fixed before test unsealing | ✅ | `docs/FROZEN_analysis_plan.md`, `artifacts/final/freeze_v3.json` (SHA-256) |
| Sealed test opened once, with touch-log | ✅ | `test_touch_log.json`; audit check |
| Group-aware splits, leakage audit | ✅ | `check_dataset_integrity_v2.py`, audit checks |
| Deviations disclosed (A1, D1, D2) | ✅ | plan + manuscript Limitations 10 |
| Source-decoupled test rests on one source (n = 55) | 🟡 | Limitation 1; stated in abstract-level wording |
| Independent registry deposit of the freeze | ⛔ (optional but advised) | Limitation 14; deposit plan on OSF/AsPredicted *before* submission, citing hashes |

## 2. Statistics
| Item | Status | Evidence |
|---|---|---|
| Clustered paired bootstrap, B = 2000, seed 20261004 | ✅ | `final_stats.py` |
| Holm over 5 primary models; H1 supported 5/5 (adj. p = 0.0025) | ✅ | `artifacts/final/stats` |
| Metrics independently recomputed | ✅ | `audit_results.py` 13/13 PASS |
| Post-hoc analyses labelled exploratory | ✅ | hip/shoulder-only gap, same-source control, macro-F1 gap |
| Seeds capture training variability, not source sampling | 🟡 | Limitation 6 |

## 3. Data validity
| Item | Status | Evidence |
|---|---|---|
| FracAtlas knee labels (94) provisional, AI-assigned | ⛔ | Clinician package ready: `clinician_review/PROTOCOL.md`, `packet/`, `analysis/`. Needs ≥ 2 blinded clinician readers; then run `analyze_clinician_review.py` and `rerun_primary_with_consensus.py`, report both label sets side by side. Until then every claim carries the "provisional" caveat; sensitivity analysis shows conclusions survive without the knee class (gap 0.10–0.34, lower CI 0.02–0.21). |
| Provenance/licence of each source | 🟡 | `docs/submission/dataset_licences.md`; open points: Kaggle hip images (rights of the underlying figures), AV-DDH export marked "Private", OAI derivative terms, Figure 8 (failure cases) image permission |
| Implant confound | 🟡 | worded as plausible confound, never as cause |
| MURA / LERA / MRKR | ✅ decision | not necessary for the central claim; LERA = optional independent replication (`External_data_necessity_memo.md`); nothing added |

## 4. Citations
| Item | Status | Evidence |
|---|---|---|
| All 28 references resolved to a real record (Crossref/arXiv/OpenAlex) | ✅ | `scripts/verify_references.py`, `paper/sections/99_refs.md` |
| Geirhos 2020 and Holm 1979 verified | ✅ | OpenAlex records |
| References read only at abstract level (paywalled/blocked) | 🟡 ⛔ | statuses listed in `99_refs.md`; claims attributed to them are limited to abstract content. You should read the full texts of those flagged before submission. |
| No "first study" claim | ✅ | wording: "to our knowledge we found no study…; search not exhaustive" |

## 5. Reproducibility
| Item | Status | Evidence |
|---|---|---|
| Pinned environment | ✅ | `requirements.txt` |
| Step-by-step pipeline and expected outputs | ✅ | `REPRODUCIBILITY.md` |
| Checkpoint hashes; audit script | ✅ | `ft_registry.json`; `audit_results.py` |
| Fine-tuning bit-reproducibility | 🟡 | GPU non-determinism disclosed |
| Public code/artifact deposit (Zenodo/GitHub) with DOI | ⛔ | to be done by authors after licence decisions; image data must **not** be redistributed where licences forbid |
| Companion website (research demo) | ✅ | `site/`; API reports checkpoint hashes |

## 6. Overclaiming review
| Risk | Status |
|---|---|
| Clinical/diagnostic language | ✅ none; site and paper state "not a medical device" |
| Causal wording on implants | ✅ "plausible source-associated confound" |
| Generalisation of the 0.31–0.50 gap to other settings | ✅ scoped to "these public collections", three-class endpoint |
| Novelty | ✅ hedged |
| Hospital deployment inference | ✅ explicitly excluded (Limitation 7) |
| Grad-CAM as explanation | ✅ labelled activation only |
| Demo probabilities | ✅ labelled uncalibrated; softmax ≠ probability of correctness |

## Actions only you can take
1. **Clinician verification** of the 94 knee labels (two blinded readers, protocol in `clinician_review/`), then rerun the two analysis scripts and update Results/Abstract numbers if labels change.
2. **Authors, affiliations, contributions, funding, conflicts, ethics statement** — fill `docs/submission/author_and_declarations_TEMPLATE.md`. No such statement has been invented.
3. **Licences**: confirm Kaggle hip, AV-DDH ("Private"), OAI terms, and permission for any image shown in Figure 8; remove Figure 8 if permission cannot be established (the site already omits it).
4. **Read the abstract-only references** in full (list in `99_refs.md`) and adjust any sentence that depends on them.
5. **Optional**: deposit the freeze in an external registry; deposit code/artifacts with a DOI; decide on a LERA extension (needs a data-use agreement you must accept yourself).
6. **Deploy the website** to a host of your choice (Docker instructions in `site/README.md`); only you can supply hosting credentials.
