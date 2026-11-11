# Clinician-review protocol: FracAtlas knee labels

**Purpose.** In the study, 94 FracAtlas images were labelled "knee" by an AI assistant (visual inspection of 200 randomly sampled images from the dataset's "leg" category; 101 judged non-knee, 5 ambiguous). The labels are unverified. They matter because (a) the knee class carries much of the decoupled-test error (post-hoc analysis: gap 0.10-0.34 without it) and (b) 14 of the 94 are in the sealed test set. This protocol obtains independent clinician labels so the dependence on the AI labels can be quantified. **It is a sensitivity analysis; the frozen primary result (original labels) is not replaced.**

## 1. Reviewers
- Two independent reviewers: board-certified radiologists or orthopaedic surgeons/fellows (any musculoskeletal-experienced clinician with routine knee/hip/shoulder radiograph reading). Record role and years of experience.
- One adjudicator (same qualification) who sees only the images on which the two reviewers disagree or one marked "unclear". Reviewers and adjudicator must be independent of each other's labels.
- No reviewer should be an author of the study, or if so, must label before seeing any results (disclose).

## 2. Materials (all in `clinician_review/packet/`)
230 FracAtlas images (CC BY 4.0) in random order with blind IDs R001-R230: the 200 sampled "leg" images + 30 attention-check images (15 hip-only, 15 shoulder-only per the dataset's own region flags). Reviewers see **no** AI labels, model outputs, source names, file names or test/train status. The key file lives in `clinician_review/private/` and must not be shared with reviewers.
Tool: open `packet/review_tool.html` locally in a browser (offline; progress saved in the browser; exports a CSV). Time: about 30-45 minutes.

## 3. Labelling rules
For each image choose the **main subject region**: (1) Knee - the femorotibial joint is a main subject of the image (AP, lateral, bilateral, long-leg with the knee included; implants allowed); (2) Hip/pelvis; (3) Shoulder; (4) Ankle/foot; (5) Lower leg or thigh without knee, ankle or hip joint; (6) Other; (7) Unclear/unreadable. Also tick "metal implant/hardware visible" when present. Images may be windowed/zoomed in the tool; do not use outside information.

## 4. Analysis plan (fixed before labels are collected)
1. Reliability: percent agreement and Cohen's kappa for knee vs non-knee (images labelled "unclear" by either reviewer excluded from kappa), 7-class kappa, accuracy on the 30 attention checks (a reviewer below 27/30 is replaced), kappa for hardware.
2. Consensus: both reviewers agree -> that label; otherwise the adjudicator's label; "unclear" after adjudication -> excluded.
3. AI vs consensus on the 200 leg images: confusion matrix, precision/recall of the AI "knee" label, kappa. Pre-stated expectation: if kappa < 0.80 the knee-dependent results are described as label-sensitive in the abstract.
4. Impact on the frozen analysis (script `analysis/rerun_primary_with_consensus.py`): sealed-test FracAtlas images whose AI "knee" label is not confirmed are removed; the primary gap (clustered paired bootstrap, B = 2000) is recomputed from the saved predictions and reported **alongside** the original. Models are **not** retrained and no threshold is changed. If > 20% of the AI-knee training images are unconfirmed, retraining with consensus labels is reported as a separate, clearly labelled extension.
5. Reporting: Methods paragraph (reviewers' roles, blinding, number of images, kappa), supplementary table of AI-vs-consensus, and the sensitivity result in Section 16.1.

## 5. Documentation to keep
Signed reviewer declaration (below), the three exported CSVs, `output/review_summary.json`, `consensus_labels.csv`, `changed_test_rows.csv`, the date and software version of the tool. Reviewers receive no per-image feedback until labelling is complete.

## 6. Reviewer declaration (copy into each reviewer's file)
I reviewed the images independently, without access to model outputs, prior labels or other reviewers' labels. Name/role/institution: ______  Years of experience: ______  Conflicts of interest: ______  Date: ______

## 7. Commands after labelling
```
python clinician_review/analysis/analyze_clinician_review.py R1_labels.csv R2_labels.csv [adjudicator_labels.csv]
python clinician_review/analysis/rerun_primary_with_consensus.py
```
