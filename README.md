# OrthoTrace

OrthoTrace compares X-ray anatomy predictions across training sources. Its local workbench runs a six-region classifier, four benchmark checkpoints, and a Grad-CAM overlay on the same de-identified image. It also exports model scores and agreement for dataset quality review.

## 1. Problem and objectives

When a public dataset mostly contains one joint, a model can guess the joint from framing, dimensions, or other features associated with the source. We test how recognition changes when an entire source is left out, then expose those changes on individual X-rays.

1. Measure the difference between pooled and source-decoupled Hip, Knee, and Shoulder evaluation.
2. Test simple shortcuts with dimensions-only models and paired border interventions.
3. Compare classical classifiers and image models under defined protocols.
4. Make predictions, disagreements, and label conflicts inspectable in a live report.

## 2. Data and prediction tasks

| Task | Data | Output |
|---|---|---|
| Frozen benchmark | Six public sources and 657 held-out images. The source-decoupled test uses 55 FracAtlas images. | One label from Hip, Knee, and Shoulder. |
| Expanded workbench | Multi-region dataset labels, provisional FracAtlas visual reviews, and two labeled elbow sources. | Independent Hip, Knee, Shoulder, Hand, Leg, and Elbow flags. |
| External check | 54 BTXRD images with one of the three selected joint tags. | Comparison of expanded-model flags with published Elbow, Knee, and Shoulder tags. |

Read the [dataset credits](ML3/site/downloads/dataset_licences.md) and [literature survey](literaturesurvey.md) for provenance and label limitations.

## 3. Methodology

- **Preprocessing.** Convert to greyscale, resize to 160 × 160, and apply ImageNet normalization. The expanded model scores the center crop across eight views and compares each region score with a development-set cutoff.
- **Benchmark.** Compare pooled testing with training that excludes FracAtlas. Inspect the pooled and source-held-out predictions on the same images where the protocol allows a direct comparison.
- **Model comparison.** The frozen study includes EfficientNet-B3, ConvNeXt-T, Swin-T, logistic probes, and Random Forest controls. A separate development experiment compares six classical classifiers on the same PCA-reduced EfficientNet-B3 features.
- **Shortcut test.** Use image dimensions alone, then compare edits to the border of the same image while keeping the center pixels fixed.
- **Evaluation.** Report balanced accuracy for the three-class benchmark, per-region flags for the expanded model, and per-image disagreements for the workbench. Record cohort sizes with each result.

## 4. Results

| Experiment | Result | Interpretation |
|---|---|---|
| Dimensions-only Random Forest | 97.1% pooled balanced accuracy and 33.3% source-decoupled balanced accuracy | Image size carried predictive information in the pooled setting. |
| Classical source holdout | RBF SVM led the six tested methods with 56.5% balanced accuracy on 47 FracAtlas validation images | Applies to the three-class development experiment. |
| BTXRD before and after center cropping | Knee detections rose from 8 to 21 of 37. Extra Elbow flags fell from 33 to 16 of 49. | The same 54 images were reused after inspecting the first run. |
| Specimen 06 | The current model flags Elbow alone with a score of 99.7%. | The image stayed out of training, and its visual review is provisional. |

Evidence files include the [classical comparison](ML3/artifacts/retraining/algorithm-comparison.json), [BTXRD baseline](ML3/artifacts/retraining/btxrd-mirror-evaluation.json), and [center-crop follow-up](ML3/artifacts/retraining/center-crop-candidates.json).

## 5. Workbench and local performance

**X-ray → image validation → preprocessing → six-region scores and four benchmark predictions → Grad-CAM → review record**

The live report displays each region cutoff and benchmark agreement. The export omits image pixels and filenames. Saved specimens remain available when the inference service is offline.

A local CPU check ran 12 sequential requests using four bundled X-rays. The median round-trip time was **305 ms**, with a range of **214–395 ms**. Each response included both prediction tracks and Grad-CAM. These timings describe one laptop and a running server. See the [raw timing data](ML3/artifacts/retraining/local-inference-timing.json).

## 6. Run and verify

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

The API test expects the local server on port 8000. Rebuild pages with `python ML3/site/build_site.py`.

## 7. Repository guide

| Path | Contents |
|---|---|
| [ML3/site](ML3/site) | Website source, built pages, example images, API, and five checkpoints |
| [ML3/scripts](ML3/scripts) | Expanded-model training, classical comparison, and BTXRD evaluation scripts |
| [ML3/artifacts/retraining](ML3/artifacts/retraining) | Saved comparisons and frozen baseline configuration |
| [literaturesurvey.md](literaturesurvey.md) | Thematic review, prior-work comparison, research gaps, and sources |
| [context.md](context.md) | Full explanation of the task, methods, and scores |
| [Viva guide](ML3/docs/DEMO_AND_VIVA.md) | Eight-minute presentation and likely questions |

## 8. Research use and limitations

Imaging research teams can use OrthoTrace to investigate model disagreement and questionable labels on de-identified evaluation images. Clinician review of provisional labels and a fresh external test are pending. The BTXRD follow-up used a cohort that had already informed the change, and its elbow subset contains five images. The release includes trained checkpoints and runnable examples. The full training datasets are maintained separately.

The documentation organization was informed by the [classmate NIDS project](https://github.com/jaslyn-j/Concept-drift-detecting_NIDS), particularly its separation of methodology, measured results, dashboard behavior, and limitations.
