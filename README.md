# NCKH_DATA

Data pipeline for: **How AI-Driven Personalization Shapes Customer Engagement in
Omnichannel Retail: A Privacy-Aware AI Agent Approach**

Data cleaning · Cronbach's α · EFA · CFA/HTMT/PLS-SEM · t-test · ANOVA

## Start here

Read [`CLAUDE.md`](./CLAUDE.md) before running or editing anything in `src/`. It is
the operating manual for this pipeline: exact column names, exclusion rules, known
bugs already fixed, and the governance rules (hypothesis numbering, naming locks,
what belongs to Study 1 vs Study 2) that the code must not silently drift from.

The governing specification is `docs/Theoretical_Foundations_vN_updated.docx` (single
source of truth for theory, hypotheses H1–H7b, and the measurement register) and
`docs/Master_Codebook_vN_updated.docx` (variable-level bridge between the Qualtrics
instrument and this code) — **both docs get re-issued under a new filename with a
higher N periodically; always check `docs/` for the current highest N** rather than
trusting a filename pinned here, which will go stale. As of 2026-09-11 the current
pair is `Theoretical_Foundations_v2_11_updated.docx` (self-titled "Version 2.9") and
`Master_Codebook_v2_6_updated.docx`. Where code and docs disagree, TF prevails on
substance — fix the code, not the doc, unless a governance decision changes.

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

`data/processed/` and `outputs/` are *intended* to be gitignored entirely — they're
script-generated and reproducible from a committed de-identified raw export, so
there's no reason to version them. **In practice, several files under both were
committed before that `.gitignore` rule existed and are still tracked** — see
"Known PII exposure" below before assuming those directories are safe.

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
├── docs/                       # governing documents (TF, Master Codebook — check for highest vN)
├── requirements.txt
├── data/
│   ├── raw/                    # de-identified exports only — see Data handling
│   │   └── _local/             # gitignored: your original exports for local use
│   └── processed/              # should be gitignored script output (regenerate, don't
│                                # commit) — but see "Known PII exposure" below: some
│                                # files here are currently tracked in git anyway
├── src/
│   ├── _config.py               # single source of truth: columns, item lists,
│   │                             # thresholds, PII_COLUMNS
│   ├── _qualtrics_io.py         # raw-export loader/normalizer
│   ├── strip_pii.py             # de-identify a RAW export before committing
│   ├── 00_generate_synthetic.py
│   ├── 01_clean.py              # exclusions (missing/duplicate/straightlining),
│   │                             # ITT-based manipulation-check reporting, construct
│   │                             # scores, PII stripping on the CLEANED output too
│   ├── 02_descriptives.py       # demographics, cell balance, construct descriptives
│   ├── 03_reliability_efa.py    # Cronbach's alpha, CR/AVE, HTMT, AIP/REL EFA,
│   │                             # ENG within-dimension reliability (pilot only)
│   ├── 04_manipulation_check.py # MC_AIP / MC_DISC t-tests, Cohen's d gate
│   ├── 05_anova_h3.py           # two-way ANOVA — sole confirmatory test of H3
│   ├── 06_power_analysis.py     # OD-2 (closed) — power for beta_M1 / beta_M2
│   ├── 07_plssem_bridge.R       # seminr PLS-SEM model (main collection only)
│   └── run_plssem.py            # rpy2 bridge orchestrator
└── outputs/
    ├── tables/                  # should be gitignored (regenerate, don't commit) —
    │                            # same caveat as data/processed/ above
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

See `CLAUDE.md` §7 for what's done and what's still open — it's the living record,
this section is just a pointer so it doesn't rot the way the paragraph it replaced
did (REL4 is no longer excluded from the measurement model; that reflected a since-
reversed Amendment A-9 decision). As of 2026-09-11: pipeline runs end-to-end on real
pilot data (`data/raw/pilot_real.csv`, a live/growing export); reliability is strong
across constructs; AIP↔REL discriminant validity (HTMT) is an open concern under
active investigation; the MC_AIP manipulation check is borderline/failing the
|d|≥0.50 gate depending on checkpoint and uses an Intention-to-Treat (ITT) design
(report-only, no individual-level exclusion) as of the same date — see `CLAUDE.md`
§6.1 for why.

## ⚠️ Known PII exposure in git history (as of 2026-09-11)

`data/processed/*.csv` and most of `outputs/tables/*.csv` are declared in
`.gitignore` but were tracked in git **before** that rule was added, so the ignore
rule doesn't retroactively untrack them — several of those files (e.g.
`pilot_clean.csv`) carry real respondent `IPAddress`/`LocationLatitude`/
`LocationLongitude` values and are sitting in git history right now. `01_clean.py`
was fixed (2026-09-11) to strip those columns before writing any future
`{phase}_clean.csv`, which stops the leak going forward, but does **not** remove
what's already committed. Untracking (`git rm --cached`) and, if this repo has ever
been pushed anywhere, scrubbing history (e.g. `git filter-repo`) are still open —
deliberately not done automatically, since a history rewrite is destructive and
needs your explicit go-ahead (and coordination with any remote/collaborators).
