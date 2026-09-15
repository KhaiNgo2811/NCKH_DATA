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

## How to run the pipeline

### 1. Get a raw export in place

`pilot_real.csv` is a **live, growing** Qualtrics export — every re-export can
change both the row count and (occasionally) the column set (two new
demographic items, `LOC` and `REF`, were added mid-collection; see `CLAUDE.md`
§9). Two ways to get a new export in:

```bash
# If you have a fresh raw export with PII (IPAddress/location/recipient info):
python src/strip_pii.py --input <your_export.csv> --output data/raw/pilot_deidentified.csv

# If you're just re-running against the export already in data/raw/pilot_real.csv:
# nothing to do here, skip to step 2.
```

### 2. Clean + label (`01_clean.py`) — always run this first

```bash
python src/01_clean.py --input data/raw/pilot_real.csv --phase pilot
```

This single command:
- Applies the 3 hard-drop exclusions (missing data, duplicate response
  pattern, straightlining — see `CLAUDE.md` §6.1).
- Prints a **before-filtering breakdown** of MC_AIP (genuine miscomprehension
  vs. dropout) and, after filtering, the **group-level manipulation-check
  evidence** (Welch's t + Cohen's d for both MC_AIP and MC_DISC, plus a
  supplementary AIP_mean composite check) — report-only, excludes nobody
  (Intention-to-Treat design, `CLAUDE.md` §6.1).
- Adds `{construct}_mean` columns (AIP_mean, REL_mean, ...) and a
  `flag_extreme_reverser` column (robustness-check flag, never a filter).
- Adds `collection_phase` (`pre_LOC`/`post_LOC`) and `sample_role`
  (`pilot`/`main`) — an **administrative** label based on when the `LOC` field
  was added to the instrument, **not** a measurement-readiness boundary (see
  `CLAUDE.md` §9). Prints and writes a checkpoint
  (`outputs/tables/collection_checkpoint_log.csv`) with n and AIP_COND
  breakdown by both.
- Strips PII columns before writing the output.

Output: `data/processed/pilot_clean.csv` + `outputs/tables/pilot_exclusion_log.csv`.

### 3. Descriptives, reliability, manipulation check

```bash
python src/02_descriptives.py --input data/processed/pilot_clean.csv --phase pilot
python src/03_reliability_efa.py --input data/processed/pilot_clean.csv
python src/04_manipulation_check.py --input data/processed/pilot_clean.csv
```

- `02_descriptives.py` → cell balance (AIP_COND × DISC_COND), demographic
  summary (including `LOC`/`REF`), and construct-level mean/SD.
- `03_reliability_efa.py` → Cronbach's α, outer loadings, CR/AVE, HTMT
  (ENG excluded from the pooled tables per Amendment A-12, gets its own
  within-dimension table instead), and the AIP/REL EFA cross-loading check.
- `04_manipulation_check.py` → the pre-registered gate (|d| ≥ 0.50 for both
  MC_AIP and MC_DISC).

### 4. Optional: filter by `sample_role` (pilot vs. main subset)

`03_reliability_efa.py` and `04_manipulation_check.py` both accept
`--sample-role {pilot,main,all}` (default `all` = no filtering, identical to
omitting the flag). This runs the exact same formulas/thresholds on a subset
of rows and writes to a `_{role}`-suffixed filename, so it never overwrites
the unfiltered result:

```bash
python src/04_manipulation_check.py --input data/processed/pilot_clean.csv --sample-role main
python src/03_reliability_efa.py --input data/processed/pilot_clean.csv --sample-role main
```

Remember: `sample_role="main"` is a bookkeeping label, not a governance
sign-off that main collection has formally opened (`CLAUDE.md` §9) — a PASS
on a `main`-filtered subset does not by itself mean the checklist in
`CLAUDE.md` §7 is satisfied.

### 5. Main-collection-only scripts

`05_anova_h3.py`, `06_power_analysis.py`, and the PLS-SEM bridge (`07`/`run_plssem.py`)
are for **main collection (n ≥ 400) only** — do not run them confirmatorily on pilot
data (see `CLAUDE.md` §7).

## Current status

See `CLAUDE.md` §7–§10 for what's done and what's still open — it's the living
record, this section is just a pointer so it doesn't rot the way the paragraph it
replaced did (REL4 is no longer excluded from the measurement model; that
reflected a since-reversed Amendment A-9 decision).

**No synthetic data as of 2026-09-15** — `00_generate_synthetic.py` and every
synthetic/stale scaffold-era file under `data/raw/` and `data/processed/` were
removed; `data/raw/pilot_real.csv` is the only raw file, and it's real
throughout (see `CLAUDE.md` §10).

As of 2026-09-14: `data/raw/pilot_real.csv` is a live, growing export — 289 raw
responses as of this update, n=173 after exclusions (`sample_role`: 60 `pilot`
/ 113 `main`, see step 4 above). Two new demographic items, `LOC` (area of
residence) and `REF` (referral source — "who did you receive this survey
from?"), were added to the instrument mid-collection.

**The manipulation-check gate now clears at this n** — MC_AIP d≈0.81–1.04,
MC_DISC d≈1.20–1.47 depending on whether you look at the full n=173 or the
`sample_role="main"` n=113 subset (both comfortably above the 0.50 gate; see
`CLAUDE.md` §9). This is a reversal of the 2026-09-13 status (d≈0.45–0.49,
failing) — the manipulation looks like it was always fine and the earlier
numbers were an underpowered pilot n, not a broken vignette. Reliability is
strong across all constructs (α > 0.85 for most, including PDPL which used to
have a weak PDPL1 loading — that's resolved at this n). **AIP↔REL discriminant
validity (HTMT ≈ 0.86, still above the 0.85 threshold) remains the one
persistent open concern** — it has trended down as n grew (0.95 → 0.86) but
hasn't cleared, and the specific item driving the EFA cross-loading has moved
around between checkpoints (AIP2/AIP4/REL2 earlier, REL3 most recently),
suggesting a genuine content-overlap issue rather than a sampling artifact.

`01_clean.py` labels each response `sample_role = pilot/main` using an
**administrative** cutoff (when the `LOC` field was added, 2026-09-12
02:15:56) — this is explicitly not the same as a measurement-readiness
sign-off; see `CLAUDE.md` §9 before treating `sample_role="main"` as "main
collection has opened."

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
