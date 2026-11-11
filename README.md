<p align="center"><img src="ML3/site/assets/logo.svg" alt="OrthoTrace logo" width="112"></p>

# OrthoTrace: source-controlled evaluation of orthopaedic joint recognition

OrthoTrace is a machine-learning study and workbench that asks whether hip, knee and shoulder X-ray classifiers learn anatomy or learn which dataset an image came from. It compares predictions across training sources, then exposes the differences on individual de-identified images: a six-region classifier, four benchmark checkpoints, a Grad-CAM overlay and an anatomy-free shortcut probe, with model scores and agreement exported for dataset quality review.

**Live site:** <https://yenigalladheeraj.github.io/ML-Project/> (static demo mode with precomputed specimens; live inference, upload and the shortcut probe need the local server, see section 10).

Model training and the benchmark experiments ran locally and in Google Colab. The workbench runs on a personal computer from the saved checkpoints and results.

---

## 1. What the project does

1. Builds a leakage-audited benchmark of six public radiograph sources with group-aware splits and a sealed, hash-recorded test partition.
2. Shows that near-perfect pooled accuracy (0.993–1.000 balanced accuracy) falls to 0.498–0.686 when a whole source, FracAtlas, is left out.
3. Shows that image dimensions or file metadata alone reach about 0.96–0.97 pooled and exactly chance (0.333) when decoupled.
4. Compares classical classifiers, linear probes and fine-tuned image models under frozen protocols.
5. Tests how models fail when an implant-bearing source is held out, and whether their confidence is informative.
6. Presents every prediction, disagreement and shortcut cue in a live workbench, with saved evidence for offline use.

## 2. Key features

- Three-class benchmark (Hip, Knee, Shoulder) and an expanded six-region model (adds Hand, Leg, Elbow).
- Pooled, source-decoupled and leave-one-source-out protocols, with clustered paired-bootstrap intervals and Holm correction.
- Anatomy-free baselines: dimensions-only and metadata-only random forests, and a paired border intervention with within-source controls.
- Four EfficientNet-B3 checkpoints trained on different source sets, compared on the same image.
- Grad-CAM overlay, per-region cutoffs, and an exportable review record that omits pixels and filenames.
- Anatomy-free shortcut probe that guesses the joint and the source from file properties alone and flags answers that are reproducible without anatomy.
- Frozen analysis plan, checkpoint hashes, touch log and an automated audit of the evaluation.
- Measured CPU inference time, regression tests and a static page audit.

## 3. Problem and objectives

When a public dataset mostly contains one joint, a model can guess the joint from framing, dimensions or other features associated with the source. We test how recognition changes when an entire source is left out, then expose those changes on individual X-rays.

| Objective | Metric |
|---|---|
| O1. Quantify the pooled versus source-decoupled gap | Balanced-accuracy gap above 0.10 for at least 4 of 5 primary models |
| O2. Test anatomy-free shortcuts | Dimensions-only and metadata-only random forests; paired border intervention |
| O3. Compare model families under defined protocols | Balanced accuracy across random forests, linear probes and fine-tuned networks |
| O4. Characterise reliability under source shift | Leave-one-source-out accuracy, calibration, selective prediction, unknown-joint AUROC |
| O5. Make behaviour inspectable | Four predictions, six region scores, Grad-CAM and a probe per image |

## 4. Data and prediction tasks

| Task | Data | Output |
|---|---|---|
| Frozen benchmark | Six public sources and 657 held-out images. The source-decoupled test uses 55 FracAtlas images. | One label from Hip, Knee, and Shoulder. |
| Expanded workbench | Multi-region dataset labels, provisional FracAtlas visual reviews, and two labeled elbow sources. | Independent Hip, Knee, Shoulder, Hand, Leg, and Elbow flags. |
| External check | 54 BTXRD images with one of the three selected joint tags. | Comparison of expanded-model flags with published Elbow, Knee, and Shoulder tags. |

The datasets themselves are not in this repository. Read the [dataset credits](ML3/site/downloads/dataset_licences.md) and the [literature survey](literaturesurvey.md) for provenance, licences and label limitations.

## 5. Methodology

### 5.1 Preprocessing

Convert to greyscale, resize to 160 × 160, and apply ImageNet normalization. The expanded model scores the center crop across eight views and compares each region score with a development-set cutoff.

### 5.2 Protocols

Compare pooled random testing with training that excludes FracAtlas (source-decoupled) and with leaving each source out in turn. The analysis plan, code and training recipes are frozen and hash-recorded before the sealed test partition is opened once.

### 5.3 Models

The frozen study includes EfficientNet-B3, ConvNeXt-T, Swin-T, logistic probes and Random Forest controls. A separate development experiment compares six classical classifiers on the same PCA-reduced EfficientNet-B3 features.

### 5.4 Shortcut tests

Use image dimensions and file metadata alone, then compare edits to the border of the same image while keeping the center pixels fixed. The workbench's shortcut probe applies the same idea to every analysed file.

### 5.5 Evaluation

Report balanced accuracy for the three-class benchmark, per-region flags for the expanded model, and per-image disagreements for the workbench. Record cohort sizes with each result.

## 6. Results

| Experiment | Result | Interpretation |
|---|---|---|
| Pooled vs source-decoupled (five primary models) | 0.993–1.000 pooled, 0.498–0.686 decoupled, gap 0.31–0.50 (adjusted p = 0.002) | Pooled evaluation overstates generalisation to a new source. |
| Dimensions-only Random Forest | 97.1% pooled balanced accuracy and 33.3% source-decoupled balanced accuracy | Image size carried predictive information in the pooled setting. |
| Implant-source holdouts | Balanced accuracy 0.00–0.04 (hip implants) and 0.00–0.17 (shoulder implants) | Systematic joint swaps, with no protection from confidence. |
| Classical source holdout | RBF SVM led the six tested methods with 56.5% balanced accuracy on 47 FracAtlas validation images | Applies to the three-class development experiment. |
| BTXRD before and after center cropping | Knee detections rose from 8 to 21 of 37. Extra Elbow flags fell from 33 to 16 of 49. | The same 54 images were reused after inspecting the first run. |
| Specimen 06 | The current model flags Elbow alone with a score of 99.7%. | The image stayed out of training, and its visual review is provisional. |

Evidence files include the [classical comparison](ML3/artifacts/retraining/algorithm-comparison.json), [BTXRD baseline](ML3/artifacts/retraining/btxrd-mirror-evaluation.json) and [center-crop follow-up](ML3/artifacts/retraining/center-crop-candidates.json).

## 7. The workbench

**X-ray → image validation → preprocessing → six-region scores and four benchmark predictions → Grad-CAM → shortcut probe → review record**

The live report displays each region cutoff and benchmark agreement. The export omits image pixels and filenames. Saved specimens remain available when the inference service is offline.

**Shortcut probe.** Beside the model outputs, the workbench runs an anatomy-free probe that sees only file properties (size, aspect, colour mode, format, file size), never pixels. It reports the joint those properties alone would suggest, which source the file resembles, and whether the pooled model's answer is *shortcut-compatible*, meaning reproducible without anatomy. On development data the probe reaches 0.99 balanced accuracy pooled and 0.31 when trained without FracAtlas, matching the study's finding. Compatible with a shortcut is not proof of one. Rebuild it with `python ML3/scripts/build_probe.py`; it is trained on development rows only and the sealed test set is never read.

**Local performance.** A CPU check ran 12 sequential requests using four bundled X-rays. The median round-trip time was **305 ms**, with a range of **214–395 ms**. Each response included both prediction tracks and Grad-CAM. These timings describe one laptop and a running server. See the [raw timing data](ML3/artifacts/retraining/local-inference-timing.json).

## 8. Industry relevance

Radiograph recognition feeds routing, label cleaning and implant-identification pipelines, and a pooled benchmark score can hide the fact that it only works on familiar sources.

- **Imaging research teams:** inspect model disagreement and questionable labels on de-identified evaluation images before trusting a score.
- **Machine-learning evaluators:** run the dimensions, metadata and border controls on a candidate dataset as a quick shortcut check.
- **Cost and deployment:** inference runs on a laptop CPU with no GPU, database or login; a container recipe is in [ML3/site/DEPLOY.md](ML3/site/DEPLOY.md). No user study or clinical validation has been run, and no adoption is claimed.

## 9. Limitations

- Clinician review of the provisional FracAtlas knee and leg labels is pending.
- The source-decoupled test is small (55 FracAtlas images), several intervals collapse to 0.00–0.00, and there are few independent sources.
- Implant presence is a plausible source-associated confound, not a demonstrated cause.
- The BTXRD follow-up used a cohort that had already informed the change, and its elbow subset contains five images. A fresh external test is pending.
- Fine-tuning was compute-limited, and some holdouts have a single seed.
- The shortcut probe uses only file properties and cannot prove that a deep model used a shortcut.
- The models are evaluation tools, not diagnostic devices.

## 10. Run and verify

From the repository root on Windows with Python 3.11:

```powershell
.\setup.ps1
.\start.ps1
```

Open [the workbench](http://127.0.0.1:8000/demo.html), [benchmark results](http://127.0.0.1:8000/results.html), or [the evidence page](http://127.0.0.1:8000/evaluation.html). See [container deployment](ML3/site/DEPLOY.md).

```powershell
.\.venv\Scripts\python.exe -X utf8 ML3/site/qa/qa_audit.py
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s ML3/site/qa -p test_service.py -v
.\.venv\Scripts\python.exe -X utf8 ML3/site/qa/qa_api.py
```

The API test expects the local server on port 8000. Rebuild pages with `python ML3/site/build_site.py`. The Colab notebook for the earlier joint-identification stage is in [notebooks](notebooks).

## 11. Repository guide

| Path | Contents |
|---|---|
| [literaturesurvey.md](literaturesurvey.md) | Literature survey: scope, thematic review, comparison table, analysis, research gap, objectives, methodology, references |
| [Literature_Survey.docx](Literature_Survey.docx) | The same survey as a Word document |
| [context.md](context.md) | Full explanation of the task, methods, and scores |
| [notebooks](notebooks) | Google Colab notebook for the joint-identification stage |
| [ML3/site](ML3/site) | Website source, built pages, example images, API, shortcut probe and five checkpoints |
| [ML3/scripts](ML3/scripts) | Training, evaluation, statistics, audit and probe-building scripts |
| [ML3/artifacts/retraining](ML3/artifacts/retraining) | Saved comparisons and frozen baseline configuration |
| [ML3/docs](ML3/docs) | Delivery notes, team checklist, viva guide and literature matrix |
| [ML3/report](ML3/report) | Project report in the department template format and its build script |

## 12. Tools used

Python 3.11, PyTorch and torchvision, scikit-learn, NumPy, pandas, SciPy, OpenCV, Pillow, matplotlib, seaborn, FastAPI and Uvicorn, vanilla JavaScript with GSAP and Lenis, python-docx, Google Colab, GitHub Actions and GitHub Pages.

The documentation organization was informed by the [classmate NIDS project](https://github.com/jaslyn-j/Concept-drift-detecting_NIDS), particularly its separation of scope, methodology, measured results, dashboard behavior, and limitations, and the structure of its literature survey.
