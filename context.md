# OrthoTrace — the complete project explained simply

Prepared from the existing implementation, saved predictions and evaluation artifacts on 10 November 2026. This is the current explanation for presenting the project. The older `ML3/context.md` is retained as a historical development record.

## 1. What is our project?

**OrthoTrace is an end-to-end X-ray joint-recognition and model-evaluation project.** It classifies an image as Hip, Knee or Shoulder, compares four real model checkpoints and explains how their answers depend on the sources used for training.

The main question is: **Did the model learn the anatomy, or did it learn clues about the dataset?**

The website provides a live inference workbench, interactive source-sensitivity comparison, measured results, literature survey, medical context, implant-history timeline and evaluation evidence. It is a working software system built around an existing source-controlled benchmark.

It does not identify implant manufacturers, diagnose a fracture, choose a treatment or determine the age of an implant. Those are different prediction tasks with different required labels and validation.

### A 30-second introduction

“Our project is OrthoTrace. It recognizes Hip, Knee and Shoulder from X-rays and compares four checkpoints trained on different dataset sources. We found that very high scores on a mixed public dataset can drop substantially when a source is excluded from training. Our contribution is a source-controlled evaluation, simple shortcut baselines and a working interface that makes the evidence easy to inspect.”

## 2. Why does this problem matter?

Imagine training a model with hip images from website A, shoulder images from website B and knee images from scanner C. Even if we shuffle the images into training and test sets, the test images still have the same sources and styles.

The model might recognize image size, borders, cropping or implant appearance. Because the source is associated with the joint, recognizing the source can produce the correct label without learning anatomy robustly.

This is called **source–label confounding**. A **shortcut** is an easy clue that helps on the available test but may fail in another setting. **Distribution shift** means the new images differ from the images used during training.

A good pooled test score is a valid measurement for that test. The problem is treating it as evidence of performance on unfamiliar sources without checking.

## 3. How the project evolved

1. An earlier three-class prototype produced high scores on a smaller pooled collection.
2. An audit found that joint labels were strongly associated with source. The original high scores were therefore insufficient evidence of robust anatomy recognition.
3. The benchmark expanded to six sources, with grouped splits, multiple model families, anatomy-free baselines and source-held-out evaluation.
4. Model recipes and the analysis plan were recorded before the final test evaluation. Checkpoints, predictions and statistics were saved.
5. The current application integrates four of those checkpoints with live image inference, comparisons, image facts and an activation overlay.
6. The frontend was redesigned around the project's story and evidence. Better presentation did not change the saved scientific scores.

## 4. What already existed, and what did we add?

| Existing foundation | Our project contribution |
|---|---|
| EfficientNet, Swin, ConvNeXt, random forests and logistic regression | A controlled comparison on this particular six-source Hip/Knee/Shoulder benchmark |
| Public orthopaedic image datasets | A source-aware target manifest, grouped partitions and explicitly documented provenance/label limitations |
| Research on shortcut learning and external validation | A focused test of pooled versus source-decoupled joint recognition, with anatomy-free controls |
| Work on implant identification | A separate joint-recognition task and an explanation of why implant-related source differences can complicate evaluation |
| Saved trained networks | A working four-checkpoint application with real inference, probabilities, agreement, image properties and Grad-CAM |
| Standard metrics | Traceable results, uncertainty estimates, baseline comparisons and saved-prediction verification |

The useful distinction is **how the project evaluates and explains model behaviour**, not a claim that we invented a new neural architecture. Do not describe it as the first project to discover shortcut learning or as better than commercial implant-identification software.

## 5. The datasets

The target benchmark contains **4,427 images** from six sources.

| Code | Source | Hip | Knee | Shoulder | Important detail |
|---|---|---:|---:|---:|---|
| F | FracAtlas | 179 | 94 | 101 | Only source containing all three target joints |
| K | Kaggle hip-implant collection | 206 | 0 | 0 | Compiled hip implant images |
| U | UCI shoulder-implant collection | 0 | 0 | 597 | Shoulder implant images |
| A | AV-DDH | 400 | 0 | 0 | Paediatric hip images |
| G | Gornale knee | 0 | 1,650 | 0 | Knee images with source-specific acquisition characteristics |
| O | OAI-derived knee collection | 0 | 1,200 | 0 | Pre-cropped knee images |

The recorded target partitions are **3,102 training**, **668 validation** and **657 test** images. Groups, rather than just individual images, are kept in one partition. Groups represent available patient/reference identifiers or duplicate-related clusters. This reduces leakage from related images appearing on both sides of a split; it cannot prove that all unknown patient relationships were recovered.

The FracAtlas test subset contains **55 images: 26 Hip, 14 Knee and 15 Shoulder**. The 94 FracAtlas knee labels in the benchmark were provisionally assigned using AI-assisted visual inspection and are not clinician-verified. That limitation directly affects interpretation.

There is a separate unknown-joint pool of hand/non-knee leg images for secondary out-of-distribution evaluation. These are not extra prediction classes in the live three-class model.

## 6. The evaluation methods

### E0: pooled random evaluation

Train on development data from the mixed sources, then test on the pooled target test partition. Training and testing contain familiar source types. The main pooled endpoint contains 657 images.

### E1: source-balanced evaluation

This protocol adjusts the influence of source/joint cells in pooled training. Balancing reduces dominance of large sources, but does not automatically remove source–label associations.

### E2: source-decoupled evaluation

Exclude FracAtlas from training, then evaluate the FracAtlas test subset. Because FracAtlas contains all three joints, the network cannot identify the joint simply by distinguishing FracAtlas from the other sources within that test subset.

The E0 and E2 results come from **different trained checkpoints**. The main comparison uses different test endpoints: pooled test versus the 55-image FracAtlas subset. A separate same-source control evaluates the E0 and E2 models on the **same FracAtlas test images** to help examine that distinction.

### E3: leave one source out

Exclude K, U, A, G or O during training and test on the held-out source. This shows which source changes cause difficulty. Most of these sources contain one target joint, so their held-out score is essentially recall for that joint; do not interpret it as a full three-class test.

### Other recorded protocols

E6 trains from FracAtlas and tests transfer to other sources. E7 studies the native-source subset without K and U. These support the broader evaluation; they are not separate functions that retrain models in the website.

## 7. Models and techniques, in plain terms

**Random forest (RF):** many decision trees vote on a label. Some baselines receive only image width, height and aspect ratio. Others receive metadata, borders, low-frequency intensities, histograms or HOG edge features. In `bench2_probes.py`, the forest recipe uses 100 trees, balanced subsampling and a fixed seed per run.

**EfficientNet-B3:** an established convolutional image model. It is one of the comparison backbones and the architecture used in all four live-demo checkpoints.

**ConvNeXt-T:** an established modern convolutional model used for comparisons.

**Swin-T:** an established image transformer using window-based attention, also used for comparisons.

**Frozen probe:** keep a pretrained backbone unchanged, extract its numerical image features and train a small logistic-regression classifier. The recorded probe recipe standardizes features and uses logistic regression with C = 0.05 and maximum 200 iterations.

**Fine-tuning (FT):** start from ImageNet-pretrained weights and update the network on the project data. The final fine-tuning function uses three epochs, AdamW, weight decay 0.01, learning rate 0.0003 for EfficientNet-B3 and 0.0001 for Swin-T/ConvNeXt-T. The recorded batch size is 16, with horizontal-flip augmentation and cross-entropy label smoothing of 0.05. GPU training and CPU inference are separate activities.

**Seeds:** repeat an experiment with controlled randomness. Probes/RF generally use five seeds; primary fine-tuned EfficientNet/Swin comparisons use three. ConvNeXt fine-tuning uses one seed. Secondary fine-tuned A/G/O holdouts use seed 0 under the recorded compute amendment. A mean over seeds is not a single image's confidence.

**Preprocessing variants:** full image, centre crop, intensity normalization, border removal, a limited implant-blob inpainting proxy and high-pass filtering. These test whether removing some easy cues changes source recognition or transfer. They do not establish implant causality.

## 8. The four live checkpoints

| Checkpoint | What changed in training? |
|---|---|
| Pooled | All six sources included in the recorded pooled setup |
| Without FracAtlas | F excluded |
| Without hip-implant source | K excluded |
| Without shoulder-implant source | U excluded |

These four are **EfficientNet-B3 seed-0 checkpoints**, not four different architectures. The broader results page compares more models and seeds than the live workbench.

### Specimen 06 and out-of-scope inputs

Specimen 06 looks like a lateral elbow on visual review. The project’s precomputed sample metadata records it as Knee, a provisional label that awaits clinician verification. The live report flags the mismatch. All four checkpoints still return Knee because the classifier must rank Hip, Knee and Shoulder. The pooled model’s roughly 97.9% softmax score is relative to those three choices. This is a qualitative example of both a possible labeling error and a closed-set classifier facing an unsupported joint. The saved benchmark labels and metrics still reflect the original evaluation and would need a label audit and rerun before any correction to those results.

## 9. The complete live workflow

1. The browser checks `/api/health` and loads the specimen library.
2. The user selects a provided specimen or uploads an image. Accepted types are JPEG, PNG, BMP, WebP and TIFF; the service limits the body to 12 MB and rejects very small images.
3. The browser sends actual image bytes to `POST /api/predict` when the service is online.
4. Pillow decodes the image in memory. The input is converted to greyscale and resized to 160 × 160, preserving the study's stretching recipe rather than inventing a new crop.
5. Greyscale intensity is copied into three channels. Each channel is normalized using ImageNet mean `[0.485, 0.456, 0.406]` and standard deviation `[0.229, 0.224, 0.225]`.
6. Four saved networks run on CPU. Their three logits are converted into probabilities using softmax.
7. The pooled model also produces Grad-CAM. The response includes probabilities, labels, image facts, warnings, agreement and `stored=false`.
8. The browser displays a report and original/activation comparison slider. Switching images animates the display; it does not alter the file sent to the models.

If the API is offline, provided specimens can use clearly labelled saved outputs. Uploaded files are not answered using a saved specimen. The homepage Lab is a saved-output comparison; it links the exact specimen into the live workbench.

## 10. Understanding every score

### Softmax and confidence: one image

For logits z, probability for class i is `exp(z_i) / sum(exp(z_j))`. The predicted label has the largest probability. Displayed confidence is that largest value × 100.

Example: sample 2's pooled checkpoint predicts Hip with about 95.5% softmax confidence. This is **not 95.5% test accuracy**. Sample 5's pooled reading is Knee at 95.3%, while its no-FracAtlas checkpoint reads Shoulder at 67.2%.

The live probabilities are raw, uncalibrated softmax values. Temperatures recorded for analysis are not silently applied to the live report. Rounding may make displayed class probabilities sum to slightly above or below 100%.

### Agreement

The report's ring counts how many of the four checkpoints agree with the **pooled checkpoint's label**. “3/4 agree” is a comparison count, not 75% accuracy and not proof that the label is correct. `all_agree` means all four predicted labels are identical.

### Accuracy

`Accuracy = correct predictions / all predictions.` It can be misleading when one class is much larger than the others.

### Recall and balanced accuracy

`Recall for a joint = correctly recognized examples of that joint / all test examples of that joint.`

`Balanced accuracy = mean recall over the classes present in the evaluation.` On the main three-class endpoint, each joint gets equal weight.

Simple invented arithmetic example, not a project result: Hip recall 90%, Knee recall 30%, Shoulder recall 90% gives balanced accuracy `(90 + 30 + 90) / 3 = 70%`. The website's actual scores come from saved predictions, not this example.

Chance is approximately 0.333 for the three-class balanced setting. On a source containing one true class, report the observed-class recall in context; the three-class chance reference is not a new random experiment.

### Generalization gap and percentage points

`Gap = pooled balanced accuracy − source-decoupled balanced accuracy.`

EfficientNet-B3: `0.9982 − 0.6859 = 0.3123`. That is a **31.23 percentage-point drop**, not a 31.23% relative drop. A relative reduction would divide by the original score, which is not how the displayed gap is defined. Rounded table inputs can differ slightly from a gap calculated at full precision.

### Actual main results

| Model | Seeds | Pooled BA | Decoupled BA | Gap, percentage points |
|---|---:|---:|---:|---:|
| EfficientNet-B3, fine-tuned | 3 | 0.9982 | 0.6859 | 31.23 |
| Swin-T, fine-tuned | 3 | 1.0000 | 0.6014 | 39.86 |
| EfficientNet-B3, frozen probe | 5 | 0.9926 | 0.5527 | 43.99 |
| ConvNeXt-T, frozen probe | 5 | 0.9953 | 0.4977 | 49.76 |
| Swin-T, frozen probe | 5 | 0.9936 | 0.6641 | 32.95 |
| Image dimensions RF baseline | 5 | 0.9713 | 0.3333 | 63.80 |
| Metadata RF baseline | 5 | 0.9605 | 0.3333 | 62.71, recorded full-precision gap |

The dimensions baseline is important: it nearly solves the pooled task without viewing anatomy and falls to chance in the decoupled setting. It supports a source-shortcut interpretation; it does not identify a single causal visual feature.

### Confusion matrix

Rows indicate the true label and columns indicate the predicted label. Diagonal cells are correct predictions. Row-normalized cells show the percentage of a true class assigned to each prediction. Some plotted counts are averaged across seeds.

### Precision, specificity and macro-F1

Precision asks how often a predicted label is correct. Specificity asks how often non-members of a class are correctly excluded. F1 balances precision and recall: `2TP / (2TP + FP + FN)`. Macro-F1 averages class F1 values, giving classes equal weight. These measure different aspects of the same predictions; they are not interchangeable with confidence.

### Confidence intervals and bootstrap

The recorded statistics resample **groups/clusters**, rather than treating every related image as independent, 2,000 times with bootstrap seed 20261004 for the main summaries. The 2.5th and 97.5th percentiles form a 95% interval. A mean across available training seeds is calculated inside the resampling procedure.

For the primary gap, the implementation resamples pooled-test clusters and uses their FracAtlas subset for the decoupled component. This preserves the shared-image linkage while retaining the different endpoints. It is not a guarantee that future hospital performance lies inside the interval.

### Hypothesis and corrected p-value

The pre-specified primary threshold was a gap greater than 0.10. The code estimates how often bootstrap gaps are at or below that threshold, with a plus-one correction. It then applies Holm's adjustment across five primary models. The recorded adjusted value is 0.0025 for all five, and their gap-interval lower bounds exceed 0.10. The recorded project decision rule required support in at least four of five; all five met it.

A p-value is not the probability that the model is wrong, that the hypothesis is true or that implants caused the failure. The finite bootstrap procedure limits numerical resolution.

### OOD detection and AUROC

OOD means “outside the training task/distribution.” The secondary test compares known joints with hand/non-knee leg images using confidence, energy or feature-distance scores. AUROC measures how well a score ranks the two groups: 0.5 is random ranking and 1.0 is perfect ranking. Score direction matters. The implementation labels known images as positive. The probe implementation uses the negative minimum squared Mahalanobis distance to a class centre, so a larger score means closer to a known class.

The live classifier still outputs one of three joint labels for any accepted image. The OOD chart does not add an automatic “unknown” class to the workbench.

### Calibration and ECE

If predictions assigned 80% confidence are correct only half the time, confidence is poorly calibrated. Expected calibration error (ECE) groups confidence into 15 bins and averages the absolute difference between confidence and observed accuracy, weighted by bin size. Lower is better.

Temperature scaling divides logits by a fitted scalar before softmax. It is fitted using designated development/calibration data. It can improve familiar-data calibration without solving source shift.

### Selective prediction and risk–coverage

Sort images by confidence and retain the most confident fraction. Coverage is the fraction kept. The graph shows accuracy on retained predictions. Accuracy at 50% coverage checks the most confident half. AURC summarizes error over coverage; lower is better in the stored implementation. Confidently wrong shifted predictions can make this strategy fail.

### Grad-CAM and entropy

Grad-CAM uses gradients and the pooled network's final convolutional features to produce a coarse activation overlay. Bright regions show activation sensitivity, not proven anatomical reasoning or a detected disease.

The API also calculates normalized entropy: `−sum(p log p) / log(3)`. A spread-out three-class probability vector has higher entropy. Low entropy does not establish correctness under source shift.

## 11. Website, backend and evidence architecture

`Browser → FastAPI → validation → preprocessing → four CPU checkpoints → probabilities / agreement / Grad-CAM → report`.

The active website is `ML3/site`, using generated HTML, CSS, vanilla JavaScript, Lenis and GSAP. `build_site.py` generates pages; `reference_home.html.template` is the active homepage. `reference.css` contains the final reference-aligned visual layer. The X-ray transition module is `assets/js/film.js`.

`api/app.py` handles requests, limits and static pages. `api/infer.py` handles preprocessing, network loading and overlays. Shared Grad-CAM inference is locked because hooks/gradients modify shared model state; it runs off the async event loop. The app has no accounts, database, payment service or external inference API key.

Saved benchmark predictions live in `ML3/artifacts/final/preds`; summary tables and intervals live in `artifacts/final/stats`. `build_data.py` converts them to website JSON. Charts display those saved results; they do not retrain models.

Historical evaluation scripts retain old machine paths and sealed-test guards. Do not rerun test unsealing just to prepare a presentation. The portable saved-results audit verifies existing evidence without opening test images or changing the frozen experiments.

## 12. What has been implemented and checked?

- Four real checkpoints integrated with uploads and sample selection.
- Input type/size checks, bounded request streams, rate limiting and explicit error states.
- Saved-output fallback that is clearly separate from live inference.
- Animated X-ray transitions and a report with image properties and Grad-CAM comparison.
- A source-shift explorer, result charts/table alternatives, literature reading room, contribution comparison and rubric evidence hub.
- A sourced implant-history timeline with original schematic reconstructions; these are not scanned or dimensionally accurate CAD models.
- Nine live saved-specimen predictions reproduced their recorded labels; maximum stored probability difference was 0.00000 in the recorded QA run.
- Ten service regressions passed. A separate audit recomputed all 438 saved BA summary cells and checked checkpoint/manifest hashes, coverage and split grouping.
- Previous full-site checks covered 16 pages at three widths. The current workbench, Robustness and Results fixes passed nine fresh page/viewport checks at 375, 768 and 1280 pixels, with no page or heading overflow. All four Results tabs, exact tables, the Mahalanobis selector after resize and the dimension baseline were checked. Evidence is recorded in `ML3/site/qa/readability-results.json`.

These checks concern implementation/evidence integrity, not clinical validation or guaranteed full marks.

## 13. What remains incomplete?

Clinician verification of provisional knee labels; independent multi-joint replication; stronger training/domain-generalization comparisons; complete full-text literature review; unresolved dataset/figure rights; department formatting and originality requirements; genuine personal contribution logs; clean-environment/container and load testing; full portability of historical training scripts. No hospital adoption, clinical benefit or user feedback has been fabricated.

## 14. An easy presentation order

1. Explain the source-shortcut problem and distinguish joint recognition from implant identity.
2. Show the live Hip specimen, then sample 5 where checkpoints disagree.
3. Explain preprocessing, four training conditions and Grad-CAM without calling it a diagnosis.
4. On Robustness, switch scenarios and choose the dimension-only RF baseline.
5. On Results, explain confidence versus BA versus percentage-point gap; show intervals and the table view.
6. Show the same-image control and knee-label sensitivity before drawing conclusions.
7. Summarize literature and what already existed versus our project contribution.
8. Show tests, artifacts and remaining limitations. Each member states only their real work.

## 15. Start and verify

From PowerShell in `D:\ML Project`, run `start.ps1` and open http://localhost:8000.

```powershell
.\.venv\Scripts\python.exe -X utf8 ML3/site/build_site.py
.\.venv\Scripts\python.exe -X utf8 ML3/site/qa/qa_audit.py
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s ML3/site/qa -p test_service.py -v
.\.venv\Scripts\python.exe -X utf8 ML3/site/qa/audit_saved_results.py
# With the server running:
.\.venv\Scripts\python.exe -X utf8 ML3/site/qa/qa_api.py
```

The original scientific scores were already present in saved artifacts. The current software work verifies and explains them; it does not claim to have generated new training outcomes.

## 16. Where this explanation comes from

Source of implementation details: `ML3/site/api/infer.py`, `app.py`, `scripts/final_eval.py`, `bench2_probes.py`, `final_stats.py` and the website source. Source of numerical values: `ML3/site/data/results.json`, `samples.json`, final statistics and saved-prediction audits. Source of literature: `literaturesurvey.md`, `paper/sections/99_refs.md` and the linked primary records.


### Expanded anatomy model

The live workbench includes a six-region model for Hip, Knee, Shoulder, Hand, Leg and Elbow alongside the four original three-class checkpoints. The expanded model uses independent sigmoid scores and per-region cutoffs. The updated checkpoint uses PediaSHF-DX, ElbowLat and provisional visual labels from the reviewed FracAtlas subset. Inference averages scores across the original image, its horizontal flip and six crops. Cutoffs are chosen on validation data.

Specimen 06 maps to FracAtlas image IMG0000335.jpg and remained in the test split. The original source tag is Leg, the original benchmark label is Knee, and the provisional visual review identifies a lateral elbow. The updated expanded model flags Elbow and Leg on this image. Leg is an extra flag relative to the visual review. In the 14 reviewed FracAtlas holdout images, the updated model flagged 5 of 6 visually reviewed elbows, compared with 2 of 6 for the previous expanded model. False Elbow flags on the other eight images fell from three to one. This small holdout relies on provisional labels.

ElbowLat source and license: https://universe.roboflow.com/ionspace/elbow_lat-lnn0s-pmycd (CC BY 4.0). PediaSHF-DX source: https://doi.org/10.6084/m9.figshare.29322869 (CC BY 4.0).


### Center-crop follow-up

The latest workbench trims 15% from each image edge before applying the expanded model's eight-view scoring. Cutoffs were selected on development validation data. Specimen 06 now flags Elbow alone at 99.7%. In a follow-up on the same 54 BTXRD images, the model flagged Knee on 21 of 37 matching images, up from 8. Extra Elbow flags fell from 33 to 16 of 49. It still flagged all 5 elbow-tagged and 12 shoulder-tagged images. This cohort informed the revision, so the result is exploratory. A fresh independent dataset and separate clinician review are pending.
