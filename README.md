# NCKH_DATA

Data pipeline for: **How AI-Driven Personalization Shapes Customer Engagement in
Omnichannel Retail: A Privacy-Aware AI Agent Approach**

Data cleaning · Cronbach's α · EFA · CFA/HTMT/PLS-SEM · t-test · ANOVA

## Start here

Read [`CLAUDE.md`](./CLAUDE.md) before running or editing anything in `src/`. It is
the operating manual for this pipeline: exact column names, exclusion rules, known
bugs already fixed, and the governance rules (hypothesis numbering, naming locks,
what belongs to Study 1 vs Study 2) that the code must not silently drift from.

The governing specification is [`docs/Theoretical_Foundations_v2_4.docx`](./docs/Theoretical_Foundations_v2_4.docx)
(single source of truth for theory, hypotheses H1–H7b, and the measurement register)
and [`docs/Master_Codebook_v2_0.docx`](./docs/Master_Codebook_v2_0.docx) (variable-level
bridge between the Qualtrics instrument and this code). Where code and docs disagree,
the docs win — fix the code, not the doc, unless a governance decision changes.

## ⚠️ Data handling — read before committing any CSV

**Never commit an original raw Qualtrics export.** It contains `IPAddress` and
precise `LocationLatitude` / `LocationLongitude` for every respondent — personal data
under **Law 91/2025/QH15 Art. 2**, the statute this project studies. This repo being
Private reduces exposure but is not a substitute for de-identification (collaborator
access changes, an accidental visibility toggle, no audit trail).

**Before committing a new raw export:**

```bash
python src/strip_pii.py --input <original_export.csv> --output data/raw/<name>.csv
```

This blanks `IPAddress`, `LocationLatitude`, `LocationLongitude`,
`RecipientEmail/FirstName/LastName`, and `ExternalReference` while keeping every
column the pipeline actually uses untouched, and keeps the file readable by
`_qualtrics_io.py` as a raw export. Keep your original, non-de-identified export in
`data/raw/_local/` (gitignored) for your own local analysis runs if you want — just
never `git add` it.

`data/processed/` and `outputs/` are gitignored entirely — they're script-generated
and reproducible from a committed de-identified raw export, so there's no reason to
version them.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`factor_analyzer` (used by `03_reliability_efa.py`) needs `scikit-learn<1.6` — already
pinned in `requirements.txt`.

For `07_plssem_bridge.R` / `run_plssem.py` (main-collection PLS-SEM only), install R
separately and then, in an R console:

```r
install.packages(c("seminr", "cSEM", "pwr"))
```

## Repo layout

```
NCKH_DATA/
├── CLAUDE.md                   # pipeline operating manual — read first
├── README.md                   # this file
├── docs/                       # governing documents (TF v2.4, Master Codebook)
├── requirements.txt
├── data/
│   ├── raw/                    # de-identified exports only — see Data handling
│   │   └── _local/             # gitignored: your original exports for local use
│   └── processed/              # gitignored: script output
├── src/
│   ├── _config.py               # single source of truth: columns, item lists, thresholds
│   ├── _qualtrics_io.py         # raw-export loader/normalizer
│   ├── strip_pii.py             # de-identify a raw export before committing
│   ├── 00_generate_synthetic.py
│   ├── 01_clean.py              # exclusions + soft flags
│   ├── 02_descriptives.py       # demographics, cell balance
│   ├── 03_reliability_efa.py    # Cronbach's alpha, AIP/REL EFA (pilot only)
│   ├── 04_manipulation_check.py # MC_AIP / MC_DISC t-tests, Cohen's d gate
│   ├── 05_anova_h3.py           # two-way ANOVA — sole confirmatory test of H3
│   ├── 06_power_analysis.py     # OD-2 (closed) — power for beta_M1 / beta_M2
│   ├── 07_plssem_bridge.R       # seminr PLS-SEM model (main collection only)
│   └── run_plssem.py            # rpy2 bridge orchestrator
└── outputs/
    ├── tables/                  # gitignored: every script writes results here
    └── figures/                 # gitignored
```

## Typical run (pilot)

```bash
python src/strip_pii.py --input <your_export.csv> --output data/raw/pilot_deidentified.csv
python src/01_clean.py --input data/raw/pilot_deidentified.csv --phase pilot
python src/02_descriptives.py --input data/processed/pilot_clean.csv --phase pilot
python src/03_reliability_efa.py --input data/processed/pilot_clean.csv
python src/04_manipulation_check.py --input data/processed/pilot_clean.csv
```

`05_anova_h3.py`, `06_power_analysis.py`, and the PLS-SEM bridge (`07`/`run_plssem.py`)
are for **main collection (n ≥ 400) only** — do not run them confirmatorily on pilot
data (see `CLAUDE.md` §7).

## Current status

See `CLAUDE.md` §7 ("Before running on real data — checklist") for what's done and
what's still open. As of the last pipeline run: reliability is strong across all
constructs (α = 0.82–0.95), REL4's exclusion from the measurement model is corroborated
on real pilot data (cross-loads 0.44/0.48 on both factors when included), and both
manipulation checks clear the d ≥ 0.50 gate.
