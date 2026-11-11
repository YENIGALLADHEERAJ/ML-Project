# Literature survey — OrthoTrace

**Topic:** source-aware evaluation of Hip/Knee/Shoulder recognition in public orthopaedic X-rays. **Updated:** 11 November 2026.

This survey explains the background, compares related methods and identifies the project's bounded contribution. It uses the repository bibliography and selected primary-source checks. It is a targeted survey, not a systematic review. “A paper exists” and “we critically reviewed its full text” are different statements.

## Why we built OrthoTrace

We started with a practical question for an imaging research team. If a model recognizes a joint in a pooled benchmark, will it still recognize that joint in images from a different source? Public collections can differ in which body regions they contain and how images are framed, sized, or labeled. When those differences align with the joint labels, a model can use them to guess the joint. A high pooled score can then overstate how well it will work on an unfamiliar source. Hill and colleagues demonstrated a related shortcut problem using knee radiographs. Ly and colleagues investigated acquisition-related shortcuts across several modalities, and Zech and colleagues showed that pneumonia prediction performance could decline across hospitals. [Hill et al.](https://www.nature.com/articles/s41598-024-79838-6) · [Ly et al.](https://www.nature.com/articles/s41746-024-01118-4) · [Zech et al.](https://doi.org/10.1371/journal.pmed.1002683)

## What existed and what OrthoTrace contributes

| Prior work | What it established | What we built for this project |
|---|---|---|
| **SAM-X** | Organized musculoskeletal radiographs into 28 anatomy categories. [Primary paper](https://doi.org/10.1007/s00330-022-09184-6) | A narrower anatomy model with a workbench for inspecting how the same X-ray is scored by four checkpoints trained on different sources. |
| **Mitsuyama et al.** | Evaluated radiograph body-part classification and chest projection/orientation across institutions, including a label-quality application. [Primary paper](https://doi.org/10.1007/s00330-025-12053-7) | A source-controlled orthopaedic benchmark that pairs dataset holdouts with simple shortcut controls and visible per-image disagreements. |
| **Hill et al. and Ly et al.** | Demonstrated why performance can reflect unintended cues and investigated ways to expose them. [Hill et al.](https://www.nature.com/articles/s41598-024-79838-6) · [Ly et al.](https://www.nature.com/articles/s41746-024-01118-4) | Dimensions-only and metadata baselines, matched-image source comparisons, and a paired border experiment with a within-source control. |
| **FracAtlas and BTXRD** | Released musculoskeletal radiographs with labels for fracture and bone-tumor research, respectively. [FracAtlas](https://doi.org/10.1038/s41597-023-02432-4) · [BTXRD](https://doi.org/10.1038/s41597-024-04311-y) | Used FracAtlas for source-decoupled testing and BTXRD for an external anatomy check. We preserve the original tags alongside later provisional visual reviews. |
| **Patel et al.** | Identified hip and knee implant models from radiographs to support research on revision planning. [Primary paper](https://doi.org/10.1148/ryai.2021200183) | Used implant-image sources to test anatomy recognition under source shift. Our output is the visible region, and our evaluation asks how well it transfers. |

The distinctive part is the workflow. A reviewer can take one radiograph, compare predictions, inspect the pooled checkpoint's Grad-CAM, see the source and provisional visual labels where available, then export a review record without image pixels or filenames. That connects a benchmark result to an image a person can inspect. An imaging research team could use this workflow to investigate mislabeled files or model disagreements in a de-identified evaluation set.

## Where the evidence supports “best”

| Comparison | Strongest result we can defend | Scope |
|---|---|---|
| Classical classifiers | **RBF SVM led the six methods at 56.5% balanced accuracy** on 47 FracAtlas validation images after training without FracAtlas. | Hip, Knee, Shoulder. The pooled validation cohort was different. |
| Expanded model preprocessing | **Center cropping performed best among the three tested crop settings on the BTXRD follow-up.** Knee detections rose from 8 to 21 of 37, and extra Elbow flags dropped from 33 to 16 of 49. Elbow and Shoulder detections stayed at 5 of 5 and 12 of 12. | Same 54 images before and after. This cohort informed the revision. |
| Specimen 06 | The current expanded model flags **Elbow alone at a model score of 99.7%**. The original benchmark recorded Knee, and the source tag was Leg. | One held-out image with a provisional visual review. The score is a model output. |
| Dataset shortcut | A random forest using only width, height and aspect ratio fell from **97.1% pooled to 33.3% source-decoupled balanced accuracy**. | An anatomy-free control on the original three-class study. |

The project’s strongest claim is about **inspectability and source-aware evaluation on this benchmark**. Establishing a best-in-class anatomy model would require a shared evaluation cohort, aligned labels and metrics, and direct comparison with prior systems. Clinical usefulness would also require independent clinician labels and a fresh test representative of the intended setting. Our current evidence supports an academic tool for model and dataset review.

## Research gaps, objectives, and evidence

The [classmate NIDS project](https://github.com/jaslyn-j/Concept-drift-detecting_NIDS) informed this section's structure. Its controlled traffic shifts and OrthoTrace's source holdouts address different prediction tasks. In OrthoTrace, source shift means a change in the image dataset or acquisition context. The workbench evaluates fixed checkpoints and has no streaming drift detector or automatic retraining trigger.

| Gap addressed in our project | Objective | Method and evidence |
|---|---|---|
| **G1. Pooled accuracy leaves source transfer unclear.** Prior studies show medical models can exploit acquisition cues. | Measure how much a score changes when a source is excluded. | Compare pooled and source-decoupled protocols, then compare the checkpoints on identical FracAtlas test images in the same-image control. [Saved benchmark](ML3/site/data/results.json) |
| **G2. A high accuracy score leaves the cue ambiguous.** A network may rely on framing, borders, or dimensions. | Test cues that carry little or no anatomical content. | Fit a dimensions-only Random Forest and run a paired border intervention with matched within-source controls. [Border experiment](ML3/site/downloads/BORDER_AUDIT.md) |
| **G3. Algorithm rankings can change with the cohort.** Pooled scores alone hide that difference. | Compare standard classifiers on shared features under stated splits. | Fit six supervised methods on PCA-reduced EfficientNet-B3 embeddings. RBF SVM led the 47-image FracAtlas validation holdout at 56.5% balanced accuracy. [Classical comparison](ML3/artifacts/retraining/algorithm-comparison.json) |
| **G4. Aggregate metrics can hide label conflicts and individual failures.** | Make single-image disagreements reviewable and check the expanded model on another dataset. | Compare four checkpoint outputs and six independent region scores. Export the review record and compare original and revised results on BTXRD. [Frozen external check](ML3/artifacts/retraining/btxrd-mirror-evaluation.json) · [Follow-up](ML3/artifacts/retraining/center-crop-candidates.json) |

### Implemented evaluation workflow

1. Track data provenance and available group identifiers before splitting.
2. Keep the frozen three-class benchmark separate from the expanded workbench and exploratory analyses.
3. Use the pooled, source-held-out and dimensions-only experiments to measure generalization and shortcut effects.
4. Inspect per-image results and provisional labels in the workbench, including specimen 06.
5. Preserve the first BTXRD run and the later crop follow-up as separate artifacts. The follow-up informed the project revision and needs a fresh external check.

## 1. What question does the literature help us ask?

An imaging model can perform well on a familiar dataset and fail on a different source. Different sources may have different scanners, crops, resolutions, patient groups, labels and implant appearances. If these differences align with the class label, learning the source can help predict the label.

Our question is narrower than general medical AI: **How much can pooled public-dataset evaluation overstate Hip/Knee/Shoulder recognition when the joint and dataset source are associated?**

The literature supports investigating this problem. It does not allow us to claim that our models diagnose disease, recognize implant brands, work in hospitals or outperform unrelated systems.

## 2. Theme A — shortcut learning and dataset-origin clues

### Hill, Koback and Schilling, 2024

*The risk of shortcutting in deep learning algorithms for medical imaging research.* Scientific Reports, 14, 29224. [Publisher DOI](https://doi.org/10.1038/s41598-024-79838-6) · [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11589829/).

This is a close medical-imaging precedent for questioning what a successful CNN actually uses. A model can exploit an unintended relationship in the data. The lesson for OrthoTrace is to test anatomy-free information and source changes rather than treat a high pooled score as sufficient evidence. It does not make our three-joint benchmark redundant: the labels, sources and evaluation endpoints differ. The repository records full-text reading; the primary text was located during this update.

### Ly and colleagues, 2024

*Shortcut learning in medical AI hinders generalization: method for estimating AI model generalization without external data.* npj Digital Medicine. [Primary article](https://www.nature.com/articles/s41746-024-01118-4).

The paper investigates how data-acquisition bias can help models succeed internally but weaken transfer. Its approach includes disrupting structural information to probe remaining shortcuts. OrthoTrace uses a different design: explicit source-held-out testing plus dimension/metadata controls. We should compare the evaluation ideas, not rank the two projects using accuracies from different clinical tasks.

### Hajishafiezahramini and colleagues, 2026

*Dataset-Origin Signatures and Shortcut Learning in Screening Mammography AI: A Cross-Dataset Case Study.* [arXiv:2607.15416](https://arxiv.org/abs/2607.15416).

The abstract describes a mammography experiment with consistent preprocessing and patient-level splits. It also tests whether representations identify the dataset of origin. This directly motivates checking source decodability in OrthoTrace: normalization alone need not remove source information. The modality and target are different, so its performance cannot be used as our baseline. This is a verified preprint record; the present summary is abstract-level, not a new full-text appraisal.

### Rafferty and Rajan, 2026

*Limitations of public chest radiography datasets for artificial intelligence: label quality, domain shift, bias and evaluation challenges.* Philosophical Transactions A, 384, 20250129. [DOI](https://doi.org/10.1098/rsta.2025.0129) · [Institutional publication record](https://www.research.ed.ac.uk/en/publications/limitations-of-public-chest-radiography-datasets-for-artificial-i/).

This related work places public-data limitations alongside model evaluation. The journal record was confirmed during this update; the repository records abstract-level reading. Its relevance is provenance, labels and shift. It is not an orthopaedic classifier benchmark, and a bibliographic confirmation does not replace full-method review.

**Theme conclusion:** the question “what did the model learn?” is already established. Our contribution must be a carefully specified test of that question on our benchmark, not a claim to have invented shortcut learning.

## 3. Theme B — generalization and cross-source evaluation

Patwary and Toma's 2026 fracture-classification paper investigates cross-dataset failure between paediatric and mixed-age radiographs. Its publisher text reports a different endpoint from our joint labels. The useful connection is that internal success and external behaviour must be reported separately. [Primary article](https://doi.org/10.3390/app16146853).

Hrubý and colleagues' 2024 cross-center musculoskeletal fracture-validation preprint is relevant to testing beyond the training center. However, hospital-center separation and public-source separation are not identical. The repository records abstract-only access. [Primary record](https://doi.org/10.1101/2024.01.17.24301244).

Kutbi, Shaban and Khogeer's 2026 work considers cross-anatomy abnormality detection using radiographs. It is useful for discussing whether visual similarities help transfer across anatomical regions. OrthoTrace instead predicts the region itself, so this is adjacent work rather than a directly comparable score. [Primary article](https://www.nature.com/articles/s41598-026-37516-9).

OpenMIBOOD, by Gutbrod and colleagues, evaluates OOD methods in medical imaging and distinguishes shifted, near-OOD and far-OOD settings. It motivates keeping our unknown-joint evaluation separate from ordinary three-class accuracy. The arXiv record was confirmed; this update does not independently confirm the conference-venue wording in the old repository bibliography. [Primary preprint](https://arxiv.org/abs/2503.16247).

**Theme conclusion:** source-held-out evaluation and explicit task definitions are necessary. Our 55-image FracAtlas subset is an informative source-decoupled test, but it is not a substitute for independent hospital validation.

## 4. Theme C — anatomy, projection and data cleanliness

Mitsuyama and colleagues study body-part and projection/orientation classification in a multi-institutional setting. Fink and colleagues study projection and body-side classification in musculoskeletal radiographs. Langer and colleagues consider anatomical-region classification and real-world data cleanliness.

These papers show that “classifying an X-ray” is not one task. Body part, projection, side, abnormality and implant identity are different labels. View differences and label cleanliness can affect our results, especially for the provisional FracAtlas knee subset. Their datasets and targets should be compared in a survey table; their reported scores should not be presented as interchangeable with our balanced accuracy.

## 5. Theme D — implant identification as related application work

THA-AID, the knee-implant external-validation work by Karnuta and colleagues, and Gong and colleagues' hip-implant work concern implant-related identification applications. HipXNet concerns hip-implant loosening.

These papers explain why implant X-rays are a practical imaging domain. They do not mean OrthoTrace implements the same tasks. The original benchmark outputs Hip, Knee or Shoulder. The current workbench also has an expanded model that scores Hand, Leg and Elbow. We have not trained manufacturer/model labels or a loosening endpoint. Implant presence is associated with some dataset sources, but our source-held-out comparisons do not isolate a causal implant effect.

## 6. Theme E — data and model foundations

FracAtlas provides multi-region musculoskeletal radiographs and annotations for its original tasks. In our benchmark it is the only source containing all three target joints. Our provisional knee selection requires its own validation; the original dataset paper does not validate labels later assigned by our project.

ConvNeXt supplies a modern convolutional architecture used in our comparisons. EfficientNet and Swin are additional established backbones. These architecture papers justify model selection, but ImageNet results do not establish robustness on our sources.

## 7. Comparison of 17 recent bibliography entries

The numbered references below correspond to the original repository's reference numbers. Years are the recorded publication/preprint years. The working recent window is calendar years 2022–2026; confirm the evaluator's precise five-year rule. A preprint/journal pair counts as one work, not two.

| Repository ref | Work and year | Method / data / task in simple terms | Why we use it | Reading limit |
|---|---|---|---|---|
| 1 | Hill et al., 2024 | Medical-image CNN shortcut investigation | Closest shortcut-learning motivation | Repository full-text record; primary full text located |
| 2 | Ly et al., 2024 | Bias-transform approach to examining generalization | Compare their indirect shortcut test with our explicit source controls | Repository page read; primary article located |
| 4 | Rafferty & Rajan, 2025 preprint / 2026 journal | Public chest-data label, bias and shift discussion | Dataset provenance and evaluation limits | Journal identity confirmed; abstract-level review |
| 5 | Hajishafiezahramini et al., 2026 | Frozen mammography features, source-origin diagnostic and patient-level splits | Why source signatures may survive preprocessing | Preprint and abstract confirmed; full-text review pending |
| 6 | Patwary & Toma, 2026 | Cross-dataset radiograph fracture classification | Internal versus shifted evaluation | Publisher text checked; task-specific detailed replication not performed |
| 7 | Hrubý et al., 2024 | Cross-center musculoskeletal fracture validation | External-validation design | Preprint, abstract only in repository |
| 8 | Kutbi et al., 2026 | Cross-anatomy abnormality detection | Anatomy similarity and transfer | Publisher record/text located; not our prediction endpoint |
| 9 | Mitsuyama et al., online 2025 / volume 2026 | Multi-institution body-part/projection classification | Related anatomy classification and external settings | Repository records full-text reading |
| 10 | Fink et al., 2024 | Projection and body-side classification | View variation and precise label definition | Repository page read |
| 11 | Langer et al., 2024 | Self-supervised anatomical-region/data-quality study | Label and dataset cleanliness | Preprint, abstract only |
| 12 | Rouzrokh et al., THA-AID, 2024 | Hip-implant identification with uncertainty/outlier analysis | Real application context, different target | Abstract only |
| 13 | Karnuta et al., 2023 | Multi-center knee-implant identification validation | Why external evaluation matters | Bibliographic match/abstract only |
| 14 | Gong et al., 2022 | AI-based hip-implant identification | Implant application context | Repository page read |
| 15 | Gutbrod et al., OpenMIBOOD, 2025 | Medical OOD benchmarks and post-hoc methods | Distinguish unknown inputs from classification | arXiv verified; conference version not confirmed here |
| 17 | Rahman et al., HipXNet, 2022 | Hip-implant loosening classification | Data/task provenance; a different endpoint | Metadata only; full-text review pending |
| 18 | Abedeen et al., FracAtlas, 2023 | Multi-region fracture dataset and annotations | Source data and target-region selection | Dataset/source record; not validation of our added knee labels |
| 28 | Liu et al., ConvNeXt, 2022 | Modern convolutional architecture | Established comparison backbone | Official author repository/arXiv confirmed; not an orthopaedic robustness result |

## 8. Critical analysis: what should not be compared directly?

1. **Different targets:** fracture detection, implant-brand recognition and joint recognition are not equivalent tasks.
2. **Different splits:** patient, image, center and source splits answer different questions.
3. **Different metrics:** accuracy, balanced accuracy and AUROC are not interchangeable.
4. **Different populations/views:** paediatric hips, implant close-ups and native knees differ beyond just the class name.
5. **Different evidence levels:** a full-text experiment, abstract-only record and dataset catalogue require different strength of interpretation.

A comparison table should expose these differences rather than declaring the paper with the largest percentage the winner. We do not provide invented numerical literature baselines for incompatible tasks.

## 9. The gap and how our methodology follows from it

**Bounded gap:** characterize pooled-versus-source-decoupled Hip/Knee/Shoulder recognition on this six-source benchmark, with anatomy-free baselines and uncertainty analysis.

| Literature lesson | Decision in OrthoTrace |
|---|---|
| Models can exploit unintended clues | Test dimensions, metadata, borders and other limited features |
| Internal success may not transfer | Separate pooled, FracAtlas-held-out and leave-one-source-out protocols |
| Related images can leak across partitions | Use available groups/reference identifiers/duplicate clusters in splitting |
| Architecture alone does not solve dataset bias | Compare RF, frozen probes and fine-tuned backbones |
| Confidence can fail under shift | Examine calibration, selective prediction and OOD scores separately |
| Results need traceable evidence | Preserve predictions, manifests, checkpoint hashes and analysis records |
| Task definitions matter | Keep joint recognition separate from implant identity and diagnosis |

This is a focused empirical/software contribution. The search was targeted and cannot prove that no related prior study exists.

## 10. Connection to our measured findings

Our saved primary-model pooled balanced accuracies are approximately 0.993–1.000, compared with 0.498–0.686 in the source-decoupled setting. The dimension-only RF baseline drops from 0.9713 to 0.3333. These are **our saved benchmark results**, not numbers borrowed from the cited papers.

They support the usefulness of source-controlled evaluation in this collection. They do not establish hospital-level performance or implant causality. One multi-joint held-out source, provisional knee labels and limited training remain important limitations. The hip/shoulder-only sensitivity analysis gives a smaller gap, which must also be shown.

## 11. Older foundational references

These works remain useful but should not be counted as 2022–2026 recent papers:

- Badgeley et al., 2019: hip-fracture prediction and confounding. [DOI](https://doi.org/10.1038/s41746-019-0105-1).
- Geirhos et al., 2020: shortcut learning in neural networks. [DOI](https://doi.org/10.1038/s42256-020-00257-z).
- Zech et al., 2018: variable cross-source chest-X-ray generalization. [DOI](https://doi.org/10.1371/journal.pmed.1002683).
- DeGrave et al., 2021: radiographic COVID-19 shortcuts. [DOI](https://doi.org/10.1038/s42256-021-00338-7).
- Tan & Le, 2019: EfficientNet architecture. [arXiv](https://arxiv.org/abs/1905.11946).
- Liu et al., 2021: Swin Transformer. [arXiv](https://arxiv.org/abs/2103.14030).
- Guo et al., 2017: calibration and temperature scaling. [arXiv](https://arxiv.org/abs/1706.04599).
- Holm, 1979: multiple-test adjustment. [DOI](https://doi.org/10.2307/4615733).

## 12. What remains to meet the highest literature criterion?

The repository contains a useful recent starting set, but this document does not certify 15 fully reviewed recent journal/conference papers. Obtain the remaining full texts; confirm venue and version; record task, data, split, model, metric, findings and limitations; then add a team-written critical comparison. Do not count preprints as confirmed conference publications, double-count versions or claim full-text reading from metadata.

Institutional citation style and similarity requirements also need confirmation. Source existence, scientific quality, full-text review and plagiarism/originality checking are separate checks.

## 13. Full recent references

The following entries retain the original repository's author/title information and reading-status notes. Status describes that record, not a new full-text review of every paper during this update.


**Repository reference 1.** Hill BG, Koback FL, Schilling PL. The risk of shortcutting in deep learning algorithms for medical imaging research. *Sci Rep* 2024;14:29224. doi:10.1038/s41598-024-79838-6 [C; full text read via PMC] [Primary identifier](https://doi.org/10.1038/s41598-024-79838-6).

**Repository reference 2.** Ly CO, Unnikrishnan B, Tadic T, et al. Shortcut learning in medical AI hinders generalization: method for estimating AI model generalization without external data. *npj Digit Med* 2024. doi:10.1038/s41746-024-01118-4 [C; page read] [Primary identifier](https://doi.org/10.1038/s41746-024-01118-4).

**Repository reference 4.** Rafferty A, Rajan A. Limitations of public chest radiography datasets for artificial intelligence: label quality, domain shift, bias and evaluation challenges. arXiv:2509.15107 (2025); *Philos Trans R Soc A* 2026, doi:10.1098/rsta.2025.0129 [X, C; abstract read] [Primary identifier](https://doi.org/10.1098/rsta.2025.0129).

**Repository reference 5.** Hajishafiezahramini P, Hamilton M, Meruvia-Pastor O, Kendall E. Dataset-origin signatures and shortcut learning in screening mammography AI: a cross-dataset case study. arXiv:2607.15416 (2026) [X; abstract read] [Primary identifier](https://arxiv.org/abs/2607.15416).

**Repository reference 6.** Patwary R, Toma M. Bidirectional domain shift failure in radiograph fracture classification across out-of-distribution pediatric and mixed-age multi-region data. *Appl Sci* 2026;16(14):6853. doi:10.3390/app16146853 [C; abstract only] [Primary identifier](https://doi.org/10.3390/app16146853).

**Repository reference 7.** Hrubý R, Kvak D, Dandár J, Atakhanova A, Misař M, Dufek D. Cross-center validation of deep learning model for musculoskeletal fracture detection in radiographic imaging: a feasibility study. medRxiv 2024. doi:10.1101/2024.01.17.24301244 [C; preprint abstract only] [Primary identifier](https://doi.org/10.1101/2024.01.17.24301244).

**Repository reference 8.** Kutbi M, Shaban K, Khogeer A. Exploring anatomical similarity in zero-shot learning for bone abnormality detection. *Sci Rep* 2026. doi:10.1038/s41598-026-37516-9 [C; abstract/page read] [Primary identifier](https://doi.org/10.1038/s41598-026-37516-9).

**Repository reference 9.** Mitsuyama Y, Takita H, Walston SL, et al. Deep learning models for radiography body-part classification and chest radiograph projection/orientation classification: a multi-institutional study. *Eur Radiol* 2026;36:2576–2590 (online 2025). doi:10.1007/s00330-025-12053-7 [C, F] [Primary identifier](https://doi.org/10.1007/s00330-025-12053-7).

**Repository reference 10.** Fink A, Tran H, Reisert M, et al. A deep learning approach for projection and body-side classification in musculoskeletal radiographs. *Eur Radiol Exp* 2024;8:23. doi:10.1186/s41747-023-00417-x [C; page read] [Primary identifier](https://doi.org/10.1186/s41747-023-00417-x).

**Repository reference 11.** Langer S, Ritter J, Braren R, Rueckert D, Hager P. Self-supervised radiograph anatomical region classification – how clean is your real-world data? arXiv:2412.15967 (2024) [X; abstract read] [Primary identifier](https://arxiv.org/abs/2412.15967).

**Repository reference 12.** Rouzrokh P, Mickley JP, Khosravi B, et al. THA-AID: deep learning tool for total hip arthroplasty automatic implant detection with uncertainty and outlier quantification. *J Arthroplasty* 2024. doi:10.1016/j.arth.2023.09.025 [C; abstract read] [Primary identifier](https://doi.org/10.1016/j.arth.2023.09.025).

**Repository reference 13.** Karnuta JM, et al. Artificial intelligence for automated implant identification in knee arthroplasty: a multicenter external validation study exceeding 3.5 million plain radiographs. *J Arthroplasty* 2023. doi:10.1016/j.arth.2023.03.039 [C, bibliographic match; abstract only] [Primary identifier](https://doi.org/10.1016/j.arth.2023.03.039).

**Repository reference 14.** Gong Z, Fu Y, He M, Fu X. Automated identification of hip arthroplasty implants using artificial intelligence. *Sci Rep* 2022;12:12179. doi:10.1038/s41598-022-16534-3 [C; page read] [Primary identifier](https://doi.org/10.1038/s41598-022-16534-3).

**Repository reference 15.** Gutbrod M, Rauber D, Weber Nunes D, Palm C. OpenMIBOOD: open medical imaging benchmarks for out-of-distribution detection. arXiv preprint 2025; conference venue not independently confirmed in this update; arXiv:2503.16247 [X; abstract read] [Primary identifier](https://arxiv.org/abs/2503.16247).

**Repository reference 17.** Rahman T, et al. HipXNet: deep learning approaches to detect aseptic loosening of hip implants using X-ray images. *IEEE Access* 2022. doi:10.1109/ACCESS.2022.3173424 [C, bibliographic match; not read] [Primary identifier](https://doi.org/10.1109/ACCESS.2022.3173424).

**Repository reference 18.** Abedeen I, et al. FracAtlas: a dataset for fracture classification, localization and segmentation of musculoskeletal radiographs. *Sci Data* 2023. doi:10.1038/s41597-023-02432-4; data: figshare doi:10.6084/m9.figshare.22363012 (CC BY 4.0) [C; dataset page read] [Primary identifier](https://doi.org/10.1038/s41597-023-02432-4).

**Repository reference 28.** Liu Z, Mao H, Wu C-Y, et al. A ConvNet for the 2020s. *CVPR* 2022; arXiv:2201.03545 [X] [Primary identifier](https://arxiv.org/abs/2201.03545).


## Paired border intervention extension

**SAM-X** categorized musculoskeletal radiographs into 28 anatomical regions. It establishes broad anatomy sorting as prior work and supplies a closer comparison than implant-brand classification. [Primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC9935683/)

**DeGrave, Janizek and Lee** exchanged laterality markers on chest radiographs and compared the shifts with random patches of the same size. This supports intervention-based shortcut testing and provides a precedent for our matched control. The 2021 paper is foundational context outside the current five-year rubric window. [Primary article](https://doi.org/10.1038/s42256-021-00338-7)

**RoentMod** used text-guided synthetic modifications to study shortcuts in chest X-ray models. It provides a recent intervention comparison. OrthoTrace uses four scalar intensities to produce a reproducible border and verifies that every center pixel remains equal. [Primary article](https://www.nature.com/articles/s41746-026-02497-6)

Our added experiment compares within-source and cross-source frames derived from donors with the same joint label. The 41-image exploratory pilot found that one checkpoint changes predictions after border edits. Its estimated additional cross-source effect was 2.4 percentage points and its interval reached zero. The rubric's recent-paper count still requires a final venue, publication-date and reading-depth audit before submission.
