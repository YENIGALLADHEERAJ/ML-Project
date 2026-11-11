# Evaluation demonstration and viva

## Eight-minute demonstration

Start OrthoTrace with `start.ps1`. Open the workbench and check that it says **Live inference**. Run the two specimens before presenting so the model weights are loaded.

1. **0:00–0:45 · State the question.** Can a model recognize the same anatomy when the image source changes? Explain that the project combines anatomy recognition with source-controlled evaluation.
2. **0:45–2:30 · Show a successful prediction.** Open [specimen 02](http://127.0.0.1:8000/demo.html?sample=2). The expanded model flags Hip and the four benchmark checkpoints agree. Walk through image selection, grayscale preprocessing, inference and the scores. Drag the Grad-CAM slider to show which image regions influenced the pooled benchmark prediction.
3. **2:30–4:30 · Show a failure and the fix.** Open [specimen 06](http://127.0.0.1:8000/demo.html?sample=6). Explain the conflict between the source tag (Leg), original benchmark label (Knee) and provisional visual review (Elbow). The latest expanded model flags Elbow alone at 99.7%. The previous version also flagged Leg. Describe the reviewed labels, second elbow source, center crop and averaging across views. The image stayed in the test split.
4. **4:30–6:00 · Show why source matters.** Open [the shortcut results](http://127.0.0.1:8000/results.html#t-short). The dimensions-only random forest fell from 97.1% pooled balanced accuracy to 33.3% in the source-decoupled test. Explain balanced accuracy as the mean of the per-class recalls.
5. **6:00–7:00 · Explain the algorithm choice.** Open [the algorithm comparison](http://127.0.0.1:8000/methodology.html#algorithm-comparison). RBF SVM led the classical three-class source holdout at 56.5% on 47 validation images. The separately trained EfficientNet-B3 handles six regions in the live demo.
6. **7:00–8:00 · State the limits.** Open [the independent dataset check](http://127.0.0.1:8000/evaluation.html#external-check). The model flagged all 5 elbow-tagged BTXRD images and also flagged Elbow on 33 of 49 other images. The follow-up on the same cohort raised Knee from 8 to 21 of 37 and reduced extra Elbow flags from 33 to 16 of 49. Explain that we froze the cutoffs before testing and that this check uses dataset tags. The separate clinician review is pending. Each teammate should describe their actual contribution.

If the API is unavailable, use the workbench's precomputed samples and say the outputs were saved from the model. An uploaded image needs the API.

## Likely viva questions and answers

**What is the actual research question?** Whether pooling orthopaedic public datasets overstates joint-recognition generalization when joint labels are confounded with dataset source. The product exposes that evaluation problem interactively.

**What is predicted?** Exactly one of Hip, Knee or Shoulder. Softmax always distributes probability across those three labels, even for an out-of-scope input. No fracture, disease, implant brand or patient outcome is predicted.

**Why does pooling produce misleadingly high scores?** Most sources supply one joint. Recognizing acquisition style, image size, borders or source-specific features can therefore recover the joint label without robust anatomy recognition. A random pooled split preserves this association in train and test.

**How is the decoupled test different?** FracAtlas contains all three target joints. E2 excludes it during training and evaluates its held-out test subset. The conventional E0 model and E2 model are separate checkpoints with the same architecture, not one network whose training is changed in the browser.

**How many images are involved?** The target benchmark contains 4,427 images from six sources. The sealed target test partition has 657 rows; the FracAtlas decoupled test subset has 55, comprising 26 Hip, 14 Knee and 15 Shoulder.

**What is the inference architecture?** FastAPI receives raw image bytes; Pillow decodes them in memory; OpenCV resizes greyscale to 160×160; intensity is replicated across three channels and ImageNet-normalized. Four EfficientNet-B3 networks with three-output classifier heads run on CPU. The pooled network additionally produces Grad-CAM.

**Why ImageNet normalization on a greyscale image?** The study uses ImageNet-pretrained networks with three-channel inputs. Replicating greyscale and applying the same recorded normalization preserves the study preprocessing. It is not evidence that this preprocessing is optimal.

**What is balanced accuracy?** The mean of per-class recall. It gives equal weight to each class despite class imbalance. Three-class chance is approximately 1/3. On a single-class held-out source, the observed-class mean recall reduces to that class's recall, so interpret the task context.

**Why use random forests on image dimensions?** They are anatomy-free negative-control baselines. If width, height and aspect alone nearly solve the pooled task but fall to chance under decoupling, the pooled score can be explained in part by non-anatomical information.

**What are the main results?** Saved primary-model pooled balanced accuracies are approximately 0.993–1.000 and source-decoupled values 0.498–0.686. The gaps are approximately 0.31–0.50. These are study results from stored artifacts; the new UI did not create new scientific outcomes.

**What did this session independently verify?** All 438 saved balanced-accuracy summary cells from per-image predictions; manifest and checkpoint hashes; group split separation; coverage and labels; nine live sample predictions and Grad-CAM; 10 API boundary/validation regressions; browser layouts and key interactions. It did not retrain networks or clinically validate labels.

**What do confidence intervals and Holm correction do?** The study uses a clustered paired bootstrap to account for grouping and uncertainty in comparisons. Holm correction controls family-wise multiplicity across five primary hypotheses. A confidence interval quantifies sampling uncertainty under those assumptions, not future hospital performance.

**Why is the prediction's 95% confidence not 95% correctness?** It is the maximum raw softmax score among three classes. Under distribution shift probabilities may be poorly calibrated. The study's ECE and selective-prediction analyses examine this failure.

**Does Grad-CAM prove the model uses anatomy?** No. It weights feature maps using gradients for a target class. It visualizes activation sensitivity at low spatial resolution and cannot establish causal reasoning. Bright regions may reflect correlated features.

**Why a lock and a worker thread?** A single cached model is shared. Grad-CAM installs hooks and computes gradients; overlapping requests could interfere. A lock serializes those operations. A worker thread prevents CPU inference from blocking the async event loop, allowing lightweight endpoints to remain serviceable. This does not establish high concurrency capacity.

**Where is the database?** There is none in the active demo. Public data, precomputed results and checkpoints are files; uploaded image bytes remain in memory for the request. This architecture fits an evaluation demo without accounts or persistent records.

**How is offline mode honest?** Health detection explicitly changes the label to saved/precomputed mode and uploaded files are not answered from the sample library. With the API online, clicking a sample now sends its image to the actual prediction endpoint.

**Why not claim implant detection or causality?** Implant presence is correlated with sources K and U. The experiment changes dataset source, not implant presence independently. Thus it cannot isolate a causal implant effect or provide an implant-detection model.

**What is the biggest validity limitation?** The single decoupled source and provisional AI-assigned knee labels. The hip/shoulder-only sensitivity gap is narrower. The BTXRD check adds an independent dataset and exposes high false Elbow flagging. Separate clinician review of the project labels is still pending.

**Is it novel?** The claim is a focused source-controlled orthopaedic benchmark and integrated explanation, not invention of shortcut learning, a new neural architecture, or a first-ever result. Related work must be acknowledged.

**How would deployment scale?** Run a container behind HTTPS with explicit resource and request limits. More worker processes require additional model memory; a bounded queue and shared limiter are needed before multi-user scaling. Docker and throughput were not validated here.

**What is your personal contribution?** Answer using your own evidence form in RUBRIC_AUDIT.md. Do not recite an assigned role that you did not perform. Explain assistance and what you personally verified or learned.
