# Pre-submission fix list and final peer-review round

Updated after the final audit (`scripts/audit_results.py`: 13/13 checks PASS), the reference verification (`artifacts/final/reference_verification.csv`) and the post-hoc robustness checks. Round 1 of the simulated review is in `Peer_Review_Simulation.md`; this file adds round 2 (after audit) and the concrete to-do list.

## A. Audit findings (scientific correctness)
| Item | Result |
|---|---|
| Test set opened once; 54 units each evaluated once; one unsealing attempt | PASS |
| Training sets (65 recomputed) disjoint from the 657 test rows | PASS |
| Prediction coverage complete, no duplicates, labels match manifest | PASS |
| 29 checkpoint hashes match registry and addendum | PASS |
| Balanced accuracy and gaps independently recomputed (max error 1e-16) | PASS |
| Leakage audit (4,427 images): 0 cross-split / cross-source near-duplicates, 0 groups across splits | PASS |
| Files changed after their freeze record | only `make_figures.py` (layout code; no analysis effect) |
| **Disclosure added**: early prototype audit looked at all 806 prototype images (incl. some later sealed) for metadata predictability; no reported model used it | disclosed (Section 9, Limitation 13) |
| **Disclosure added**: freeze is a local hash record, not an external registry | disclosed (Limitation 14, Declarations) |
| **Nuance added**: "decoupled" evaluation also removes FracAtlas from training, so the gap combines "source seen in training" with shortcut use. Same-source control shows the identical test images are classified at 1.000 by pooled models | added (Section 16.2, Table 14) |
| **Nuance added**: gap depends on the provisional FracAtlas knee class (hip/shoulder-only gap 0.10-0.34) | added (Section 16.1, Tables 12-13) |
| Held-out single-class "balanced accuracy" equals recall, and RF dimension/metadata values there are trivial | caption note added (Table 4) |
| Implant language | audited by text search: only "plausible source-associated confound"; no causal claim; mechanistic phrases softened to "consistent with" |

## B. Citation audit
28 of 28 reference checks confirmed (Geirhos and Holm via OpenAlex) against Crossref/arXiv (DOI, first author, year, venue). Corrections applied: Rafferty & Rajan journal year is 2026 (arXiv 2025); Mitsuyama et al. is *Eur Radiol* vol. 36 (online 2025); Gong et al. *Sci Rep* 12:12179; Karnuta et al. DOI 10.1016/j.arth.2023.03.039 found; HipXNet DOI 10.1109/ACCESS.2022.3173424 found. **Unverified**: Geirhos 2020 and Holm 1979 (lookup failed). One unverifiable snippet-level source was removed. Research gap wording: "To our knowledge we found no study specifically evaluating ...", never "first".

## C. Round 2 of the simulated review (after audit)
**Reviewer 1 (medical imaging).** (1) *The decoupled gap conflates removing FracAtlas from training with shortcut use.* -> Same-source control and explicit wording added; unresolved without a second multi-joint source (Fix 3). (2) *Knee labels.* -> still the weakest link (Fix 1). (3) *55 test images.* -> CIs reported; development decoupled set (n = 319) reported as supporting evidence; Fix 3 would increase power.
**Reviewer 2 (machine learning).** (1) *Is the pre-registration credible?* -> local hash record, deviations A1/D1/D2 disclosed, test-touch log; external registry not available (Limitation 14). (2) *Undertrained networks.* -> acknowledged (Fix 5). (3) *No mitigation tested beyond input variants.* -> out of scope, stated. (4) *Post-hoc analyses (hip/shoulder-only, same-source, macro-F1) could be seen as forking paths.* -> all labelled post hoc/exploratory; none changes a pre-specified verdict.
**Reviewer 3 (clinical).** (1) *Clinical relevance limited.* -> Section 19 restricts claims to evaluation practice. (2) *AI-assigned labels.* -> declared in Ethics and Declarations; clinician check required (Fix 1).

## D. Concrete fixes before submission (ordered)
| # | Fix | Who | Status |
|---|---|---|---|
| 1 | Clinician review of the 94 FracAtlas knee labels (`artifacts/benchmark/fracatlas_leg_visual_labels.csv`) and, if labels change, re-run `final_stats.py` on the *same* predictions (labels only) and report both versions | clinician + analyst | open |
| 2 | Verify Geirhos 2020 and Holm 1979 manually; read Patwary & Toma 2026, Hrubý et al. 2024 and Karnuta et al. 2023 in full (only abstracts read) | authors | open |
| 3 | Add at least one more multi-joint or per-joint source (MURA, LERA, MRKR; data-use agreements must be accepted by the authors) and re-run the frozen pipeline as a clearly labelled extension | authors | open |
| 4 | Complete author list, contributions, funding, competing interests; decide whether to deposit the frozen plan in an external registry (e.g. OSF) with timestamps | authors | open |
| 5 | Optional: longer fine-tuning (more epochs/resolution), more ConvNeXt-T fine-tuning seeds, and a domain-generalisation baseline | analyst | optional |
| 6 | Confirm licences for the Kaggle hip set and AV-DDH ("Private" in the Roboflow export) and the OAI terms before sharing any derived data | authors | open |
| 7 | Replace author-year citation keys with the journal's style; copy-edit; check figure legibility at print size | authors | open |
| 8 | Re-run `scripts/audit_results.py` and `scripts/check_dataset_integrity_v2.py all` on the final repository state and archive with a DOI | analyst | at submission |

## E. Verdict
The study is internally consistent and reproducible from the recorded artefacts, and its central claims are stated at the strength the evidence supports. It is a complete draft; submission should wait for Fixes 1-4. If Fix 3 cannot be done, the paper should say plainly that the decoupled test rests on one source of 55 images.
