# CLAUDE.md — Python Analysis Pipeline
## Project: AI-Driven Personalization & Customer Engagement (Privacy-Aware AI Agent)

This file orients Claude Code (or any Claude instance / team member working in this
repo) on how to run the Study 1 survey-experiment data (pilot n=30, then main n≥400)
in Python inside VS Code. It encodes the project's governance rules from
`Theoretical_Foundations_v2.4.docx` (consolidated — absorbs Amendments A-7 through
A-10 in full; this is the single source of truth, no cross-reference to amendment files
needed) and the `91qh_signed.pdf` regulatory anchor (Law 91/2025/QH15).

**Read this file before writing or running any analysis script.**

**Status as of 2026-08-19: the full scaffold (`00`–`07` + `run_plssem.py`) is written
and smoke-tested end-to-end against synthetic data AND against a real 2-response
Qualtrics raw export.** Three real bugs were caught and fixed during that smoke test
(see §1.5) — this is exactly why the scaffold-before-data approach in §0.2 exists.
`07_plssem_bridge.R` / `run_plssem.py` could not be smoke-tested in the build sandbox
(no R interpreter available there) — test these locally in VS Code before relying on
them; see §5.

---

## 0. Non-negotiable naming rules (governance rule 1 & 2)

- Use **"PDPL"** / **"Law 91/2025/QH15"** everywhere. Never write "PDPD" or "Decree
  13/2023/NĐ-CP" in code, comments, variable names, or output labels (Decree 13 may
  appear only in historical comparison context, explicitly labeled as such).
- Hypothesis codes are locked: **H1, H2, H3, H4, H5, H6a, H6b, H6c, H7a, H7b**. Established
  paths are **E1 (TRU→ENG), E2 (ENG→PI)** only — never renumber these as H-something.
- Moderation/product-term coefficients use **β_M1 (INT×PDPL→TRU, the H7a test)** and
  **β_M2 (INT×DISC→TRU, the H7b test)** only. β_M3 (PDPL×DISC) and β_M4
  (INT×PDPL×DISC) are RETIRED as of Amendment A-8 (TF v2.3) — do not reintroduce a
  three-way product term anywhere in this repo.
- **DISC is never a Likert/reflective construct.** It is a 0/1 dummy (`DISC_COND`
  column). Never compute Cronbach's α, loadings, AVE, or HTMT for it, and never let
  it appear in a measurement-model table.
- H3 has exactly **one** confirmatory test: the ANOVA main effect of Disclosure on
  INT (Study 1, two-way ANOVA — per Amendment A-7, this ANOVA belongs to Study 1, not
  Study 2). The DISC→INT path estimated inside the SEM is a specification term only —
  report it, never test it as H3.

---

## 1. ⚠️ Open items

### 1.1 RESOLVED — TRU/ENG item count (ratified by Amendment A-10 / TF v2.4, 26 Aug 2026)

The TF v2.2 Table 5 register was wrong; the **fielded instrument is correct**. Amendment
A-10 corrected the register to match the instrument — no code or data change required.

| Construct | TF v2.2 Table 5 (wrong — register error) | Actual fielded / now ratified |
|---|---|---|
| TRU | 6 items | **5 items** (TRU1–TRU5) ✅ |
| ENG | 5 items | **6 items** (ENG1–ENG6) ✅ |

Total still reconciles to 33 either way, which is why the discrepancy went unnoticed
until the docx audit. **`src/_config.py::CONSTRUCT_ITEMS` is already correct** (uses
actual fielded counts). Remove any `GOVERNANCE-OPEN` comment in `_config.py` or
`07_plssem_bridge.R` that refers to this issue — it is closed. No code change needed.

### 1.2 SUPERSEDED — REL item count (superseded by Amendment A-9 / TF v2.4, 26 Aug 2026)

An earlier scaffold draft assumed REL had 3 items. The docx audit confirmed 4 items
(REL1–REL4) and this was marked resolved. **That resolution is now superseded:**
Amendment A-9 excludes REL4 from the measurement model on two independent grounds:
(i) content validity — REL1–REL3 all measure *fit* (content matches my needs/
preferences/me); REL4 measures *decision usefulness / search-effort reduction*, which
is a distinct facet closer to perceived usefulness than to relevance, making the
construct multidimensional contrary to its unidimensional specification; (ii) pilot
EFA (n = 35) corroboration — REL4 had a primary loading < 0.60 with a narrow
primary-to-secondary gap, the signature of a misplaced facet. See §1.2b.

### 1.2b ACTIVE — REL4 fielded but excluded from measurement model (Amendment A-9)

**What this means for the pipeline:**

- `src/_config.py::CONSTRUCT_ITEMS["REL"]` must be **`["REL1", "REL2", "REL3"]`** —
  REL4 must not appear in this list. If it does, fix it now.
- `REL_mean` = mean(REL1, REL2, REL3) — the construct score used for ANOVA and
  two-stage interaction terms.
- `REL_mean_4item` = mean(REL1, REL2, REL3, REL4) — retained for **sensitivity
  analysis only**; never the primary score.
- REL4 **stays in the raw and clean datasets** — do not drop it from the CSV. It is
  excluded from analysis, not from the data file.
- Any α, AVE, HTMT, or loading table containing REL4 is a pre-v2.4 remnant and must
  be corrected before the manuscript goes out.
- **Residual risk:** REL is now at the 3-item floor for a reflective construct. If any
  REL item underperforms at main collection the construct cannot be purified further.

### 1.3 Instrument content gaps flagged during audit (not a pipeline blocker, but log it)

Recorded here for traceability — these are questionnaire-content issues, not data-processing
issues, but they affect what the cleaned data can support:
- PDPL1–4 do not cite Law 91/2025/QH15 by name — weakens ecological validity of the
  PDPL Awareness construct (see chat log, docx audit).
- Cell2/Cell4 disclosure vignette text is a generic privacy reference, not the
  statutorily-specific "tracking basis + opt-out + retention" content TF Part B
  requires for H3 to test a "legally realistic disclosure."
- REL/INT measurement blocks lack a recall-framing lead-in sentence (M_ENG has one,
  M_REL/M_INT do not) — may affect response validity, not something `01_clean.py` can fix.

### 1.4 Missing input for `run_plssem.py` at build time

R was not available in the sandbox used to build this scaffold — `07_plssem_bridge.R`
and `run_plssem.py` are **written but not smoke-tested**. Test them locally (see §5)
before trusting any number they produce, even on synthetic data.

### 1.5 Bugs caught during smoke-testing (fixed — documented so they aren't reintroduced)

These were caught only because the scaffold was tested against the real 2-response
Qualtrics export, not just synthetic data — the whole reason §0.2's "build now, test
against synthetic AND a real sample early" approach exists:

1. **`_io.py` module name collision.** `_io` shadows a CPython built-in module; any
   script importing it silently imported the wrong thing. Renamed to `_qualtrics_io.py`.
2. **Raw-export detection false negative.** The bilingual (VI\nEN) choice-text
   questions contain literal embedded newlines inside quoted CSV fields (e.g. the
   consent text). A naive `.readline()`-based row-count check for the raw-export
   signature (question-text row / ImportId-JSON row) miscounted lines and returned
   `False` on the real file, so the loader fell through to a plain `pd.read_csv()` and
   left the question-text and ImportId metadata rows in as if they were real data.
   Fixed by reading with `csv.reader` (respects RFC-4180 quoting) instead of raw
   `readline()`.
3. **Consent/screener anchors stripped of Vietnamese diacritics.** An early draft of
   `_config.py` used ASCII-only anchor strings (`"Toi dong y tham gia"`) to match
   against the choice-text consent/screener answers. The real exported values keep
   full diacritics (`"Tôi đồng ý tham gia"`), so the ASCII anchors matched **zero**
   real responses and the `consent_not_given` exclusion step silently dropped both
   real test respondents (n: 2 → 0). Fixed by restoring diacritics in every anchor
   constant in `_config.py`. **This is the single most important fix in this file** —
   an ASCII-stripped anchor is a silent, 100%-drop-rate bug that would have looked
   like "nobody consented" instead of a code bug.

Two library-version fixes were also needed (not data bugs, just environment drift):
- `pingouin` ≥0.6 renamed `p-val`→`p_val` and `p-unc`→`p_unc`; `04_manipulation_check.py`
  and `05_anova_h3.py` now check for both column names.
- `statsmodels.stats.power.FTestPower.power()`'s `effect_size` parameter did not
  behave as documented for this use case (power stayed flat at ≈α regardless of n).
  `06_power_analysis.py` now computes power directly via `scipy.stats.ncf` using the
  standard Cohen (1988)/G*Power noncentrality convention (`ncp = f2*(df_num+df_denom+1)`),
  validated by hand to reproduce TF v2.2's stated n≈402 (f²=0.02) and n≈882 (f²=0.009)
  before being trusted.

---

## 2. Repo layout

```
project-root/
├── CLAUDE.md                      # this file
├── data/
│   ├── raw/
│   │   ├── pilot_n30_synthetic.csv     # scaffold-testing only, see §3
│   │   ├── main_n400_synthetic.csv     # scaffold-testing only, see §3
│   │   └── pilot_partial_raw.csv       # REAL Qualtrics export, 2 test responses
│   │                                   # (not a pilot result — just proves the
│   │                                   # loader works on a real file; see §4.1)
│   └── processed/                 # cleaned, scored datasets (script-generated only)
├── src/
│   ├── _config.py                 # single source of truth: column names, item
│   │                               # lists, exclusion thresholds — see §4
│   ├── _qualtrics_io.py           # raw-export detector + normalizer (Likert-text
│   │                               # parsing, VIG_TIME de-duplication, CHAN decode)
│   ├── 00_generate_synthetic.py   # scaffold-testing data — never used for real results
│   ├── 01_clean.py                # loads raw or clean CSV, applies exclusions
│   ├── 02_descriptives.py         # demographics, cell balance, soft-flag summary
│   ├── 03_reliability_efa.py      # Cronbach's alpha, EFA (pilot only)
│   ├── 04_manipulation_check.py   # t-tests / Cohen's d on MC_AIP / MC_DISC
│   ├── 05_anova_h3.py             # two-way ANOVA, Disclosure main effect = H3 test
│   ├── 06_power_analysis.py       # OD-2 (CLOSED by Amendment A-8): power for beta_M1/beta_M2, two
│   │                                # independent two-way terms (scipy.stats.ncf-based)
│   ├── 07_plssem_bridge.R         # seminr model — called via rpy2 (NOT smoke-tested,
│   │                               # see §1.4 / §5)
│   └── run_plssem.py              # rpy2 bridge orchestrator (main n≥400 only)
├── outputs/
│   ├── tables/                    # every script writes its results here
│   └── figures/
├── requirements.txt
└── .venv/                         # local virtual environment (gitignored, not included)
```

---

## 3. Environment setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` (already in the repo):
```
pandas
numpy
pingouin
factor_analyzer
statsmodels
scipy
matplotlib
seaborn
openpyxl
rpy2
```

**Known version pin:** `factor_analyzer` (used by `03_reliability_efa.py`) is
incompatible with `scikit-learn>=1.6` (`check_array() got an unexpected keyword
argument 'force_all_finite'`). Install `"scikit-learn<1.6"` explicitly if you hit this:
```bash
pip install "scikit-learn<1.6"
```

R side (run once, in an R console, not Python — required for §5's `07_plssem_bridge.R`):
```r
install.packages(c("seminr", "cSEM", "pwr"))
```

---

## 4. Data dictionary — CONFIRMED against the real Qualtrics raw export

Every column name below was verified directly against
`1787112675195_PROJ_MAIN_August_18__2026_22_10.csv` (2 real test responses, checked
2026-08-19), not guessed from the survey document. **Earlier scaffold drafts had
several of these wrong** (`Consent`/`Age18`/`Omnichannel2ch` instead of the real
`CONSENT`/`SCR_AGE`/`SCR1`; assumed `AIP_COND` was `"Low"`/`"High"` text when it is
actually numeric 0/1; assumed `MC1`/`MC2` instead of the real `MC_AIP`/`MC_DISC`) — do
not revert to those.

| Block | Real column(s) | Construct | Raw format | Notes |
|---|---|---|---|---|
| Consent | `CONSENT` | — | choice text, VI first line + EN second line | Anchor-matched against `"Tôi đồng ý tham gia"` (**keep diacritics** — see §1.5 bug #3) |
| Screener | `SCR_AGE`, `SCR1` | — | choice text | Anchors: `"Có, tôi đã từ 18 tuổi trở lên"`, `"Có"` |
| Embedded Data | `AIP_COND`, `DISC_COND`, `CELL` | AIP, DISC | **numeric 0/1** (AIP_COND/DISC_COND), numeric 1–4 (CELL) | `CELL` is redundant — used only as a Survey-Flow integrity cross-check (`01_clean.py::check_cell_consistency`), never analyzed directly |
| Timing | `VIG_TIME_First Click`, `VIG_TIME_Last Click`, `VIG_TIME_Page Submit`, `VIG_TIME_Click Count` | — | numeric, **physically duplicated 4× in the raw CSV** (one set per Vignette_Cell1–4 block) | `_qualtrics_io.py` coalesces the 4 duplicate-named column sets into one before anything else sees the data |
| CC_Gate | `CC1`, `CC2` | — | choice text | Correctness depends on `AIP_COND`/`DISC_COND` — see `_config.py` anchors. Comprehension failures are **flagged, not auto-dropped** (soft flag `flag_cc1_wrong`/`flag_cc2_wrong`) per the team's pre-registered rule (§6.1) |
| M_AIP | `AIP1`–`AIP6` | AIP | choice text, e.g. `"7 - Hoàn toàn đồng ý\n(Strongly agree)"` | 6 items |
| M_REL | `REL1`–`REL4` | REL | choice text | **4 items fielded, 3 analysed** — REL4 excluded from measurement model by Amendment A-9 (§1.2b). `CONSTRUCT_ITEMS["REL"]` = REL1–REL3 only. REL4 kept in dataset for sensitivity analysis. |
| M_INT | `INT1`–`INT5` | INT | choice text | 5 items |
| Att1_Check | `ATT1` | — | choice text | Must parse to `5` |
| M_TRU | `TRU1`–`TRU5` | TRU | choice text | 5 items — **ratified by Amendment A-10** (§1.1). TRU1–TRU3 = trusting beliefs; TRU4–TRU5 = affective trust. |
| M_ENG | `ENG1`–`ENG6` | ENG | choice text | 6 items — **ratified by Amendment A-10** (§1.1). |
| Att2_Check | `ATT2` | — | choice text | Must parse to `2` |
| M_PI | `PI1`–`PI3` | PI | choice text | 3 items |
| M_PDPL | `PDPL1`–`PDPL4` | PDPL | choice text | 4 items |
| MC_Checks | `MC_AIP`, `MC_DISC` | — | choice text | **Real names, NOT `MC1`/`MC2`.** Feed into `04_manipulation_check.py`, never into the measurement model |
| Demographics | `AGE_BAND`, `GEN`, `EDU`, `INC`, `FREQ`, `PLAT`, `PLAT_5_TEXT`, `PRIOR` | — | choice text / free text | Covariates / sample description only |
| Channels | `CHAN` | — | comma-separated codes, e.g. `"CHAN_APP,CHAN_LIVE"` | Decoded by `_qualtrics_io.py` into boolean columns `CHAN_APP`, `CHAN_WEB`, `CHAN_LIVE`, `CHAN_STORE`, `CHAN_SOC` |
| Qualtrics system | `Duration (in seconds)`, `Finished`, `ResponseId`, `Progress`, `RecordedDate` | — | native Qualtrics columns | `Duration (in seconds)` feeds the speeding exclusion rule |

**Every Likert-type column (33 items + ATT1 + ATT2 + MC_AIP + MC_DISC) arrives as
choice TEXT**, e.g. `"3 - Không đồng ý một phần\n(Partly disagree)"`, not a bare
integer. `_qualtrics_io.py::parse_likert_text()` regex-extracts the leading number
(`^\s*(\d+)\s*-`) before any statistic touches these columns. This single fact was the
scaffold's biggest wrong assumption pre-real-data — a script that reads these raw
without going through the loader will silently coerce every item to `NaN` mean.

**Do not create a `DISC1`/`DISC2` reliability column anywhere** — DISC is `DISC_COND`,
a single numeric 0/1 field from Embedded Data, full stop.

---

## 5. Pipeline steps

### `_qualtrics_io.py` (not a pipeline step — imported by `01_clean.py`)
- `is_raw_qualtrics_export(path)`: detects the 3-header-row raw-export signature via
  `csv.reader` (not naive line-splitting — see §1.5 bug #2).
- `load_and_normalize(path)`: if raw, skips the 2 metadata header rows, coalesces the
  4× VIG_TIME duplicate columns, parses all Likert-text columns to integers, decodes
  `CHAN`. If already clean (synthetic / previously processed), passes through untouched.
- `anchor_match(series, anchor)`: casefold-normalized first-line match, used for
  CONSENT/SCR_AGE/SCR1/CC1/CC2 comparisons. **Anchors must keep Vietnamese
  diacritics** (§1.5 bug #3).

### `01_clean.py`
- Loads via `_qualtrics_io.load_and_normalize()`, then applies **pre-registered** hard
  exclusions in order: consent, age, omnichannel screener, ATT1, ATT2, speeding
  (`Duration (in seconds)` < `SPEEDING_MIN_SECONDS`, default 150s — revisit after
  pilot), excess missingness (>`MAX_MISSING_ITEM_PCT`, default 10%, on the 33-item
  battery).
- Adds **soft flags** (not auto-dropped, so `02_descriptives.py` can report a
  with/without sensitivity check): `flag_straightliner` (SD across all 33 items below
  `STRAIGHTLINE_SD_THRESHOLD`, default 0.5), `flag_cc1_wrong`, `flag_cc2_wrong`,
  `flag_cell_mismatch` (CELL vs AIP_COND×DISC_COND disagreement — a Survey-Flow bug
  signal, not a respondent-quality issue).
- Every threshold above lives in `_config.py` as a named constant — change **only**
  there, with the change and reason logged (see §6.1), never inline in the script.
- Output: `data/processed/{pilot|main}_clean.csv` + `outputs/tables/{phase}_exclusion_log.csv`.

### `02_descriptives.py`
- Cell counts per `AIP_COND` × `DISC_COND` (flags any cell <20% of an even quarter
  share — relevant to the Qualtrics Randomizer "Evenly Present Elements" setting).
- Demographic summary table → `outputs/tables/{phase}_sample_profile.csv`.
- Reports soft-flag counts (straightliners, CC1/CC2 wrong, CELL mismatch) without
  removing anyone.

### `03_reliability_efa.py` (pilot only, n=30)
- Cronbach's α per construct via `pingouin.cronbach_alpha()`. **Never run for DISC.**
- EFA (principal-axis + oblimin) on the AIP/REL item set specifically, flagging any
  cross-loading (known discriminant-validity risk per TF v2.4 §C.4 — AIP6 showed a
  borderline cross-loading on the synthetic smoke-test data, worth watching on real
  pilot data too).
- Output: `outputs/tables/pilot_reliability.csv`, `outputs/tables/pilot_efa_aip_rel_crossloadings.csv`.

### `04_manipulation_check.py`
- Independent-samples t-test: `MC_AIP` across `AIP_COND`; `MC_DISC` across `DISC_COND`.
- Reports Cohen's d. **Gate: |d| ≥ 0.50** for both, or vignettes go back to task B2.10
  for rewrite before main collection opens.

### `05_anova_h3.py`
- Two-way ANOVA: `INT_mean ~ AIP_COND * DISC_label`.
- The **Disclosure main effect is the sole H3 test statistic** — reported regardless
  of significance (TF v2.4 reporting-integrity rule). AIP main effect reported as an
  H1/H2 experimental replication (not itself H-numbered). AIP×DISC interaction
  reported as exploratory only.

### `06_power_analysis.py` (OD-2 — CLOSED by Amendment A-8, kept for methods-documentation)
- A priori power for β_M1 (INT×PDPL→TRU) and β_M2 (INT×DISC→TRU), each estimated as
  an independent two-way interaction term in the same model (k reduced from 8 to 6
  predictor terms — see script docstring), via `scipy.stats.ncf` (Cohen/G*Power
  noncentrality convention — see §1.5 for why this replaced an earlier
  `statsmodels`-based attempt).
- Because β_M1 and β_M2 share the same k and the same formula, the required-n figure
  applies identically to both terms — this is not a calculation for just one of them.
- Re-run 2026-08-26 with `k=6`: a priori target (f²=0.02) → **n=400**, matching the
  n≥400 main-collection quota exactly — this is the figure that made Amendment A-8
  ("two parallel two-way terms are feasible at n≥400") correct. Conservative risk band
  (f²=0.009, Aguinis et al. 2005) → **n=880**, essentially unchanged from the retired
  3-way term's n≈882. Dropping k from 8→6 barely moves this number because required n
  is dominated by the effect size, not k. **GOVERNANCE-OPEN:** Amendment A-8 closes
  OD-2 against the a priori target only — the conservative risk band is not resolved
  by moving to two-way terms and remains a real exposure if either interaction's true
  effect size lands nearer f²≈0.009 than 0.02. Flagged for Khải, not silently
  downgraded.
- **Still only an OLS cross-check** — reconcile against the R-side `pwr::pwr.f2.test()`
  or WebPower before the Qualtrics per-cell quota is frozen.

### `07_plssem_bridge.R` + `run_plssem.py` (main collection, n≥400 — NOT smoke-tested, see §1.4)
- Core PLS-SEM model (H1, H2, H4, H5, H6a, H6b, H6c, E1, E2) specified via `seminr`,
  called from Python through `rpy2`. `DISC_COND` enters as an observed dummy predictor
  — never in the measurement model.
- **Before trusting this on real data:**
  1. Add the β_M1 (INT×PDPL) and β_M2 (INT×DISC) interaction terms — TWO separate
     two-way terms, NOT a three-way product — via `seminr::interactions()` / the
     two-stage approach (Becker et al., 2018) per TF v2.3 §C.2 (Amendment A-8).
  2. Add MICOM (measurement invariance) via `cSEM` before any PLS-MGA interpretation.
     NOTE: per Amendment A-8, PLS-MGA/MICOM is no longer required specifically for H7
     (DISC is now a pooled predictor/moderator, not a grouping variable for a
     three-way test). Keep this bullet only if PLS-MGA is still needed elsewhere in
     the model; otherwise this step can be skipped for H7 purposes.
  3. Replace the `ave`/reliability placeholder with a real `reliability()`/AVE
     extraction call.
  4. **Run it locally in VS Code first** (install R + `seminr`/`cSEM`/`pwr`, then
     `python src/run_plssem.py --input data/processed/main_n400_synthetic.csv`) to
     confirm the rpy2 bridge round-trips before pointing it at real main-collection data.
  5. Cross-validate every reported number against SmartPLS 4 output before it goes in
     the manuscript.

---

## 6. Reporting conventions

- Every output table/figure filename encodes the hypothesis or construct it supports
  (e.g. `H3_anova_disclosure_main_effect.csv`), not `results1.csv`.
- Any script producing a manuscript number should print both the value and its
  governing document + section reference (e.g. "β_M1 per TF v2.3 §A.5.1 / §C.2") in a
  header comment, so provenance survives a git diff.
- Null/non-significant results are reported, not deleted from scripts or outputs
  (Reporting-integrity rule, TF v2.4 §C.1.1).

### 6.1 Pre-registered exclusion rules (do not modify after seeing real data without logging why)

| Rule | Threshold | Type | Location |
|---|---|---|---|
| Consent | must match anchor | hard drop | `_config.py::CONSENT_OK_ANCHOR` |
| Age ≥18 | must match anchor | hard drop | `_config.py::AGE_OK_ANCHOR` |
| Omnichannel screener | must match anchor | hard drop | `_config.py::OMNI_OK_ANCHOR` |
| ATT1 | must equal 5 | hard drop | `_config.py::ATT1_CORRECT` |
| ATT2 | must equal 2 | hard drop | `_config.py::ATT2_CORRECT` |
| Speeding | `Duration (in seconds)` ≥ 150s | hard drop | `_config.py::SPEEDING_MIN_SECONDS` |
| Missing data | ≤10% of the 33 items missing | hard drop | `_config.py::MAX_MISSING_ITEM_PCT` |
| Straightlining | SD across 33 items ≥ 0.5 | **soft flag only** | `_config.py::STRAIGHTLINE_SD_THRESHOLD` |
| CC1/CC2 wrong | matches expected cell | **soft flag only** | computed in `01_clean.py::add_soft_flags` |

These are proposed defaults, not yet formally ratified by the team in writing (pilot
tracker / B1.5). The speeding and straightlining thresholds in particular should be
revisited once real pilot-duration data exists — 150s and SD<0.5 are reasonable priors,
not measured facts.

---

## 7. Before running on real data — checklist

**Done:**
- [x] Full scaffold (`00`–`06` + `run_plssem.py` structure) written and smoke-tested
      end-to-end against synthetic data.
- [x] Loader (`_qualtrics_io.py`) smoke-tested against a **real** raw Qualtrics export
      (2 test responses) — 3 real bugs caught and fixed (§1.5).
- [x] REL item-count discrepancy resolved (§1.2, superseded by §1.2b / Amendment A-9).
      **Action required:** confirm `CONSTRUCT_ITEMS["REL"]` = REL1–REL3 in `_config.py`.
- [x] Power analysis (`06_power_analysis.py`) validated to reproduce TF v2.2's stated
      n≈402 / n≈882 figures exactly (pre-Amendment-A-8, 3-way term, k=8).
- [x] Power analysis re-run post-Amendment-A-8 (k=6, two parallel two-way terms,
      2026-08-26): a priori target reproduces n=400 exactly. See §5's
      `06_power_analysis.py` entry for the unresolved conservative-risk-band figure.

**Still open:**
- [x] ~~Resolve §1.1 TRU/ENG item-count discrepancy~~ — **CLOSED by Amendment A-10**
      (TF v2.4, 26 Aug 2026). Remove `GOVERNANCE-OPEN` comments in `_config.py` and
      `07_plssem_bridge.R` that referred to this issue.
- [ ] **Verify `CONSTRUCT_ITEMS["REL"]` = `["REL1","REL2","REL3"]` in `_config.py`**
      (Amendment A-9). REL4 must not be in this list. The sensitivity score
      `REL_mean_4item` should be computed separately in scripts that need it, not via
      `CONSTRUCT_ITEMS`.
- [ ] Formally ratify the exclusion thresholds in §6.1 with the team in writing
      (pilot tracker / B1.5), especially speeding/straightlining.
- [ ] Test `07_plssem_bridge.R` / `run_plssem.py` locally (R not available in the
      build sandbox — see §1.4/§5).
- [ ] Once the Qualtrics instrument is frozen, re-export a fresh raw CSV and re-run
      `01_clean.py` against it to catch any last column-name drift before pilot n=30
      opens for real.
- [ ] **GOVERNANCE-OPEN (Amendment A-8):** decide whether the n≈880 conservative
      risk-band exposure for β_M1/β_M2 (f²=0.009, §5's `06_power_analysis.py` entry)
      needs a mitigation before main collection, or is accepted as a known residual
      risk now that the a priori target (f²=0.02, n=400) is met.

**Before Phase 1 (pilot, n=30) fielding:**
- [ ] Confirm `AIP_COND`/`DISC_COND`/`CELL` populate for every respondent (already
      confirmed working in the 2-response test export).
- [ ] Point `01_clean.py --input <real_pilot_export.csv> --phase pilot` at the real
      pilot CSV once n=30 closes — the loader handles raw Qualtrics exports directly,
      no manual pre-processing needed.

**Before Phase 2 (main, n≥400) fielding — do not open main collection until both pass:**
- [ ] Pilot manipulation checks (`04_manipulation_check.py`) clear Cohen's d ≥ 0.50 for
      both `MC_AIP` and `MC_DISC`. If not, vignettes go back to B2.10 for rewrite and
      the pilot re-runs before this box can be checked.
- [ ] OD-2 power analysis (`06_power_analysis.py`, reconciled against the R-side
      `pwr`/`WebPower` check) has produced a final per-cell quota target.
- [ ] Do **not** run `run_plssem.py` on pilot data (n=30) for confirmatory purposes —
      pilot is reliability/EFA/manipulation-check only (TF v2.4 §C.3 mandatory pilot
      gate). It only runs once `data/processed/main_clean.csv` exists from real n≥400 data.