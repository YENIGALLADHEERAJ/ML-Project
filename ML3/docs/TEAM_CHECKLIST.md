# Team checklist

The department's evaluation rubric (PBL 2, PBL 3, Record and Viva) is a **reference for the team**. Marks are awarded by the faculty, and nothing in this project assigns or predicts a mark. This checklist only records where the evidence for each area lives and what the team still has to supply. It is not a self-assessment.

Last updated 12 November 2026.

| # | Area | Where the evidence is | What the team still has to do |
|---:|---|---|---|
| 1 | Literature survey | `literaturesurvey.md` and `Literature_Survey.docx`: 21 works compared, of which 16 are journal or conference papers dated 2022–2026 by identity (the rest are preprints and one older paper). Reading depth is recorded for every reference. | Read the full texts of the papers you may be asked about, confirm venues and versions, and add your own critical comparison. Do not claim full-text reading from abstracts. |
| 2 | Critical analysis and research gap | Survey sections 4 and 5, the manuscript's related-work chapter and the paired border audit. | Be ready to defend why existing work does not answer this exact benchmark question. Avoid claiming to be first, or any causal implant effect. |
| 3 | Relevance and problem formulation | Survey section 6 (research questions, objectives with metrics) and the frozen analysis plan (`docs/FROZEN_analysis_plan.md`). | Explain the relevance as reliable evaluation of imaging models, not diagnosis. |
| 4 | Methodology and system design | README section 5, the frozen plan and report Chapter 4. | Add a truthful dated team timeline if your department asks for one. |
| 5 | Individual contribution and Q&A (PBL 2) | The contribution form below. | Each member supplies their own work and can answer questions on any part of the system. |
| 6 | Working end-to-end demo | The workbench (`start.ps1`), 13 service tests and the static page audit. | Rehearse on the presentation machine and test an upload beforehand. GitHub Pages shows only the static demo mode. |
| 7 | Industry relevance | README section 8 and report Section 5.6 (users, deployment, cost drivers, CPU timing). | Add real user feedback if you have it. Do not invent adoption, revenue or performance. |
| 8 | Testing, metrics and results | `qa/` tests, the saved-result audit, frozen statistics and baseline charts. | Present the evidence with its limitations. Load testing and clinical validation were not done. |
| 9 | Objectives and innovation | README section 3, the shortcut probe, the border audit and the source-controlled evaluation. | Map your department's approved PBL 2 objective sheet to the evidence. That sheet was not available to the project. |
| 10 | Individual demo and Q&A (PBL 3) | `docs/DEMO_AND_VIVA.md` and the module map. | Each member demonstrates a workflow and explains all modules. |
| 11 | Report structure and formatting | `ML3/report/OrthoTrace_Project_Report.docx`, built in the department template (build script alongside). | Fill the cover page (names, registration numbers, guide), update fields in Word (contents and lists), and add any required certificates or signatures. |
| 12 | Technical content across phases | Report Chapters 1–8 and the appendices. | Attach your contribution log and final screenshots. |
| 13 | References and originality | Numbered references that match across the survey, manuscript and report, with a verification registry. | Run your institution's similarity report and finish the full-text checks. |
| 14 | Technical understanding | `docs/DEMO_AND_VIVA.md`. | Explain algorithms, preprocessing, confounding, metrics, bootstrap and limitations unaided. |
| 15 | Whole-project answers | Module map and cross-module questions in the viva guide. | Rotate questions across all members rather than dividing knowledge by module. |
| 16 | Personal contribution and learning | The contribution form below. | Each student writes their own, using real tasks, challenges and lessons. |

## Measurable objectives mapped to evidence

- Quantify the pooled-to-decoupled generalisation gap: saved `gap.csv`; all five primary hypotheses supported at the recorded corrected significance level. This is a study finding.
- Test anatomy-free shortcuts: dimensions-only RF 0.9713 pooled → 0.3333 decoupled; metadata RF 0.9605 → 0.3333. The workbench's shortcut probe reproduces this pattern on development data (0.99 → 0.31).
- Characterise held-out sources and reliability: leave-one-source-out, ECE, OOD AUROC and risk–coverage charts.
- Demonstrate actual checkpoint behaviour: four live checkpoints, saved parity, pooled Grad-CAM and explicit input warnings.
- Establishing clinical validity or causal implant dependence: **not achieved and not claimed**.

## Contribution evidence form (each student completes independently)

Name / registration number:

Tasks actually performed, dates and supporting file, commit or notebook evidence:

Design decision personally made and its trade-off:

Bug or experimental issue personally investigated:

Module outside own work that the student can now explain:

What was learned; what assistance and tools were used:

Do not fill these fields using guessed team roles. The department rubric has four student columns while `site/parts.py` lists five names; confirm the actual evaluation team.
