# OrthoTrace

OrthoTrace is a radiograph anatomy and model-evaluation workbench. It lets imaging researchers and dataset reviewers compare predictions on the same de-identified X-ray, investigate disagreements, and export a review record containing scores without image pixels or filenames.

## Run locally

With Python 3.11 on Windows, run these commands from the repository root.

```powershell
.\setup.ps1
.\start.ps1
```

Open [OrthoTrace](http://127.0.0.1:8000/) or [run specimen 06](http://127.0.0.1:8000/demo.html?sample=6). For a container, see [deployment](ML3/site/DEPLOY.md).

## What the project adds

- A live six-region anatomy model, four source-controlled benchmark checkpoints, and a pooled Grad-CAM overlay.
- A paired border audit that compares interventions on the same images, plus a source-holdout benchmark and classical-model comparison.
- A browser-generated review record for sharing model scores and disagreement during research and dataset quality review.
- A documented failure and revision on specimen 06, with baseline and follow-up BTXRD results available in the evidence page.

On the same 54 BTXRD images, the center-crop revision increased knee flags on matching images from 8 to 21 of 37 and reduced Elbow flags on other tagged images from 33 to 16 of 49. It retained all five elbow-tagged and twelve shoulder-tagged detections. The revision followed inspection of this cohort and needs a fresh external evaluation. The clinical usefulness of the project remains unverified.

## Check the release

```powershell
.\.venv\Scripts\python.exe -X utf8 ML3/site/qa/qa_audit.py
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s ML3/site/qa -p test_service.py -v
.\.venv\Scripts\python.exe -X utf8 ML3/site/qa/qa_api.py
```

The API test expects the service on port 8000. Rebuild the pages with `python ML3/site/build_site.py`. The release includes the live checkpoints, public example images, source files, and saved evaluations. Large training datasets and the full training workspace are maintained separately. See [dataset credits](ML3/site/downloads/dataset_licences.md) and [the viva guide](ML3/docs/DEMO_AND_VIVA.md).
