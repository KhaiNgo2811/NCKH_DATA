# CLAUDE.md — Python Analysis Pipeline
## Project: AI-Driven Personalization & Customer Engagement (Privacy-Aware AI Agent)

This file orients Claude Code (or any team member working in this repo) on how to
run the Study 1 survey-experiment data (pilot, then main n≥400) in Python inside
VS Code. It encodes the project's governance rules from
`docs/Theoretical_Foundations_v2_11_updated.docx` (self-titled "Version 2.9",
consolidated reissue absorbing Amendments A-7 through A-17 in full, plus a later
un-numbered "post-B1.5 correction pass" reversing part of A-10 — this is the
single source of truth for theory, hypothesis numbering, and the measurement
register) and `docs/Master_Codebook_v2_6_updated.docx` (the variable-level bridge
between the Qualtrics instrument, this pipeline, and TF). Where TF and the
Codebook disagree, **TF prevails on substance**.

**Read this file before writing or running any analysis script.** Both governing
docs get re-issued under new filenames periodically (`_vN_updated.docx`) — if you
see a docs/ file with a higher version number than named above, re-extract and
diff it before trusting anything below.

**Status as of 2026-09-10:** the full scaffold (`00`–`07` + `run_plssem.py`) is
written and has been run end-to-end (`01`→`02`→`03`→`04`) against real pilot data
(`data/raw/pilot_real.csv`, 47 responses, n=22 after exclusions). `07_plssem_bridge.R`
/ `run_plssem.py` are still **not** smoke-tested locally (no R interpreter in the
build environment) — test these in VS Code before relying on them; see §5.

---

## 0. Non-negotiable naming rules (governance rule 1 & 2)

- Use **"PDPL"** / **"Law 91/2025/QH15"** everywhere. Never write "PDPD" or "Decree
  13/2023/NĐ-CP" as the operative instrument in code, comments, variable names, or
  output labels (Decree 13 may appear only in historical/comparison context,
  explicitly labeled as such — it was superseded 1 Jan 2026).
- Hypothesis codes are locked: **H1, H2, H3, H4, H5, H6a, H6b, H6c, H7a, H7b**.
  Established paths are **E1 (TRU→ENG), E2 (ENG→PI)** only — never renumber these
  as H-something, and never let TRU→PI (a competing-model robustness check, no
  H-number, no E-label) leak into the main structural model.
- Moderation coefficients: **β_M1 (INT×PDPL→TRU, the H7a test)** and **β_M2
  (INT×DISC→TRU, the H7b test)** only. β_M3 (PDPL×DISC) and β_M4 (INT×PDPL×DISC)
  are RETIRED (Amendment A-8) — no three-way product term anywhere in this repo.
  Both interactions moderate the H6a path (INT→TRU) **only** — never H6b, never H6c.
- **DISC is never a Likert/reflective construct.** It is a 0/1 dummy (`DISC_COND`
  column). Never compute Cronbach's α, loadings, AVE, or HTMT for it, and never let
  it appear in a measurement-model table. It does enter the Study 1 structural
  model as an observed dummy — predictor in H3 (via ANOVA), moderator in H7b.
- H3 has exactly **one** confirmatory test: the two-way ANOVA main effect of
  Disclosure on INT (Study 1). The DISC→INT path estimated inside the SEM is a
  specification term only (Aiken & West, 1991) — report it, never test it as H3.
- **ENG stays a single first-order reflective composite in the structural model**
  (H5, H6b, E1, E2) — no second-order specification — but its *reliability and
  item-retention diagnostics* must be computed within dimension (Cognitive:
  ENG1,ENG2; Affection: ENG3,ENG6; Activation: ENG4,ENG5), never pooled across all
  six items (Amendment A-12). See §1.3.

---

## 1. Current measurement register (ratified — TF v2.11 §C.4, Table 5 / Codebook v2.6 §4.7)

**34 reflective items fielded, 34 analysed** across 7 constructs — fielded and
analysed counts are identical for every construct; there is no fielded-but-excluded
item anywhere in the instrument. This is a change from an earlier project state
(Amendments A-9/A-10, 26 Aug 2026) where REL4 was excluded and TRU was reduced to
5 — both of those were later reversed. Do not revert to the old counts.

| Construct | Items | n | Source (verified, item-level) |
|---|---|---|---|
| AIP | AIP1–AIP5 | 5 | AIP1–3: Yin, Qiu & Wang (2025), JTAER 20(1) Art.21, "Insightful Experience" IS3/IS4/IS6. AIP4–5: Rahman, Carlson, Gudergan, Wetzels & Grewal (2022), *J. Retailing* 98(4), "Personalization (PERS)". |
| REL | REL1–REL4 | 4 (**all analysed, no exclusion**) | REL1: Srinivasan, Anderson & Ponnavolu (2002), *J. Retailing* 78(1), item (a). REL2–3: Yin, Qiu & Wang (2025) "Relevance Experience" RE4/RE1. REL4: repurposed semantic-differential pair (Klar, 1990, via Ahluwalia et al., 2001), operationalized by De Keyzer, Dens & De Pelsmacker (2015) — **Klar (1990) not independently verified, open flag**. |
| INT | INT1–INT5 | 5 | Li, Edwards & Lee (2002), *J. Advertising* 31(2). |
| TRU | TRU1–TRU6 | 6 (**not 5 — see note below**) | McKnight et al. (2002); TRU1–3 cognitive (trusting beliefs), TRU4–6 affective (trusting intentions — secure/comfortable/content, Komiak & Benbasat, 2006). |
| ENG | ENG1–ENG6 | 6 | Hollebeek, Glynn & Brodie (2014) CBE scale, 2 items/dimension. Three dimensions: Cognitive (ENG1,ENG2), Affection (ENG3,ENG6), Activation (ENG4,ENG5). Conceptual grounding only: Brodie et al. (2011) FP1/FP4. |
| PI | PI1–PI4 | 4 | PI1–3: Pavlou (2003) (3-item max, no 4th item exists in that scale). PI4: Dodds, Monroe & Grewal (1991), *JMR* 28(3), converted from semantic differential. |
| PDPL | PDPL1–PDPL4 | 4 | Newly developed on Law 91/2025/QH15 Arts. 8–10, 28. Item stems are and remain generic — never name the statute (§1.4). |
| DISC | — | — | Not a construct. Manipulation only (0/1 dummy). |

**RETRACTED sources — do not cite:** Awad & Krishnan (2006) for AIP; Xu et al.
(2011) and any "Shanahan, Tran & Taylor (2019) via Aydin (2026)" chain for REL.
Both were checked against the primary-source PDFs and found not to contain
matching items. **Aydin (2026)**, in any paper version, must not be cited anywhere
in this project pending independent re-review (a second fabricated-item pattern
was found under that name during verification).

### 1.1 TRU = 6 items (TRU1–TRU6) — this was genuinely revised, not a typo

Timeline, because an earlier draft of this file (and the Codebook's own §4.7 TRU
narrative, which has not been fully corrected) says TRU=5:
1. Amendment A-10 (26 Aug 2026) reduced TRU from 6 to 5 items (TRU1–TRU5) to match
   what was fielded *at that time*.
2. A later, un-numbered "post-B1.5 correction pass" **explicitly reverses A-10 for
   TRU specifically** (TF v2.11 amendment log, Table 0c note under A-10): *"the
   team and faculty advisor confirmed the current, correct standard is TRU = 6
   items (TRU1–TRU6: TRU1-3 cognitive; TRU4-6 affective — secure, comfortable,
   content — Komiak & Benbasat, 2006), as fielded in B1.5."* A-10's ENG
   reconciliation (6 items) is unaffected and still stands.
3. This matches `pilot_real.csv` (47 responses, 10 Sep 2026) exactly — TRU4/5/6
   wording is "an toàn / thoải mái / an lòng khi dựa vào ShopWave để đưa ra quyết
   định mua sắm" (secure/comfortable/content relying on ShopWave for shopping
   decisions).

**`src/_config.py::CONSTRUCT_ITEMS["TRU"]` = `["TRU1", ..., "TRU6"]` is correct
and ratified.** If you find a copy of the Master Codebook or an old CLAUDE.md
saying TRU=5, it is describing the withdrawn A-10 state, not current fact.

### 1.2 REL4 is not excluded — do not reintroduce the old A-9 exclusion

Amendment A-9 (26 Aug 2026) originally excluded REL4 from the measurement model on
content-validity + pilot-EFA grounds. **That REL4 item (Tam & Ho, 2006,
decision-usefulness wording) has since been removed from the instrument entirely**
— not merely excluded. The REL4 fielded today (Yin, Qiu & Wang, 2025, wording:
"Overall, the product list I saw was useful to me") is a different, unrelated
item and is **fully included** in α, AVE, HTMT, loadings, and `REL_mean`.

- `CONSTRUCT_ITEMS["REL"]` = `["REL1","REL2","REL3","REL4"]`, all analysed.
- `REL_mean` = mean(REL1…REL4). The old `REL_mean_4item` sensitivity-analysis
  variable name is retired — do not reuse it, no sensitivity analysis is needed.
- REL4's primary source (Klar, 1990) is independently unverified — an open flag
  for the team's judgement (further sourcing vs. self-development), not a
  pipeline blocker.

### 1.3 ENG: single composite in the model, within-dimension reliability at pilot

Amendment A-12 (1 Sep 2026) gave ENG an explicit three-dimension structure
(Cognitive: ENG1,ENG2; Affection: ENG3,ENG6; Activation: ENG4,ENG5), sourced to
Hollebeek, Glynn & Brodie (2014) rather than Brodie et al. (2011) (conceptual only,
no item battery). This **does not** make ENG a second-order structural construct —
H5, H6b, E1, E2 still use `ENG_mean` (mean of all 6 items) as a single reflective
composite, for the same parsimony reason TRU isn't modeled as second-order despite
an equally multidimensional source theory.

What it *does* change: Cronbach's α, item-rest correlation, and outer-loading
diagnostics for ENG must be computed **within dimension**, never pooled across all
six items — pooling compares items with genuinely different content and produces
misleading item-retention decisions. This reverses an earlier provisional plan to
drop ENG4 (which had a pooled outer loading of −0.381 at pilot n=46, looking like
a REL4-style exclusion candidate); within-dimension, ENG4's problem is *low
Activation-facet reliability* (r(ENG4,ENG5) = 0.212, α = 0.345 at n=46), not a bad
item — dropping it would leave Activation as an unassessable single-item facet.
**ENG4 is retained; report the weak Activation reliability transparently in
Limitations.**

`03_reliability_efa.py` implements this: ENG is excluded from the pooled
alpha/loadings/CR-AVE tables and gets its own
`pilot_eng_dimension_reliability.csv` (α per dimension) instead. `ENG_mean` for
the structural model is computed elsewhere (not by this diagnostic script).

### 1.4 PDPL Awareness: generic items, generic preamble, statute named nowhere in Qualtrics (OD-11, closed A-17)

PDPL1–PDPL4 item stems have never named Law 91/2025/QH15 (true since A-13) and
still don't. What changed across A-16→A-17 (both same-day, 8 Sep 2026) was
whether the fielded **preamble** should name the statute:
- A-16 (superseded the same day) split the preamble into a generic segment before
  PDPL1 and a statute-naming segment after PDPL1/before PDPL2. **Withdrawn.**
- A-17 (current, operative) reverts to a **single generic preamble**, no segment
  anywhere naming the statute. PDPL1–PDPL4 are administered identically; there is
  no pre-/post-anchor distinction in the current instrument or codebook.

The statute's name, effective date, and its relationship to each item's statutory
anchor (PDPL1: existence; PDPL2: Art.10 withdrawal/restriction; PDPL3: Art.9
consent; PDPL4: Art.8/28 rights) are documented only in the literature review
(Chapter 2) and the Method section's instrument-development narrative — **never in
Qualtrics**. Do not reintroduce "(Law No. 91/2025/QH15)" into any item stem or
preamble segment; both attempts were drafted and explicitly rejected.

### 1.5 H7 is two independent second-order interactions, not one three-way term (Amendment A-8)

`06_power_analysis.py` and `07_plssem_bridge.R` already reflect this — flagging it
here because it's the single most-repeated correction across the amendment log.
H7a (PDPL×INT→TRU, β_M1) and H7b (DISC×INT→TRU, β_M2) are estimated as two
independent two-way terms in one pooled model (two-stage approach, Becker et al.
2018), each with its own 10,000-resample BCa bootstrap CI and individual f² — do
not report a joint test. β_M3 (PDPL×DISC) and β_M4 (the three-way product) are
retired and not estimated anywhere. PLS-MGA/MICOM is **no longer required for H7**
specifically (DISC is now a pooled predictor/moderator, not a between-group
factor) — MICOM remains a prerequisite only if PLS-MGA is used elsewhere (e.g. a
demographic robustness check).

### 1.6 Item wording: pilot statistics are indicative, not confirmatory (Amendment A-13)

Item wording for AIP, INT, TRU, PDPL, and PI was finalized for main collection
(`PROJ_MAIN_final_v2`) after the pilot ran — mostly clarifying clauses, plus one
substantive fix (TRU2 was double-barreled at pilot: "...honestly and reliably /
always keeps its commitments..."; reverted to a single claim). **Any pilot (n=46
or n=47) reliability/EFA/HTMT number computed before this wording finalization is
indicative of construct behaviour, not confirmatory of the exact finalized item
text.** Main collection (n≥400) is the authoritative validity test — say so in the
Method section if citing pilot numbers.

---

## 2. Repo layout

```
project-root/
├── CLAUDE.md                      # this file
├── docs/
│   ├── Theoretical_Foundations_vN_updated.docx   # governing doc — always check for a newer N
│   └── Master_Codebook_vN_updated.docx           # variable-level bridge — always check for a newer N
├── data/
│   ├── raw/
│   │   ├── pilot_real.csv              # REAL pilot export, 47 responses (10 Sep 2026)
│   │   ├── pilot_n30_synthetic.csv     # scaffold-testing only
│   │   └── main_n400_synthetic.csv     # scaffold-testing only
│   └── processed/                 # cleaned, scored datasets (script-generated only)
├── src/
│   ├── _config.py                 # single source of truth: column names, item
│   │                               # lists, exclusion thresholds — see §4
│   ├── _qualtrics_io.py           # raw-export detector + normalizer (Likert-text
│   │                               # parsing, VIG_TIME de-duplication, CHAN decode)
│   ├── 00_generate_synthetic.py   # scaffold-testing data — never used for real results
│   ├── 01_clean.py                # loads raw or clean CSV, applies exclusions, recodes -98
│   ├── 02_descriptives.py         # demographics, cell balance, soft-flag summary
│   ├── 03_reliability_efa.py      # Cronbach's alpha, loadings, CR/AVE, HTMT, EFA,
│   │                               # ENG within-dimension reliability (§1.3)
│   ├── 04_manipulation_check.py   # t-tests / Cohen's d on MC_AIP / MC_DISC
│   ├── 05_anova_h3.py             # two-way ANOVA, Disclosure main effect = H3 test
│   ├── 06_power_analysis.py       # power for beta_M1/beta_M2, two independent
│   │                                # two-way terms (scipy.stats.ncf-based)
│   ├── 07_plssem_bridge.R         # seminr model — called via rpy2 (NOT smoke-tested,
│   │                               # see §5)
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

## 4. Data dictionary — confirmed against `pilot_real.csv` (47 responses, 10 Sep 2026)

| Block | Real column(s) | Construct | Raw format | Notes |
|---|---|---|---|---|
| Consent | `CONSENT` | — | numeric 0/1 in this export (choice text in older exports — the loader handles both) | 1 = agree. Anchor must retain Vietnamese diacritics when text-based — an ASCII-stripped anchor matches zero real responses. |
| Screener | `SCR_AGE`, `SCR_OMNI` | — | numeric 0/1 | **Column is `SCR_OMNI`, not `SCR1`** — confirmed against the real export; `_config.py::OMNI_COL` was wrong in an earlier draft and has been fixed. |
| Embedded Data | `AIP_COND`, `DISC_COND`, `CELL` | AIP, DISC | numeric 0/1 (AIP_COND/DISC_COND), numeric 1–4 (CELL) | `CELL` is a redundant Survey-Flow integrity cross-check only (`01_clean.py::check_cell_consistency`), never analyzed directly. |
| Timing | `VIG_TIME_First Click`, `VIG_TIME_Last Click`, `VIG_TIME_Page Submit`, `VIG_TIME_Click Count` | — | numeric, physically duplicated 4× in the raw CSV (one set per vignette cell) | `_qualtrics_io.py` coalesces the 4 duplicate-named column sets into one before anything else sees the data. |
| CC_Gate | `CC1`, `CC2` | — | numeric 1–3 | Correct answer depends on `AIP_COND`/`DISC_COND`. Hard drop on failure (§6.1) — the instrument terminates on failure, so a surviving wrong answer indicates a flow anomaly, not a normal respondent to soft-flag. |
| M_AIP | `AIP1`–`AIP5` | AIP | numeric 1–7 (choice text in some exports) | **5 items**, not 6 — the self-reference item (highest AIP–REL overlap risk) was dropped. |
| M_REL | `REL1`–`REL4` | REL | numeric 1–7 | **4 items, all analysed** — no exclusion (§1.2). |
| M_INT | `INT1`–`INT5` | INT | numeric 1–7 | 5 items. |
| Att1_Check | `ATT1` | — | numeric 1–7 | Must parse to `5`. |
| M_TRU | `TRU1`–`TRU6` | TRU | numeric 1–7 | **6 items** (§1.1). TRU1–3 cognitive, TRU4–6 affective. |
| M_ENG | `ENG1`–`ENG6` | ENG | numeric 1–7 | 6 items, 3 dimensions (§1.3). |
| Att2_Check | `ATT2` | — | numeric 1–7 | Must parse to `2`. |
| M_PI | `PI1`–`PI4` | PI | numeric 1–7 | **4 items**, not 3 — PI4 added. |
| M_PDPL | `PDPL1`–`PDPL4` | PDPL | numeric 1–7 | 4 items, generic wording/preamble (§1.4). |
| MC_Checks | `MC_AIP`, `MC_DISC` | — | numeric 1–7 | Real names, NOT `MC1`/`MC2`. Never enter the measurement model. |
| Demographics | `AGE_BAND`, `GEN`, `EDU`, `INC`, `FREQ`, `PLAT`, `PLAT_5_TEXT`, `PRIOR` | — | numeric / free text | `AGE_BAND`, `GEN`, `EDU`, `INC` carry a `-98` "prefer not to say" sentinel; `FREQ`, `PLAT`, `PRIOR` do not. **Recode `-98` to missing before any statistic** — `01_clean.py::recode_pnts` does this. |
| Channels | `CHAN` | — | comma-separated codes | Decoded by `_qualtrics_io.py` into boolean columns `CHAN_APP`, `CHAN_WEB`, `CHAN_LIVE`, `CHAN_STORE`, `CHAN_SOC`. |
| Qualtrics system | `Duration (in seconds)`, `Finished`, `ResponseId`, `Progress`, `RecordedDate` | — | native Qualtrics columns | `Duration (in seconds)` feeds the speeding exclusion rule. |

**Loader is format-agnostic.** Older raw exports carried Likert values as choice
text (e.g. `"3 - Không đồng ý một phần\n(Partly disagree)"`); the current export
format (`pilot_real.csv`) carries them as bare integers already. `_qualtrics_io.py`'s
`parse_likert_text()` and `anchor_match()` both handle either representation — a
leading-number regex first, a full-string fallback second — so no script needs to
know which format a given raw file uses. Still, **always go through
`load_and_normalize()`**; a script reading the raw CSV directly picks up the 2
Qualtrics metadata rows (question text, ImportId JSON) as if they were data.

**Do not create a `DISC1`/`DISC2` reliability column anywhere** — DISC is
`DISC_COND`, a single numeric 0/1 field from Embedded Data, full stop.

---

## 5. Pipeline steps

### `_qualtrics_io.py` (not a pipeline step — imported by `01_clean.py`)
- `is_raw_qualtrics_export(path)`: detects the 3-header-row raw-export signature via
  `csv.reader` (not naive line-splitting — bilingual choice-text questions contain
  embedded newlines inside quoted CSV fields, which broke a naive `readline()` check).
- `load_and_normalize(path)`: if raw, skips the 2 metadata header rows, coalesces the
  4× VIG_TIME duplicate columns, parses all Likert-text/numeric columns to integers,
  decodes `CHAN`. If already clean (synthetic / previously processed), passes through
  untouched.
- `anchor_match(series, anchor)`: matches on a leading numeric code first (handles
  both `"1"` and `"1 - Có, tôi đã từ 18 tuổi..."`), then falls back to a
  casefold-normalized full-string match for pure-text anchors. **Anchors must keep
  Vietnamese diacritics** when text-based — an ASCII-stripped anchor matches zero
  real responses and silently drops the entire sample.

### `01_clean.py`
- **POLICY CHANGE (2026-09-11, requested by Khai, amended twice same day):**
  the hard-drop pipeline was first narrowed to four criteria (replacing the
  previous consent/age/screener/ATT1/ATT2/CC1/CC2/speeding set), then the
  manipulation-check step was pulled back out into a report-only ITT design
  after being identified as post-treatment conditioning risk. Current state —
  see §6.1 for the full rationale and table:
  1. **Missing data** — >`MAX_MISSING_ITEM_PCT` of the 34-item battery missing
     (also catches MC-block dropouts, since MC sits after all 34 items).
  2. **Duplicate response pattern** — another respondent's answers across the
     full item battery differ on at most `DUPLICATE_MAX_DIFFERING_ITEMS` items
     (default 2) — flags both members of the pair.
  3. **Straightlining** — SD across the full item battery below
     `STRAIGHTLINE_HARD_SD_THRESHOLD` (0.10 — near-zero, a much stricter bar than
     the old 0.5 soft-flag threshold). Hard drop.
  4. **NOT a filter**: `report_manipulation_check()` (Welch's t + Cohen's d,
     MC_AIP vs AIP_COND and MC_DISC vs DISC_COND) runs after the three drops
     above and only reports/logs — it excludes nobody. `breakdown_mc_groups()`
     runs before filtering and splits the old conflated "manipulation check
     fail" label into (a) genuine miscomprehension vs (b) dropout.
     `flag_extreme_reversers()` adds a non-dropping column for a separate
     robustness check elsewhere. See §6.1 for why (post-treatment conditioning,
     Montgomery, Nyhan & Torres 2018).
- Loads via `_qualtrics_io.load_and_normalize()`; still runs
  `check_cell_consistency()` (CELL vs AIP_COND×DISC_COND) as a non-dropping
  diagnostic (`flag_cell_mismatch`).
- Recodes the demographic `-98` sentinel to missing (`recode_pnts`, §1's data
  dictionary note) — unaffected by the policy change above.
- Every threshold lives in `_config.py` as a named constant — change **only**
  there, with the change and reason logged (see §6.1), never inline in the script.
- Output: `data/processed/{pilot|main}_clean.csv` + `outputs/tables/{phase}_exclusion_log.csv`.

### `02_descriptives.py`
- Cell counts per `AIP_COND` × `DISC_COND` (flags any cell <20% of an even quarter
  share — relevant to the Qualtrics Randomizer "Evenly Present Elements" setting).
- Demographic summary table → `outputs/tables/{phase}_sample_profile.csv`.
- Reports soft-flag counts (straightliners, cell mismatch) without removing anyone.

### `03_reliability_efa.py` (pilot only)
- Cronbach's α, outer loadings, CR/AVE, and HTMT per construct in
  `_config.py::CONSTRUCT_ITEMS`, **except ENG** which is excluded from these pooled
  tables (§1.3) and gets its own `pilot_eng_dimension_reliability.csv` instead.
  **Never run for DISC.**
- EFA (principal-axis + oblimin) on the AIP/REL item set (9 items: 5+4), flagging
  any cross-loading. TF explicitly calls out the AIP–REL HTMT pair as the
  decisive discriminant-validity test (< 0.85) — watch it specifically.
- Output: `outputs/tables/pilot_reliability.csv`, `outputs/tables/pilot_eng_dimension_reliability.csv`,
  `outputs/tables/pilot_outer_loadings.csv`, `outputs/tables/pilot_cr_ave.csv`,
  `outputs/tables/pilot_htmt.csv`, `outputs/tables/pilot_efa_aip_rel_crossloadings.csv`.
- Thresholds (TF v2.11 §C.3): loadings ≥ 0.60 at pilot / ≥ 0.70 at main; AVE > 0.50;
  Cronbach's α and ρ_A > 0.70; HTMT < 0.85.

### `04_manipulation_check.py`
- Independent-samples t-test: `MC_AIP` across `AIP_COND`; `MC_DISC` across `DISC_COND`.
- Reports Cohen's d. **Gate: |d| ≥ 0.50** for both, or vignettes go back to task B2.10
  for rewrite before main collection opens.

### `05_anova_h3.py`
- Two-way ANOVA: `INT_mean ~ AIP_COND * DISC_label`.
- The **Disclosure main effect is the sole H3 test statistic** — reported regardless
  of significance (reporting-integrity rule, TF v2.11 §C.1.1). AIP main effect
  reported as an H1/H2 experimental replication (not itself H-numbered). AIP×DISC
  interaction reported as exploratory only — never H-numbered without a logged
  team decision.

### `06_power_analysis.py` (kept for methods-documentation)
- A priori power for β_M1 (INT×PDPL→TRU) and β_M2 (INT×DISC→TRU), each an
  independent two-way interaction term in the same model (k=6 predictor terms —
  INT, PDPL, DISC, INT×PDPL, INT×DISC, +1), via `scipy.stats.ncf` (Cohen/G*Power
  noncentrality convention).
- Because β_M1 and β_M2 share the same k and formula, the required-n figure applies
  identically to both — not a calculation for just one of them.
- a priori target (f²=0.02) → n=400, matching the main-collection quota. Conservative
  risk band (f²=0.009, Aguinis et al. 2005) → n≈880 — remains a real exposure if
  either interaction's true effect size lands nearer 0.009 than 0.02; not resolved
  by the two-way respecification, only made *detectable at the a priori target*.
- **Still only an OLS cross-check** — reconcile against the R-side `pwr::pwr.f2.test()`
  or WebPower before the Qualtrics per-cell quota is frozen (TF v2.11 §C.2).

### `07_plssem_bridge.R` + `run_plssem.py` (main collection, n≥400 — NOT smoke-tested)
- Core PLS-SEM model (H1, H2, H4, H5, H6a, H6b, H6c, E1, E2) specified via `seminr`,
  called from Python through `rpy2`. `DISC_COND` enters as an observed dummy predictor
  — never in the measurement model. Item ranges: AIP 1:5, REL 1:4, INT 1:5, TRU 1:6,
  ENG 1:6, PI 1:4, PDPL 1:4 (§1).
- H7a/H7b interaction terms via `interaction_term(..., method = two_stage)` — two
  independent two-way terms, no three-way product anywhere (§1.5).
- **Before trusting this on real data:**
  1. Confirm MICOM (via `cSEM`) is only invoked if PLS-MGA is used for something
     *other* than H7 — it's no longer a prerequisite for H7 itself (§1.5).
  2. Verify `summary(model)$reliability` and `summary(model)$validity$htmt` extract
     correctly against your installed seminr version.
  3. **Run it locally in VS Code first** (install R + `seminr`/`cSEM`/`pwr`, then
     `python src/run_plssem.py --input data/processed/main_n400_synthetic.csv`) to
     confirm the rpy2 bridge round-trips before pointing it at real main-collection data.
  4. Cross-validate every reported number against SmartPLS 4 output before it goes in
     the manuscript.
- **Do not run on pilot data for confirmatory purposes** — pilot is
  reliability/EFA/manipulation-check only (TF v2.11 §C.3 mandatory pilot gate). It
  only runs once `data/processed/main_clean.csv` exists from real n≥400 data.

---

## 6. Reporting conventions

- Every output table/figure filename encodes the hypothesis or construct it supports
  (e.g. `H3_anova_disclosure_main_effect.csv`), not `results1.csv`.
- Any script producing a manuscript number should print both the value and its
  governing document + section reference (e.g. "β_M1 per TF §A.5.1/§C.2") in a
  header comment, so provenance survives a git diff.
- Null/non-significant results are reported, not deleted from scripts or outputs
  (reporting-integrity rule, TF v2.11 §C.1.1).
- Cite pilot-stage reliability/EFA/HTMT numbers with the Amendment A-13 caveat
  (§1.6) — they're indicative of construct behaviour, not confirmatory of the
  finalized item wording.

### 6.1 Sample-filtering criteria (amended twice on 2026-09-11 — see below; log any further change)

**Current (as of the 2026-09-11 ITT amendment, requested by Khai):**

| Rule | Threshold | Type | Location |
|---|---|---|---|
| Missing data | ≤10% of the 34 items missing (also catches MC-block dropouts, since MC sits after all 34 items in the instrument) | hard drop | `_config.py::MAX_MISSING_ITEM_PCT` |
| Duplicate response pattern | ≤`DUPLICATE_MAX_DIFFERING_ITEMS` (2) items differ from another respondent's full-battery answers | hard drop | `_config.py::DUPLICATE_MAX_DIFFERING_ITEMS`, `01_clean.py::flag_duplicate_response_pattern` |
| Straightlining | SD across 34 items ≥ 0.10 (near-zero) | hard drop | `_config.py::STRAIGHTLINE_HARD_SD_THRESHOLD` |
| Demographic -98 | recode to missing before any stat | recode, not exclusion | `01_clean.py::recode_pnts` |

**MC_AIP / MC_DISC are NOT a filter of any kind as of this amendment.** The
individual-level manipulation-check exclusion that briefly existed earlier the
same day (2026-09-11: "MC_AIP/MC_DISC on expected side of midpoint (4), missing
MC = fail") was identified as **post-treatment conditioning**: MC_AIP is
measured *after* the AIP_COND treatment is administered, so filtering
respondents by how they answered it can bias the causal estimate of AIP_COND's
effect (Montgomery, Nyhan & Torres, 2018, *AJPS*). It is replaced by an
**Intention-to-Treat (ITT) design**:
- `01_clean.py::report_manipulation_check(df, mc_col, cond_col)` runs AFTER the
  three hard-drop steps above and reports group-level manipulation strength
  (Welch's t-test + Cohen's d, MC_AIP vs AIP_COND and MC_DISC vs DISC_COND) —
  **excludes no one**, warns if |d| < 0.50. Logged as a
  `manipulation_check_group_evidence (report only, n_excluded=0, d=..., p=...)`
  row in `outputs/tables/{phase}_exclusion_log.csv` so the log makes clear this
  step no longer subtracts n.
- `01_clean.py::flag_extreme_reversers(df, mc_col, cond_col, high_reverse_thresh=3, low_reverse_thresh=5)`
  adds a non-dropping `flag_extreme_reverser` column (AIP High but MC_AIP≤3, or
  AIP Low but MC_AIP≥5) for a separate robustness check only — e.g. re-running
  H2/H3/H7 with vs. without this group in `03_reliability_efa.py` or a later
  analysis script. Never used as a filter in this script.
- A respondent who quit before reaching the MC block still gets excluded, but
  via the ordinary missing-data screen (their substantive-item completion rate
  fails on its own merits) — not mislabeled as "manipulation check fail."

`01_clean.py::breakdown_mc_groups()` runs BEFORE filtering and prints/logs the
split that used to be conflated under one "manipulation_check_fail" label: (a)
answered MC_AIP but on the wrong side of the midpoint (genuine
miscomprehension) vs. (b) MC_AIP missing (dropout, never reached it). On
`pilot_real.csv` (62 raw, 2026-09-11): (a)=17, (b)=30, correct=15 — confirming
most of the earlier "manipulation_check_fail" count was actually dropout, not
miscomprehension.

**Superseded same-day (both no longer applied by `01_clean.py`):**
1. The original 9-step set (consent, age, omnichannel screener `SCR_OMNI`,
   ATT1=5, ATT2=2, CC1/CC2 cell-correct comprehension checks, speeding
   `Duration (in seconds)` ≥ `SPEEDING_MIN_SECONDS`).
2. The brief individual-level MC_AIP/MC_DISC midpoint filter described above,
   superseded by the ITT redesign the same day.

All constants for both superseded states are left in `_config.py`, unused, in
case reinstated. Speeding and straightlining thresholds are reasoned priors,
not measured facts — revisit against real pilot duration data (available in
`pilot_real.csv`) and log any change.

---

## 7. Real pilot run — status as of 2026-09-11

`data/raw/pilot_real.csv` is a live, growing export — it has gone 47 → 62 raw
responses across this project's sessions so far; re-run `01_clean.py` against it
before trusting any downstream number, and check the raw response count first
(`pd.read_csv(path, skiprows=[1,2])` row count) since the exclusion picture
changes with both new responses AND the filtering-criteria policy change below.

**Under the current ITT-based filter (§6.1, amended 2026-09-11):**
62 raw → excess_missing_items drops 30 → duplicate/straightlining drop 0 more
→ **n=32** after exclusions. This is up from the n=13 the brief individual-level
MC filter produced earlier the same day, confirming that filter's problem: most
of what it removed (30 of the 62 raw responses) was actually MC-block dropout
(caught anyway by missing-data), not miscomprehension. Group-level ITT evidence
on this n=32: **MC_AIP d=0.468, p=0.126 (below the 0.50 gate)**; MC_DISC
d=0.905, p=0.014 (clears well). `flag_extreme_reverser` caught **16/32 (50%)**
— a high rate worth a robustness re-run of H2/H3/H7 with vs. without this group
once main collection allows it. This has NOT yet been run through `02`/`03`/`04`
— do that before drawing any conclusion from it.

**Under the two now-superseded criteria sets, for reference:** the same
62-raw export gave n=29 under the original 9-step set (up from n=22 at 47 raw,
n=28 at a 55-raw checkpoint in between), and n=13 under the brief
individual-level MC filter that existed for part of 2026-09-11 before the ITT
amendment. Headline results at the n=28/29 checkpoint, run through
`01`→`02`→`03`→`04` under the original 9-step criteria:

- **Attrition was heavy under the old criteria too**: driven mostly by ATT1
  (roughly half of screener-passing respondents failed it) — worth checking item
  placement/wording, not just writing it off as low respondent quality. This
  factor no longer applies under the current 4-criterion filter since ATT1 isn't
  one of them anymore.
- **Reliability was strong** across the board at n=28/29: AIP α≈.906–.942,
  REL α≈.87–.91, INT α≈.87–.91, TRU α≈.89–.90, PI α≈.89, PDPL α≈.78–.86.
  ENG within-dimension: Cognitive α≈.78–.82, Affection α≈.70–.73,
  Activation α≈.45–.50 (expected — see §1.3, known 2-item abbreviation
  weakness, not a new problem).
- **Discriminant validity flags (HTMT > 0.85) at full item sets**: AIP↔REL ≈
  0.93 and TRU↔PI ≈ 0.88 both exceeded threshold at n=28/29 (values drift
  slightly between checkpoints — recompute rather than trusting a cached number).
  EFA cross-loadings on AIP2, AIP4, REL2 corroborated the AIP–REL finding.
- **Item-removal exploration (ad hoc, n=28/29, single/paired-item trims — not
  wired into `03_reliability_efa.py`, just checked manually):**
  - Dropping **PI2** resolves TRU↔PI cleanly (down to ≈0.83, under threshold).
    Dropping TRU6 instead barely moves it (≈0.88→0.876) — PI2 is the item to
    act on, not TRU6.
  - AIP↔REL was harder: dropping AIP3 alone helps some (≈0.93→0.887) but stays
    over threshold. Dropping AIP5 does almost nothing (≈0.929, item isn't the
    problem). Dropping REL2 *in addition* to AIP3 made it **worse**, not
    better (≈0.911) — a reminder that removing a flagged item doesn't always
    help once you're at n≈28, since it also shrinks the construct's own
    internal (monotrait) correlation.
  - The one combination that got **all** discriminant-validity pairs under
    0.85 simultaneously: drop **AIP3 + REL3 + PI2 + PDPL1** together — AIP↔REL
    down to 0.846 (barely under), TRU↔PI to 0.83, every other pair already
    fine, and no construct's α/CR/AVE got worse (PDPL actually improved
    substantially: AVE .624→.795 after dropping PDPL1). This is a promising
    lead for the eventual item-trimming decision, but it's one lucky-looking
    combination found by manual trial at n≈29 — **not a substitute for
    re-testing once more pilot data (or main collection) exists.**
  - **PDPL1 outer loading ≈ −0.51** (below the 0.60 pilot threshold) is a
    separate, cleaner finding: it isn't about mean/SD (PDPL1's descriptives
    are indistinguishable from PDPL2–4) — its inter-item correlation with
    PDPL2–4 is just low (r≈.34–.40), a content-validity issue (PDPL1 asks
    about awareness that the law *exists*; PDPL2–4 ask about awareness of
    specific *rights*) rather than a data-quality artifact.
- **Manipulation checks are trending toward marginal for MC_AIP as n grows**:
  d(MC_DISC) has stayed strong (≈1.1–1.6). d(MC_AIP) dropped from 0.604 (n=22)
  to **0.498** (n=29) — just under the |d|≥0.50 gate. Watch this closely as
  more pilot data comes in; if it keeps trending down, the AIP vignette may
  need the B2.10 rewrite before main collection.
- **n≈13–29 is small either way** — every number above is indicative, not a
  final pilot verdict, and even more so now that the filtering-criteria policy
  change (§6.1) has not yet been run through `02`/`03`/`04`. Re-run the full
  pipeline and redo the HTMT/item-removal exploration under the current
  4-criterion sample before treating any of the above as current fact.

**Before Phase 2 (main, n≥400) fielding — do not open main collection until:**
- [ ] Re-run `01`→`02`→`03`→`04` under the current 4-criterion filter (§6.1) and
      redo the reliability/HTMT/manipulation-check picture above — everything
      in this section predates that policy change.
- [ ] Decide whether the AIP3+REL3+PI2+PDPL1 trim (or some other combination)
      is adopted, and if so, feed it through `_config.py::CONSTRUCT_ITEMS` /
      TF and Codebook amendments first (governance rule: TF → Codebook →
      `_config.py`, never skip a step) rather than only testing it ad hoc.
- [ ] Pilot manipulation checks clear d ≥ 0.50 for both MC_AIP and MC_DISC —
      MC_AIP is currently borderline/failing depending on checkpoint.
- [ ] AIP↔REL discriminant validity resolved or explicitly accepted as a known
      risk in Limitations — no single/double item removal tried so far gets it
      convincingly under 0.85 on its own merits (the 4-item combination above
      does, barely, but needs re-verification).
- [ ] OD-2 power analysis reconciled against the R-side `pwr`/`WebPower` check.
- [ ] `07_plssem_bridge.R` / `run_plssem.py` smoke-tested locally with R installed.
- [ ] PDPL1 reviewed for removal or rewording (content-validity issue, not a
      data artifact — see above).

---

## 8. Code review fixes — 2026-09-12

An external review (`analysis_results.md`) was checked against the actual code and
mostly held up. Fixed:

- **PII in `data/processed/*.csv` (critical, worse than the review described):**
  not only was `pilot_clean.csv` never stripped of `IPAddress`/`LocationLatitude`/
  `LocationLongitude` before being written, those files (and most of
  `outputs/tables/*.csv`) turned out to be **tracked in git** despite
  `.gitignore` declaring `data/processed/*.csv` and `outputs/tables/*.csv` —
  they were added before that rule existed, and `.gitignore` doesn't retroactively
  untrack anything. Real respondent IP/location data has been sitting in git
  history. Fixed going forward: `_config.py::PII_COLUMNS` is now the single
  source of truth (shared by `strip_pii.py` and the new
  `01_clean.py::strip_pii()`, called right before `to_csv()`). **Not yet done,
  needs your decision:** `git rm --cached` the currently-tracked processed/output
  CSVs, and — if this repo has ever been pushed anywhere — scrub the PII out of
  git history (e.g. `git filter-repo`). Both are left undone deliberately; a
  history rewrite is destructive and needs explicit sign-off, especially if
  there's a remote or collaborators involved. See README's new "Known PII
  exposure" section.
- `_config.py`'s exclusion-policy comment still said "4 criteria -- manipulation
  check fail, missing data, ..." after the ITT amendment (§6.1) dropped MC to a
  report-only step — corrected to describe the actual 3 hard-drop criteria.
- `03_reliability_efa.py::htmt_table()` intentionally keeps ENG pooled (unlike
  the reliability/loadings/CR-AVE tables, which exclude it per Amendment A-12)
  — added a comment explaining why this isn't an inconsistency: A-12's pooling
  ban targets item-retention diagnostics, not ENG's cross-construct
  discriminant-validity coverage.
- `00_generate_synthetic.py` still generated a `SCR1` column; the real fielded
  name is `SCR_OMNI` (§4's data dictionary) — fixed for consistency, though it
  had no pipeline impact since `01_clean.py` no longer filters on this column.
- `02_descriptives.py` checked `flag_straightliner`/`flag_cc1_wrong`/
  `flag_cc2_wrong`, none of which `01_clean.py` has produced since the
  2026-09-11 policy changes (§6.1) — updated to check `flag_cell_mismatch` and
  `flag_extreme_reverser` instead, and added a construct-level mean/SD table
  (`{phase}_construct_descriptives.csv`) that didn't exist anywhere before.
- **Construct scores were never persisted anywhere** — `05_anova_h3.py`
  computed `INT_mean` inline and discarded it; nothing else computed the rest.
  Added `01_clean.py::compute_construct_scores()`, which writes an
  `{construct}_mean` column for every construct in `CONSTRUCT_ITEMS` into
  `{phase}_clean.csv`. `ENG_mean` here is still the pooled score (the sole
  structural-model input, Amendment A-12) — per-dimension ENG diagnostics stay
  in `03_reliability_efa.py`, not here.
- `run_plssem.py` only extracted `path_coefficients` and `boot_paths` from
  `07_plssem_bridge.R`'s result, silently dropping `reliability`, `f_squared`
  (needed for β_M1/β_M2 effect sizes), `htmt`, `loadings`, and `weights` —
  now extracts and saves all seven. Still unverified end-to-end (no R/rpy2 in
  this environment — see §5's `07_plssem_bridge.R` entry).
- `04_manipulation_check.py` hardcoded `pilot_manipulation_check.csv` as its
  output path with no `--phase` flag, so running it on main-collection data
  would silently overwrite the pilot results — added `--phase` (default
  `pilot` for backward compatibility).
- `05_anova_h3.py`'s ANOVA didn't report partial η² — added
  `effsize="np2"` to the `pg.anova()` call.
- README.md pinned `Theoretical_Foundations_v2_4.docx` / `Master_Codebook_v2_0.docx`
  and a stale "REL4 excluded, α=0.82-0.95" status paragraph — updated to point at
  "whatever's the highest vN in docs/" instead of a specific filename (same
  staleness risk this file already warns about at the top), and to a status
  paragraph that points at CLAUDE.md §7 instead of duplicating numbers that will
  drift again.
- Removed `src/import numpy as np.py` (scratch file, unrelated to the pipeline),
  `outputs/tables/OD2_power_analysis_beta_M4.csv` (references the retired
  three-way term, Amendment A-8), and
  `outputs/tables/_smoketest_real_2resp_exclusion_log.csv` (stale smoke-test
  artifact that shouldn't have been tracked either).

**Reviewed and NOT changed (review flagged these, judged not worth acting on, or
already fine):**
- HTMT keeping ENG pooled — see above, this is correct, not a bug.
- `pilot_eng_dimension_reliability.csv` — the review said this output was
  missing; it exists (`outputs/tables/pilot_eng_dimension_reliability.csv`).
  Likely just needed a re-run after a data update, not a code fix.
- `flag_duplicate_response_pattern()`'s O(n²) pairwise comparison — noted in a
  `_config.py` comment as a scalability concern for main collection (n≥400,
  ~80k pairs) rather than fixed now; pilot n is small enough that it's not
  worth the added complexity yet.
