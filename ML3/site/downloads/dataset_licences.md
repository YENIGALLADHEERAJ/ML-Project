# Dataset licences and reuse (verified where stated)

| Source | Host / DOI | Licence (how verified) | Redistribution of images | Notes |
|---|---|---|---|---|
| FracAtlas | figshare 10.6084/m9.figshare.22363012 | CC BY 4.0 (figshare API + PMC article) | allowed with attribution | cite Abedeen et al., Sci Data 2023; some images contain logos/text |
| UCI shoulder implants | UCI 10.24432/C5F893 | CC BY 4.0 (UCI page) | allowed with attribution | images were collected from the UW Shoulder Site, manufacturer websites and a UCSF lab (third-party rights not assessed). The Kaggle copy `yasserhessein/shoulder-implant-xray` shows licence **"unknown"** - use the UCI original as the citation |
| Kaggle hip implant (HipXNet) | Kaggle `tawsifurrahman/aseptic-loose-hip-implant-xray-database` | **CC0-1.0** per Kaggle CLI | nominally allowed | the dataset's own metadata shows the images were taken from ~100 published papers and web pages, so CC0 on the compilation may not clear the rights of the underlying figures; **do not republish the images** |
| Gornale knee X-ray | Mendeley 10.17632/t9ndx37v5h.1 (Kaggle copy `tommyngx/digital-knee-xray`: CC BY 4.0) | CC BY 4.0 (Mendeley API; Kaggle CLI) | allowed with attribution | cite Gornale & Patravali 2020 |
| AV-DDH | Mendeley 10.17632/4gvcb6gmh2.2 | CC BY 4.0 on Mendeley; the Roboflow export's `data.yaml` says "license: Private" | **do not redistribute** until the authors/Roboflow project clarify | paediatric images; use only as downloaded by each user |
| OAI-derived knee | Kaggle `shashwatwork/knee-osteoarthritis-dataset-with-severity` (Mendeley 56rmx5bjcr) | CC BY 4.0 (Kaggle CLI; Mendeley API) | **do not redistribute**: derived from the Osteoarthritis Initiative, whose data-use terms may restrict onward sharing | confirm OAI terms with the data providers |
| Emory MRKR / MURA / LERA | not accessed | MRKR: CC BY-SA 4.0 with registration; MURA and LERA: research-use agreements without redistribution | - | would need agreements accepted by the authors |

**What the repository may contain:** code, manifests with file identifiers, split definitions, predictions, statistics, figures that contain no raw patient images. **Figure 8** shows crops of images from the Kaggle hip, UCI shoulder and AV-DDH sources; before publication either obtain permission, replace it with FracAtlas-only examples, or remove it. The website uses only FracAtlas (CC BY 4.0) example images.
