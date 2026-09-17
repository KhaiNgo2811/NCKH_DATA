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

**R (for `07_plssem_bridge.R` / `run_plssem.py`, main-collection PLS-SEM only)** —
confirmed working end-to-end as of 2026-09-17 (Windows, via `winget`):

```powershell
winget install --id RProject.R
winget install --id RProject.Rtools
```

Then add R's `bin\x64` folder (e.g. `C:\Program Files\R\R-4.6.x\bin\x64`) to your
`PATH` (User environment variable) so `rpy2` can find it, and install the R packages
in an R console:

```r
install.packages(c("seminr", "cSEM", "pwr"))
```

Verify with `python -c "import rpy2.robjects"` — if that imports without error,
`run_plssem.py` is ready to use.

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
│   ├── 01_clean.py              # 9-step hard-drop policy, ITT-based manipulation-check
│   │                             # reporting + sensitivity analysis, sample_role/
│   │                             # collection_phase labeling, construct scores, PII
│   │                             # stripping on the CLEANED output too
│   ├── 02_descriptives.py       # demographics (LOC/REF w/ labels), cell balance,
│   │                             # construct descriptives
│   ├── 03_reliability_efa.py    # Cronbach's alpha, CR/AVE, HTMT, AIP/REL EFA --
│   │                             # ENG pooled like every other construct (Amendment A-20)
│   ├── 04_manipulation_check.py # MC_AIP / MC_DISC t-tests, Cohen's d gate
│   ├── 05_anova_h3.py           # two-way ANOVA — sole confirmatory test of H3
│   ├── 06_power_analysis.py     # OD-2 (closed) — power for beta_M1 / beta_M2;
│   │                             # optional --input fits an empirical f2 too
│   ├── 07_plssem_bridge.R       # seminr PLS-SEM model (main collection only) --
│   │                             # verified working end-to-end 2026-09-17
│   └── run_plssem.py            # rpy2 bridge orchestrator; 05/07/03/04 all accept
│                                 # --sample-role {pilot,main,all}
└── outputs/
    ├── tables/                  # should be gitignored (regenerate, don't commit) —
    │                            # same caveat as data/processed/ above
    └── figures/                 # gitignored
```

## How to run the pipeline

### 1. Get a raw export in place

`pilot_real.csv` is a **live, growing** Qualtrics export — every re-export can
change both the row count and (occasionally) the column set (three new
demographic items, `LOC`/`REF` and their labels, were added mid-collection;
see `CLAUDE.md` §9/§11). Two ways to get a new export in:

```bash
# If you have a fresh raw export with PII (IPAddress/location/recipient info):
python src/strip_pii.py --input <your_export.csv> --output data/raw/pilot_deidentified.csv
# then rename/move it to data/raw/pilot_real.csv, or point --input at it directly below.

# If you're just re-running against the export already in data/raw/pilot_real.csv:
# nothing to do here, skip to step 2.
```

### 2. Clean + label (`01_clean.py`) — always run this first, on every new export

```bash
python src/01_clean.py --input data/raw/pilot_real.csv --phase pilot
```

This single command:
- Prints a **before-filtering breakdown** of MC_AIP and of ATT1/ATT2, each
  split into "genuine fail" vs. "dropout" (previously conflated under one
  label) — diagnostic only, not a filter step.
- Applies the current **9-step hard-drop policy** in order — consent →
  age screener → omnichannel screener → attention checks (ATT1/ATT2) →
  comprehension checks (CC1/CC2) → speeder floor (<120s) → missing item
  (**zero tolerance** — any missing item among the 34 drops the row) →
  duplicate response pattern → straightlining. See `CLAUDE.md` §12 for the
  full table and the constants each step reads from `_config.py`.
- Adds `{construct}_mean` columns (AIP_mean, REL_mean, ...) and a
  `flag_extreme_reverser` column (robustness-check flag, never a filter).
- Adds `collection_phase` (`pre_LOC`/`post_LOC`) and `sample_role`
  (`pilot`/`main`) — an **administrative** label based on when the `LOC` field
  was added to the instrument (timestamp-based, Amendment A-19), **not** a
  measurement-readiness boundary (see `CLAUDE.md` §9/§12).
- Reports **group-level manipulation-check evidence** (Welch's t + Cohen's d
  for MC_AIP and MC_DISC, plus a supplementary AIP_mean composite check) —
  report-only, excludes nobody (Intention-to-Treat design, `CLAUDE.md` §6.1).
  Prints a dynamic PASS/FAIL note reflecting the actual result of this run.
- Runs `manipulation_check_sensitivity()` — the same MC evidence recomputed
  across 5 sample definitions (full sample, excluding the speeder floor, by
  `collection_phase`, excluding extreme reversers) — additive robustness
  evidence, still excludes nobody from the output file. Written to
  `outputs/tables/{phase}_manipulation_check_sensitivity.csv`.
- Prints/writes the `sample_role`×`collection_phase` checkpoint
  (`outputs/tables/collection_checkpoint_log.csv`).
- Strips PII columns before writing the output.

Output: `data/processed/pilot_clean.csv` + `outputs/tables/pilot_exclusion_log.csv`.

### 3. Descriptives, reliability, manipulation check

```bash
python src/02_descriptives.py --input data/processed/pilot_clean.csv --phase pilot
python src/03_reliability_efa.py --input data/processed/pilot_clean.csv
python src/04_manipulation_check.py --input data/processed/pilot_clean.csv
```

- `02_descriptives.py` → cell balance (AIP_COND × DISC_COND), demographic
  summary (including `LOC`/`REF`, `REF` shown with the referrer's name via
  `_config.py::REF_LABELS`), and construct-level mean/SD.
- `03_reliability_efa.py` → Cronbach's α, outer loadings, CR/AVE, HTMT, and
  the AIP/REL EFA cross-loading check. **ENG is included in every pooled
  table** (Amendment A-20 supersedes the old A-12 exclusion) — its
  within-dimension breakdown is now supplementary-only, not the governing
  diagnostic. Outer loadings are sign-normalized (a construct's loading
  vector is flipped positive if its mean would otherwise print negative —
  single-factor PCA extraction has an arbitrary sign).
- `04_manipulation_check.py` → the pre-registered gate (|d| ≥ 0.50 for both
  MC_AIP and MC_DISC).

### 4. Filtering by `sample_role` (pilot vs. main subset)

`03_reliability_efa.py`, `04_manipulation_check.py`, `05_anova_h3.py`, and
`run_plssem.py` all accept `--sample-role {pilot,main,all}` (default `all` =
no filtering, identical to omitting the flag). This runs the exact same
formulas/thresholds on a subset of rows and writes to a `_{role}`-suffixed
filename, so a filtered run never overwrites the unfiltered one:

```bash
python src/04_manipulation_check.py --input data/processed/pilot_clean.csv --sample-role main
python src/03_reliability_efa.py --input data/processed/pilot_clean.csv --sample-role main
python src/05_anova_h3.py --input data/processed/pilot_clean.csv --sample-role main
```

Remember: `sample_role="main"` is a bookkeeping label, not a governance
sign-off that main collection has formally opened (`CLAUDE.md` §9) — a PASS
(or a significant H3 test) on a `main`-filtered subset does not by itself mean
the checklist in `CLAUDE.md` §7 is satisfied. `05_anova_h3.py` and
`run_plssem.py` print an explicit warning when the filtered n is still below
400.

### 5. `05_anova_h3.py` and PLS-SEM (`07_plssem_bridge.R` / `run_plssem.py`)

These are the two **confirmatory-analysis** scripts — do not report their
output as confirmatory until real `sample_role="main"` n reaches ≥400
(`CLAUDE.md` §7); below that, treat any run (with or without `--sample-role`)
as exploratory only.

```bash
python src/05_anova_h3.py --input data/processed/pilot_clean.csv --sample-role main

# PLS-SEM requires R + the seminr/cSEM/pwr packages -- see Setup above.
python src/run_plssem.py --input data/processed/pilot_clean.csv --sample-role main
```

### Latest 05/06/07 results (exploratory — n=328 `sample_role="main"`, 2026-09-17)

**⚠️ n=328 < 400 — none of this is the confirmatory run yet.** Table kept here
so the three scripts' output lives in one place instead of scattered across
terminal scrollback; re-run and replace this table once n≥400.

**`05_anova_h3.py` — H3 (two-way ANOVA, `INT_mean ~ AIP_COND * DISC_COND`):**

| Source | F | p | η²p | Verdict |
|---|---|---|---|---|
| **H3 — DISC main effect (sole confirmatory test)** | 1.529 | 0.217 | 0.005 | NOT SUPPORTED |
| AIP main effect (H1/H2 replication, not H-numbered) | 0.985 | 0.322 | 0.003 | — |
| AIP × DISC interaction (exploratory only) | 5.001 | **0.026** | 0.015 | flagged — see `CLAUDE.md` §13 note on extreme reversers |

**`06_power_analysis.py` — a priori power for β_M1/β_M2, plus (new, 2026-09-17,
updated same day to a per-term refit) an empirical f² fitted SEPARATELY for
each interaction term from real data via `--input`/`compute_observed_f2()`.**
An earlier same-day version reported one blended f² for "M1+M2 combined" —
superseded, since H7a/H7b are two independent terms (§1.5) that turned out to
have very different individual effect sizes once split apart:

| Scenario | β (path coef.) | f² | p (incremental F-test) | k | required n | achieved power at n |
|---|---|---|---|---|---|---|
| a priori target (TF §C.2) | — | 0.020 | — | 6 | 400 | 0.8006 |
| conservative risk band (Aguinis et al. 2005) | — | 0.009 | — | 6 | 880 | 0.8004 |
| **observed H7a (β_M1, INT×PDPL, n=328, `main`)** | — | **0.0106** | — | 6 | **748** | 0.8003 |
| **observed H7b (β_M2, INT×DISC, n=328, `main`)** | — | **0.0008** | — | 6 | **>5000 (not achievable)** | — |
| **observed H7a (β_M1, INT×PDPL, n=380, `all`)** | **−0.0832** | **0.0099** | **0.0554** | 6 | **800** | 0.8003 |
| **observed H7b (β_M2, INT×DISC, n=380, `all`)** | **−0.0463** | **0.0025** | **0.3346** | 6 | **3143** | 0.8000 |

H7a's observed f² is close to the conservative risk band (n≈750–800), and its
p=.0554 at n=380 sits right at the edge of the incremental-F .05 cutoff — more
data could plausibly flip this significant. **H7b's observed f² is far
smaller** than either assumed scenario, isn't close to significant (p=.33),
and implies a required n well outside any realistic quota — worth flagging as
a real risk for H7b specifically, not just "power is a bit tight" in general.

`beta` (new, 2026-09-17) is each term's own path coefficient
(`INT*PDPL -> TRU` / `INT*DISC -> TRU`) pulled straight from the full model's
`path_coef` — the real seminr coefficient, not an OLS proxy. Both are close
to `run_plssem.py`'s own bootstrap-run values at n=328 (β_M1=−0.089,
β_M2=−0.027) — a cross-check that this script's duplicated model definitions
still match `07_plssem_bridge.R`'s.

`p_value` (new, 2026-09-17, `f2_significance()`) is the incremental-F-test
significance of each term's own f² (central F, df_num=1, df_denom=n−k−1) — an
OLS-analogue sanity check, **not** the real PLS-SEM bootstrap p-value for
β_M1/β_M2 (that's `run_plssem.py`'s 10,000-resample bootstrap CI, e.g. H7a
p=.199/H7b p=.610 at n=328 — see `CLAUDE.md` §13's robustness table).
Cross-validate against that before drawing any conclusion; the n=328 rows
above predate the beta/p_value addition and weren't re-run.

The observed rows need R (fits full/without-M1/without-M2 PLS-SEM models and
takes each term's own Cohen's f² from its R²(TRU) difference — see
`CLAUDE.md` §13); omit `--input` to get the original two-scenario table with
no R dependency. Re-run once n≥400 before using either for a quota decision.

**"As-perceived" H7b check (new, 2026-09-17, `--perceived-disc`,
`compute_observed_f2_perceived()`, `CLAUDE.md` §14, also updated to the
per-term refit):** swaps `DISC_COND` (assigned) for `MC_DISC` (measured,
continuous) in the `DISC` composite for H7b only, to test whether
misclassification in the assigned condition is suppressing H7b's observed
f² above. `PDPL`/H7a is unaffected (already fully continuous, nothing to
swap).

| Sample | β_M2(assigned) | f²_M2(assigned) | p(assigned) | β_M2(perceived) | f²_M2(perceived) | p(perceived) |
|---|---|---|---|---|---|---|
| n=380 (`all`) | −0.0463 | 0.0025 | 0.3346 | −0.0140 | 0.0002 | 0.7740 |

Neither reading of H7b is close to significant at n=380 — consistent with the
finding that **perceived is lower than assigned, not higher — no evidence
misclassification is suppressing H7b's f²**.

**Perceived f² is lower than assigned at both n, not higher — no evidence
misclassification is suppressing H7b's observed f².**

```bash
python src/06_power_analysis.py --input data/processed/pilot_clean.csv --sample-role main --perceived-disc
```

**`run_plssem.py` — PLS-SEM path coefficients (bootstrap 10,000 resamples):**

| Path | β | p (bootstrap) | Verdict |
|---|---|---|---|
| H1 AIP→REL | 0.701 | <.001 | Supported |
| H2 AIP→INT | 0.034 | .651 | Not supported |
| H4 REL→TRU | 0.348 | <.001 | Supported |
| H5 REL→ENG | 0.116 | .109 | Not supported |
| H6a INT→TRU (expect −) | −0.178 | .007 | Supported |
| H6b INT→ENG (expect −) | 0.008 | .932 | Not supported |
| H6c INT→PI (expect −) | −0.125 | .005 | Supported |
| E1 TRU→ENG (established) | 0.389 | <.001 | — |
| E2 ENG→PI (established) | 0.612 | <.001 | — |
| H7a β_M1 (INT×PDPL→TRU) | −0.089 | .199 | Not supported |
| H7b β_M2 (INT×DISC→TRU) | −0.027 | .610 | Not supported |
| DISC→INT (spec. term, NOT the H3 test) | −0.072 | .202 | — |
| PDPL→TRU (spec. term for H7a) | 0.097 | .084 | — |
| DISC→TRU (spec. term for H7b) | 0.080 | .099 | — |

**Reliability** (α/ρ_A/ρ_C/AVE): all 7 substantive constructs clear every
threshold (α .86–.90, AVE .59–.76). **Inner VIF**: max 1.25 (ENG←TRU) — no
common-method-bias signal (Kock 2015 threshold is 3.3). **HTMT**: AIP↔REL
0.78 (under 0.85 at this checkpoint — see `CLAUDE.md` §13 for why this has
moved around across checkpoints).

Full tables: `outputs/tables/{H3_anova_disclosure_main_effect_main,
OD2_power_analysis_beta_M1_M2, plssem_*_main}.csv`.

`run_plssem.py` (confirmed working end-to-end 2026-09-17) writes 7 tables to
`outputs/tables/plssem_*_{role}.csv`: outer loadings, outer weights,
reliability (α/ρ_A/ρ_C/AVE), path coefficients, f², HTMT, **inner VIF**
(collinearity/common-method-bias diagnostic, Kock 2015 convention — flags
>3.3), and bootstrapped path CIs (10,000 resamples, ~2–5 min). **Cross-validate
every number against SmartPLS 4 before it goes in the manuscript** — this
bridge has not been independently verified against SmartPLS output yet.

`06_power_analysis.py` is an a priori calculator, not data-dependent by
default — run it any time with no arguments. `--input` is optional (added
2026-09-17): if given, it also fits an empirical f² from real data (needs R,
same as `run_plssem.py`) and adds it as a third row to the comparison table:

```bash
python src/06_power_analysis.py
python src/06_power_analysis.py --input data/processed/pilot_clean.csv --sample-role main
```

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
