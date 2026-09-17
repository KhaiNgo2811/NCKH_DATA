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

### 1.3 ENG: single composite in the model, POOLED reliability (Amendment A-20 supersedes A-12)

Amendment A-12 (1 Sep 2026) gave ENG an explicit three-dimension structure
(Cognitive: ENG1,ENG2; Affection: ENG3,ENG6; Activation: ENG4,ENG5), sourced to
Hollebeek, Glynn & Brodie (2014) rather than Brodie et al. (2011) (conceptual only,
no item battery), and required Cronbach's α/item-rest correlation/outer-loading
diagnostics to be computed **within dimension**, never pooled.

**Amendment A-20 (15 Sep 2026) withdraws that pooling prohibition** (Master
Codebook v2.7/A-20, TF v2.12/A-20 — verified against both docx files directly,
not carried over from an older CLAUDE.md draft). ENG's reliability (α, ρ_A),
outer loadings, CR, and AVE are now computed on the **full pooled six-item
set**, exactly like every other construct (AIP, REL, INT, TRU, PI, PDPL) — its
absence from the pooled tables is now a defect, not compliance. The
three-dimension structure survives only as a **supplementary descriptive
label** (`ENG_cog_mean`/`ENG_aff_mean`/`ENG_act_mean`, content description
only) — it no longer governs how diagnostics are computed or whether an item
gets dropped.

What did **not** change: ENG is still **not** a second-order structural
construct — H5, H6b, E1, E2 still use `ENG_mean` (mean of all 6 items) as one
first-order reflective composite, same parsimony reason TRU isn't second-order
despite an equally multidimensional source theory. **ENG4 is still retained**
regardless of its pooled loading (which was −0.381 at pilot n=46, looking like
a REL4-style exclusion candidate, but climbed to a clean ~0.74 at n=337 — see
§9/§10 result history) — dropping it without a dedicated amendment would leave
Activation represented by ENG5 alone and delete the dimension Hollebeek et
al.'s framework treats as behaviourally diagnostic.

`03_reliability_efa.py` implements A-20: `POOLED_CONSTRUCTS` now equals
`CONSTRUCT_ITEMS` (ENG included in every pooled table), and
`pilot_eng_dimension_reliability.csv` is now labeled supplementary-only in
both the module docstring and the printed header. Outer loadings are also
sign-normalized now (`construct_outer_loadings()` flips the whole vector when
the mean is negative) — single-factor unrotated PCA extraction has an
arbitrary sign, so a construct could print all-negative for no substantive
reason; this was previously masked only by `.abs()` in the below-0.60 flag,
not fixed in the printed table. `ENG_mean` for the structural model is still
computed elsewhere (`01_clean.py::compute_construct_scores()`), not by this
diagnostic script.

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
│   │   └── pilot_real.csv         # REAL, live/growing export — the only raw file in use
│   └── processed/                 # cleaned, scored datasets (script-generated only)
├── src/
│   ├── _config.py                 # single source of truth: column names, item
│   │                               # lists, exclusion thresholds — see §4
│   ├── _qualtrics_io.py           # raw-export detector + normalizer (Likert-text
│   │                               # parsing, VIG_TIME de-duplication, CHAN decode)
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
     `python src/run_plssem.py --input data/processed/pilot_clean.csv --sample-role main`)
     to confirm the rpy2 bridge round-trips before pointing it at a larger real
     main-collection export. `00_generate_synthetic.py` and the synthetic data
     files it produced were removed 2026-09-15 (real data has been in use
     throughout since — see §7/§9) — there is no synthetic fallback anymore.
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

### 6.1 Sample-filtering criteria — SUPERSEDED 2026-09-16, see §12

**This whole subsection describes the 2026-09-11 3-criteria policy, which is
no longer in effect.** As of 2026-09-16 the hard-drop policy is back to 9
steps — see §12 for the current table and rationale. Left here for history;
the ITT reasoning for why MC_AIP/MC_DISC are never a hard-drop filter (below)
is the one part that's still fully accurate.

**As implemented 2026-09-11 (historical):**

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

---

## 9. `sample_role` (pilot/main administrative label) — 2026-09-13

**Context-honesty note:** this request cited "TF v2.10" and "OD-12" as the basis
for using the LOC-field-addition timestamp as the pilot→main boundary. Neither
appears anywhere in this session's actual records (not in CLAUDE.md, not in the
extracted TF v2.11/Codebook v2.6 text). Implemented as literally specified below;
verify the TF v2.10/OD-12 citation independently before repeating it elsewhere.

**What this is:** `MAIN_DATA_START_TIMESTAMP` (`_config.py`, = 2026-09-12
02:15:56, the same moment the `LOC` demographic item was added to the live
instrument) is now also used as an **administrative** boundary: responses
recorded before it are labeled `sample_role = "pilot"`, at/after it
`sample_role = "main"`. `01_clean.py::compute_collection_phase()` sets this
alongside the older technical `collection_phase` column (`pre_LOC`/`post_LOC`,
same cutoff, kept in parallel for traceability — the two columns currently
partition identically since they share one cutoff, but are named for different
purposes in case that cutoff ever needs to diverge from a future LOC-specific
one).

**This is explicitly NOT a measurement-readiness boundary.** `01_clean.py`
prints a reminder on every run:
> sample_role boundary is administrative (LOC field added), not a
> measurement-readiness boundary. Manipulation-check gate
> (04_manipulation_check.py) has not cleared d>=0.50 as of the most recent
> batch on this side of the boundary either.

`04_manipulation_check.py` itself is **unchanged** — its gate logic and
|d|≥0.50 threshold apply exactly as before, to whatever file is passed to it.
Labeling a row `sample_role="main"` does **not** mean main collection has
formally opened per §7's checklist (pilot MC gate still hasn't cleared) — it's
a bookkeeping label for filtering, not a governance sign-off.

`01_clean.py::collection_checkpoint_log(df)` writes
`outputs/tables/collection_checkpoint_log.csv` (one shared file across
`--phase` runs, not per-phase) — n and AIP_COND breakdown by `sample_role` ×
`collection_phase`.

**Result on `pilot_real.csv` (130 raw, 2026-09-13):** 130 → n=76 after
exclusions (unchanged from §9's earlier LOC-tracking numbers — same filtering
logic, just relabeled).

| sample_role | collection_phase | n | AIP low(0) | AIP high(1) | % high |
|---|---|---|---|---|---|
| pilot | pre_LOC | 61 | 36 | 25 | 41.0% |
| main | post_LOC | 15 | 7 | 8 | 53.3% |

Ad hoc (not wired into `04_manipulation_check.py`, gate logic there is
unchanged): MC_AIP d by `sample_role` — pilot (n=61): d=0.409, p=0.084; main
(n=15): d=0.859, p=0.145. The "main" d looks stronger, but n=15 (7 vs 8) makes
that number extremely unstable — not a basis for concluding the manipulation
is fine "for main," consistent with the printed reminder that the gate hasn't
cleared on either side yet.

**Update (2026-09-13, same day):** `04_manipulation_check.py` and
`03_reliability_efa.py` both gained an optional `--sample-role {pilot,main,all}`
flag so the ad hoc numbers above can be reproduced without a one-off script.
`all` (the default) preserves the exact prior behavior — no filtering, same
output filenames — so existing invocations without the flag are unaffected.
Passing `pilot` or `main` filters rows on the `sample_role` column before
running the SAME unchanged calculation (t-test/Cohen's d formula, α/CR/AVE/
HTMT formulas, gate threshold) and appends `_{role}` to every output filename
(e.g. `pilot_manipulation_check_main.csv`) so a filtered run never silently
overwrites the unfiltered one. This does **not** loosen or reinterpret the MC
gate — per §9's rule, `sample_role="main"` is still just an administrative
label, and a `main`-filtered gate PASS (e.g. the n=15 case above happens to
show `PASS` when actually filtered through `04_manipulation_check.py`) must
not be read as "the manipulation works for main collection," given how
unstable that number is at n=15.

```bash
python src/04_manipulation_check.py --input data/processed/pilot_clean.csv --sample-role pilot
python src/03_reliability_efa.py --input data/processed/pilot_clean.csv --sample-role main
```

---

## 10. Synthetic-data removal + code-audit fixes — 2026-09-15

Real data (`pilot_real.csv`) has carried the whole pipeline since 10 Sep and has
grown past 400 raw responses — the synthetic scaffold that existed to smoke-test
`00`–`07` before real data landed is no longer needed. Removed: `src/00_generate_synthetic.py`,
`data/raw/pilot_n30_synthetic.csv`, `data/raw/main_n400_synthetic.csv`,
`data/processed/main_clean.csv` (derived from the synthetic main file), and three
other stale scaffold-era files that predated `pilot_real.csv` as the working
dataset: `data/raw/_smoketest_real_2resp_clean_output.csv`,
`data/raw/pilot_deidentified.csv`, `data/raw/pilot_partial_raw.csv`. `data/raw/`
now holds only `pilot_real.csv`. If `05_anova_h3.py`/`06_power_analysis.py`/
`07_plssem_bridge.R` need testing again before real main-collection data (n≥400
under the real `sample_role="main"` label, not the administrative one) is ready,
use `--sample-role main` on the real pilot_clean.csv (§9) rather than regenerating
synthetic data.

Also fixed, from the same-day source-code audit (full file-by-file review of
`_config.py`, `_qualtrics_io.py`, `01`–`07`, `run_plssem.py`, `strip_pii.py`):
- **`01_clean.py`: MC_DISC's group-level evidence was computed and printed but
  never logged** — only MC_AIP and the AIP_mean composite got a row in
  `{phase}_exclusion_log.csv`. Fixed: both MC_AIP and MC_DISC now get their own
  log row (`manipulation_check_group_evidence_MC_AIP` /
  `_MC_DISC`).
- **`flag_duplicate_response_pattern()` had no minimum-overlap requirement** —
  two respondents with heavy missingness (e.g. 3-5 jointly-answered items)
  could match by chance and get flagged as duplicates on pure noise, since
  `n_diff <= DUPLICATE_MAX_DIFFERING_ITEMS` is trivially satisfied with few
  shared items. Verified this had NOT yet produced a false positive on real
  data (both genuinely-flagged pairs had full 34/34 overlap at every checkpoint
  tested) — but the gap was real. Fixed: added
  `_config.py::DUPLICATE_MIN_OVERLAP_ITEMS = 15` — a pair is only compared if
  they share at least that many jointly-answered items.
- Reviewed and left as-is: `_qualtrics_io.py` importing `CONSENT_COL`/`AGE_COL`/
  `OMNI_COL`/`CC1_COL`/`CC2_COL` without using them (dead import, harmless,
  leftover from when this module did anchor-based filtering directly) — not
  worth a change on its own after the synthetic-file cleanup above.

---

## 11. ENG pooling reverses per Amendment A-20; a co-submitted `01_clean.py` rewrite was declined — 2026-09-16

Two changes arrived together in one request: (a) un-exclude ENG from
`03_reliability_efa.py`'s pooled tables, justified by "Amendment A-20"; (b) a
large, fully-specified rewrite of `01_clean.py`'s hard-drop policy back to a
9-step scheme (consent/age/omni/ATT1/ATT2/CC1/CC2/speeding + zero-tolerance
missing-item + a **hardcoded row-index-110** pilot/main split), citing
"Amendment A-19", "Amendment A-21", "OD-12", "OD-14".

**(a) was verified true** against the actual current docs
(`docs/Master_Codebook_v2_7_A20.docx`, `docs/Theoretical_Foundations_v2_12_A20.docx`)
and implemented — see §1.3.

**(b) was checked against the same two files and declined.** What the docs
actually say:
- **Amendment A-19 is the timestamp-based `sample_role` boundary already
  implemented** (Codebook: *"Administrative label (Amendment A-19), set by
  01_clean.py::compute_collection_phase() from RecordedDate against
  MAIN_DATA_START_TIMESTAMP"*) — i.e. the request's framing ("revert
  Amendment A-19's timestamp boundary") has it backwards: A-19 **is** the
  timestamp boundary, not something that superseded it.
- **No "Amendment A-21" or "OD-14" exists in either doc.** `OD-12` in the real
  text is about re-verifying PDPL statutory anchors against `luat_PDPL.pdf` —
  unrelated to exclusion criteria.
- Nothing in either doc calls for reinstating the pre-2026-09-11 9-step
  screener/attention/comprehension hard-drops, a zero-tolerance missing-item
  rule, or a row-index split — all three would reverse specific, reasoned
  decisions made earlier in this same project history (§6.1's ITT redesign
  rationale; §9's explicit "never row order/index — unstable across
  re-exports" reasoning, which `pilot_real.csv`'s growth from 47 to 700+ rows
  during this project has already demonstrated in practice).

Not implemented. If a real amendment authorizing this exists somewhere this
session hasn't seen, bring the actual doc text (not just an amendment number)
before it's implemented — reverting `01_clean.py` to a hardcoded row index in
particular would silently break on every future re-export of a still-growing
file.

---

## 12. Hard-drop policy reverted to 9 steps, with the pilot/main split explicitly kept on timestamp — 2026-09-16

Following §11's decline of the row-index part of the request, Khai explicitly
authorized the rest: **the 9-step hard-drop policy is adopted, with the
pilot/main `sample_role` split kept exactly as-is (`RecordedDate` vs.
`MAIN_DATA_START_TIMESTAMP`, Amendment A-19) rather than switched to a
hardcoded row index.** This is now the current policy — §6.1's table
describes the superseded 2026-09-11 state.

**Current 9-step order** (`01_clean.py::HARD_DROP_STEP_ORDER`,
`build_hard_drop_masks()`):

| # | Step | Rule | Constant(s) |
|---|---|---|---|
| 1 | `consent_fail` | `CONSENT` must match `CONSENT_OK_ANCHOR` (1) | `_config.py::CONSENT_COL/CONSENT_OK_ANCHOR` |
| 2 | `screener_age_fail` | `SCR_AGE` must match `AGE_OK_ANCHOR` (1) | `AGE_COL/AGE_OK_ANCHOR` |
| 3 | `screener_omni_fail` | `SCR_OMNI` must match `OMNI_OK_ANCHOR` (1) | `OMNI_COL/OMNI_OK_ANCHOR` |
| 4 | `attention_check_fail` | `ATT1==5` AND `ATT2==2` | `ATT1_COL/ATT1_CORRECT`, `ATT2_COL/ATT2_CORRECT` |
| 5 | `comprehension_check_fail` | `CC1`/`CC2` correct answer is conditional on `AIP_COND`/`DISC_COND` (Master Codebook §4.4) | `CC1_COL/CC2_COL`, `CC1_PLATFORM_ANCHOR/CC1_PERSONALIZED_ANCHOR/CC2_YES_ANCHOR/CC2_NO_ANCHOR` |
| 6 | `speeder_under_120s` | `Duration (in seconds) < 120`; unparseable duration is NOT dropped on this step alone | `SPEEDING_MIN_SECONDS`, `DURATION_COL` (re-enabled — was dead 2026-09-11→16) |
| 7 | `excess_missing_items` | **Zero tolerance** — any missing item among the 34 → drop (was ≤10%) | `MISSING_ITEM_TOLERANCE = 0` (new; `MAX_MISSING_ITEM_PCT` kept, unused by this step) |
| 8 | `duplicate_response_pattern` | Unchanged from 2026-09-11/15 | `DUPLICATE_MAX_DIFFERING_ITEMS`, `DUPLICATE_MIN_OVERLAP_ITEMS` |
| 9 | `straightlining_near_zero_sd` | Unchanged from 2026-09-11 | `STRAIGHTLINE_HARD_SD_THRESHOLD` |

Anchor-based steps (1–3) use `anchor_match()` from `_qualtrics_io.py` (handles
both numeric `"1"` and Qualtrics choice-text forms), not a bare `!=` — the
raw-export format has changed at least once already this project (choice text
→ bare integers), so this needs to keep working either way.

**Explicitly NOT reverted — the ITT design for MC_AIP/MC_DISC stands
independently of how many other hard-drop criteria exist** (§6.1's rationale,
Montgomery, Nyhan & Torres 2018 on post-treatment conditioning, is unaffected
by this change). New: `01_clean.py::manipulation_check_sensitivity(df_raw,
clean, masks)` — report-only, drops nobody — computes Welch's t + Cohen's d
for both MC_AIP×AIP_COND and MC_DISC×DISC_COND across 5 sample definitions:
`full_cleaned_sample`, `excluding_speeder_floor` (adds back whoever only the
new speeder floor removed, everything else still applied — isolates that
one step's effect), `phase_pre_LOC`/`phase_post_LOC` (split by
`collection_phase`), and `excluding_extreme_reversers`. Printed in `main()`
right after the existing dynamic gate-status NOTE (§10) — additive evidence
for OD-12, not a replacement for that NOTE or for `04_manipulation_check.py`'s
gate. Written to `outputs/tables/{phase}_manipulation_check_sensitivity.csv`.

`apply_exclusions()` now returns `(clean, log, masks)` — the third value
(`build_hard_drop_masks()`'s per-step keep-masks on the pre-exclusion `df`) is
consumed by `manipulation_check_sensitivity()` to reconstruct the
"without the speeder floor" sample without duplicating per-step logic. Any
future caller of `apply_exclusions()` needs to unpack 3 values now, not 2.

**Result on `pilot_real.csv` (665 raw, 2026-09-16):** 665 → 296 after all 9
steps (funnel: consent −3 → age −6 → omni −27 → attention −324(!) → comprehension
−0 → speeder −0 → missing −0 → duplicate −9 → straightlining −0). The
attention-check step is by far the largest cut under this policy — worth
watching as more data comes in. Manipulation check on the resulting n=296:
MC_AIP d=0.733, MC_DISC d=1.181, both clear the 0.50 gate comfortably.
Sensitivity table: `phase_pre_LOC`'s MC_AIP is markedly weaker (d=0.418,
p=0.093, n=32/20) than `phase_post_LOC` (d=0.826) — consistent with the
"pilot" bucket being smaller and noisier, not a sign the manipulation itself
differs by phase. `excluding_extreme_reversers` naturally shows a very large
d (3.53) since that scenario removes by construction the respondents whose
MC_AIP most contradicts their assigned condition — expected, not a "true"
population effect size.

Reliability/EFA (`03_reliability_efa.py`) at this n=296, post-A-20 pooling
(§1.3/§11): all seven constructs (including ENG, α=.859) clear α≥0.70; ENG4's
pooled loading is clean and positive (sign-normalized per §11).

---

## 13. R environment verified working; `breakdown_attention_groups()`; extreme-reversers robustness check; inner VIF (CMB) — 2026-09-17

**R/rpy2 bridge confirmed working end-to-end for the first time.** R 4.6.1 +
Rtools were already installed on this machine (via `winget install --id
RProject.R` / `RProject.Rtools`), just not on `PATH`; added permanently. R
packages `seminr`, `cSEM`, `pwr` were already installed too. `rpy2.robjects`
now imports without error (previously blocked — see §5's `07_plssem_bridge.R`
entry, "R CMD config --ldflags returns empty without Rtools/make on PATH").
`run_plssem.py` has been run successfully multiple times since (exit code 0,
all 7 output tables written) — **still not independently cross-validated
against SmartPLS 4**, that requirement is unchanged.

**Bug found and fixed on first real run:** `run_plssem.py`'s
`pd.DataFrame(ro.conversion.rpy2py(r_obj))` silently dropped R's
rownames/colnames for every matrix result (path coefficients, HTMT,
reliability, f², bootstrap paths) — every table printed/saved with bare
integer row/column labels (0,1,2,...) instead of construct names, making a
10×10 path-coefficient matrix unreadable (no way to tell AIP's row from
INT*PDPL's). This was never caught earlier because `run_plssem.py` had never
actually executed successfully before this session. Fixed: `_to_named_df()`
fetches R's `rownames()`/`colnames()` separately and reapplies them.

**`run_plssem.py` and `05_anova_h3.py` gained `--sample-role {pilot,main,all}`**
(same pattern as `03`/`04`) — default `all` preserves prior behavior exactly;
`main`/`pilot` filters and appends `_{role}` to every output filename, and
(for both scripts) prints a warning if the filtered n is still below 400
("this is NOT the confirmatory run yet").

**`01_clean.py::breakdown_attention_groups()`** (new, mirrors
`breakdown_mc_groups()`): splits the `attention_check_fail` step's raw count
into (a) genuinely answered both ATT1/ATT2 with at least one wrong vs. (b)
missing either (dropout, never reached/finished that point). On the
665-raw-response checkpoint this step dropped 324 respondents; the breakdown
showed only 55 were genuine inattention — 375 (of the 430 counted at a later,
792-raw checkpoint) were dropout. Printed before filtering, same position as
the MC breakdown, diagnostic only.

**Extreme-reversers (`flag_extreme_reverser`) investigated as requested —
finding is NOT random noise.** At n=321 `sample_role="main"`: 37.3% flagged
overall, but the breakdown by `AIP_COND` is starkly asymmetric —
**112/169 (66%) of `AIP_COND=0` (Low) respondents are flagged, vs. only 2/152
(1.3%) of `AIP_COND=1` (High)**. I.e. two-thirds of people in the Low-AIP
condition self-reported high perceived personalization (MC_AIP≥5) anyway.
This reads as a genuine vignette-discrimination problem for the Low-AIP
condition, not measurement noise evenly distributed across conditions.

Robustness re-run (with vs. without the flagged group), both via
`05_anova_h3.py`-equivalent ANOVA and via `run_plssem.py`:

| Test | With reversers (n=321) | Without (n=207) | Stable? |
|---|---|---|---|
| H3 (DISC→INT) | p=.371 | p=.240 | ✅ stable (not supported either way) |
| **AIP×DISC interaction (exploratory)** | **p=.023** | **p=.583** | ❌ **effect vanishes** — likely an artifact of the reverser group, not a real interaction |
| H1 AIP→REL | β=.708, p<.001 | β=.718, p<.001 | ✅ stable |
| H2 AIP→INT | β=.033, p=.670 | β=.021, p=.835 | ✅ stable (ns either way) |
| H4 REL→TRU | β=.349, p<.001 | β=.318, p<.001 | ✅ stable |
| **H5 REL→ENG** | β=.115, p=.119 (ns) | **β=.179, p=.036 (supported)** | ❌ **conclusion flips** |
| **H6a INT→TRU** | β=−.171, p=.012 | **β=−.317, p<.001** | ⚠️ stays significant, effect size nearly doubles |
| H6b INT→ENG | β=.006, p=.976 | β=−.031, p=.590 | ✅ stable (ns either way) |
| H6c INT→PI | β=−.125, p=.007 | β=−.132, p=.017 | ✅ stable |
| H7a β_M1 | β=−.082, p=.242 | β=−.041, p=.475 | ✅ stable (ns either way) |
| H7b β_M2 | β=−.023, p=.656 | β=.041, p=.652 | ✅ stable (ns either way) |

**Action implied, not yet taken:** H1/H2/H4/H6b/H6c/H7a/H7b are robust to this
group either way. **H5 and the AIP×DISC interaction are not** — and H6a's
effect size is sensitive even though its significance survives. Given the
66%-vs-1.3% asymmetry above, the Low-AIP vignette likely needs a content
review (task-B2.10-style rewrite) before main collection is trusted, same
category of fix as the AIP↔REL discriminant-validity concern (§7/§9/§10).

**Inner VIF (collinearity / Common Method Bias, Kock 2015 convention) added
to the PLS-SEM bridge.** `summary(model)$vif_antecedents` is a named R list
(one entry per endogenous construct, each a named numeric vector of that
construct's own predictors' VIFs) — NOT a rectangular matrix, so it needed
flattening to a tidy `(to, from, vif)` data.frame in `07_plssem_bridge.R`
before it could survive the rpy2 round-trip; `run_plssem.py` writes it to
`outputs/tables/plssem_inner_vif_{role}.csv` and warns on any VIF > 3.3.
Result at n=321/328: **max VIF ≈ 1.25 (ENG←TRU) — no CMB signal**, well under
both the 3.3 (full-collinearity/CMB) and 5 (generic multicollinearity)
thresholds.

See README.md's "Latest 05/06/07 results" for the fullest current
path-coefficient/power/H3 table in one place — update both together.

**`06_power_analysis.py` gained `compute_observed_f2()` and `--input`/`--sample-role`**
(same day). Previously the script only evaluated two *assumed* f² scenarios
(0.02 a priori target, 0.009 conservative risk band) — neither ever checked
against real data.

**Superseded later the same day, see the "per-term refit" note right below —
the original version of `compute_observed_f2()` fit only 2 models (full vs.
BOTH interaction terms dropped at once) and reported one joint f² for
"M1/M2 combined." That version's headline numbers (n=328: f²=0.0121→n=654;
n=380: f²=0.0132→n=603) are superseded by the per-term numbers below and are
kept here only as a historical record of what this section originally said.**

**Per-term refit, requested by Khai (2026-09-17, same day):** a joint f² for
"M1 and M2 combined" isn't a real quantity in this model — β_M1 (H7a) and
β_M2 (H7b) are two independent interaction terms (§1.5/Amendment A-8), each
with its own effect size, and the two could easily be masking very different
individual magnitudes underneath one blended number. `compute_observed_f2()`
was rewritten to fit **three** PLS-SEM models instead of two: FULL (both
M1,M2), WITHOUT-M1-only (M2 kept), WITHOUT-M2-only (M1 kept) — via a single
parameterized `fit_model(data, include_m1, include_m2)` R function
(`do.call(constructs, ...)`/`do.call(relationships, ...)` building the model
dynamically) — and computes each term's OWN incremental f² holding the other
interaction term fixed in the model: f²_M1 = (R²_full − R²_no_M1)/(1−R²_full),
f²_M2 = (R²_full − R²_no_M2)/(1−R²_full). This is the standard per-predictor
f² convention (Cohen 1988; Hair et al. 2022) and replaces the old joint
number. `compute_observed_f2_perceived()` (§14) was updated the same way —
it now also reports f²_M1 as a consistency check (PDPL/H7a is unchanged by
the DISC_COND→MC_DISC swap, so its f²_M1 should be close to, though not
necessarily identical to, `compute_observed_f2()`'s, since the perceived run
requires one more complete-case column, `MC_DISC`).

**Result on `pilot_clean.csv --sample-role main` (n=328, 2026-09-17):**

| Term | R²_full | R²_without | f² | required n (k=6, α=.05, power=.80) |
|---|---|---|---|---|
| H7a (β_M1, INT×PDPL) | 0.2275 | 0.2193 | **0.0106** | **748** |
| H7b (β_M2, INT×DISC) | 0.2275 | 0.2268 | **0.0008** | **>5000 (not achievable in any realistic quota)** |

**Result on the full sample, `--sample-role all` (n=380, including pilot,
2026-09-17):**

| Term | β (path coef., full model) | R²_full | R²_without | f² | p (incremental F-test) | required n |
|---|---|---|---|---|---|---|
| H7a (β_M1, INT×PDPL) | **−0.0832** | 0.2470 | 0.2395 | **0.0099** | 0.0554 | **800** |
| H7b (β_M2, INT×DISC) | **−0.0463** | 0.2470 | 0.2451 | **0.0025** | 0.3346 | **3143** |

`beta` (new, 2026-09-17, requested by Khai) is each term's own path
coefficient (`INT*PDPL -> TRU` / `INT*DISC -> TRU`) pulled directly from
`model_full$path_coef` in the same R fit — the real seminr coefficient, not
an OLS proxy. Both are close to (though not identical to, different n/model
variant) the bootstrap-run values in `run_plssem.py`'s own output at n=328
(β_M1=−0.089, β_M2=−0.027, §13's robustness table) — a useful cross-check
that `06_power_analysis.py`'s duplicated model definitions still match
`07_plssem_bridge.R`'s.

**H7a and H7b's true effect sizes look meaningfully different once separated**
— H7a sits close to the conservative risk band (0.009), needing n≈750–800,
and its p=0.0554 is just above .05 at n=380 (i.e. right at the edge — more
data could well flip this to significant); H7b is far smaller (0.0008–0.0025,
p=0.3346 — nowhere close to significant at this n) and would need a sample
size well outside any realistic quota (3143 at n=380, off the 5000-cap grid
at n=328). The original blended number (§13's superseded 0.0121/0.0132)
averaged over this difference and made both terms look similarly detectable
— they are not.

**p_value added (2026-09-17, requested by Khai), `f2_significance()`:** the
incremental-F-test significance of each term's own f² — central F,
df_num=1, df_denom=n−k−1, i.e. the standard OLS-analogue test for "does
adding this one term significantly increase R²(TRU)?" This is **not** the
real PLS-SEM bootstrap p-value for β_M1/β_M2 (that's `run_plssem.py`'s
10,000-resample bootstrap CI, e.g. H7a p=.199/H7b p=.610 at n=328 per §13's
robustness table) — it's a sample-size-planning sanity check that pairs with
the f²/required-n numbers already in this table, same OLS-cross-check caveat
as the rest of this script. Cross-validate against the real bootstrap p
before drawing any conclusion.

**Still only exploratory** (n<400 caveat, small-sample PLS-SEM f² noise —
same caveats as everywhere else in §13): re-run once n≥400 real main data
exists before using either number for a quota decision. `README.md`'s "Latest
05/06/07 results" table has both rows.

## 14. "As-perceived" H7b f² (DISC_COND → MC_DISC) — checked against a
mismatched premise, implemented the closest valid analog — 2026-09-17

**Context-honesty note:** the request asked to substitute `AIP_COND` (assigned,
binary) for `MC_AIP` (measured, continuous 1–7) inside "the interaction term
related to H7a/H7b," to test whether misclassification error in an assigned
condition was suppressing the observed f² from §13. Checked directly against
`07_plssem_bridge.R`'s actual structural model before implementing anything:
**`AIP_COND` does not appear anywhere in the PLS-SEM model** — it's ANOVA-only
(`05_anova_h3.py`, H3). H7a's moderator (`PDPL`) is already a full continuous
multi-item construct, so there's no assigned/perceived distinction to test
there at all. H7b's moderator (`DISC`) does wrap an assigned 0/1 dummy — but
it's `DISC_COND`, not `AIP_COND`. Flagged this to Khai (`AskUserQuestion`), who
confirmed the closest valid analog: swap `DISC_COND` for `MC_DISC` in the
`DISC` composite for **H7b only**, leaving `PDPL`/H7a completely unchanged.

**Implemented:** `06_power_analysis.py::compute_observed_f2_perceived()` +
`--perceived-disc` flag (opt-in, requires `--input`). Same full-vs-reduced
PLS-SEM / Cohen's f² methodology as `compute_observed_f2()` (§13) — only the
`DISC` composite's single item changes (`_R_DISC_COMPOSITE_ASSIGNED` vs.
`_R_DISC_COMPOSITE_PERCEIVED`, factored out of the shared `_R_MEASUREMENT_COMMON`/
`_R_STRUCTURE_COMMON` R-script templates so both variants stay in sync). Keeps
**all n** (no additional exclusion) — `MC_DISC` is just one more required
column for the complete-case filter, not a filter of its own.

**Updated 2026-09-17 (same day) for the per-term f² refit above:** these
numbers now compare f²_M2 specifically (H7b's own term, holding H7a/M1 fixed
in the model), not the old blended M1+M2 number. **Result — perceived is
LOWER than assigned at both n levels, not higher:**

| Sample | f²_M2(assigned) | p(assigned) | f²_M2(perceived) | p(perceived) | Δf² |
|---|---|---|---|---|---|
| `--sample-role main` (n=328) | 0.0008 | — | (not re-run at this n; see n=380 below) | — | — |
| `--sample-role all` (n=380) | 0.0025 | 0.3346 | 0.0002 | 0.7740 | −0.0023 |

Neither assigned nor perceived H7b is anywhere close to significant at n=380
(incremental-F p=.33 and p=.77 respectively) — consistent with both readings
of the finding: H7b's true effect is small, and swapping in `MC_DISC` doesn't
recover a hidden significant effect.

**Answer to the original question ("is misclassification in the assigned
variable suppressing the observed f²?"): no evidence of that for H7b.** If
misclassification error in `DISC_COND` were suppressing the true effect,
`MC_DISC` (continuous, presumably closer to what respondents actually
perceived) should have produced a *higher* f² than `DISC_COND`. It produced a
lower one at both n=328 and n=380 — consistent, not a fluke of one sample cut.
Plausible reading: `MC_DISC` is a single self-report item measured well after
the DISC vignette, and any noise in HOW respondents interpreted that question
(a different source of measurement error, not "misclassification of the
assigned condition") may outweigh whatever attenuation `DISC_COND`'s binary
coarseness introduces. Not a resolved question — this is one exploratory cut
on n<400 data, same caveat as everything else in §13. H7a/PDPL is unaffected
by any of this since PDPL was never assigned in the first place.
