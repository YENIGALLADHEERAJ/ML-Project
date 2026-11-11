# Literature Survey for Source-Controlled Evaluation of Orthopaedic Joint Recognition (OrthoTrace)

## 1. Scope of the survey

This survey divides the project topic into three areas: (a) shortcut learning and dataset bias in medical imaging, (b) cross-source generalisation, out-of-distribution (OOD) behaviour and reliability, and (c) anatomy, projection and implant recognition in orthopaedic radiographs, together with the public data and model backbones the project builds on. It is a targeted survey, not a systematic review.

Twenty-one works are compared in Section 3. Counting by identity, 16 are journal or conference publications dated 2022–2026 (the working recent window; confirm the evaluator's exact five-year rule), four are preprints (refs [5], [7], [11], [15]; [15] is listed as CVPR 2025 in the project bibliography, but the venue was not independently confirmed) and one is an older application paper (ref [34], 2021). A preprint and its journal version count as one work. The reading depth reached for every reference (full text, page or abstract only) is recorded in Section 8. An entry that was only read at abstract level is summarised at that level and nothing more.

## 2. Thematic review

### 2.1 Shortcut learning and dataset-origin clues

Hill et al. [1] showed that convolutional networks can predict attributes of knee radiographs that cannot be seen in the image, because the labels are tied to confounding variables, and that standard pre-processing did not remove these links. Ly et al. [2] studied acquisition-related shortcuts across several modalities and proposed a way of estimating generalisation without external data by disrupting image structure. Hajishafiezahramini et al. [5] found that the dataset of origin of mammograms remained decodable from learned features even after consistent pre-processing. Rafferty and Rajan [4] discussed how label quality, domain shift and bias limit what public chest datasets can show. Earlier foundations are consistent with this: shortcut learning is a general property of deep networks [23], confounders can carry a hip-fracture prediction [3], a pneumonia model can generalise unevenly across hospitals [24], and radiographic COVID-19 models can select shortcuts over signal [25], with an intervention that swapped laterality markers and compared the effect with random patches of the same size. Cooke et al. [35] extended intervention-based testing with synthetic image modifications.

Together, these works establish that a high score does not show what a model used. They motivate testing anatomy-free information (image dimensions, file metadata, borders) and source changes directly, rather than treating a pooled score as sufficient evidence.

### 2.2 Cross-source generalisation, OOD behaviour and reliability

Patwary and Toma [6] reported failures in both directions when a fracture classifier moved between paediatric and mixed-age radiographs, and Hrubý et al. [7] examined cross-centre validation for fracture detection as a feasibility study. Kutbi et al. [8] studied transfer of abnormality detection across anatomical regions using anatomical similarity. Gutbrod et al. [15] benchmarked OOD detection in medical imaging and separated different kinds of shift. Guo et al. [29] showed that modern networks are often poorly calibrated.

Together, these works motivate reporting internal and shifted performance separately, defining the task precisely, and examining calibration, selective prediction and unknown-input detection independently of ordinary accuracy.

### 2.3 Anatomy, projection and implant recognition and data cleanliness

Mitsuyama et al. [9] evaluated body-part and chest-projection classification across institutions, including an application to label quality. Fink et al. [10] classified projection and body side in musculoskeletal radiographs, and Langer et al. [11] studied how clean real-world anatomical-region labels are. Hinterwimmer et al. [32] sorted musculoskeletal radiographs into 28 anatomical categories. Implant studies address a different label: identifying hip implants [12, 14], knee implants with large external validation [13], orthopaedic implants generally [34], and loosening of hip implants [17].

Together, these works show that "classifying an X-ray" covers several different tasks (body part, projection, side, abnormality, implant identity), so scores cannot be compared across them. They also show why implant radiographs are a realistic imaging domain, which makes them useful as source-held-out test cases without OrthoTrace attempting implant identification itself.

### 2.4 Data and model foundations

FracAtlas [18] supplies multi-region musculoskeletal radiographs and, in our benchmark, is the only source containing all three target joints. BTXRD [33] supplies radiographs with anatomy tags used for our external check. MURA [16], a large musculoskeletal abnormality dataset, was not used because it requires a research-use agreement. The remaining sources are the UCI shoulder-implant set [19], the Gornale knee set [20], an OAI-derived knee set [21], the AV-DDH paediatric hip set [22] and the Kaggle hip-implant set [17]. We use EfficientNet [26], Swin Transformer [27] and ConvNeXt [28] as established backbones, and Holm's procedure [30] for multiple comparisons. ImageNet results for these architectures do not establish robustness on our sources.

## 3. Comparison of the surveyed work

| S. No | Reference | Data / task | Main finding | Limitation relevant to this project |
|---|---|---|---|---|
| 1 | Hill et al. [1] | Knee radiographs; shortcut investigation | Networks predict unseen attributes through confounders; pre-processing did not remove them | Different target; internal validation |
| 2 | Ly et al. [2] | Several modalities; shortcuts and generalisation | Acquisition shortcuts help internal accuracy and weaken transfer; structure disruption probes them | Indirect test; no explicit source holdout for joint recognition |
| 3 | Rafferty and Rajan [4] | Public chest radiograph datasets | Label quality, shift and bias limit evaluation | Chest, not orthopaedic; abstract-level reading |
| 4 | Hajishafiezahramini et al. [5] | Mammography, cross-dataset | Dataset origin stays decodable after consistent pre-processing | Preprint; other modality and target |
| 5 | Patwary and Toma [6] | Radiograph fracture classification, paediatric vs mixed-age | Failure under shift in both directions | Fracture endpoint; abstract only |
| 6 | Hrubý et al. [7] | Cross-centre fracture detection | Cross-centre validation is feasible and needed | Preprint; centre separation is not public-source separation |
| 7 | Kutbi et al. [8] | Bone abnormality detection across regions | Anatomical similarity can aid transfer | Abnormality, not region recognition |
| 8 | Mitsuyama et al. [9] | Body-part and projection classification, multi-institution | High accuracy across institutions; label-quality use | No shortcut or source-decoupled test for joints |
| 9 | Fink et al. [10] | Projection and body-side classification | View and side are separate learnable labels | Different target |
| 10 | Langer et al. [11] | Anatomical-region classification | Real-world labels are not clean | Preprint; abstract only |
| 11 | Rouzrokh et al. (THA-AID) [12] | Hip-implant identification | Implant detection with uncertainty and outlier flags | Different target; abstract only |
| 12 | Karnuta et al. [13] | Knee-implant identification | Multi-centre external validation at scale | Implant identity; abstract only |
| 13 | Gong et al. [14] | Hip-arthroplasty implant identification | Implants can be identified automatically | No source shift analysis |
| 14 | Gutbrod et al. (OpenMIBOOD) [15] | Medical OOD benchmark | OOD methods behave differently by shift type | Benchmark, not our task; venue unconfirmed |
| 15 | Rahman et al. (HipXNet) [17] | Hip-implant loosening | Provenance of the Kaggle hip source | Metadata only; different endpoint |
| 16 | Abedeen et al. (FracAtlas) [18] | Multi-region radiograph dataset | Source of the only three-joint data | Fracture labels; our knee labels are provisional |
| 17 | Liu et al. (ConvNeXt) [28] | ImageNet architecture | Modern convolutional baseline | No medical robustness evidence |
| 18 | Hinterwimmer et al. (SAM-X) [32] | 28-category musculoskeletal sorting | Broad anatomy sorting is feasible | Our question is narrower: source transfer |
| 19 | Yao et al. (BTXRD) [33] | Bone-tumour radiograph dataset | Public data with anatomy tags | Tumour labels; 54-image external subset |
| 20 | Patel et al. [34] | Orthopaedic implant identification | Implants can be identified from radiographs | 2021 (outside the window); different task |
| 21 | Cooke et al. (RoentMod) [35] | Chest radiographs, synthetic modification | Intervention-based shortcut testing | Chest; synthetic edits |

## 4. Analysis

**Evaluation protocol.** Studies of anatomy and implant recognition [9, 10, 12–14] report performance on internal splits or on multi-centre external validation. Few separate pooled random evaluation from a test on an entire unseen source, and the dataset-quality warnings [4, 11] suggest that even the static numbers may be inflated.

**Task definition.** Body part [9], projection and side [10], abnormality [8], implant identity [12–14] and implant loosening [17] are different targets. Accuracy, balanced accuracy and AUROC are also not interchangeable. A comparison that ranks papers by their largest percentage would be misleading, so this project does not borrow numerical baselines from incompatible tasks.

**Shortcut evidence.** The shortcut literature [1–3, 5, 24, 25, 35] shows the problem exists in other tasks and modalities, using different test designs: attribute prediction [1], structure disruption [2], origin decoding [5], marker exchange [25] and synthetic modification [35]. We found no study that combines anatomy-free baselines, an explicit source holdout and a paired border intervention for orthopaedic joint recognition. The search was targeted, so this does not prove that none exists.

**Evidence level.** A full-text experiment, an abstract-only record and a dataset catalogue deserve different strength of interpretation. References read only at abstract level (see Section 8) are used for motivation, not for numerical comparison.

## 5. Research gap

1. **G1.** Pooled accuracy leaves source transfer unclear: few studies of orthopaedic region recognition report how much a score changes when a whole source is excluded.
2. **G2.** A high accuracy leaves the cue ambiguous: a network may rely on framing, borders, dimensions or file properties instead of anatomy, and these are rarely tested with anatomy-free baselines and matched interventions.
3. **G3.** Algorithm rankings can change with the cohort, which pooled scores hide.
4. **G4.** Aggregate metrics can hide label conflicts and single-image failures, and per-image disagreement is rarely exposed to a reviewer.

## 6. Problem statement and objectives

**Problem statement.** A model that recognises hip, knee or shoulder radiographs can score near-perfectly on pooled public data because the joint label is tied to the data source. Imaging research teams need to know how much of that score survives a new source, which image properties explain it, and which individual predictions deserve suspicion.

**Research questions**

- **RQ1.** How much does pooled evaluation overstate Hip/Knee/Shoulder recognition compared with a source-decoupled test?
- **RQ2.** Can image properties unrelated to anatomy reproduce the pooled accuracy?
- **RQ3.** How do models behave when an implant-bearing source is held out, and is their confidence informative?
- **RQ4.** Can disagreement and shortcut cues be made inspectable on individual X-rays?

**Objectives**

| S. No | Objective | Metric of evaluation |
|---|---|---|
| O1 | Quantify the pooled versus source-decoupled gap on a leakage-audited six-source benchmark | Balanced-accuracy gap above 0.10 for at least 4 of 5 primary models (Holm-adjusted clustered bootstrap, p < 0.05) |
| O2 | Test anatomy-free shortcuts | Balanced accuracy of dimensions-only and metadata-only random forests, pooled versus decoupled; prediction change under a paired border intervention against a within-source control |
| O3 | Compare model families under frozen protocols | Balanced accuracy for random forests, linear probes and fine-tuned networks; six classical classifiers on shared features with source holdout |
| O4 | Characterise reliability under source shift | Leave-one-source-out balanced accuracy, expected calibration error, selective prediction and unknown-joint AUROC |
| O5 | Make behaviour inspectable in a workbench | Four checkpoint predictions, six region scores, Grad-CAM and a shortcut probe per image; median CPU latency; passing regression tests |

## 7. Proposed methodology

- **Data and pre-processing.** Six public sources (4,427 benchmark images, 657 in a sealed test partition) with group-aware splits; images converted to greyscale, resized to 160 × 160 and ImageNet-normalised.
- **Protocols.** Pooled random evaluation, source-decoupled evaluation (train without FracAtlas, test on FracAtlas) and leave-one-source-out evaluation; the analysis plan, code and training recipes are frozen and hash-recorded before the test set is opened.
- **Models.** Random forests on anatomy-free feature groups, logistic probes on frozen EfficientNet-B3, ConvNeXt-T and Swin-T embeddings, and fine-tuned EfficientNet-B3 and Swin-T; six classical classifiers on PCA-reduced EfficientNet-B3 features.
- **Shortcut tests.** Dimensions-only and metadata-only models, a paired border intervention that keeps centre pixels fixed, and an anatomy-free shortcut probe in the workbench.
- **Evaluation.** Balanced accuracy with clustered paired-bootstrap intervals, calibration, selective prediction, OOD detection and per-image error analysis.
- **Tools and feasibility.** Python, scikit-learn, PyTorch, FastAPI and a static web front end; all components are open source and run on a laptop CPU.
- **Known limitations.** Few independent sources, a small source-decoupled test set, provisional knee labels, compute-limited fine-tuning and no clinical validation.

## 8. References

Verification tags: **[C]** DOI, title, first author and year confirmed against Crossref; **[X]** confirmed against the arXiv record; **[A]** confirmed to exist, abstract only read; **[U]** cited from background knowledge, not verified in this project. Entries [32]–[35] were confirmed against Crossref for this survey; reading depth for them is citation and abstract level only.

[1] Hill BG, Koback FL, Schilling PL. The risk of shortcutting in deep learning algorithms for medical imaging research. *Sci Rep* 2024;14:29224. doi:10.1038/s41598-024-79838-6 [C; abstract read]

[2] Ly CO, Unnikrishnan B, Tadic T, et al. Shortcut learning in medical AI hinders generalization: method for estimating AI model generalization without external data. *npj Digit Med* 2024. doi:10.1038/s41746-024-01118-4 [C; page read]

[3] Badgeley MA, Zech JR, Oakden-Rayner L, et al. Deep learning predicts hip fracture using confounding patient and healthcare variables. *npj Digit Med* 2019. doi:10.1038/s41746-019-0105-1 [C; page read]

[4] Rafferty A, Rajan A. Limitations of public chest radiography datasets for artificial intelligence: label quality, domain shift, bias and evaluation challenges. arXiv:2509.15107 (2025); *Philos Trans R Soc A* 2026, doi:10.1098/rsta.2025.0129 [X, C; abstract read]

[5] Hajishafiezahramini P, Hamilton M, Meruvia-Pastor O, Kendall E. Dataset-origin signatures and shortcut learning in screening mammography AI: a cross-dataset case study. arXiv:2607.15416 (2026) [X; abstract read]

[6] Patwary R, Toma M. Bidirectional domain shift failure in radiograph fracture classification across out-of-distribution pediatric and mixed-age multi-region data. *Appl Sci* 2026;16(14):6853. doi:10.3390/app16146853 [C; abstract only]

[7] Hrubý R, Kvak D, Dandár J, Atakhanova A, Misař M, Dufek D. Cross-center validation of deep learning model for musculoskeletal fracture detection in radiographic imaging: a feasibility study. medRxiv 2024. doi:10.1101/2024.01.17.24301244 [C; preprint abstract only]

[8] Kutbi M, Shaban K, Khogeer A. Exploring anatomical similarity in zero-shot learning for bone abnormality detection. *Sci Rep* 2026. doi:10.1038/s41598-026-37516-9 [C; abstract/page read]

[9] Mitsuyama Y, Takita H, Walston SL, et al. Deep learning models for radiography body-part classification and chest radiograph projection/orientation classification: a multi-institutional study. *Eur Radiol* 2026;36:2576–2590 (online 2025). doi:10.1007/s00330-025-12053-7 [C; page read]

[10] Fink A, Tran H, Reisert M, et al. A deep learning approach for projection and body-side classification in musculoskeletal radiographs. *Eur Radiol Exp* 2024;8:23. doi:10.1186/s41747-023-00417-x [C; page read]

[11] Langer S, Ritter J, Braren R, Rueckert D, Hager P. Self-supervised radiograph anatomical region classification – how clean is your real-world data? arXiv:2412.15967 (2024) [X; abstract read]

[12] Rouzrokh P, Mickley JP, Khosravi B, et al. THA-AID: deep learning tool for total hip arthroplasty automatic implant detection with uncertainty and outlier quantification. *J Arthroplasty* 2024. doi:10.1016/j.arth.2023.09.025 [C; abstract read]

[13] Karnuta JM, et al. Artificial intelligence for automated implant identification in knee arthroplasty: a multicenter external validation study exceeding 3.5 million plain radiographs. *J Arthroplasty* 2023. doi:10.1016/j.arth.2023.03.039 [C, bibliographic match; abstract only]

[14] Gong Z, Fu Y, He M, Fu X. Automated identification of hip arthroplasty implants using artificial intelligence. *Sci Rep* 2022;12:12179. doi:10.1038/s41598-022-16534-3 [C; page read]

[15] Gutbrod M, Rauber D, Weber Nunes D, Palm C. OpenMIBOOD: open medical imaging benchmarks for out-of-distribution detection. *CVPR* 2025; arXiv:2503.16247 [X; abstract read]

[16] Rajpurkar P, et al. MURA: large dataset for abnormality detection in musculoskeletal radiographs. arXiv:1712.06957 (2017) [X; not read beyond abstract]

[17] Rahman T, et al. HipXNet: deep learning approaches to detect aseptic loosening of hip implants using X-ray images. *IEEE Access* 2022. doi:10.1109/ACCESS.2022.3173424 [C, bibliographic match; not read]

[18] Abedeen I, et al. FracAtlas: a dataset for fracture classification, localization and segmentation of musculoskeletal radiographs. *Sci Data* 2023. doi:10.1038/s41597-023-02432-4; data: figshare doi:10.6084/m9.figshare.22363012 (CC BY 4.0) [C; dataset page read]

[19] Shoulder implant X-ray manufacturer classification. UCI Machine Learning Repository, doi:10.24432/C5F893 (CC BY 4.0) [dataset page read]

[20] Gornale S, Patravali P. Digital knee X-ray images. *Mendeley Data* 2020. doi:10.17632/t9ndx37v5h.1 (CC BY 4.0) [dataset page read]

[21] Knee osteoarthritis severity grading dataset (derived from the Osteoarthritis Initiative). *Mendeley Data*, doi:10.17632/56rmx5bjcr.1; Kaggle copy "shashwatwork/knee-osteoarthritis-dataset-with-severity" [licence as reported by hosts]

[22] Acetabular-vision hip developmental dysplasia (AV-DDH) dataset. *Mendeley Data*, doi:10.17632/4gvcb6gmh2.2 [host page read; export config lists "Private"]

[23] Geirhos R, Jacobsen J-H, Michaelis C, et al. Shortcut learning in deep neural networks. *Nat Mach Intell* 2020;2:665–673 [U: the DOI lookup failed in this project]

[24] Zech JR, Badgeley MA, Liu M, et al. Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: a cross-sectional study. *PLoS Med* 2018;15:e1002683. doi:10.1371/journal.pmed.1002683 [C]

[25] DeGrave AJ, Janizek JD, Lee S-I. AI for radiographic COVID-19 detection selects shortcuts over signal. *Nat Mach Intell* 2021;3:610–619. doi:10.1038/s42256-021-00338-7 [C]

[26] Tan M, Le QV. EfficientNet: rethinking model scaling for convolutional neural networks. *ICML* 2019; arXiv:1905.11946 [X]

[27] Liu Z, Lin Y, Cao Y, et al. Swin Transformer: hierarchical vision transformer using shifted windows. *ICCV* 2021; arXiv:2103.14030 [X]

[28] Liu Z, Mao H, Wu C-Y, et al. A ConvNet for the 2020s. *CVPR* 2022; arXiv:2201.03545 [X]

[29] Guo C, Pleiss G, Sun Y, Weinberger KQ. On calibration of modern neural networks. *ICML* 2017; arXiv:1706.04599 [X, title confirmed]

[30] Holm S. A simple sequentially rejective multiple test procedure. *Scand J Stat* 1979;6:65–70 [U: not found in Crossref in this project]

[31] Removed from the project bibliography because the source could not be verified; the number is kept so that numbering matches the manuscript.

[32] Hinterwimmer et al. SAM-X: sorting algorithm for musculoskeletal x-ray radiography. *Eur Radiol* 2023;33:1537–1544 (online 2022). doi:10.1007/s00330-022-09184-6 [C; citation level]

[33] Yao et al. A radiograph dataset for the classification, localization, and segmentation of primary bone tumors. *Sci Data* 2025;12:88. doi:10.1038/s41597-024-04311-y [C; citation level]

[34] Patel et al. Automated identification of orthopedic implants on radiographs using deep learning. *Radiol Artif Intell* 2021;3:e200183. doi:10.1148/ryai.2021200183 [C; citation level]

[35] Cooke et al. RoentMod: a synthetic chest X-ray modification model to identify and correct image interpretation model shortcuts. *npj Digit Med* 2026;9:324. doi:10.1038/s41746-026-02497-6 [C; citation level]
