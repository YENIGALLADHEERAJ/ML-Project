# Simulated peer review of the manuscript (`paper/manuscript.md`)

Three reviewers were simulated by the authors' analysis assistant after the sealed-test results existed. For every criticism the disposition is one of **Fixed** (manuscript changed), **Analysed** (a new, clearly labelled post-hoc analysis was run), or **Acknowledged** (listed as a limitation; cannot be fixed with the available data). No pre-specified conclusion was changed after seeing the test results.

## Reviewer 1: medical imaging

| # | Criticism | Disposition |
|---|---|---|
| 1.1 | The decoupled test is 55 images from one source, and the knee class (14 images) rests on labels the authors assigned themselves. The headline gap could be a knee-label or view artefact. | **Analysed + Fixed.** Per-class recall with CIs and a hip/shoulder-only gap were added (Section 16.1, Tables 12–13, `final_sensitivity.py`). Result: knee recall is low for every model; excluding knee shrinks the gap to 0.10–0.34 (fine-tuned EfficientNet-B3 0.10, CI 0.02–0.21), so the 3-class result depends materially on the knee class. The abstract, discussion and conclusion now say so. The pre-specified H1 verdict is not changed, but the size of the effect is qualified. |
| 1.2 | FracAtlas knee labels are not clinician-verified. | **Acknowledged** (Limitations 2; Ethics): needs a clinician review. The conclusions that do not depend on these labels (anatomy-free baselines, implant-source holdouts) are stated separately. |
| 1.3 | Age, sex, device and view differ between sources (paediatric AV-DDH; pre-cropped OAI knees). Are these confounds or the signal? | **Acknowledged** (Limitations 3; Section 14 table). They are part of what "source" means here; no metadata allow separating them. |
| 1.4 | Public datasets without patient IDs: leakage within source cannot be excluded. | **Acknowledged** (Section 7). Group splitting by reference, id neighbourhood and near-duplicate cluster was used; audit shows zero cross-split near-duplicates. |
| 1.5 | Is joint recognition a clinically meaningful task? | **Fixed** (Section 19): reframed as a routing/label-QC/implant-pipeline building block; no clinical-outcome claim. |

## Reviewer 2: machine learning

| # | Criticism | Disposition |
|---|---|---|
| 2.1 | Fine-tuning was short (3 epochs, 160 px, no tuning) and may be under-trained; the gap may partly reflect weak training. | **Acknowledged** (Limitations 5). Mitigating evidence: frozen probes and fine-tuned models agree; development within-source accuracy is near 1.0. Not resolvable with the available compute. |
| 2.2 | Seeds vary only the training-set draw and initialisation, not the source; CIs hold models fixed. | **Fixed**: stated in Sections 15 and 18; seed SD, range and cluster-bootstrap CIs are reported separately and not mixed. |
| 2.3 | Multiple comparisons. | **Fixed**: only H1 is a confirmatory family (Holm over 5 models); everything else is labelled descriptive/exploratory, including variant comparisons and the sensitivity analysis. |
| 2.4 | The metadata/dimension RF at exactly 0.333 is a trivial constant prediction, not "learning a shortcut". | **Fixed**: the text now says these models predicted every FracAtlas image as shoulder, i.e. the source-to-label mapping carries no joint information once broken. |
| 2.5 | AUPR is not comparable between pooled and decoupled settings (different known/unknown ratios). | **Fixed**: caption of Table 6 states this; AUROC and FPR are the comparable metrics. |
| 2.6 | AUROC of confidence for correctness is undefined when all or no predictions are correct, which limits H4. | **Fixed**: reported as undefined; H4 stated as "supported where defined"; accuracy at 50% coverage and ECE (defined everywhere) carry the conclusion. |
| 2.7 | The "source-controlled method" is not a method; no mitigation is shown to work. | **Fixed/Acknowledged**: the paper is framed as an evaluation study; input variants are exploratory and none rescues the implant holdouts; domain-generalisation methods (adversarial, balanced sampling beyond weighting) were not tested. |
| 2.8 | Models were retrained for the test set; results may differ from development. | **Fixed**: Table 10 compares development and test side by side; differences are small for the primary comparison. |
| 2.9 | The unknown-joint pool and Mahalanobis settings were fixed in development. | **Acknowledged** (Limitations 11); neither was tuned on test data. |
| 2.10 | Source decodability (Figure 3b) is development data only. | **Acknowledged**: labelled as development evidence in the text and caption. |
| 2.11 | Code defects during the final run (D1 import error; D2 process stopped). | **Fixed**: disclosed with hashes in the frozen plan and Limitations 10; no test output existed at either point. |

## Reviewer 3: clinical / orthopaedic

| # | Criticism | Disposition |
|---|---|---|
| 3.1 | Implant claims: are implants the cause? | **Fixed**: the manuscript says only that implant presence is a plausible source-associated confound; the weak implant-mask proxy is reported with its flag rates; the error-analysis table separates evidence from hypothesis. |
| 3.2 | Real radiographs rarely come as 224-pixel crops or web figures; relevance to clinical PACS images is unclear. | **Acknowledged** (Limitations 3, 7; Section 19). No hospital data were available. |
| 3.3 | Paediatric hip images are a different population; are they a fair "hip" source? | **Acknowledged**: reported separately (hold-out A); not pooled into a claim about adult hips. |
| 3.4 | Recommendations should not overreach to clinical AI products. | **Fixed**: Section 19 states the study shows nothing about any particular product or about clinical outcomes. |
| 3.5 | Ethics and licensing of the data. | **Fixed**: Section 22 lists licences, redistribution limits and that AI-assigned labels must not be used clinically. |
| 3.6 | Would a clinician or hospital validate the knee labels and add an institutional set? | **Acknowledged** as the recommended next step. |

## Readiness verdict
The manuscript is a complete **draft** of an evaluation/benchmark study. It is not ready for submission until (1) a clinician checks the FracAtlas knee labels, (2) at least one more multi-joint source is added (MURA, LERA or MRKR, which need user-side data-use agreements), (3) the two blocked fracture papers and the other V2/V3 references are read in full and the reference list is verified, and (4) the "[B]"-flagged references are checked.
