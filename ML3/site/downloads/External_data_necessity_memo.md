# Are MURA, LERA or MRKR scientifically necessary?

**Short answer: not for the central claim; one of them (LERA) would be a valuable independent replication, and MRKR would address a different question (implants). None should be added merely to strengthen the results.**

## What the current claim needs
Central claim (H1): pooled evaluation of public joint recognition overstates generalisation to a source where joint ≠ source. It is supported by a pre-specified endpoint (5/5 primary models; gaps 0.31-0.50, CI lower bounds 0.23-0.40 against a 0.10 threshold), by the anatomy-free baselines (chance when decoupled), by the implant-source holdouts, and by the same-source control (1.000 vs 0.50-0.69 on identical images). These do not depend on additional sources. The weakness is not "too few datasets" but the **provisional FracAtlas knee labels** and the **single 55-image decoupled test set**; the first is fixed by clinician verification, the second is a limitation to state.

## What each dataset would and would not add
| Dataset | Access | What it uniquely offers | Necessary? | Risk |
|---|---|---|---|---|
| **LERA** (Stanford; hip, knee, ankle, foot; 182 patients) | agreement + registration; no redistribution | the only candidate with **hip and knee from one institution with study-level body-part labels** -> a second, independent decoupled test bed that does not rely on our knee labels | **Useful, not necessary.** Best candidate for an *independent replication* | small (182 patients); no shoulder; "hardware" is an abnormality class, not a joint label |
| **MRKR** (Emory; 503,261 knee radiographs; `arthroplasty` flag) | registration; 2.3 TB, subsample | the only route to an **implant-matched contrast within one source** (knee with vs without arthroplasty), the missing piece for the implant-confound question | **Not for H1.** Needed only if the paper wants to test the implant hypothesis rather than state it as a plausible confound | answers a different question (knee only; no joint contrast); large effort |
| **MURA** (Stanford; shoulder + elbow, humerus, wrist, hand...) | agreement; no redistribution | real clinical shoulder source; elbow/humerus/wrist as a **clinical unknown-joint pool** for OOD | **Optional.** Strengthens the secondary OOD analysis and gives a second shoulder source | upper-limb only: no decoupled hip/knee test; the dataset has been used for body-part transfer work |

## Recommendation
1. **Do now:** clinician verification of the knee labels (protocol in `clinician_review/PROTOCOL.md`), report the original and consensus-label results side by side, and state that the decoupled test rests on one source (n = 55).
2. **Do not** add datasets to the frozen analysis. Any new data would be a **pre-specified extension** with its own frozen plan, its own sealed split and the same reporting standard, and every result (including a null or opposite one) would be reported.
3. If resources allow one extension, choose **LERA** (independent replication of H1 with reliable joint labels). Choose **MRKR** only if the research question is expanded to implants. MURA only for the OOD pool.
4. Access is a user action: the agreements/registrations (Stanford AIMI for MURA and LERA; `data.hitilab.com/auth/register` for MRKR) must be accepted by the authors; the assistant must not do so.
