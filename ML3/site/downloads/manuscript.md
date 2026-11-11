# Pooled public data overstate orthopaedic joint recognition: a pre-specified, source-controlled evaluation of shortcut learning in hip, knee and shoulder radiographs

**Authors:** [to be completed]. **Status:** manuscript draft generated from frozen, hash-recorded analyses; not peer-reviewed.

## Abstract

**Background.** Hip, knee and shoulder recognition on pooled public radiograph collections is reported with near-perfect accuracy, but most collections supply one joint each, so the joint label is confounded with the data source. We asked whether conventional pooled evaluation substantially overestimates anatomical generalisation.

**Methods.** We built a leakage-audited benchmark of six public sources (4,427 images; FracAtlas is the only source containing all three joints) with group-aware splits and a sealed test partition (657 images). Before opening it we froze the analysis plan, statistics, code and training recipes. We compared pooled random evaluation with source-decoupled evaluation (train without FracAtlas, test on FracAtlas; n = 55) and leave-one-source-out evaluation, using random-forest baselines (image dimensions, file metadata, border, low frequency, HOG), frozen ImageNet backbones with linear probes (EfficientNet-B3, ConvNeXt-T, Swin-T), and fine-tuned networks (3 seeds for EfficientNet-B3 and Swin-T; one for ConvNeXt-T). The primary endpoint was the pooled-minus-decoupled difference in balanced accuracy (H1: > 0.10; clustered paired bootstrap; Holm correction over five primary models). Secondary analyses covered anatomy-free baselines, implant-bearing source holdouts, confidence, calibration and unknown-joint detection.

**Results.** Pooled balanced accuracy was 0.993–1.000 for the five primary models; on the source-decoupled test it fell to 0.498–0.686 (gap 0.31–0.50; all adjusted p = 0.002; H1 supported for 5/5 models). Random forests on file metadata or image dimensions alone reached 0.960 and 0.971 pooled and exactly chance (0.333) when decoupled. Holding out the source that supplied all hip implants or all shoulder implants gave balanced accuracy of 0.00–0.04 and 0.00–0.17 (held-out hip implants were called shoulder in 88–100% and held-out shoulder implants hip in 80–99% of predictions, i.e. systematic swaps rather than chance), whereas knee sources transferred to each other. In these holdouts the models were confidently wrong (accuracy on the most confident half ≤ 0.10; expected calibration error 0.57–0.95), and temperature scaling fitted on in-distribution data worsened calibration under the milder decoupled shift. In development data the source remained decodable (balanced accuracy ≥ 0.97) after cropping, border removal, normalisation or high-pass filtering.

A post-hoc sensitivity analysis showed that the knee class (provisional FracAtlas labels, view shift) contributes substantially to the decoupled error: restricted to hip and shoulder, the gap was 0.10–0.34, with lower CI bounds of 0.02–0.21.

**Conclusions.** In these public orthopaedic collections, pooled evaluation overstated anatomical generalisation by 0.31–0.50 balanced accuracy on the pre-specified three-class endpoint (less, and for some models near the 0.10 threshold, when the provisional knee class is excluded), and part of the apparent performance is attributable to image properties unrelated to anatomy. Implant presence is a plausible source-associated confound but was not shown to be causal. We recommend source-decoupled and leave-source-out reporting, anatomy-free baselines, and caution about confidence-based abstention under source shift. To our knowledge we found no study specifically evaluating this question for orthopaedic joint recognition, although related shortcut-learning and cross-dataset failures are reported in other medical-imaging and orthopaedic tasks; our search was not exhaustive. Limitations include few independent sources, a small decoupled test set, provisional knee labels and compute-limited fine-tuning.

**Keywords:** shortcut learning; dataset shift; orthopaedic radiographs; joint recognition; leave-one-source-out; calibration; benchmark.


## 3. Introduction

Deep-learning models that recognise the anatomical region of a radiograph, or the implant it contains, are routinely reported with accuracies above 95% [Mitsuyama 2025; Fink 2024; Langer 2024]. Such recognition is a building block of automated radiograph routing, label cleaning and implant-identification pipelines. Most public orthopaedic radiograph collections, however, were assembled for a different purpose and are small, single-purpose and single-origin: a shoulder-implant set from web and laboratory sources, a hip-loosening set compiled from published figures, a knee-osteoarthritis grading set from one scanner. When such collections are pooled to build a multi-joint classifier, the joint label becomes almost perfectly confounded with the data source, and anything that distinguishes the sources, such as image size, file format, framing, borders or implant appearance, becomes a valid shortcut to the label.

Shortcut learning and dataset bias are established problems in medical imaging [Geirhos 2020; Zech 2018; Badgeley 2019; DeGrave 2021; Ly 2024; Rafferty 2025; Hajishafiezahramini 2026], and cross-dataset failures have been reported for musculoskeletal fracture detection [Patwary 2026; Hrubý 2024]. In knee radiographs, models can predict attributes that cannot be seen in the image through confounding variables, and pre-processing does not remove them [Hill 2024]. What remains unclear is how far these findings undermine the *reported* performance of orthopaedic **joint recognition** on pooled public data, how that performance behaves when the joint label is decoupled from the data source, and whether the confidence of such classifiers can be trusted when the source changes.

We therefore ask: **can conventional pooled evaluation of public orthopaedic radiograph datasets substantially overestimate anatomical generalisation because joint labels are confounded with source and acquisition characteristics?** We built a leakage-audited benchmark of six public sources in which one source (FracAtlas) contains all three joints, allowing a source-decoupled test, and in which every other source can be held out in turn. We pre-specified and froze the analysis before opening a sealed test partition. Our contributions are empirical and methodological:

1. a quantification of the gap between pooled and source-decoupled evaluation for hip/knee/shoulder recognition across a handcrafted-feature baseline, three frozen backbones and three fine-tuned networks;
2. evidence that image-level features carrying no anatomy (dimensions, file metadata) reproduce pooled performance and fall to chance when decoupled, and that the source remains decodable after common pre-processing;
3. a characterisation of leave-one-source-out failure when a source is the only bearer of implants, including its error taxonomy, with the explicit caveat that implant presence is a plausible source-associated confound rather than a demonstrated cause;
4. a reliability analysis showing that confidence-based unknown-joint detection, calibration and selective prediction, which look sound under pooled evaluation, degrade or become uninformative under source shift.

We do not propose a new classifier, and we do not claim to be the first to describe shortcuts in medical imaging.


## 4. Related work

**Shortcut learning and dataset bias in medical imaging.** Models exploit hospital, scanner and processing signatures that correlate with the label. Hospital-process variables explained much of a hip-fracture model's performance, which fell to chance when cohorts were matched [Badgeley 2019]. Chest-radiograph and COVID-19 classifiers learned dataset-specific cues [DeGrave 2021], public chest datasets can be told apart almost perfectly by a source classifier [Rafferty 2025], and shuffling-based estimates suggest that standard validation overestimates external accuracy by about 20% on average across non-orthopaedic modalities [Ly 2024]. In mammography, dataset-origin signatures persist despite identical pre-processing [Hajishafiezahramini 2026]. The closest orthopaedic precedent is Hill et al. [2024], who showed that knee radiographs allow models to predict non-anatomical attributes through confounding and latent variables that pre-processing cannot remove; that study concerned spurious outcomes rather than joint recognition, source-decoupled evaluation or reliability under shift.

**Cross-dataset generalisation in musculoskeletal imaging.** Fracture detectors trained on one public set can collapse on another, with specificity falling to zero in extreme cases [Patwary 2026; Hrubý 2024], and transfer between body parts depends on anatomical similarity [Kutbi 2026]. Body-part and projection recognition has been validated across institutions at coarse granularity, with hip, knee and shoulder grouped as "extremities" [Mitsuyama 2025], or within a single centre at fine granularity [Fink 2024; Langer 2024].

**Orthopaedic implant identification and reliability.** Implant identification for hip, knee and shoulder arthroplasty has been validated on external cohorts [Karnuta 2023; Gong 2022], and a hip-implant tool added conformal prediction and outlier detection [Rouzrokh 2024 (THA-AID)]. These studies address implant model recognition within one anatomical region and do not study how joint-label/source confounding affects joint recognition.

**Confidence and out-of-distribution (OOD) detection under shift.** Feature-space OOD scores outperform probabilistic ones in medical imaging benchmarks [Gutbrod 2025 (OpenMIBOOD)], and we use these findings as context only; we do not propose a new OOD method.

**Table P1. Closest prior work and how this study differs.** "Joint recognition" means classifying hip/knee/shoulder; verification levels are in the reference list.

| Study | Modality and task | Data | Validation | Shortcut / source analysis | Joint recognition | Relation to this study |
|---|---|---|---|---|---|---|
| Hill et al. 2024 | Knee radiographs; predicting non-anatomical attributes | OAI knee radiographs | internal | Yes: confounders and latent variables; pre-processing did not remove them | No | Closest orthopaedic precedent for shortcuts; different task |
| Badgeley et al. 2019 | Hip radiographs; fracture | 23,602 radiographs, 9,024 patients | single institution | Yes: scanner and hospital-process variables; AUC 0.78 → 0.52 when matched | No | Orthopaedic confounding precedent |
| Ly et al. 2024 | Chest X-ray, CT, ECG, audio, text; many tasks | 13 datasets | external | Yes: standard validation overestimated external accuracy by about 20% | No | Quantifies inflation outside orthopaedics |
| Rafferty & Rajan 2025 | Public chest X-ray datasets | MIMIC-CXR, ChestX-ray14, PadChest, CheXpert | cross-dataset | Yes: source classifier near-perfect | No | Method precedent (chest) |
| Hajishafiezahramini et al. 2026 | Screening mammography | three datasets | cross-dataset | Yes: origin near-perfectly decodable; added external cases lowered AUC | No | Method precedent (mammography) |
| Mitsuyama et al. 2025 | Body-part classification | 429,341 radiographs, two institutions + MURA | external 98.5% | No | Coarse (hip/knee/shoulder pooled as "extremities") | Coarse-level generalisation |
| Fink et al. 2024 | Projection / side classification | 23,663 radiographs, 45 projections | single centre, none external | No | Fine-grained, internal only | Within-site recognition |
| Langer et al. 2024 | Anatomical-region classification | 48,434 radiographs, 14 regions | single institution | Label noise (35% incorrect) and out-of-domain images found on review | Yes, internal | Real-world data quality |
| Kutbi et al. 2026 | MURA abnormality, cross-body-part transfer | MURA; FracAtlas as external | cross-part, external | No source analysis | No | Anatomical similarity governs transfer |
| Patwary & Toma 2026; Hrubý et al. 2024 | Fracture classification/detection | GRAZPEDWRI-DX, FracAtlas; MURA | cross-dataset | Cross-dataset collapse (abstract-level) | No | Cross-dataset failure in MSK |
| Rouzrokh et al. 2024 (THA-AID) | Hip implant identification | 241,419 radiographs | internal + external | Uncertainty and outlier detection | No (implant design) | Reliability tooling within one region |
| Gong et al. 2022; Karnuta et al. 2023 | Hip / knee implant identification | 714 images; 4,724 radiographs | internal; multicentre external (knee) | No | No | Implant identification |
| **This study** | Hip/knee/shoulder recognition | six public sources, 4,427 images | pooled, source-decoupled, leave-source-out, sealed test | Yes: anatomy-free baselines, source decodability, source holdouts, reliability | Yes | Evaluation of joint recognition under source shift |


## 5. Research gap

Prior work establishes that medical-imaging datasets contain shortcuts, that cross-dataset performance can collapse in musculoskeletal tasks, and that implant identification can be externally validated within one anatomical region. To our knowledge, we found no study specifically evaluating whether pooled public orthopaedic radiograph joint recognition is inflated by joint-source confounding using source-decoupled and leave-source-out evaluation, nor one that characterises the reliability of confidence, calibration and abstention for such classifiers under source shift, although shortcut learning and cross-dataset failures have been reported in other medical-imaging and orthopaedic tasks. This statement rests on a targeted but non-exhaustive search (PubMed, Google Scholar, IEEE Xplore and several publisher databases were not queried systematically; some full texts were inaccessible), and it should be read as the absence of evidence we found, not as a proof of priority.


## 6. Dataset construction

We assembled six public sources (Table 1). Only FracAtlas contains more than one target joint, which is what makes a source-decoupled test possible. Images were never relabelled except for the FracAtlas knee subset described below.

**Table 1. Dataset inventory.** Counts are target images used (development + sealed test). "Implants" are from a visual check of 30 random images per source and, for FracAtlas, the dataset's hardware flag.

| Source | Joint(s) | Images | Provenance, licence | Implants | Notes |
|---|---|---|---|---|---|
| F FracAtlas | Hip 179, Knee 94, Shoulder 101 | 374 | Three Bangladeshi hospitals; CC BY 4.0; figshare 10.6084/m9.figshare.22363012 | hardware flag: hip 3, knee 3, shoulder 0 | Single-region images only. The knee subset is **not an official FracAtlas class**: 94 images were labelled by visual inspection from 200 randomly sampled "leg" images (101 non-knee, 5 ambiguous excluded); labels are provisional and were not verified by a clinician |
| K Kaggle hip (HipXNet) | Hip | 206 | Images compiled from ~100 papers and web pages (per the dataset's metadata); licence not re-verified | 30/30 | Close-up proximal-femur crops of arthroplasty |
| U UCI shoulder implants | Shoulder | 597 | UCI repository 10.24432/C5F893, CC BY 4.0; web and laboratory sources | ~29/30 | Close-up arthroplasty crops |
| A AV-DDH | Hip | 400 (sampled) | Mendeley 10.17632/4gvcb6gmh2.2, CC BY 4.0 (the Roboflow export lists "Private"); not redistributed | 0/30 | Paediatric pelvis, 640×640 RGB, Roboflow-processed; 400 unique originals sampled |
| G Gornale knee | Knee | 1,650 | Mendeley 10.17632/t9ndx37v5h.1, CC BY 4.0 | 0/30 | One scanner; about 10% near-blank frames in a 30-image sample |
| O OAI-derived knee | Knee | 1,200 (sampled of 9,786) | Osteoarthritis Initiative derivative (Kaggle copy; Kaggle reports CC BY 4.0); further OAI terms may apply; not redistributed | 0/30 | 224×224 pre-cropped single knees; patient IDs available |

An **unknown-joint pool** for reliability analysis consisted of FracAtlas hand radiographs (400 sampled) and 101 FracAtlas leg images we judged not to show the knee. Emory MRKR, MURA and LERA, which would add independent knee, shoulder and hip sources, require data-use agreements and were not accessed.

**Splits.** Within each (source, label) cell, images were assigned 70/15/15 to train/validation/test **by group**, where a group is a patient (OAI), a literature reference (K), a connected component of near-duplicate images (perceptual dHash-16, Hamming distance ≤ 6), or a neighbourhood of consecutive FracAtlas identifiers for multi-scan images. The 657 test rows (A 60, F 55, G 247, K 24, O 182, U 89) were sealed before any model comparison and opened once, after the protocol was frozen (Section 9).


## 7. Data-leakage audit

We audited all 4,427 target images (development and sealed test) with an automated script (`check_dataset_integrity_v2.py`, machine-readable output `integrity_all.json`). Exact duplicates were detected by MD5 and near-duplicates by 16×16 difference hashes (Hamming distance ≤ 6).

- **Exact duplicates:** 32 images in 15 duplicate groups; all duplicates lie within one split because duplicate images share a group.
- **Near-duplicates:** 229 pairs (225 in Gornale knee, 1 in FracAtlas, 3 in OAI-derived knee); **none crossed a train/validation/test boundary, none crossed sources, and none paired images with different labels.**
- **Group integrity:** no group spans more than one split.
- **Source leakage:** by design, label and source are confounded in five of six sources; this confounding, not duplicate leakage, is the object of the study.
- **Not auditable:** public data do not provide patient identifiers for FracAtlas, the UCI shoulder set, the Kaggle hip set or AV-DDH. Patient- or study-level leakage within these sources therefore cannot be excluded; grouping used literature reference (Kaggle hip), id neighbourhoods and near-duplicate clusters instead. The audit was run on development rows before unsealing (163 pairs, zero crossings) and repeated on all rows after unsealing as a descriptive check; it was not used to alter any split.


## 8. Shortcut analysis

We asked which image properties, unrelated to anatomy, can reproduce pooled performance. Random forests were trained on single feature groups: image dimensions (width, height, aspect), file metadata (adding colour mode, format and file size), the outer border frame, an 8×8 low-frequency thumbnail, a grey-level histogram, and HOG. On the sealed test set (Table 3, Figure 3a) the dimension-only and metadata-only models reached balanced accuracy of 0.971 and 0.960 on the pooled split and **exactly the chance level of 0.333** on the source-decoupled split; the border frame alone gave 0.962 pooled and 0.431 decoupled, and the low-frequency thumbnail 0.959 and 0.610. The dimension- and metadata-only models predicted *every* FracAtlas test image as shoulder (shoulder recall 1.0, hip and knee 0): they carry no joint information once the source-to-label mapping is broken. These feature groups contain no anatomy that a clinician would use, so a large part of the pooled accuracy of every model, including the deep ones, is available without recognising any joint.

**Does pre-processing remove the shortcut?** In development data, a classifier could identify the source of an image within a joint class with balanced accuracy of at least 0.97 from frozen embeddings of the full image, a centre crop, a normalised image, a border-removed image, a bright-blob-inpainted image and a high-pass-filtered image (selected variants shown in Table S1). Pre-processing therefore changed what the models used less than it changed what they are required to ignore; this agrees with Hill et al. [2024] for knee radiographs. On the sealed test set, input variants shifted decoupled performance in some backbones (Table S2: for example ConvNeXt-T probe 0.498 → 0.658 with normalisation) but never approached pooled performance, and none rescued the implant-source holdouts (Table S3). Variant comparisons are exploratory (six variants, three backbones, no multiplicity correction).

![Figure 3. (a) Feature groups without anatomy match deep models on pooled data and fall to or toward chance when decoupled; (b) the source remains decodable after pre-processing (development data).](figures/F3_shortcut_evidence.png)


![Figure 1. Study workflow.](figures/F1_workflow.png)

![Figure 2. Dataset and source composition.](figures/F2_dataset_composition.png)

## 9. Experimental protocol

All tasks are three-class (Hip, Knee, Shoulder); chance balanced accuracy is 0.333. Each model family was trained on development partitions only, using a capped random draw of at most 300 images per (source, label) cell; a *seed* is one such draw plus, for fine-tuning, model initialisation and data order.

**Table 2. Evaluation protocols.**

| Protocol | Training data | Evaluated on (sealed test rows) | Purpose |
|---|---|---|---|
| E0 pooled random | all sources, train partition | all 657 test rows | conventional evaluation |
| E1 pooled, source-balanced | same, cell-balanced weights | all 657 | does balancing change pooled results? |
| **E2 source-decoupled** | all sources except FracAtlas | FracAtlas test rows (n = 55: 26 hip, 14 knee, 15 shoulder) | joint ≠ source; primary comparison |
| E3 leave-one-source-out | all sources except X (K, U, A, G, O) | X test rows | domain generalisation |
| E6 FracAtlas-only | FracAtlas development rows | each other source's test rows | cross-source transfer |
| E7 native-only | no implant-bearing source (K, U removed) | native test rows / hold-out A, G, O | joint recognition without implant sources |

**Freeze and unsealing.** Before any test image was opened we froze the analysis plan, endpoints, statistics, planned tables/figures, code hashes and training recipes (`docs/FROZEN_analysis_plan.md`, `artifacts/final/freeze_v3.json`). Fine-tuned checkpoints were trained on development data and their SHA-256 hashes recorded before unsealing; classical and probe models were refit with recipe hashes verified. The test images were opened once, each unit was evaluated once (touch-log), and no tuning followed. One amendment made before unsealing (fine-tuned A, G, O holdouts for seed 0 only, for compute) is reported in the plan. Because earlier development runs had not stored checkpoints, all reported test-set models were retrained from the same recipes.

**Development study.** Development results (validation-partition evaluation, five seeds) guided the design of the protocol and are reported separately as supporting evidence; they are labelled "development" throughout and were never used to tune test-time choices.

**Design-informing exposures (disclosure).** The research question arose from an initial audit of a previous 806-image prototype (three of the present sources, original random split). That audit cross-validated simple metadata classifiers over *all* 806 images, which include images later assigned to the sealed test partition, and showed that image dimensions alone predicted the joint (99.9%). No model, threshold or hyper-parameter used in the reported study was derived from that audit, and no prototype model is used, but it shaped the hypotheses (H2) and so is a source of researcher degrees of freedom. The FracAtlas knee/non-knee labelling and the unknown-joint pool were created during development from images outside the sealed test partition; sealed FracAtlas test rows (55) were assigned by group before any evaluation.


## 10. Models

We deliberately used standard baselines, since the contribution is the evaluation, not a model.

- **Anatomy-free and handcrafted baselines (random forest, 100 trees):** image dimensions (width, height, aspect); file metadata (dimensions, colour mode, PNG vs JPEG, file size); the outer 12% border frame (pooled 2×2); an 8×8 low-frequency thumbnail; a 32-bin grey-level histogram; HOG on the full image; HOG on the central 50%.
- **Frozen-backbone linear probes:** ImageNet-pretrained EfficientNet-B3, ConvNeXt-Tiny and Swin-Tiny embeddings with standardised logistic regression (C = 0.05), for six input variants: full image (stretched to 160 px), centre 50% crop, normalised (letterbox, robust rescaling, CLAHE), border removed (15% crop), bright-blob inpainted (a heuristic proxy, not a validated implant detector), and high-pass filtered.
- **Fine-tuned networks:** EfficientNet-B3, Swin-T and ConvNeXt-T (ImageNet initialisation; 3 epochs, AdamW, 160 px, flip augmentation, label smoothing 0.05; 3 seeds for EfficientNet-B3 and Swin-T, one seed for ConvNeXt-T because of compute).
- **Confidence and OOD scores:** maximum softmax probability, negative entropy, energy, temperature-scaled MSP (temperature fitted on a group-held-out 20% of the training set) and, for probes, Mahalanobis distance in feature space.


## 11. Source-controlled evaluation

**Primary result.** Table 3 and Figure 4 give the central comparison. Pooled random evaluation (E0) yielded balanced accuracy of 0.993–1.000 for all five primary models, with per-class recall at or above 0.98. When the same families were trained without FracAtlas and tested on FracAtlas images, whose joint label is no longer tied to the source, balanced accuracy fell to 0.686 (0.60–0.77) (EfficientNet-B3, fine-tuned), 0.601 (0.53–0.68) (Swin-T, fine-tuned), 0.664 (0.57–0.76) (Swin-T probe), 0.553 (0.44–0.67) (EfficientNet-B3 probe) and 0.498 (0.40–0.60) (ConvNeXt-T probe). The pooled-minus-decoupled gaps were 0.31 (0.23–0.40), 0.40 (0.32–0.48), 0.33 (0.23–0.43), 0.44 (0.32–0.55) and 0.50 (0.40–0.60) respectively; for all five, the Holm-adjusted one-sided p-value against a 0.10 gap was 0.002 and the CI lower bound exceeded 0.10, so **H1 was supported (5 of 5 primary models; criterion ≥ 4)**. The single-seed ConvNeXt-T fine-tuned model (secondary) showed the same pattern (0.581 (0.48–0.69); gap 0.42 (0.31–0.52)).

**Where the decoupled errors lie.** Recall for the knee class on FracAtlas was low in every model (EfficientNet-B3, fine-tuned 0.26; Swin-T, fine-tuned 0.17; EfficientNet-B3, probe 0.34; ConvNeXt-T, probe 0.17; Swin-T, probe 0.29), whereas hip recall was 0.88–1.00. FracAtlas knees are mostly wide long-leg or lateral views, unlike the pre-cropped anteroposterior knees in the two other knee sources, and their labels are provisional (Section 18), so part of the knee error may reflect view shift or label noise rather than shortcut use. Source-balanced training weights did not change pooled performance (E1, probes: EfficientNet-B3, probe 0.991 vs 0.993 unbalanced; ConvNeXt-T, probe 0.995 vs 0.995 unbalanced; Swin-T, probe 0.991 vs 0.994 unbalanced), which is expected if the cue is carried by the source itself (balancing weights cannot remove a source-specific cue when label and source coincide).

**Table 3.** Pooled versus source-decoupled balanced accuracy (BA) on the sealed test rows. Gap CIs are clustered paired-bootstrap intervals; the CI of the decoupled BA reflects test-image sampling (n = 55) with trained models held fixed.

| Model | Seeds | Pooled random test (E0), BA | FracAtlas decoupled test (E2), BA (95% CI) | Pooled − decoupled gap (95% CI) | Holm-adjusted p (H0: gap ≤ 0.10) |
|---|---|---|---|---|---|
| EfficientNet-B3, fine-tuned **(primary)** | 3 | 0.998 | 0.686 (0.60–0.77) | 0.312 (0.23–0.40) | 0.002 |
| Swin-T, fine-tuned **(primary)** | 3 | 1.000 | 0.601 (0.53–0.68) | 0.399 (0.32–0.48) | 0.002 |
| ConvNeXt-T, fine-tuned (1 seed) | 1 | 1.000 | 0.581 (0.48–0.69) | 0.419 (0.31–0.52) | – |
| EfficientNet-B3, probe **(primary)** | 5 | 0.993 | 0.553 (0.44–0.67) | 0.440 (0.32–0.55) | 0.002 |
| ConvNeXt-T, probe **(primary)** | 5 | 0.995 | 0.498 (0.40–0.60) | 0.498 (0.40–0.60) | 0.002 |
| Swin-T, probe **(primary)** | 5 | 0.994 | 0.664 (0.57–0.76) | 0.329 (0.23–0.43) | 0.002 |
| Image dimensions (RF) | 5 | 0.971 | 0.333 (0.33–0.33) | 0.638 (0.62–0.65) | – |
| File metadata (RF) | 5 | 0.960 | 0.333 (0.33–0.33) | 0.627 (0.61–0.64) | – |
| Border frame (RF) | 5 | 0.962 | 0.431 (0.37–0.49) | 0.531 (0.47–0.59) | – |
| Low-frequency 8x8 (RF) | 5 | 0.959 | 0.610 (0.55–0.66) | 0.349 (0.30–0.42) | – |
| Grey-level histogram (RF) | 5 | 0.878 | 0.343 (0.30–0.40) | 0.535 (0.47–0.59) | – |
| HOG (RF) | 5 | 0.973 | 0.345 (0.28–0.42) | 0.627 (0.55–0.70) | – |
| HOG centre crop (RF) | 5 | 0.908 | 0.453 (0.37–0.54) | 0.454 (0.37–0.54) | – |

![Figure 4. Pooled random versus source-decoupled balanced accuracy for each model on the sealed test rows (lines show the gap; label gives gap with 95% cluster-bootstrap CI).](figures/F4_pooled_vs_decoupled.png)



## 12. Cross-dataset evaluation

**Leave-one-source-out (E3).** Table 4 and Figure 5 hold out each source in turn. Holding out the only hip-implant source (Kaggle hip, K; n = 24) gave balanced accuracy of 0.000, 0.000, 0.017, 0.000, 0.042 for the five primary models (in the order of Table 3), and holding out the only shoulder-implant source (UCI, U; n = 89) gave 0.169, 0.034, 0.000, 0.000, 0.027. All values are below the pre-specified 0.25 threshold (**H3 supported**), and they are far below the chance level of 0.333: held-out hip implants were called shoulder and held-out shoulder implants were called hip, i.e. a systematic swap, not random guessing. In contrast, holding out either knee source left the other available and gave 0.95–1.00 (O) and 0.81–0.97 (G), and the paediatric hip source (A), whose images differ in age and framing, gave 0.62–0.76. The failure is therefore consistent with being specific to the pairing of source and joint rather than a uniform loss of generalisation.

**Table 4.** Leave-one-source-out balanced accuracy on the held-out source's sealed test rows (recall of its single joint; 95% cluster-bootstrap interval in brackets). n/a = model not trained for that protocol under the amended plan. For the dimension/metadata random forests, high values on a single-joint source only reflect a fixed mapping from image size to class learned in training; they are not evidence of anatomical transfer.

| Model | Hold out K | Hold out U | Hold out A | Hold out G | Hold out O |
|---|---|---|---|---|---|
| EfficientNet-B3, fine-tuned | 0.000 [0.00–0.00] | 0.169 [0.10–0.24] | 0.733 [0.62–0.83] | 0.968 [0.91–1.00] | 1.000 [1.00–1.00] |
| Swin-T, fine-tuned | 0.000 [0.00–0.00] | 0.034 [0.01–0.06] | n/a | n/a | n/a |
| EfficientNet-B3, probe | 0.017 [0.00–0.04] | 0.000 [0.00–0.00] | 0.620 [0.50–0.73] | 0.814 [0.73–0.89] | 0.953 [0.92–0.98] |
| ConvNeXt-T, probe | 0.000 [0.00–0.00] | 0.000 [0.00–0.00] | 0.737 [0.63–0.84] | 0.964 [0.89–1.00] | 0.996 [0.99–1.00] |
| Swin-T, probe | 0.042 [0.00–0.12] | 0.027 [0.00–0.06] | 0.763 [0.65–0.87] | 0.944 [0.86–0.99] | 0.956 [0.92–0.98] |
| Image dimensions (RF) | 0.000 [0.00–0.00] | 0.000 [0.00–0.00] | 0.000 [0.00–0.00] | 1.000 [1.00–1.00] | 0.000 [0.00–0.00] |
| File metadata (RF) | 0.000 [0.00–0.00] | 0.000 [0.00–0.00] | 0.000 [0.00–0.00] | 0.971 [0.95–0.99] | 0.000 [0.00–0.00] |
| Border frame (RF) | 0.533 [0.34–0.72] | 0.043 [0.01–0.08] | 0.450 [0.34–0.57] | 0.451 [0.39–0.52] | 0.879 [0.84–0.91] |
| Low-frequency 8x8 (RF) | 0.392 [0.26–0.54] | 0.013 [0.00–0.03] | 0.533 [0.41–0.65] | 0.397 [0.34–0.45] | 0.888 [0.84–0.93] |
| HOG (RF) | 0.008 [0.00–0.03] | 0.000 [0.00–0.00] | 0.573 [0.45–0.69] | 0.269 [0.22–0.32] | 0.909 [0.88–0.94] |

**FracAtlas-only training (E6).** Training on FracAtlas alone transferred inconsistently (Table 5), for example the Swin-T probe reached 1.000 on the paediatric hip source but 0.000 on the OAI-derived knees; metadata alone is meaningless in this setting.

**Table 5.** Balanced accuracy on each other source's test rows after training on FracAtlas only.

| Model | F → K | F → U | F → A | F → G | F → O |
|---|---|---|---|---|---|
| EfficientNet-B3, probe | 0.542 | 0.398 | 0.907 | 0.183 | 0.056 |
| ConvNeXt-T, probe | 1.000 | 0.067 | 1.000 | 0.346 | 0.000 |
| Swin-T, probe | 0.883 | 0.252 | 1.000 | 0.351 | 0.000 |
| File metadata (RF) | 1.000 | 0.018 | 0.190 | 0.008 | 0.022 |
| HOG (RF) | 0.292 | 0.072 | 0.783 | 0.206 | 0.001 |

**Native-only subset (E7).** With the implant-bearing sources removed, pooled native performance was 1.000 (Swin-T probe) and 0.827 for metadata alone; native leave-source-out accuracy remained source-dependent (hold out A: 0.840, G: 0.976, O: 0.940 for the Swin-T probe). The native subset contains no independent shoulder source other than FracAtlas, so shoulder generalisation without implants could not be tested.

![Figure 5. Leave-one-source-out balanced accuracy on the held-out source's sealed test rows. The dashed line is chance (0.333). Missing bars: model not trained for that protocol.](figures/F5_leave_one_source_out.png)


## 13. Out-of-distribution and reliability analysis

We treat this as a secondary reliability finding; it is not a new OOD method. Unknown-joint detection used FracAtlas hand radiographs and non-knee leg images as unknown, with max-softmax, energy, negative entropy, temperature-scaled max-softmax and (for probes) Mahalanobis distance as scores.

**Unknown-joint detection (Table 6).** Confidence-based detection was strong under pooled training and weaker when the model had been trained without FracAtlas; feature-space Mahalanobis distance retained more of its performance. The decoupled evaluation uses the same FracAtlas source for known and unknown images, so source differences cannot explain the scores.

**Table 6.** Unknown-joint detection (known = test images of the evaluation set; unknown = 501 FracAtlas hand/non-knee images). AUPR depends on the known/unknown ratio (657 vs 501 pooled, 55 vs 501 decoupled) and is therefore not comparable across the two columns; AUROC and FPR are.

| Model | Score | AUROC pooled (95% CI) | AUROC decoupled (95% CI) | FPR@95%TPR pooled → decoupled | AUPR(unknown) pooled → decoupled |
|---|---|---|---|---|---|
| EfficientNet-B3, fine-tuned | energy | 0.859 (0.83–0.88) | 0.747 (0.67–0.82) | 0.40 → 0.87 | 0.83 → 0.94 |
| EfficientNet-B3, fine-tuned | msp | 0.897 (0.87–0.92) | 0.792 (0.73–0.86) | 0.31 → 0.75 | 0.87 → 0.96 |
| Swin-T, fine-tuned | energy | 0.910 (0.88–0.93) | 0.647 (0.57–0.71) | 0.22 → 0.92 | 0.90 → 0.93 |
| Swin-T, fine-tuned | msp | 0.926 (0.90–0.94) | 0.616 (0.54–0.69) | 0.15 → 0.95 | 0.92 → 0.91 |
| ConvNeXt-T, probe | energy | 0.951 (0.92–0.97) | 0.652 (0.57–0.74) | 0.32 → 0.83 | 0.89 → 0.94 |
| ConvNeXt-T, probe | mahalanobis | 0.989 (0.98–0.99) | 0.956 (0.94–0.98) | 0.03 → 0.18 | 0.98 → 0.99 |
| ConvNeXt-T, probe | msp | 0.953 (0.92–0.97) | 0.667 (0.58–0.75) | 0.28 → 0.88 | 0.90 → 0.94 |
| EfficientNet-B3, probe | energy | 0.958 (0.93–0.97) | 0.578 (0.48–0.67) | 0.23 → 0.97 | 0.93 → 0.90 |
| EfficientNet-B3, probe | mahalanobis | 0.974 (0.97–0.98) | 0.710 (0.65–0.78) | 0.17 → 0.72 | 0.96 → 0.96 |
| EfficientNet-B3, probe | msp | 0.957 (0.93–0.97) | 0.557 (0.46–0.65) | 0.24 → 0.97 | 0.93 → 0.90 |
| Swin-T, probe | energy | 0.952 (0.92–0.97) | 0.651 (0.56–0.74) | 0.29 → 0.92 | 0.90 → 0.93 |
| Swin-T, probe | mahalanobis | 0.980 (0.97–0.99) | 0.910 (0.86–0.96) | 0.09 → 0.55 | 0.97 → 0.99 |
| Swin-T, probe | msp | 0.952 (0.93–0.97) | 0.657 (0.57–0.75) | 0.28 → 0.88 | 0.91 → 0.93 |

**Calibration and selective prediction (Table 7).** On pooled data confidence was well calibrated and abstention was beneficial (accuracy at 50% coverage 1.0). Under the source-decoupled test, raw ECE rose to 0.13–0.22 and **temperature scaling, fitted on held-out in-distribution data, made it worse for every primary model** (ECE 0.22–0.36); accuracy rose to 0.89–0.98 on the most confident half, so abstention helped under this moderate shift. In the implant-source holdouts the models were confidently wrong: ECE was 0.57–0.95, accuracy at 50% coverage was at most 0.10 and the AUROC of confidence for correctness, where defined (it is undefined when no prediction is correct), was ft-effnet U: 0.30, ft-swin U: 0.12, lr-effnet K: 0.02, lr-swin K: 0.20, lr-swin U: 0.03, i.e. below 0.5 (**H4**: the 95% CI upper bound was below 0.5 in 5 of the 5 cases in which it is defined). Abstention thresholds chosen on in-distribution data therefore cannot be expected to protect against this kind of shift.

**Table 7.** Calibration and selective prediction (seed-averaged; AUROC of confidence for correctness is undefined when every or no prediction is correct).

| Model | Protocol | n | ECE raw | ECE after temperature scaling | AURC | Accuracy @ 50% coverage | AUROC (confidence → correct) | Macro-F1 |
|---|---|---|---|---|---|---|---|---|
| EfficientNet-B3, fine-tuned | pooled | 657 | 0.047 | 0.002 | 0.000 | 1.000 | 0.994 | 0.997 |
| EfficientNet-B3, fine-tuned | decoupled F | 55 | 0.137 | 0.217 | 0.069 | 0.975 | 0.903 | 0.661 |
| EfficientNet-B3, fine-tuned | hold out K | 24 | 0.904 | 0.992 | 1.000 | 0.000 | undefined | 0.000 |
| EfficientNet-B3, fine-tuned | hold out U | 89 | 0.573 | 0.776 | 0.896 | 0.098 | 0.301 | 0.288 |
| Swin-T, fine-tuned | pooled | 657 | 0.031 | 0.003 | 0.000 | 1.000 | undefined | 1.000 |
| Swin-T, fine-tuned | decoupled F | 55 | 0.160 | 0.274 | 0.144 | 0.938 | 0.807 | 0.579 |
| Swin-T, fine-tuned | hold out K | 24 | 0.947 | 0.991 | 1.000 | 0.000 | undefined | 0.000 |
| Swin-T, fine-tuned | hold out U | 89 | 0.868 | 0.952 | 0.994 | 0.000 | 0.121 | 0.065 |
| EfficientNet-B3, probe | pooled | 657 | 0.016 | 0.011 | 0.000 | 1.000 | 0.994 | 0.985 |
| EfficientNet-B3, probe | decoupled F | 55 | 0.200 | 0.306 | 0.138 | 0.904 | 0.851 | 0.562 |
| EfficientNet-B3, probe | hold out K | 24 | 0.873 | 0.946 | 0.999 | 0.000 | 0.022 | 0.033 |
| EfficientNet-B3, probe | hold out U | 89 | 0.892 | 0.979 | 1.000 | 0.000 | undefined | 0.000 |
| ConvNeXt-T, probe | pooled | 657 | 0.011 | 0.005 | 0.000 | 1.000 | 0.985 | 0.993 |
| ConvNeXt-T, probe | decoupled F | 55 | 0.221 | 0.364 | 0.166 | 0.889 | 0.824 | 0.482 |
| ConvNeXt-T, probe | hold out K | 24 | 0.839 | 0.932 | 1.000 | 0.000 | undefined | 0.000 |
| ConvNeXt-T, probe | hold out U | 89 | 0.889 | 0.977 | 1.000 | 0.000 | undefined | 0.000 |
| Swin-T, probe | pooled | 657 | 0.011 | 0.005 | 0.000 | 1.000 | 0.984 | 0.994 |
| Swin-T, probe | decoupled F | 55 | 0.128 | 0.248 | 0.092 | 0.956 | 0.808 | 0.664 |
| Swin-T, probe | hold out K | 24 | 0.824 | 0.895 | 0.989 | 0.000 | 0.200 | 0.080 |
| Swin-T, probe | hold out U | 89 | 0.773 | 0.916 | 0.999 | 0.000 | 0.026 | 0.053 |

![Figure 7. Reliability under source shift: (a) unknown-joint detection AUROC pooled versus decoupled, (b) accuracy versus coverage for selective prediction, (c) change in ECE after temperature scaling.](figures/F7_ood_reliability.png)


## 14. Error analysis

**What the failures look like.** Figure 8 shows representative errors of the fine-tuned EfficientNet-B3. Held-out hip arthroplasty crops are called shoulder and held-out shoulder arthroplasty crops are called hip, in most predictions across seeds; held-out paediatric pelvis radiographs (many with lead shields and large black margins) are mostly called hip (62–76% of predictions) but 17–34% are called shoulder; FracAtlas knees in wide or lateral views are called hip or shoulder. Confusion matrices are in Figure 6.

**Candidate explanations (development evidence).** In development data, the nearest training neighbours of held-out hip-implant images came from the *shoulder-implant* source, and vice versa (Table 8), and adding 5–20 labelled images of the held-out source restored most of the accuracy for hold-out K, more slowly for hold-out U. This is consistent with the embeddings still containing separable joint information and with the failure arising mainly in the decision boundary learned from source-specific appearance (an interpretation of development evidence, not a demonstrated mechanism).

**Table 8.** Development-set error analysis of the implant-source holdouts (frozen-embedding probes, 5 seeds).

| Backbone (probe) | Held-out source | Nearest training neighbours (top 2, share) | Predicted class share | Accuracy with 0 → 5 → 10 → 20 labelled images added |
|---|---|---|---|---|
| effnet | hold out K | U:Shoulder 0.83, A:Hip 0.06 | Hip 0.07 / Knee 0.06 / Shoulder 0.87 | 0.07 → 0.67 → 0.86 → 0.97 |
| effnet | hold out U | K:Hip 0.66, A:Hip 0.10 | Hip 0.98 / Knee 0.02 / Shoulder 0.01 | 0.01 → 0.36 → 0.58 → 0.79 |
| swin | hold out K | U:Shoulder 0.69, F:Hip 0.12 | Hip 0.07 / Knee 0.08 / Shoulder 0.85 | 0.07 → 0.81 → 0.89 → 0.93 |
| swin | hold out U | K:Hip 0.30, F:Shoulder 0.23 | Hip 0.77 / Knee 0.19 / Shoulder 0.04 | 0.04 → 0.47 → 0.69 → 0.85 |
| convnext | hold out K | U:Shoulder 0.73, F:Hip 0.10 | Hip 0.15 / Knee 0.01 / Shoulder 0.84 | 0.15 → 0.74 → 0.90 → 0.96 |
| convnext | hold out U | K:Hip 0.43, F:Hip 0.22 | Hip 0.96 / Knee 0.04 / Shoulder 0.00 | 0.00 → 0.45 → 0.70 → 0.86 |

**Table 8b. Candidate causes of the implant-source failures: evidence versus hypothesis.**

| Candidate cause | Evidence | Status |
|---|---|---|
| Source/style similarity (the model maps "implant-crop appearance" to the joint of the other implant source) | nearest-neighbour composition; few-shot recovery; test-set swaps | **Supported** |
| Implant presence | both implant sources are in training with opposite joints; no knee source has implants; proxy mask weak and did not help | **Plausible source-associated confound; not shown causal** |
| Missing anatomical information | few-shot recovery; within-source accuracy near 1.0 in development; knee sources transfer | Not supported |
| Field of view / cropping | K and U are tight crops, others wide views; centre crop and border removal change results modestly | Possible, untested in isolation |
| Label semantics | "hip" means adult arthroplasty crop in K but paediatric pelvis in A; "knee" in FracAtlas is mostly long-leg views | Possible |
| Pre-processing | six variants, three backbones, HOG fail alike | Not supported |
| Model-specific failure | all architectures and baselines fail alike | Not supported |

![Figure 6. Seed-averaged confusion matrices of the fine-tuned EfficientNet-B3 on the sealed test rows.](figures/F6_confusion_matrices.png)

![Figure 8. Representative failures (true class → predicted class; majority of seeds wrong).](figures/F8_failure_cases.png)


## 15. Statistical analysis

All analysis choices were fixed before unsealing (`docs/FROZEN_analysis_plan.md`). The primary metric is balanced accuracy (macro-averaged recall over classes present), appropriate for the unequal class sizes of a three-class problem. We also report macro-F1, per-class recall (sensitivity) and one-vs-rest specificity from seed-averaged confusion matrices, expected calibration error (15 bins), the area under the risk–coverage curve (AURC) and accuracy at 50% coverage.

**Primary endpoint and test (H1).** For each model, Δ = BA(pooled test) − BA(decoupled FracAtlas test), with BA the mean over seeds. We tested H0: Δ ≤ 0.10 against Δ > 0.10 with a **clustered, paired bootstrap** (2,000 resamples). Clusters (patient, literature reference or near-duplicate group) are drawn with replacement from the *pooled* test set and both balanced accuracies are computed on the same draw, because the FracAtlas test images belong to the pooled set and images within a cluster are not independent. One-sided p-values were Holm-adjusted across the five primary models (at least three seeds, full image). H1 was defined as supported if the adjusted p < 0.05 and the 95% CI lower bound exceeded 0.10 for at least four of the five.

**Other intervals and comparisons.** Per-evaluation 95% intervals are percentile cluster-bootstrap intervals that hold the trained models fixed, so they reflect sampling of test images, not training variability; seed variability is reported as SD and range. Model-versus-model contrasts on the same FracAtlas test images use a paired cluster bootstrap of the balanced-accuracy difference; McNemar's test was not used because predictions are clustered and averaged over seeds. OOD metrics (AUROC, AUPR with unknown as positive, FPR at 95% TPR of known images) use independent cluster bootstraps of known and unknown sets. For H4 we report the seed-averaged AUROC of maximum-softmax confidence for correctness with a cluster-bootstrap interval. All secondary analyses are descriptive and not adjusted for multiplicity.

**Power.** The decoupled test set has 55 images (26 hip, 14 knee, 15 shoulder), so intervals are wide. We therefore also report the development decoupled evaluation (319 images), clearly labelled as development evidence.


## 16. Results (summary of confirmatory outcomes)

**Table 9. Pre-specified hypotheses and outcomes.**

| Hypothesis (pre-specified) | Outcome | Evidence |
|---|---|---|
| H1: pooled − decoupled gap > 0.10 in ≥ 4/5 primary models (Holm p < 0.05, CI lower bound > 0.10) | **Supported (5/5)** | gaps 0.31–0.50; adjusted p = 0.002 |
| H2: metadata/dimension RF ≥ 0.90 pooled and ≤ 0.40 decoupled | **Supported** | metadata 0.960 → 0.333; dimensions 0.971 → 0.333 |
| H3: BA < 0.25 on both implant-source holdouts for all primary models | **Supported** | K 0.00–0.04; U 0.00–0.17 |
| H4: confidence not positively informative on K/U holdouts | **Supported where defined** | AUROC below 0.5 wherever defined; undefined when no prediction was correct (Table 7) |
| H5 (descriptive): OOD detection weaker under decoupled evaluation | See Table 6 | confidence scores degrade; Mahalanobis degrades less |

**Table 10. Development versus sealed-test balanced accuracy** (development: validation partitions of the same sources; models retrained for test, so values are not identical even for identical recipes).

| Model | Protocol | Development BA | Test BA | Test − development |
|---|---|---|---|---|
| EfficientNet-B3, fine-tuned | E0_pooled | 1.000 | 0.998 | -0.002 |
| EfficientNet-B3, fine-tuned | E2_hold_F | 0.678 | 0.686 | +0.008 |
| EfficientNet-B3, fine-tuned | E3_hold_K | 0.005 | 0.000 | -0.005 |
| EfficientNet-B3, fine-tuned | E3_hold_U | 0.074 | 0.169 | +0.094 |
| Swin-T, fine-tuned | E0_pooled | 1.000 | 1.000 | +0.000 |
| Swin-T, fine-tuned | E2_hold_F | 0.579 | 0.601 | +0.023 |
| Swin-T, fine-tuned | E3_hold_K | 0.004 | 0.000 | -0.004 |
| Swin-T, fine-tuned | E3_hold_U | 0.054 | 0.034 | -0.021 |
| ConvNeXt-T, probe | E0_pooled | 1.000 | 0.995 | -0.005 |
| ConvNeXt-T, probe | E2_hold_F | 0.469 | 0.498 | +0.029 |
| ConvNeXt-T, probe | E3_hold_K | 0.180 | 0.000 | -0.180 |
| ConvNeXt-T, probe | E3_hold_U | 0.006 | 0.000 | -0.006 |
| EfficientNet-B3, probe | E0_pooled | 0.996 | 0.993 | -0.003 |
| EfficientNet-B3, probe | E2_hold_F | 0.548 | 0.553 | +0.004 |
| EfficientNet-B3, probe | E3_hold_K | 0.073 | 0.017 | -0.056 |
| EfficientNet-B3, probe | E3_hold_U | 0.005 | 0.000 | -0.005 |
| Swin-T, probe | E0_pooled | 0.997 | 0.994 | -0.003 |
| Swin-T, probe | E2_hold_F | 0.663 | 0.664 | +0.001 |
| Swin-T, probe | E3_hold_K | 0.073 | 0.042 | -0.031 |
| Swin-T, probe | E3_hold_U | 0.044 | 0.027 | -0.017 |

**Table 11. Model-versus-model contrasts on the FracAtlas decoupled test (exploratory).**

| Model A | Model B | BA(A) − BA(B) on FracAtlas test | 95% paired cluster-bootstrap CI |
|---|---|---|---|
| Swin-T, fine-tuned | EfficientNet-B3, fine-tuned | -0.084 | -0.16 to -0.01 |
| Swin-T, probe | EfficientNet-B3, probe | 0.111 | -0.01 to 0.23 |
| Swin-T, probe | ConvNeXt-T, probe | 0.166 | 0.05 to 0.27 |
| EfficientNet-B3, probe | ConvNeXt-T, probe | 0.055 | -0.07 to 0.18 |
| EfficientNet-B3, fine-tuned | EfficientNet-B3, probe | 0.133 | 0.02 to 0.24 |
| Swin-T, fine-tuned | Swin-T, probe | -0.063 | -0.15 to 0.02 |
| EfficientNet-B3, fine-tuned | File metadata (RF) | 0.353 | 0.26 to 0.44 |
| Swin-T, probe | File metadata (RF) | 0.331 | 0.23 to 0.43 |
| Swin-T, probe | HOG (RF) | 0.319 | 0.21 to 0.42 |

**16.1 Post-hoc sensitivity analysis (exploratory, added after the simulated peer review; not part of the frozen plan).** Because the FracAtlas knee labels are provisional and FracAtlas knees are mostly long-leg views, we asked how much of the decoupled error comes from the knee class. Per-class recall on the decoupled test (Table 12) shows that knee recall is low for every model while hip recall is high; restricting the endpoint to hip and shoulder rows (Table 13) shrinks the gap for the best fine-tuned and Swin models to the neighbourhood of the 0.10 threshold, while it stays large for the EfficientNet and ConvNeXt probes. **The pre-specified three-class conclusion (H1 supported) is unchanged, but its size depends materially on the knee class, whose labels we cannot vouch for.** The anatomy-free baselines (Table 3) and the implant-source holdouts (Table 4) do not involve the FracAtlas knee labels and are unaffected.

**Table 12. Per-class recall on the decoupled FracAtlas test (95% cluster-bootstrap CI; post hoc).**

| Model | Hip recall (n = 26) | Knee recall (n = 14) | Shoulder recall (n = 15) |
|---|---|---|---|
| EfficientNet-B3, fine-tuned | 0.88 (0.75–1.00) | 0.26 (0.09–0.45) | 0.91 (0.76–1.00) |
| Swin-T, fine-tuned | 0.95 (0.86–1.00) | 0.17 (0.04–0.30) | 0.69 (0.50–0.86) |
| EfficientNet-B3, probe | 0.92 (0.79–1.00) | 0.34 (0.13–0.56) | 0.40 (0.18–0.62) |
| ConvNeXt-T, probe | 0.96 (0.87–1.00) | 0.17 (0.01–0.38) | 0.36 (0.14–0.60) |
| Swin-T, probe | 1.00 (1.00–1.00) | 0.29 (0.09–0.50) | 0.71 (0.49–0.91) |
| ConvNeXt-T, fine-tuned (1 seed) | 1.00 (1.00–1.00) | 0.14 (0.00–0.36) | 0.60 (0.33–0.85) |

**Table 13. Pooled-minus-decoupled gap restricted to Hip and Shoulder rows (post hoc; balanced accuracy over two classes).**

| Model | Hip/shoulder-only BA, pooled | Hip/shoulder-only BA, decoupled (n = 41) | Gap (95% CI) |
|---|---|---|---|
| EfficientNet-B3, fine-tuned | 0.998 | 0.898 | 0.10 (0.02–0.21) |
| Swin-T, fine-tuned | 1.000 | 0.819 | 0.18 (0.09–0.29) |
| EfficientNet-B3, probe | 0.996 | 0.658 | 0.34 (0.21–0.47) |
| ConvNeXt-T, probe | 0.995 | 0.661 | 0.33 (0.20–0.45) |
| Swin-T, probe | 0.990 | 0.853 | 0.14 (0.04–0.26) |
| ConvNeXt-T, fine-tuned (1 seed) | 1.000 | 0.800 | 0.20 (0.08–0.33) |

**16.2 Further post-hoc robustness checks (no refitting; saved predictions only).** (i) *Same-source control.* The identical FracAtlas test images were scored by the pooled-trained models, which had seen FracAtlas training images: balanced accuracy was 1.000–1.000, against 0.50–0.69 for models trained without FracAtlas. The difference cannot be due to test-image difficulty, but it combines "source seen in training" with any shortcut use and should not be read as isolating shortcuts alone. (ii) *Metric.* The gap in macro-F1 was 0.33–0.51, consistent with balanced accuracy. (iii) *Threshold.* The lower 95% CI bounds of the primary gaps (0.23–0.40) exceeded 0.20 for all five models and 0.30 for 3 of five. (iv) *Seeds.* Every individual seed gave a gap above 0.27 (Table 14).

**Table 14. Same-source control, macro-F1 gap and per-seed gaps (post hoc).**

| Model | Pooled-trained model on FracAtlas test rows (FracAtlas in training), BA | Decoupled model on the same rows (FracAtlas excluded), BA | Within-FracAtlas-rows gap (95% CI) | Macro-F1 gap, pooled − decoupled (95% CI) | Per-seed gaps |
|---|---|---|---|---|---|
| EfficientNet-B3, fine-tuned | 1.000 (1.00–1.00) | 0.686 | 0.31 (0.23–0.40) | 0.34 (0.24–0.45) | 0.275, 0.316, 0.346 |
| Swin-T, fine-tuned | 1.000 (1.00–1.00) | 0.601 | 0.40 (0.32–0.48) | 0.43 (0.34–0.53) | 0.340, 0.470, 0.386 |
| EfficientNet-B3, probe | 1.000 (1.00–1.00) | 0.553 | 0.45 (0.34–0.56) | 0.43 (0.31–0.57) | 0.432, 0.391, 0.429, 0.523, 0.425 |
| ConvNeXt-T, probe | 1.000 (1.00–1.00) | 0.498 | 0.50 (0.40–0.60) | 0.51 (0.38–0.65) | 0.495, 0.518, 0.489, 0.492, 0.495 |
| Swin-T, probe | 1.000 (1.00–1.00) | 0.664 | 0.34 (0.24–0.44) | 0.33 (0.22–0.47) | 0.392, 0.316, 0.297, 0.319, 0.324 |
| ConvNeXt-T, fine-tuned (1 seed) | 1.000 (1.00–1.00) | 0.581 | 0.42 (0.31–0.52) | 0.45 (0.32–0.59) | 0.419 |

The test results agree with the development study in direction and approximate size for the primary comparison, the anatomy-free baselines and the implant-source holdouts; differences in individual cells are expected from retraining, the small FracAtlas test set (n = 55) and different image samples.


## 17. Discussion

**Principal finding.** On public orthopaedic radiograph collections, conventional pooled evaluation of joint recognition reports accuracy that does not carry over to a source in which the joint label is no longer tied to the source: balanced accuracy fell from 0.99–1.00 to 0.50–0.69. File metadata and image dimensions alone, which contain no anatomy, reproduced 0.96–0.97 pooled balanced accuracy. The study was designed so that a null result was possible (H1 required a gap above 0.10); on the pre-specified three-class endpoint the gap was several times larger (see below for the contribution of the knee class).

**What this adds to existing evidence that medical-imaging datasets contain shortcuts.** Shortcut learning, source signatures and cross-dataset failure are well documented in chest, mammography, fracture and knee-radiograph work [Badgeley 2019; Ly 2024; Rafferty 2025; Hajishafiezahramini 2026; Hill 2024]. What we add is specific to orthopaedic joint recognition and rests on our experiments: (i) a quantified pooled-versus-source-decoupled gap for hip/knee/shoulder recognition with a pre-specified endpoint and sealed test set; (ii) a demonstration that anatomy-free image properties reproduce pooled performance and are chance-level once decoupled; (iii) the pattern of leave-one-source-out failure, in which holding out the single source that contains all implants of a joint produces systematic swaps between joints (balanced accuracy near 0, below chance), whereas knee sources, which are native radiographs from different cohorts, transfer to each other; and (iv) evidence that, in exactly this regime, confidence, abstention and in-distribution temperature scaling are not protective. We do not claim to be the first to observe shortcuts in medical imaging or in orthopaedic images: to our knowledge we found no study specifically evaluating this question for orthopaedic joint recognition, although related shortcut-learning and cross-dataset failures have been reported in other medical-imaging and orthopaedic tasks [Hill 2024; Badgeley 2019; Ly 2024; Patwary 2026], and our search was not exhaustive.

**Role of the knee class.** The decoupled error is not evenly spread: knee recall on FracAtlas was low for all models, and a post-hoc analysis restricted to hip and shoulder reduced the gap to 0.10–0.34 (fine-tuned EfficientNet-B3 0.10, 95% CI 0.02–0.21). This part of the finding therefore partly reflects a view shift (wide long-leg FracAtlas knees versus cropped anteroposterior knees elsewhere) and possibly label noise in our provisional knee labels, rather than a pure shortcut effect; we cannot separate these with the present data. The evidence for shortcut use that does not depend on the FracAtlas knee labels is the anatomy-free baselines (chance when decoupled) and the implant-source holdouts.

**Interpretation of the implant result.** Implant presence is strongly associated with source in our data (every hip-implant image is from one source and every shoulder-implant image from another; no knee source contains implants), and it is therefore a *plausible source-associated confound*. We did not demonstrate that implants cause the failure: our implant-masking proxy was weak, there is no source with both implant and native images of the same joint from one scanner, and tight-crop framing, view and label semantics co-vary with implant presence. The development nearest-neighbour and few-shot analyses support a source/style explanation more directly than an implant-specific one.

**Reliability.** Confidence-based abstention helps under moderate shift (accuracy on the most confident half 0.89–0.98) but is uninformative or anti-informative when a held-out source is systematically mapped to the wrong joint, and temperature scaling fitted in distribution did not repair calibration under shift. Whether this pattern holds in other modalities was not examined here; within this study it is a caution for any pipeline that routes images by predicted anatomy and abstains by confidence.

**Strengths.** Leakage-audited and group-aware splits; a decoupled test source; anatomy-free baselines as sanity checks; multiple backbones and seeds; pre-specified, hash-recorded analysis with sealed test data and a log of deviations.


## 18. Limitations

1. **Few independent sources.** Six public sources, only one (FracAtlas) containing all three joints; the decoupled test therefore rests on one source with 55 test images and cannot separate source effects from FracAtlas-specific effects. FracAtlas itself spans three hospitals, so "source" is not a single device.
2. **Knee labels in FracAtlas are provisional.** The 94 knee images were labelled by visual inspection (by an AI model) and were not verified by a clinician; the knee class in the decoupled test is only as reliable as that labelling. The two further knee sources (Gornale, OAI-derived) are single-cohort, and the OAI-derived images are pre-cropped.
3. **Public-dataset provenance.** The Kaggle hip images were compiled from published figures and web pages, the UCI shoulder images from web and laboratory sources, and AV-DDH is a processed paediatric export. None provides patient identifiers, so patient-level leakage within these sources cannot be excluded, and image quality, labelling and licensing are heterogeneous.
4. **Implant presence is confounded with source.** Hip (Kaggle) and shoulder (UCI) images are almost entirely implant radiographs, whereas no knee source contains implants. Implant presence is therefore a *plausible source-associated confound*, not a demonstrated cause. Our implant-masking proxy is weak (it flags 93% of K, 83% of U, 69% of FracAtlas shoulder, 33% of A, 7% of G and 0.6% of O images), no source supplies same-joint implant and native images from one scanner, and the leave-one-source-out failures are equally compatible with field of view, cropping style and label semantics (for example adult arthroplasty crops versus paediatric pelvis views for "hip").
5. **Limited compute.** Fine-tuning used three epochs at 160 px on a 2 GB GPU. ConvNeXt-T fine-tuning has one seed and two protocols, and fine-tuned A, G and O holdouts have one seed (Amendment A1). Stronger training might narrow, but is unlikely to remove, a gap driven by label–source confounding.
6. **Seeds capture training-set sampling and initialisation, not source sampling.** Seed SDs understate uncertainty about new sources; cluster-bootstrap intervals address test-image sampling only.
7. **No hospital-level external validation** and no clinical outcome: the findings concern the *evaluation* of joint recognition on public data, not clinical deployment.
8. **Incomplete data access.** Emory MRKR, MURA and LERA, which would add independent knee, shoulder and hip sources, were not accessed (data-use agreements are required); their absence limits the number of sources per joint.
9. **The literature search was targeted, not systematic.** PubMed, Google Scholar and IEEE Xplore were not queried systematically and several full texts (including two fracture-detection papers) could not be read beyond their abstracts. The statement that we found no directly comparable study is a statement about our search.
10. **Protocol amendment and deviations**, all made before any test result was examined: Amendment A1 (fewer fine-tuned seeds for secondary holdouts), Deviation D1 (a missing-import bug fixed before the first test image was opened) and Deviation D2 (an evaluation process stopped by the analyst and restarted before any of its outputs existed). The reported test-set models were retrained from the frozen recipes because development runs had not stored checkpoints.
11. **Reliability analysis specifics.** The unknown-joint pool (FracAtlas hand and non-knee leg images) was assembled and inspected during development and reused unchanged; AUPR depends on the known/unknown ratio and is not comparable between pooled and decoupled settings; temperature scaling used a small group-held-out calibration split from the training sources; Mahalanobis distance was only evaluated for linear probes.
12. **Post-hoc analysis.** The knee-excluded sensitivity analysis (Section 16.1) was added after the simulated peer review and is exploratory.
13. **Design-informing exposure.** The initial prototype audit that suggested the metadata shortcut looked at all 806 prototype images, including some later sealed as test rows (Section 9); it did not tune any reported model but is a researcher degree of freedom.
14. **Self-contained pre-registration.** The freeze was recorded locally with file hashes and was not deposited in an independent registry, so its timing rests on the authors' records.


## 19. Clinical and research implications

For researchers, a joint- or region-recognition accuracy computed on a pooled random split of public datasets should not be read as evidence of anatomical understanding unless the label is decoupled from the source. We recommend (1) reporting leave-one-source-out or source-decoupled results alongside pooled results; (2) including metadata, dimension, border and low-frequency baselines as sanity checks; (3) auditing each source for implants, framing, age and view before pooling; (4) avoiding single-source classes; and (5) not relying on max-softmax confidence or in-distribution temperature scaling to detect source shift. For clinical workflows, the findings argue for caution about automated routing of radiographs by predicted anatomy or implant status when the deployment source differs from the training sources, and for local validation on the deploying institution's images. The study does not assess clinical outcomes and does not show that any current clinical product is affected.


## 20. Conclusion

In six public orthopaedic radiograph sources, pooled evaluation overstated joint-recognition performance by 0.31–0.50 balanced accuracy compared with a source-decoupled test (less when the provisional knee class is excluded), anatomy-free image properties reproduced pooled accuracy, and holding out implant-bearing sources produced systematic joint swaps in which confidence and calibration offered no protection. Implant presence is a plausible source-associated confound, not a demonstrated cause. The findings are limited by few independent sources, a small decoupled test set, provisional FracAtlas knee labels and compute-limited fine-tuning, and they should be replicated with additional multi-joint sources (e.g. MURA, LERA, MRKR) and clinician-verified labels.


## 21. Data and code availability

Code, configuration, the frozen plan, hashes, manifests, split definitions, per-image predictions and statistics are in the project repository (`scripts/`, `docs/`, `artifacts/benchmark`, `artifacts/final`); the repository does not contain image data. Source URLs and DOIs are given in Table 1. The 29 fine-tuned checkpoints and their SHA-256 hashes are recorded in `artifacts/final/ft_registry.json` and `freeze_addendum.json`.

## 22. Ethics and data-governance statement

All images come from public, de-identified collections used under their stated licences (CC BY 4.0 as reported by the hosts for FracAtlas, the UCI shoulder set, Gornale knee and the OAI-derived knee set; the Kaggle hip set's licence was not re-verified; AV-DDH is listed as CC BY 4.0 on Mendeley although its Roboflow export lists "Private"). No new patient data were collected and no identifiable information was accessed, so ethics approval was not sought for this secondary analysis; institutional confirmation should be obtained before any clinical use. Because redistribution terms are uncertain or restrictive for several sources (OAI-derived data, AV-DDH, and MURA/LERA if used later), we release code, manifests, split files, predictions and hashes but **not images**; users must obtain the data from the original providers. The FracAtlas knee labels were assigned by visual inspection by an AI model, not a clinician, and must not be used for clinical purposes. This work evaluates research methodology and is not a diagnostic tool.

## Declarations

**Author contributions:** [to be completed by the authors]. **Competing interests:** [to be completed]. **Funding:** none declared for this work [to be confirmed]. **Use of AI assistance:** the study design, code, analysis, figures and manuscript draft were produced with an AI coding assistant (Claude, Anthropic) operating on the authors' local machine under their instructions; the FracAtlas knee/non-knee labels were also assigned by that assistant by visual inspection. The authors remain responsible for verifying all content, and the claims should be checked against the frozen artefacts listed in Section 21 before submission. **Pre-registration:** the analysis plan was frozen and hash-recorded locally before the sealed test set was opened; it was not registered with an external registry.


## 23. References

Verification status (see `artifacts/final/reference_verification.csv`): **[C]** = DOI, title, first author and year confirmed against the Crossref record; **[X]** = confirmed against the arXiv record; **[A]** = confirmed to exist, but only the abstract was read; **[U]** = cited from background knowledge and **not verified in this project** (check before submission).

1. Hill BG, Koback FL, Schilling PL. The risk of shortcutting in deep learning algorithms for medical imaging research. *Sci Rep* 2024;14:29224. doi:10.1038/s41598-024-79838-6 [C; abstract read]
2. Ly CO, Unnikrishnan B, Tadic T, et al. Shortcut learning in medical AI hinders generalization: method for estimating AI model generalization without external data. *npj Digit Med* 2024. doi:10.1038/s41746-024-01118-4 [C; page read]
3. Badgeley MA, Zech JR, Oakden-Rayner L, et al. Deep learning predicts hip fracture using confounding patient and healthcare variables. *npj Digit Med* 2019. doi:10.1038/s41746-019-0105-1 [C; page read]
4. Rafferty A, Rajan A. Limitations of public chest radiography datasets for artificial intelligence: label quality, domain shift, bias and evaluation challenges. arXiv:2509.15107 (2025); *Philos Trans R Soc A* 2026, doi:10.1098/rsta.2025.0129 [X, C; abstract read]
5. Hajishafiezahramini P, Hamilton M, Meruvia-Pastor O, Kendall E. Dataset-origin signatures and shortcut learning in screening mammography AI: a cross-dataset case study. arXiv:2607.15416 (2026) [X; abstract read]
6. Patwary R, Toma M. Bidirectional domain shift failure in radiograph fracture classification across out-of-distribution pediatric and mixed-age multi-region data. *Appl Sci* 2026;16(14):6853. doi:10.3390/app16146853 [C; abstract only]
7. Hrubý R, Kvak D, Dandár J, Atakhanova A, Misař M, Dufek D. Cross-center validation of deep learning model for musculoskeletal fracture detection in radiographic imaging: a feasibility study. medRxiv 2024. doi:10.1101/2024.01.17.24301244 [C; preprint abstract only]
8. Kutbi M, Shaban K, Khogeer A. Exploring anatomical similarity in zero-shot learning for bone abnormality detection. *Sci Rep* 2026. doi:10.1038/s41598-026-37516-9 [C; abstract/page read]
9. Mitsuyama Y, Takita H, Walston SL, et al. Deep learning models for radiography body-part classification and chest radiograph projection/orientation classification: a multi-institutional study. *Eur Radiol* 2026;36:2576–2590 (online 2025). doi:10.1007/s00330-025-12053-7 [C; page read]
10. Fink A, Tran H, Reisert M, et al. A deep learning approach for projection and body-side classification in musculoskeletal radiographs. *Eur Radiol Exp* 2024;8:23. doi:10.1186/s41747-023-00417-x [C; page read]
11. Langer S, Ritter J, Braren R, Rueckert D, Hager P. Self-supervised radiograph anatomical region classification – how clean is your real-world data? arXiv:2412.15967 (2024) [X; abstract read]
12. Rouzrokh P, Mickley JP, Khosravi B, et al. THA-AID: deep learning tool for total hip arthroplasty automatic implant detection with uncertainty and outlier quantification. *J Arthroplasty* 2024. doi:10.1016/j.arth.2023.09.025 [C; abstract read]
13. Karnuta JM, et al. Artificial intelligence for automated implant identification in knee arthroplasty: a multicenter external validation study exceeding 3.5 million plain radiographs. *J Arthroplasty* 2023. doi:10.1016/j.arth.2023.03.039 [C, bibliographic match; abstract only]
14. Gong Z, Fu Y, He M, Fu X. Automated identification of hip arthroplasty implants using artificial intelligence. *Sci Rep* 2022;12:12179. doi:10.1038/s41598-022-16534-3 [C; page read]
15. Gutbrod M, Rauber D, Weber Nunes D, Palm C. OpenMIBOOD: open medical imaging benchmarks for out-of-distribution detection. *CVPR* 2025; arXiv:2503.16247 [X; abstract read]
16. Rajpurkar P, et al. MURA: large dataset for abnormality detection in musculoskeletal radiographs. arXiv:1712.06957 (2017) [X; not read beyond abstract]
17. Rahman T, et al. HipXNet: deep learning approaches to detect aseptic loosening of hip implants using X-ray images. *IEEE Access* 2022. doi:10.1109/ACCESS.2022.3173424 [C, bibliographic match; not read]
18. Abedeen I, et al. FracAtlas: a dataset for fracture classification, localization and segmentation of musculoskeletal radiographs. *Sci Data* 2023. doi:10.1038/s41597-023-02432-4; data: figshare doi:10.6084/m9.figshare.22363012 (CC BY 4.0) [C; dataset page read]
19. Shoulder implant X-ray manufacturer classification. UCI Machine Learning Repository, doi:10.24432/C5F893 (CC BY 4.0) [dataset page read]
20. Gornale S, Patravali P. Digital knee X-ray images. *Mendeley Data* 2020. doi:10.17632/t9ndx37v5h.1 (CC BY 4.0) [dataset page read]
21. Knee osteoarthritis severity grading dataset (derived from the Osteoarthritis Initiative). *Mendeley Data*, doi:10.17632/56rmx5bjcr.1; Kaggle copy "shashwatwork/knee-osteoarthritis-dataset-with-severity" [licence as reported by hosts]
22. Acetabular-vision hip developmental dysplasia (AV-DDH) dataset. *Mendeley Data*, doi:10.17632/4gvcb6gmh2.2 [host page read; export config lists "Private"]
23. Geirhos R, Jacobsen J-H, Michaelis C, et al. Shortcut learning in deep neural networks. *Nat Mach Intell* 2020;2:665–673 [U: the DOI lookup failed in this project]
24. Zech JR, Badgeley MA, Liu M, et al. Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: a cross-sectional study. *PLoS Med* 2018;15:e1002683. doi:10.1371/journal.pmed.1002683 [C]
25. DeGrave AJ, Janizek JD, Lee S-I. AI for radiographic COVID-19 detection selects shortcuts over signal. *Nat Mach Intell* 2021;3:610–619. doi:10.1038/s42256-021-00338-7 [C]
26. Tan M, Le QV. EfficientNet: rethinking model scaling for convolutional neural networks. *ICML* 2019; arXiv:1905.11946 [X]
27. Liu Z, Lin Y, Cao Y, et al. Swin Transformer: hierarchical vision transformer using shifted windows. *ICCV* 2021; arXiv:2103.14030 [X]
28. Liu Z, Mao H, Wu C-Y, et al. A ConvNet for the 2020s. *CVPR* 2022; arXiv:2201.03545 [X]
29. Guo C, Pleiss G, Sun Y, Weinberger KQ. On calibration of modern neural networks. *ICML* 2017; arXiv:1706.04599 [X, title confirmed]
30. Holm S. A simple sequentially rejective multiple test procedure. *Scand J Stat* 1979;6:65–70 [U: not found in Crossref in this project]
31. Reference removed: a snippet-level source on selective-prediction failure under covariate shift could not be verified and is no longer cited.


## 24. Supplementary methods and tables

**S1. Reproducibility.** Seeds 0–4 (probes, baselines) and 0–2 (fine-tuning); bootstrap seed 20261004, 2,000 resamples; Python 3.11, PyTorch 2.4.1. All code and hashes are listed in `artifacts/final/freeze_v3.json` and `freeze_addendum.json`; the frozen plan is `docs/FROZEN_analysis_plan.md` (Amendment A1; Deviations D1, D2).

**S2. Training recipes.** Capped draw of ≤ 300 images per (source, label); 20% group-wise calibration split for temperature scaling; fine-tuning: AdamW, learning rate 3e-4 (EfficientNet-B3) or 1e-4 (Swin-T, ConvNeXt-T), weight decay 0.01, batch 16, 3 epochs, 160 px, horizontal flip, label smoothing 0.05; probes: standardised logistic regression (C = 0.05); random forests: 100 trees, balanced subsample.

**S3. Image variants.** full (grey, stretched to 160 px), centre 50% crop, normalised (letterbox, 0.5–99.5% percentile rescaling, CLAHE), border-removed (15% crop per side), bright-blob inpainting (threshold 0.90 on a robustly rescaled image, area ≥ 2%, contrast ≥ 0.20, Telea inpainting; a heuristic, not a validated implant detector), and high-pass (image minus Gaussian blur σ = 10).

**Table S1. Source decodability (development data; balanced accuracy of predicting the source within a joint class; chance 0.33 for hip and knee, 0.5 for shoulder).**

| Backbone | Variant | Hip (3 sources) | Knee (3 sources) | Shoulder (2 sources) |
|---|---|---|---|---|
| effnet | full | 0.996 | 0.982 | 1.000 |
| effnet | norm | 0.998 | 0.998 | 0.991 |
| effnet | noborder | 0.989 | 0.973 | 1.000 |
| effnet | highpass | 0.993 | 0.993 | 0.994 |
| convnext | full | 1.000 | 0.989 | 1.000 |
| convnext | norm | 1.000 | 1.000 | 1.000 |
| convnext | noborder | 0.998 | 0.993 | 1.000 |
| convnext | highpass | 1.000 | 0.989 | 1.000 |
| swin | full | 0.998 | 0.989 | 1.000 |
| swin | norm | 0.998 | 1.000 | 1.000 |
| swin | noborder | 0.998 | 0.993 | 1.000 |
| swin | highpass | 1.000 | 0.989 | 1.000 |

**Table S2. Input variants on the source-decoupled test (probes; balanced accuracy).**

| Backbone (probe) | full | centre crop | normalised | border removed | blob-inpainted | high-pass |
|---|---|---|---|---|---|---|
| EfficientNet-B3 | 0.553 | 0.574 | 0.607 | 0.578 | 0.573 | 0.519 |
| ConvNeXt-T | 0.498 | 0.497 | 0.658 | 0.504 | 0.530 | 0.492 |
| Swin-T | 0.664 | 0.698 | 0.704 | 0.691 | 0.635 | 0.639 |

**Table S3. Input variants, hold out K / hold out U (probes; balanced accuracy).**

| Backbone (probe), hold out K / hold out U | full | centre crop | normalised | border removed | blob-inpainted | high-pass |
|---|---|---|---|---|---|---|
| EfficientNet-B3 | 0.02 / 0.00 | 0.04 / 0.01 | 0.06 / 0.03 | 0.04 / 0.01 | 0.14 / 0.00 | 0.00 / 0.01 |
| ConvNeXt-T | 0.00 / 0.00 | 0.00 / 0.02 | 0.10 / 0.00 | 0.05 / 0.05 | 0.00 / 0.01 | 0.03 / 0.00 |
| Swin-T | 0.04 / 0.03 | 0.04 / 0.10 | 0.04 / 0.10 | 0.00 / 0.15 | 0.07 / 0.00 | 0.00 / 0.02 |

**Table S4. Automated audit of the frozen evaluation (`scripts/audit_results.py`).**

| Audit check | Result | Detail |
|---|---|---|
| manifest hash matches freeze | PASS |  |
| test rows count 657 | PASS | 657 |
| no group spans splits | PASS |  |
| training sets disjoint from test | PASS | 65 training sets checked, 0 test paths found |
| touch log units | PASS | 54 |
| single unsealing attempt | PASS | ['2026-10-03 17:07:35'] |
| no duplicate predictions | PASS | 0 |
| prediction coverage complete | PASS | 0 (model,protocol,seed,eval) cells with missing/extra test rows |
| true labels match manifest | PASS |  |
| checkpoint hashes match | PASS | 29 checkpoints, mismatches [] |
| addendum hashes equal registry | PASS |  |
| recomputed balanced accuracy matches summary | PASS | max abs diff over 60 random cells = 1.11e-16 |
| gap equals difference of summary values | PASS | max diff 2.22e-16 |

**S5. Reference verification.** Citations were checked against Crossref and arXiv (`artifacts/final/reference_verification.csv`); two references (Geirhos 2020, Holm 1979) could not be confirmed and are flagged in the list.

**S6. Per-seed results.** `artifacts/final/stats/summary.csv` lists seed-wise balanced accuracy (`ba_seeds`), per-class recall and specificity, macro-F1, ECE, AURC and confidence AUROC for every model, protocol and evaluation set; `gap.csv`, `ood.csv`, `h4_confidence_correctness.csv`, `paired.csv` and `devtest.csv` hold the other analyses.
