# Rubric audit

Source: `D:/ML Project/Project_Rubric_PBL2_PBL3_Viva_Record.xlsx`, read on 10 November 2026. Total: PBL 2 = 20, PBL 3 = 20, Record = 10, Viva = 10. Status describes evidence, not an awarded mark or a guarantee.

| # | Criterion | Max | Evidence and status | Required for excellent |
|---|---|---:|---|---|
| 1 | Literature depth and coverage | 6 | Partial: existing numbered references and new thematic comparison matrix. Recent papers include abstract-only material and preprints. | Confirm at least 15 relevant journal/conference papers within the evaluator's five-year window; read and compare methods, datasets and findings. |
| 2 | Critical analysis and gap | 4 | Supported: pooled evaluation confounds source with anatomy; source-decoupled comparison and anatomy-free baselines address the gap. Existing feasibility/prior-art report and matrix explain scope. | Defend why existing work does not answer this exact benchmark question; avoid claiming first or causal implant evidence. |
| 3 | Relevance and formulation | 4 | Supported: measurable H1 gap >0.10; balanced accuracy, source-held-out protocols and reliability analyses are defined in frozen plan. | Explain societal relevance as reliable evaluation, not diagnosis. |
| 4 | Methodology and design | 3 | Supported: architecture, grouped splits, models, metrics, compute limits and freeze documented. | Add a truthful dated team timeline if the evaluator requires one. |
| 5 | Individual contribution / Q&A | 3 | Pending personal evidence. | Each member supplies own work and answers across the system. |
| 6 | End-to-end demo | 6 | Supported locally: live API and browser specimen workflow; all nine checkpoint outputs reproduced; static/regression checks. | Rehearse on evaluation hardware; verify startup and upload immediately beforehand. Clean-install/container testing remains separate. |
| 7 | Industry relevance | 4 | Supported discussion: researchers and ML evaluators; local CPU inference; deployment, cost drivers and scaling limits in DELIVERY.md. | Actual user feedback if available; do not invent adoption, revenue or performance. |
| 8 | Testing, metrics and results | 4 | Supported: 10 service regressions, nine-sample live parity, baseline charts, 438 saved summary cells recomputed, checkpoint/split audit. | Present systematic evidence and limitations; load and clinical validation are absent. |
| 9 | Objectives and innovation | 3 | Partial: frozen hypothesis supported in saved results; source-controlled evaluation and integrated workbench are the contribution. | Map the team's original approved PBL 2 objectives to evidence; original approved objective sheet was not supplied. Clinical verification remains pending. |
| 10 | Individual integrated demo/Q&A | 3 | Pending personal assessment. | Every member demonstrates a workflow and explains all modules. |
| 11 | Department report formatting | 3 | Unverified: manuscript and docs exist, department template missing. | Supply template, front matter, signatures, chapter requirements and formatting rules. |
| 12 | All technical phases | 5 | Substantial evidence: study reports, plan, methodology, implementation, saved results, caveats, delivery and future work. | Combine into the department's required record; attach truthful contribution log and final screenshots. |
| 13 | Citations and originality | 2 | Partial: reference verification registry and disclosures exist; primary-source spot checks made. | Finish full-text checks, consistent IEEE/APA style and institution-approved similarity report. |
| 14 | Technical understanding | 4 | Preparation supplied in DEMO_AND_VIVA.md; actual understanding must be demonstrated. | Explain algorithms, preprocessing, confounding, metrics, bootstrap and limitations unaided. |
| 15 | Whole-project answers | 4 | Module map and cross-module questions supplied. | Rotate questioning across all members; do not divide knowledge by module only. |
| 16 | Personal contribution and learning | 2 | Pending real student statements. | Give specific tasks, challenges, evidence and lessons without attributing generated work falsely. |

## Measurable objectives mapped to evidence

- Quantify pooled-to-decoupled generalization gap: saved `gap.csv`; all five primary hypotheses supported at the recorded corrected significance level. This is a study finding, not a new result produced by this UI work.
- Test anatomy-free shortcuts: dimension-only RF 0.9713 pooled → 0.3333 decoupled; metadata RF 0.9605 → 0.3333. This is a relevant baseline, not a direct accuracy competition against unrelated clinical tasks.
- Characterize held-out sources and reliability: leave-one-source-out, ECE, OOD AUROC and risk–coverage charts remain available.
- Demonstrate actual checkpoint behaviour: four live checkpoints, saved parity, pooled Grad-CAM and explicit input warnings.
- Establish clinical validity or causal implant dependence: **not achieved and not claimed**.

## Contribution evidence form — each student completes independently

Name / registration number:

Tasks actually performed, dates and supporting file/commit/notebook/review evidence:

Design decision personally made and its trade-off:

Bug or experimental issue personally investigated:

Module outside own work that the student can now explain:

What was learned; what assistance/tools were used:

Do not fill these fields using guessed team roles. The supplied rubric has four student columns while `site/parts.py` lists five names; confirm the actual evaluation team with the department.
