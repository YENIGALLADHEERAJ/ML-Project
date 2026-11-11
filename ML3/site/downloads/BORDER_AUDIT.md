# Paired border interventions for orthopaedic radiograph classification

## Abstract

A classifier can use acquisition and preprocessing cues to predict anatomical labels. We tested whether a synthetic border derived from another dataset changed a classifier's prediction more often than an identically constructed border derived from the original dataset. The pilot used 41 held-out FracAtlas hip and shoulder images and two EfficientNet-B3 checkpoints. Each image received five within-source and five cross-source interventions using donors with the same joint label. The pooled checkpoint changed zero predictions. The checkpoint trained without FracAtlas changed 12 of 205 within-source predictions and 17 of 205 cross-source predictions. The paired difference was 2.4 percentage points, with a 95% image-group bootstrap interval of 0.0 to 5.9 points. This supports sensitivity to border edits in one checkpoint. The evidence for additional cross-source sensitivity remains inconclusive.

## Prior work and contribution

| Work | Prior contribution | Relation to this pilot |
|---|---|---|
| SAM-X | Sorted musculoskeletal radiographs into 28 anatomical regions. | Establishes that anatomy sorting is an existing task. |
| DeGrave et al. | Swapped laterality markers and used patch controls to probe chest radiograph shortcuts. | Precedent for image intervention and matched controls. |
| FracAtlas | Provides musculoskeletal radiographs and region labels. | Supplies target images and within-source development donors. |
| RoentMod | Uses text-guided chest radiograph modifications to investigate shortcuts. | Demonstrates richer interventions. This pilot uses deterministic edits with exact center-pixel equality. |

The focused contribution is a paired within-source versus cross-source border-intensity test for the same held-out joint image, with same-joint donor controls and a public-facing comparison of the actual model scores. The targeted search found related interventions and sorting systems. It cannot establish priority over all published or unpublished work.

## Methods

1. Select the original 26 Hip and 15 Shoulder rows in the FracAtlas holdout. The provisional Knee subset is outside this analysis.
2. For each target and each donor condition, draw five development-training donors without replacement using seed 714. Donors share the target joint and have a different recorded group. Donors can recur across target images. Cross-source donors come from the other available sources for that joint.
3. Use the archived 160 × 160 greyscale model inputs. Take the median of each donor's four 12-pixel edge bands. Paint the target's corresponding outer bands with those four intensities. Top and bottom bands take precedence at the corners. The code asserts exact equality of all pixels in the central 136 × 136 region. The frames do not contain donor pixels.
4. Score the original input and each intervention with the seed-0 pooled and without-FracAtlas EfficientNet-B3 checkpoints. Define a flip as a change in the top-scoring class from the original input. A flip can correct or introduce an error. It measures sensitivity, independently of whether the original prediction matched the label.
5. Average the five flip indicators in each condition within each image. Subtract within-source from cross-source per image, then average over images. Report a percentile interval from 2,000 paired bootstrap resamples of recorded groups. The intervals are conditional on the checkpoints and sampled donor assignments.

## Results

| Checkpoint | Within-source flips | Cross-source flips | Difference | 95% paired bootstrap interval |
|---|---:|---:|---:|---:|
| Pooled | 0/205 (0.0%) | 0/205 (0.0%) | 0.0 pp | 0.0 to 0.0 pp |
| Without FracAtlas | 12/205 (5.9%) | 17/205 (8.3%) | +2.4 pp | 0.0 to 5.9 pp |

The 205 interventions per condition reuse 41 target images. The bootstrap unit is the recorded group, of which there are 41. The zero-width interval for the pooled checkpoint reflects zero observed flips in both conditions and limited bootstrap support. It gives no population guarantee. The interval for the without-FracAtlas checkpoint reaches zero.

## Limitations and next evaluation

This is an exploratory reuse of the existing study holdout. The protocol choices were set before running this experiment, with no independent preregistration. The rim can contain peripheral anatomy and the edits can introduce seams. The center is pixel-identical across comparisons. The within-source condition controls the type and location of the edit, while the donor distributions can differ in intensity and acquisition characteristics. The experiment does not identify the cause of any source difference or generalize to all border styles.

An independent replication should freeze the protocol, use clinician-reviewed test labels from additional sources, repeat across training seeds and ring widths, and report the sensitivity of the result to the donor draw. Before submission, check dataset and checkpoint redistribution terms, finish the author contribution statements and obtain any required institutional review. Publication acceptance and literature priority have not been established.

## Reproduction and evidence

Run `python ML3/scripts/border_audit.py` from the workspace with the project's Python environment and existing archived development/test arrays. The script produces a machine-readable report with per-image probabilities, donor manifest identifiers, frame parameters and checkpoint hashes under `ML3/artifacts/border-audit`. The website shows two representative inputs and their saved scores. The feature runs without additional model requests.

- **PBL 2:** Related-work comparison, bounded gap, measurable endpoint and matched intervention design.
- **PBL 3:** Reproducible model outputs, paired uncertainty interval and browser demonstration. Use case is dataset and model quality auditing. The experiment requires no retraining and the visualization uses saved outputs.
- **Record:** Draft methods, table, citations, limitations and reproduction steps. Transfer into the required department template before submission.
- **Viva:** Explain why the joint stays matched, why the central pixels are asserted equal, why 205 edits do not give 205 independent images, and why an interval reaching zero matters. Each teammate must document their actual work.

## References

1. SAM-X: sorting algorithm for musculoskeletal X-ray radiography. European Radiology. DOI: [10.1007/s00330-022-09184-6](https://doi.org/10.1007/s00330-022-09184-6).
2. DeGrave AJ, Janizek JD, Lee SI. AI for radiographic COVID-19 detection selects shortcuts over signal. Nature Machine Intelligence. 2021. DOI: [10.1038/s42256-021-00338-7](https://doi.org/10.1038/s42256-021-00338-7).
3. Abedeen I et al. FracAtlas: A dataset for fracture classification, localization and segmentation of musculoskeletal radiographs. Scientific Data. 2023. DOI: [10.1038/s41597-023-02432-4](https://doi.org/10.1038/s41597-023-02432-4).
4. RoentMod: a synthetic chest X-ray modification model to identify and correct image interpretation model shortcuts. npj Digital Medicine. 2026. DOI: [10.1038/s41746-026-02497-6](https://doi.org/10.1038/s41746-026-02497-6).
