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

**Newer TF exists (2026-09-22, superseding the §16 description below):
`docs/Theoretical_Foundations_v2_13_A22_main400_DRAFT (1).docx` — the `.md` draft
`Theoretical_Foundations_v2_13_A23_DRAFT_r2.md` that §16 was written against no longer
exists on disk; this `.docx` is the only TF file present now, and its content moved on
without §16 being updated. Confirmed with Khai (2026-09-22): **Amendment A-22 IS
ratified** (Project Lead & Faculty Advisor, 21 Sep 2026) — Holm-Bonferroni is removed
project-wide, and H7a is re-signed to Dampening (βM1 < 0). The same session also
authorized **Amendment A-23** (H7b re-signed to Dampening, βM2 < 0; H7a/H7b estimation
of record switched from one pooled two-interaction OLS model to two separate
single-moderator regressions per Hayes' PROCESS Model 1 template) — A-23 is recorded in
the TF docx but is, like A-22 before it, still pending the Project Lead & Faculty
Advisor sign-off; only the sign/estimator change itself is authorized. **See §17 for
the full reconciliation — §16 below is left as a historical record of a snapshot that
is no longer current; do not trust its "NOT ratified" / "decision rule is BCa + Holm"
claims.**

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

## 15. Full 01→04 + `run_plssem.py` re-run on the grown raw export (888 raw,
n=388 clean) — MC gate now clears; run-log added — 2026-09-17

**Context-honesty note on the triggering request:** it asked for "toàn bộ path
H1-H9" — this project's hypothesis codes are locked at H1–H7b (§0); there is
no H8 or H9 anywhere in TF/Codebook. Read as shorthand for "every path in the
model" (which is what's reported below), not as a claim that H8/H9 exist. It
also asked to switch to "p-value bootstrap thật (percentile, không dùng
OLS-analogue)" — checked `run_plssem.py`'s actual output against seminr's
installed source (`seminr:::parse_boot_array`, seminr 2.5.0) before changing
anything: the "Bootstrap P Val" column this script has printed since §13 was
**already** `2 * min(mean(boot_array <= 0), mean(boot_array > 0))` — the
standard empirical percentile bootstrap p-value, computed straight from the
10,000-resample distribution. It was never an OLS/t-distribution analogue —
that phrase only ever applied to `06_power_analysis.py`'s separate
`f2_significance()` (§13/§14), a different, clearly-labeled sanity check for
sample-size planning, not for testing an already-estimated model. No code
change was needed for the p-value method itself; the module docstring in
`run_plssem.py` now spells out the exact formula so this doesn't need
re-verifying next time.

**Implemented:** `run_plssem.py` now prints the final n actually going into
`estimate_pls()` (after `--sample-role` filtering and the PLS-SEM
complete-case requirement) and cross-checks it against the row count right
before that filter, warning if they differ (would mean some row has a missing
`DISC_COND`/item despite passing `01_clean.py`'s zero-tolerance missing-item
step). Every run now also appends one row (UTC timestamp, input file,
`--sample-role`, n before/after the complete-case filter) to
`outputs/tables/plssem_run_log.csv` — created with a header on first run,
appended after that — so repeated runs on the still-growing `pilot_real.csv`
can be told apart instead of only ever showing the latest numbers.

**Full pipeline re-run, no `--sample-role` filter (`pilot_real.csv` grown to
888 raw responses):**

```
consent −5 → age −6 → omni −37 → attention −440 → comprehension −0 →
speeder −0 → missing −0 → duplicate −12 → straightlining −0
888 raw → n=388 clean
```

n=388 confirmed as the exact n `run_plssem.py` used (`[run_plssem] n going
into PLS-SEM: 388 ... 0 more dropped for missing values` — matches
`pilot_clean.csv` exactly, logged in `plssem_run_log.csv`).

**Manipulation-check gate now clears outright, both checks:** MC_AIP
d=0.632 (p<.001), MC_DISC d=1.119 (p<.001) — both comfortably above the
|d|≥0.50 gate for the first time in this project's history (earlier
checkpoints, e.g. §12's n=296 or §7's early pilot numbers, were borderline or
failing for MC_AIP specifically). **HTMT is now clean everywhere**, including
AIP↔REL (0.800, was flagged >0.85 at multiple earlier pilot checkpoints,
§7/§9/§10) — `03_reliability_efa.py` prints "OK: no construct pair exceeds
the 0.85 HTMT threshold" for the first time.

**Full PLS-SEM path table at n=388, α=.05, real percentile bootstrap p (10,000
resamples):**

| Path | β | p (bootstrap, percentile) | Verdict |
|---|---|---|---|
| H1 AIP→REL | 0.715 | <.001 | Supported |
| H2 AIP→INT | 0.040 | .531 | Not supported |
| H4 REL→TRU | 0.341 | <.001 | Supported |
| H5 REL→ENG | 0.107 | .082 | Not supported |
| **H6a INT→TRU** | **−0.240** | **<.001** | Supported — effect size grew noticeably vs. n=328 (was −0.178, §13) |
| H6b INT→ENG | −0.017 | .709 | Not supported |
| H6c INT→PI | −0.142 | <.001 | Supported |
| E1 TRU→ENG | 0.404 | <.001 | — |
| E2 ENG→PI | 0.617 | <.001 | — |
| DISC→INT (spec. term) | −0.059 | .253 | — |
| DISC→TRU (spec. term) | 0.043 | .321 | — |
| **PDPL→TRU (spec. term)** | **0.103** | **.046** | newly crosses .05 at this n (was .084 at n=328) |
| H7a INT×PDPL→TRU (β_M1) | −0.083 | .185 | Not supported |
| H7b INT×DISC→TRU (β_M2) | −0.063 | .255 | Not supported |

H7a/H7b are still not significant at n=388, consistent with §13/§14's power
analysis (both need n well above 388 to reliably detect at their observed
effect sizes). **Reliability**: all 7 substantive constructs clear α/ρ_A/ρ_C
> 0.70, AVE > 0.50. **Inner VIF**: max ≈1.29 (ENG←TRU) — still no CMB signal.
The 3-cell f² gap (INT→TRU, DISC→TRU, PDPL→TRU showing `NaN` in
`plssem_f_squared.csv`) from §13 persists unchanged at this n — still an open
item, not investigated yet.

**n=388 is still below the n≥400 main-collection target** (CLAUDE.md §5) —
this remains an exploratory run, not the confirmatory one. It is, however,
the strongest checkpoint so far: MC gate clears, HTMT is clean, and H6a's
effect has both grown and tightened. `README.md`'s "Latest 05/06/07 results"
table still shows the older n=328/380 numbers from §13/§14 — not yet
reconciled with this n=388 run since this request only covered `01`→`04` +
`run_plssem.py`, not `05_anova_h3.py`/`06_power_analysis.py`.

## 16. TF v2.13 DRAFT (A-21/A-22/A-23) reconciled with the pipeline; changes since §15 — 2026-09-20

**Status of the source.** `docs/Theoretical_Foundations_v2_13_A23_DRAFT_r2.md` (title
"Version 2.13 (DRAFT — A-21, A-22 and A-23 pending ratification)"). All three
amendments are self-declared drafts: they need Khải's own statement of reason (left
blank as `[ ]` in the file) and ratification by the faculty advisor (Tống Gia Tường).
**Nothing in A-21..A-23 governs the pipeline yet.** Ratified state remains v2.12/A-20
(§1.3, §11); the ratified prediction for H7a/H7b is still buffering, β_M > 0
("attenuates the negative slope of INT→TRU", TF §A.5.1).

**What the draft says.**
- **A-21:** records the first full structural model (n=394): supported H1, H4, H6a, H6c;
  not supported H2, H3 (ANOVA F=1.320, p=.251), H5, H6b, H7a, H7b; both β_M negative
  (opposite to buffering) and non-significant; no alternative estimator substituted
  for two-stage PLS-SEM in search of significance. Also closes Introduction citation
  fixes (Aydin 2026 market figures → Wasilewski & Kolaczek 2024; Xie 2026; Kumar et
  al. 2019) and opens a flag that the §A.1/§A.7 "Aydin (2026)" characterization does
  not match the verified Sustainability paper (unresolved; affects the H7a novelty
  argument, not its empirical status).
- **A-22:** proposes OLS moderated regression as the estimation of record for H7a/H7b
  (§C.2.2). Disclosed as a POST-DATA decision. PLS-SEM estimates stay reported alongside.
- **A-23:** respecifies the predicted sign of H7a/H7b to negative (amplification), post
  hoc, two-tailed, BCa 95% CI, Holm across the two; original prediction + verdict kept;
  any "supported" is labelled "supported (post hoc)", never confirmatory.
- **§C.2.2 fixed specification:** TRU ~ INT + PDPL + DISC + INT×PDPL + INT×DISC + REL on
  equal-weighted mean scores, INT/PDPL/DISC mean-centred before products; case bootstrap
  10,000, BCa 95% CI, seed recorded; HC3 and classical p alongside; Holm across H7a/H7b;
  f²; simple slopes with bootstrap CIs; full sample = record, main-only = sensitivity;
  moderated mediation and re-targeting are exploratory only.

**Verified against outputs (draft's own instruction: "verify before circulation").**
Matches: the n=394 PLS-SEM values in A-21 (H1 .716, H4 .350, H6a −.239, H6c −.141,
H2 .039/p .539, H5 .103/p .094, H6b −.020/p .664, H7a −.084/p .180, H7b −.062/p .258,
E1 .399, E2 .613), the H3 ANOVA, MC_AIP d=.658 / MC_DISC d=1.119; Table C.2-M rows for
"PLS R cross-check n=346" and both "OLS Model 1" rows (n=397 / n=345). The row
"SmartPLS 4.1.1.8" is the user's own run and could not be verified here.

**Discrepancies found (flagged, not silently fixed).**
1. **VIF in A-22 (2.57 / 2.61 for INT→TRU and DISC×INT→TRU)** vs this pipeline's seminr
   two-stage inner VIF for TRU's predictors: INT 1.019, INT×DISC 1.024, INT×PDPL 1.026
   (max over all inner VIFs ≈1.30). Different specification (the draft's is the uncentred
   product in SmartPLS); the draft should say which software the 2.57/2.61 came from.
2. **OD-14 is stale.** It says `01_clean.py` applies three criteria and the codebook's
   consent/age/omni/attention/comprehension/speeding drops are disabled. The 9-step policy
   has been in force since 2026-09-16 (§12). OD-14 should be updated or closed.
3. **OD-17(ii) n reconciliation.** The different n are export growth, not different case
   selection: raw 888 → n=388; 912 → 394 (A-21); 915 → 397 (OLS full, SmartPLS import 397;
   main-only 345); 917 → 398 (current; main-only 346). Table C.2-M mixes main-only 345
   (OLS rows) and 346 (PLS rows) for that reason. Current sample of record: n=398.
4. **TF §C.2 requires BCa CIs for the PLS β_M; `07_plssem_bridge.R` reports seminr's
   percentile CI.** Not implemented; open gap. (The §C.2.2 OLS script does use BCa.)
5. Interaction-term SEs/p in the draft's OLS Model 1 rows came from an earlier bootstrap
   seed; a re-run gave DISC full p_boot .072 vs .063 (Monte Carlo variation only).

**New: `src/13_h7_ols_record.R` implements §C.2.2 exactly** → `outputs/tables/h7_ols_record_C22_DRAFT.csv`
(filled row "OLS pooled model per §C.2.2 (BCa 10,000)" of Table C.2-M). Labelled DRAFT.

| | Full (record) n=398 | Main-only n=346 |
|---|---|---|
| H7a β_M1 (centred mean scores) | −0.0721, BCa [−0.198, 0.001], p_boot .0996, Holm .199, classical .031, HC3 .153, f² .0120 | −0.0760, [−0.199, 0.005], p .108, Holm .216, classical .033, HC3 .160, f² .0135 |
| H7b β_M2 | −0.1106, [−0.299, 0.094], p .249, Holm .249, classical .152, HC3 .282, f² .0053 | −0.0805, [−0.285, 0.142], p .436, classical .345, HC3 .482, f² .0026 |
| Verdict fields | H7a/H7b: not supported (original buffering) and not supported (post hoc amplification) | same |

Simple slopes of INT→TRU are negative everywhere and significant at PDPL +1SD (−.277) and
DISC=1 (−.248) but not at PDPL −1SD or DISC=0: the base negative effect, not evidence of
moderation. **Under the specification the draft itself fixes, neither hypothesis is
supported under either direction, in either sample** — the single nominally significant
cell seen earlier (OLS Model 1, main-only, bootstrap p=.044) does not survive the fixed
specification (REL covariate, both interactions, BCa, Holm).

**Standing rules for future sessions.** Do not treat A-22/A-23 as ratified. The decision
rule for H7 is the one fixed in §C.2.2 (BCa + Holm + sign), not whichever estimator or
sample gives p<.05. The many H7 variants run (PLS, PLS-MGA + MICOM, moderated mediation,
J-N, OLS Model 1 classical/HC3/bootstrap, §C.2.2) are the multiverse; none is dropped.
MICOM: PDPL groups partially invariant; DISC groups NOT compositionally invariant for INT
(p=.006) and ENG (p=.039), so the DISC MGA is not interpretable.

**Changes since §15 not yet documented elsewhere:** `01_clean.py` — CC_Gate termination
diagnostic (`breakdown_cc_gate_terminations`, 383/915 raw, 0 survive filtering), SmartPLS
numeric export, and a 3-way split `clean_pilot.csv` (n=52) / `clean_main.csv` (346) /
`clean_pooled.csv` (398, identical to `pilot_clean.csv`, which stays the file existing
scripts read) with `smartpls_input_{pilot,main,pooled}.csv`; `07_plssem_bridge.R` /
`run_plssem.py` — Fornell-Larcker (7 reflective constructs), outer VIF, specific indirect
effects (percentile CI on the same 10,000 resamples) with Zhao-Lynch-Chen classification,
f² for INT/DISC→TRU filled (seminr sets NA for interaction components by design; PDPL→TRU
cannot be estimated), `--tag` output suffix; `06_power_analysis.py` — per-term f²/β/p,
`--perceived-disc`; new scripts `08_data_quality_robustness.py` (duration/Mahalanobis
sensitivity, stable), `09_h7_supplementary.py/.R` (PLS-MGA permutation + moderated
mediation), `10_jn_micom.R` (Model 1, J-N, MICOM), `11_ols_model1_bootstrap.R`,
`12_process_moderated_mediation.R`, `13_h7_ols_record.R`. Power (OLS analogue, checked
against `pwr::pwr.f2.test`): H7a f²≈.010 → ~790 clean n; H7b f²≈.005 → ~1,580 (f²=.0046 → 1,706).

## 17. §16 was stale; A-22 is actually ratified; H7b re-signed negative (A-23); H7 estimation
switched to two separate Hayes PROCESS Model 1 regressions; Holm removed everywhere — 2026-09-22

**Discrepancy found and reconciled.** §16 described the current TF as
`docs/Theoretical_Foundations_v2_13_A23_DRAFT_r2.md` — a draft with A-21/A-22/A-23 all
unratified, Holm still the H7 decision rule. That `.md` file does not exist on disk. The
only TF file present in this session is the untracked
`docs/Theoretical_Foundations_v2_13_A22_main400_DRAFT (1).docx` (its filename still says
"DRAFT", which is itself misleading). Extracted and read directly (via `python-docx`,
`pip install python-docx` — not previously installed): its actual content is materially
ahead of what §16 describes:
- **Amendment A-22 is ratified** — "Ratified by Project Lead & Faculty Advisor, 21
  September 2026" is written into Table 0k in the document itself.
- **Holm-Bonferroni is already formally removed project-wide** ("multiple testing
  adjustments such as the Holm-Bonferroni method are formally removed... induces severe
  Type II error rates, masking substantive interaction effects" — citing Hair et al. 2022,
  Henseler et al. 2015, Becker et al. 2018).
- **The replacement decision rule is NOT "keep HC3 only".** It is: nominal two-tailed
  p < .05 **and** a 5,000-resample non-parametric bootstrap 95% CI (percentile/BCa)
  excluding zero. HC3 and classical p survive only as reported-alongside diagnostics, not
  as the criterion.
- **H7a was already re-signed to Dampening (βM1 < 0)** by A-22 — opposite the original
  buffering prediction (βM1 > 0). Confirmed with Khai before treating this as fact (it
  contradicts §16's "not ratified" framing).

Confirmed with Khai this session (`AskUserQuestion`): apply the TF's actual rule (nominal
p + bootstrap CI, not "HC3-only"), and treat A-22 as genuinely ratified. Do not repeat
§16's now-stale claims about A-22/A-23 in future sessions; this section supersedes them.

**New instruction the same session, applied to the TF file directly:** re-sign **H7b**
to Dampening (βM2 < 0) as well — mirroring A-22's H7a logic — and switch the H7a/H7b
estimation of record from one pooled OLS model containing both interaction terms to
**two separate single-moderator OLS regressions, one per hypothesis, following Hayes'
PROCESS Model 1 template** (Y = TRU_mean; X = INT_mean, centred; W = PDPL_mean centred
for H7a, DISC_COND centred for H7b; the other institutional carrier and REL_mean enter
each model as covariates, with no interaction term of their own).

**Recorded as Amendment A-23** (added to the TF docx's Table 0k, and to Table 3's H7b
row, and the A.5.1 prose was rewritten for H7b using the same Legal-Sensitization/salience
logic already used for H7a — disclosure raises conscious, transaction-specific salience
of the personalization practice at the moment of exposure, which is expected to sharpen
rather than soften the perceived breach when that practice is also intrusive).
**Authorized directly by Khai in this session (2026-09-22) — not yet independently
ratified by the Project Lead & Faculty Advisor the way A-22 was.** Per this project's own
standing rule for A-21/A-22/A-23-style changes (§16), A-23 needs Khai's own fuller
written rationale and faculty sign-off before it governs the manuscript; the sign flip and
estimator change are implemented in the pipeline now on Khai's direct instruction, but the
TF docx itself flags A-23 as pending the same ratification A-22 already received. A
bracketed supersession note was also added at the historical (pre-ratification) §C.2.2
paragraph in the docx, pointing forward to the ratified rule rather than rewriting it —
consistent with this project's practice of never silently rewriting a dated, disclosed
methodological choice (§6.1, §11, §16's own "context-honesty" notes).

**TF docx edits made (via `python-docx`, run/edit/save; the file could not be edited as
plain text since it's a binary `.docx` — `Read` on it fails, and there is no in-repo
tool for round-tripping the raw `word/document.xml` safely other than `python-docx`,
which edits whole-paragraph/whole-cell text and does not preserve sub-paragraph run-level
formatting boundaries — acceptable here since none of the edited spans had internal
formatting):**
1. Table 0k: added a new "A-23" row (Amendment / Rationale and Authority columns) as
   described above.
2. Table 3 (the "Updated Amendment A-22" copy near the end of the document): H7b's
   Predicted Sign cell changed from `βM2 > 0 (Buffering)` to `βM2 < 0 (Dampening)`, and its
   Theoretical Rationale cell rewritten to the disclosure-salience mechanism above.
3. §A.5.1 prose (the post-A-22 copy): heading changed from "De Facto Assurance & The
   Buffering Effect — Disclosure Level (H7b, βM2 > 0)" to "...The Dampening Effect...
   (H7b, βM2 < 0)", and the paragraph body rewritten accordingly.
4. The historical (pre-ratification, still says "Holm's correction across H7a and H7b")
   §C.2.2 verdict-rule paragraph was left in place (dated, disclosed snapshot) with a
   bracketed `[Note added 22 September 2026: superseded...]` appended, pointing at the
   ratified rule and both sign changes rather than rewriting the original text.

**Code changes to match:**
- **`src/13_h7_ols_record.R` rewritten.** Was: one pooled OLS model
  (`TRU_mean ~ REL_mean + INT_c + PDPL_c + DISC_c + INT_x_PDPL + INT_x_DISC`), 10,000
  resamples, Holm-adjusted bootstrap p as part of the verdict rule, output
  `outputs/tables/h7_ols_record_A22_main_INTERIM_DRAFT.csv`. Now: **two independent
  Hayes PROCESS Model 1 regressions** —
  `H7a: TRU_mean ~ REL_mean + DISC_COND + INT_c + PDPL_c + INT_c:PDPL_c` and
  `H7b: TRU_mean ~ REL_mean + PDPL_mean + INT_c + DISC_c + INT_c:DISC_c` — each with its
  own Cook's-distance-flagged-cases sensitivity run, its own simple slopes, its own
  BCa bootstrap CI (5,000 resamples, matching the TF's `A-22` spec, was 10,000), and
  **no Holm adjustment anywhere** — verdict is CI-excludes-zero at nominal p < .05.
  HC3/classical p are kept as reported-alongside columns only, per TF's actual rule
  (§ this section, "Discrepancy found"), not as an HC3-only criterion. Output renamed
  to `outputs/tables/h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv`. The verdict table's
  `sign_all_N`/`supported_as_predicted` columns now read against **Dampening (βM < 0)**
  as the predicted direction for both H7a and H7b, not the old buffering (β > 0)
  prediction.
- **`src/14_final_results_table.py` updated**: Section G's header, source CSV filename,
  and the removed `p_holm` column reference; Section E's H7a/H7b predicted-sign labels
  in the PLS-SEM path table changed from `+ (buffering, ratified)` to
  `- (dampening, A-22)` / `- (dampening, A-23)` (this also fixes the sign-match check
  used to classify "Supported" vs. "Significant, OPPOSITE sign", which previously tested
  against the wrong direction).
- **`src/11_ols_model1_bootstrap.R`** (an earlier, still-useful exploratory sensitivity
  script that already ran H7a/H7b as two separate `TRU_mean ~ INT_mean * W` models, one
  per sample) — its header comment describing the predicted direction as buffering
  (βM > 0, TF v2.12) was corrected to note the A-22/A-23 sign flip; the script's logic
  itself needed no change since it never assigned a verdict, only reported b/p/CI.
- Checked `09_h7_supplementary.{py,R}`, `10_jn_micom.R`, `12_process_moderated_mediation.R`,
  `06_power_analysis.py`, `07_plssem_bridge.R`, `run_plssem.py` for Holm and for
  hardcoded buffering-direction language — none found; these scripts report β/p/CI
  without assigning a directional verdict, so they need no change (per-term f²/power
  numbers in `06_power_analysis.py` and PLS-SEM path coefficients in `07_plssem_bridge.R`
  are estimator outputs, not predictions, and are unaffected by which sign was predicted).

**Not done, left to the user:** the TF docx's filename still literally contains "DRAFT",
which is inconsistent with the ratified-A-22 content now inside it — left as-is, since
renaming a file the user is actively working in is not this session's call to make.
`docs/Theoretical_Foundations_v2_13_A23_DRAFT_r2.md`, which §16 was written against, was
never found — if it exists elsewhere it was not reconciled against the docx here; if it
was deleted, §16's description of its content is now purely historical.

## 18. `src/` pruned and renumbered to match the model actually being reported — 2026-09-23

Requested by Khai after reviewing which scripts the current model (PLS-SEM for H1, H2,
H4, H5, H6a, H6b, H6c, E1, E2; two-way ANOVA for H3; two separate Hayes PROCESS Model 1
OLS regressions for H7a/H7b, per A-22/A-23; descriptives; VIF; HTMT; EFA cross-loadings)
actually needs. **Removed** (none were tracked in git, so nothing was lost from history):
- `09_h7_supplementary.py` / `.R` — ran PLS-MGA (permutation) + moderated mediation for
  H7. TF §1.5 says PLS-MGA is **no longer required for H7** (DISC is a pooled
  predictor/moderator now, not a between-group factor), and moderated mediation was
  always "exploratory only" (§C.2) — neither fed the reported model once
  `09_h7_ols_record.R` (renumbered from `13_...`, see below) became the estimation of
  record for H7a/H7b.
- `10_jn_micom.R` — Johnson-Neyman + MICOM. MICOM was a prerequisite only if PLS-MGA was
  used *somewhere* (§1.5); with `09_h7_supplementary` gone, nothing in the repo calls
  PLS-MGA anymore, so MICOM has no remaining purpose here.
- `11_ols_model1_bootstrap.R` — an earlier draft of the same idea now implemented
  properly in `09_h7_ols_record.R` (formerly `13_...`): two separate simple-moderation
  OLS regressions, one per hypothesis, bootstrapped. Superseded, not complementary — kept
  a slightly different sensitivity axis (main vs. pooled sample) but duplicated the core
  logic of the file that is now the actual estimation of record.
- `12_process_moderated_mediation.R` — moderated mediation, exploratory only per TF §C.2,
  not part of the H1–H7b/E1/E2 register being reported.

**Kept, on Khai's explicit instruction, despite being outside the narrow H-testing table**
(they serve Method/robustness sections, not redundant with anything else in `src/`):
- `06_power_analysis.py` — a priori power analysis for the Method section's sample-size
  justification.
- `08_data_quality_robustness.py` — data-quality sensitivity (duration/Mahalanobis),
  supplementary robustness, not a duplicate of any other script.
- `strip_pii.py` — PII-stripping utility (§8's PII fix), a data-governance tool, not a
  statistical-model script; unaffected by which estimator H7 uses.

**Renumbered** (both files' internal filename self-references and cross-references in
other files were updated to match; no git history to preserve since neither was tracked):
- `13_h7_ols_record.R` → **`09_h7_ols_record.R`**
- `14_final_results_table.py` → **`10_final_results_table.py`** (its docstring's list of
  required upstream scripts now says `09_h7_ols_record.R`, not `13_...`)

Current `src/` numbering after this cleanup: `01_clean.py`, `02_descriptives.py`,
`03_reliability_efa.py`, `04_manipulation_check.py`, `05_anova_h3.py`,
`06_power_analysis.py`, `07_plssem_bridge.R` (+ `run_plssem.py`, unnumbered, the rpy2
orchestrator for it), `08_data_quality_robustness.py`, `09_h7_ols_record.R`,
`10_final_results_table.py`, plus the unnumbered support files `_config.py`,
`_qualtrics_io.py`, `strip_pii.py`. §2's repo-layout diagram still shows the old
`00`–`07` scaffold-era layout and was not rewritten (it already predates §7 onward) —
this section is the current source of truth for `src/` contents; treat §2 as historical.
Left over from the old numbering: `07_plssem_bridge.R`'s `boot_obj` field in its return
list was kept (harmless, still exported) even though its only consumer,
`09_h7_supplementary.py`, is gone — flagged in a comment rather than removed, since
removing it would be a behavior change to a script beyond the scope of this cleanup.

**`outputs/tables/` pruned the same day** to match — 23 files removed, none git-tracked
(`git ls-files` confirmed none of them were ever committed; most were already covered by
`.gitignore`'s `outputs/tables/*.csv` rule from §8, so nothing here touches git history):
- Outputs of the deleted scripts, orphaned once their producer was removed:
  `h7_supp_mga.csv`, `h7_supp_moderated_mediation.csv`, `h7_supp_summary.csv` (from
  `09_h7_supplementary.*`); `h7_jn_regions_PDPL.csv`, `h7_micom_cSEM.rds` (from
  `10_jn_micom.R`); `h7_ols_model1_bootstrap_by_sample.csv`, `h7_process_model1.csv`
  (from `11_ols_model1_bootstrap.R`); `h7_process_modmed_main.csv` (from
  `12_process_moderated_mediation.R`).
- Superseded H7 estimation-of-record snapshots from earlier methodology states:
  `h7_ols_record_A22_main_INTERIM_DRAFT.csv` (pre-rewrite pooled two-interaction model,
  Holm-based, old filename) and `h7_ols_record_C22_DRAFT.csv` (§16's even earlier
  pre-A-22 §C.2.2 spec, also Holm-based) — both fully superseded by
  `h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv` (current, from `09_h7_ols_record.R`,
  no Holm, two separate Hayes PROCESS Model 1 regressions).
- `final_results_summary.csv` / `final_results_summary_v2.csv` — ad hoc pre-cleanup
  summary tables whose H7a/H7b rows still used the old pure PLS-SEM two-stage estimate
  (β_M1=−0.084, β_M2=−0.063, no OLS/PROCESS columns at all) — superseded by
  `FINAL_results_main_all.csv`/`.xlsx` (from `10_final_results_table.py`, the one script
  that reads the current OLS-PROCESS-Model-1 output for Section G).
- 11 byte-for-byte duplicate files: every `plssem_{X}_main_table.csv` was confirmed
  (`diff`) identical to its `plssem_{X}_smartpls_main.csv` sibling — both were produced
  by two `run_plssem.py --tag` runs on the same frozen data (n=346 checkpoint), one
  tagged `table`, one tagged `smartpls`. Kept the `_smartpls_main` name (it's the one
  tied to the TF's SmartPLS-4 cross-validation requirement, §5); deleted the `_table`
  twin as a pure duplicate.

**Left alone, on purpose:** the no-suffix `plssem_*.csv` / `H3_anova_disclosure_main_effect.csv`
files (the `--sample-role all`, pooled pilot+main outputs — a distinct, still-legitimate
sample-role cut, not a duplicate of `_main`), and every `pilot_*`/`main_*` descriptive,
reliability, HTMT, cross-loading, cell-balance, and manipulation-check file (all current
outputs of scripts that are still in `src/`, explicitly part of what Khai asked to keep:
descriptives, VIF, HTMT, cross-loadings).

## 19. Figures added to `10_final_results_table.py` — 2026-09-23

Requested by Khai: a Figure 1 (Structural Model Diagram) and Figure 2 (Interaction Plot).
Integrated into `10_final_results_table.py` (not a new script) since it already reads
every table these figures draw from (`b` = `plssem_bootstrap_paths_main.csv`, `o` =
`h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv`, `main` = `clean_main.csv`) — no new
analysis, just plotting numbers already in Sections E/G. Needs `matplotlib` (already a
dependency) and `statsmodels.formula.api` (already a dependency, used here for the first
time in this script).

- **`figure1_structural_model()`** → `outputs/figures/Figure1_structural_model_main.png`.
  SOR layout (Stimulus/Organism/Response columns, per TF §A.1): solid arrows = H1–H6c,
  dotted = E1/E2, dash-dot = the DISC→INT specification term, dashed = H7a/H7b moderation
  (PDPL and DISC arrows converge on the INT→TRU path). Every arrow is labeled with the
  same β/b and significance star already computed in Section E (PLS-SEM) or Section G
  (H7a/H7b OLS record) — nothing is recomputed for the figure.
- **`figure2_interaction_plot()`** → `outputs/figures/Figure2_interaction_plot_main.png`.
  Two panels (H7a: PDPL ±1SD; H7b: DISC=0/1), each a simple-slopes plot of INT→TRU. This
  **refits** the same two Hayes PROCESS Model 1 OLS specifications as `09_h7_ols_record.R`
  directly in Python (`statsmodels.formula.api.ols`, same formulas, same mean-centering)
  rather than reading `h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv` — that CSV only
  stores the slope coefficients, not a full predicted-value grid across INT, so a proper
  line plot needs the refit. Both lines slope down (as expected, H6a is negative); the
  Dampening prediction (A-22/A-23) shows up as the high-PDPL / With-Disclosure line
  falling *faster* than the low-PDPL / No-Disclosure line, crossing partway through the
  INT range — visually consistent with §17's sign change even though H7b's underlying
  coefficient is not statistically significant (Figure 2 does not depict significance;
  Figure 1 and Sections E/G's p-values do).

**Known inconsistency, not fixed here:** at the time these figures were generated,
`clean_main.csv` had grown to n=363 (raw export now 991, §"mới input mẫu mới" exchanges),
but `h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv` (Section G / the H7a-H7b dashed arrows
in Figure 1) was still the n=356 run from the previous checkpoint — `10_final_results_table.py`
reads existing tables only and runs no analysis of its own for Sections A–G, so Section E
(fresh PLS-SEM at n=363) and Section G (stale OLS-record at n=356) are drawn from two
different n's in the same output until `09_h7_ols_record.R` is re-run on the current
`clean_main.csv`. Figure 2's own OLS refit, by contrast, reads `clean_main.csv` live and
so is already on n=363 — only Figure 1's H7a/H7b dashed-arrow labels (pulled from the
stale `o` table) carry the n=356 numbers. Re-run `09_h7_ols_record.R` before treating
Figure 1's H7a/H7b annotations as current.

## 20. 14 manuscript Result tables added, plus the new analysis they required — 2026-09-23

Requested by Khai: Tables 1–14 for the thesis's Results chapter. All added to
`10_final_results_table.py` (functions `table1_...` through `table14_...`, called at the
end of the script) — same "read existing outputs, run no new analysis" pattern as
Sections A–H, except three genuinely new statistics had to be added upstream first
because nothing in the pipeline computed them yet:

**New in `07_plssem_bridge.R` / `run_plssem.py`:**
- **R² / Adjusted R²** per endogenous construct (`model$rSquared`, trivial extraction) →
  `plssem_rsquared_{role}.csv`.
- **Q²predict** (Shmueli, Ray, Estrada & Danks, 2019 PLSpredict routine): 10-fold,
  10-repetition out-of-sample prediction via `seminr::predict_pls()`, seed 123.
  Q²predict per indicator = 1 − SSE/SSO, SSE from the returned held-out prediction
  error, SSO from each indicator's deviation around the **full-sample** mean (the
  standard reporting approximation — `predict_pls()` doesn't expose per-fold
  training-set means, which the strict blindfolding definition uses). Reported per
  construct as the mean across its own indicators, alongside the PLS-vs-LM-benchmark
  RMSE comparison Shmueli et al. use to grade predictive power. **Bug caught and fixed
  same day:** the power label was initially graded only from the RMSE comparison
  (High/Medium/Low by how many indicators PLS beat the naive LM benchmark on), which
  mislabeled INT as "High" even though its Q²predict is *negative* (−0.015) — Shmueli
  et al.'s own rule is that Q²predict ≤ 0 means no predictive relevance regardless of
  the RMSE comparison. Fixed: Q²predict ≤ 0 now short-circuits straight to
  `"None (Q2predict <= 0)"` before the RMSE-based grading runs. → `plssem_q2predict_{role}.csv`.
- **Extended specific indirect effects** (was 2 chains, now 6): added `REL->ENG->PI`,
  `INT->ENG->PI` (through ENG only, not TRU), and the two 3-step serial chains
  `REL->TRU->ENG->PI` / `INT->TRU->ENG->PI` (`seminr::specific_effect_significance()`
  supports a `through` vector up to 4 mediators). `run_plssem.py`'s Zhao-Lynch-Chen
  classification step was generalized: a chain whose ultimate `from->to` has no
  corresponding direct path in the structural model (e.g. `REL->PI`, never estimated —
  only `INT->PI`/H6c is) reports its estimate/CI/p but is labeled
  `"N/A (no direct path in model)"` instead of forcing a classification against a path
  that doesn't exist.

**New in `09_h7_ols_record.R`:**
- **HC3-robust SE** alongside the HC3 p that was already there (`hc3_stats()` now
  returns both; new `SE_HC3` column).
- **Breusch-Pagan and White heteroscedasticity tests** per model (both the full-N and
  Cook's-D-trimmed sensitivity runs), via the newly-installed `lmtest` package
  (`bptest()`; White implemented as the common `bptest(m, varformula = ~fitted(m) +
  I(fitted(m)^2))` approximation, per Wooldridge's textbook simplification, not the
  full all-regressors-and-cross-products White test) → new output
  `outputs/tables/h7_heteroscedasticity_diagnostics.csv`.
  **Bug found and fixed:** `bptest()` with the `fitted(m)`-based `varformula` crashed
  ("incompatible dimensions" in `lm.wfit`) specifically on the Cook's-D-trimmed
  sensitivity data (`dat_wo <- d[-flagged, ]`), because subsetting a data.frame keeps
  the original (now non-sequential) row names, and `bptest()`'s auxiliary regression
  mis-sizes itself against that. Fixed with `rownames(dat_wo) <- NULL` right after the
  subset — confirmed this is a `bptest()`/row-name interaction, not a data problem
  (the same model on the full, sequentially-row-named `d` never had this issue).
- **A third PDPL evaluation point for H7a's simple slopes**: was 2 (−1SD, +1SD), now 3
  (−1SD, Mean [PDPL_c=0], +1SD) — `analyse()`/`run_hypothesis()` generalized from
  fixed `slope_lo`/`slope_hi` arguments to a named-vector `levels` argument so the
  bootstrap `stat()` function returns a variable-length vector. H7b intentionally
  stays at its 2 natural levels (DISC=0/1 has no third "mean" category).

**`data/_config.py` addition:** `DEMOGRAPHIC_VALUE_LABELS`, transcribed verbatim from
Master Codebook v2.7/A-20 §4.8's variable table (AGE_BAND, GEN, EDU, INC, FREQ, PLAT,
PRIOR) — same pattern as the existing `REF_LABELS`. **LOC is deliberately excluded**:
checked the Codebook directly (both the paragraph text and the actual docx table cell)
and confirmed its row only says "choice numbers" with no numeric-to-region mapping
anywhere in the document — labeling it would mean fabricating a mapping that doesn't
exist in any source this session has seen.

**The 14 tables** (each also written as its own
`outputs/tables/Table{N}_....csv`, and all bundled into one
`outputs/tables/Manuscript_Results_Tables.xlsx`, one sheet per table):

| # | Table | Source(s) |
|---|---|---|
| 1 | Demographic Profile | `main_sample_profile.csv` + `DEMOGRAPHIC_VALUE_LABELS` (LOC/REF excluded, see above) |
| 2 | Cell Distribution + randomization check | `main_cell_balance.csv` + a chi-square goodness-of-fit test (H0: equal 25%/cell) added here in Python (`scipy.stats.chisquare`) — new, wasn't computed anywhere before |
| 3 | Manipulation Check | `pilot_manipulation_check_main.csv`, relabeled |
| 4 | Reliability & Validity (item loadings + construct α/ρA/CR/AVE in one table) | `plssem_outer_loadings_main.csv` + `plssem_reliability_main.csv`, merged via `CONSTRUCT_ITEMS`; DISC excluded (never a reliability construct, §0) |
| 5 | Fornell-Larcker | `plssem_fornell_larcker_main.csv` |
| 6 | HTMT | `plssem_htmt_main.csv` |
| 7 | Inner VIF | `plssem_inner_vif_main.csv`, NaN rows (single-predictor constructs) dropped |
| 8 | Path Coefficients & Hypothesis Testing | `plssem_bootstrap_paths_main.csv` + `plssem_f_squared_main.csv`, with an explicit Decision column (sign-checked against each H's predicted direction) |
| 9 | R² and Q²predict | new `plssem_rsquared_main.csv` + `plssem_q2predict_main.csv` (see above) |
| 10 | Specific Indirect Effects | extended `plssem_indirect_effects_main.csv` (see above, 6 chains not 2) |
| 11 | Heteroscedasticity Diagnostics | new `h7_heteroscedasticity_diagnostics.csv` (see above) |
| 12 | Moderation Results (H7a/H7b) | `h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv`, beta_M rows only, now with HC3 SE |
| 13 | Sensitivity Check (full vs. Cook's D-trimmed) | same file, pivoted side-by-side |
| 14 | Simple Slopes at 3 PDPL levels | same file, new 3-level slope rows (see above) |

**Verified end-to-end** by re-running `09_h7_ols_record.R` and `run_plssem.py` on the
current `clean_main.csv`/`pilot_clean.csv --sample-role main` (n=363 at the time) and
then `10_final_results_table.py` — all 14 tables and the combined `.xlsx` wrote
successfully. **INTERIM caveat applies to all 14**: n=363 is still below the N_main=400
stopping rule (TF §C.2.2). H7a's beta_M CI happened to include 0 at this exact n=363
checkpoint (it excluded 0 at the n=356 checkpoint two turns earlier in this session) —
a reminder that "supported"/"not supported" verdicts genuinely move as `pilot_real.csv`
keeps growing, not a sign anything is broken.

## 21. Figure 2's H7a panel redesigned as a Johnson-Neyman plot — 2026-09-23

Requested by Khai, matching a reference JN plot image (pink = n.s., teal = p<.05,
dashed vertical line + "W = ..." label at the JN transition, black bar marking the
observed range of the moderator, θ(W) equation annotated on the plot). Implemented in
`figure2_interaction_plot()`'s Panel A only — Panel B (H7b) intentionally kept as the
existing 2-line simple-slopes plot, since DISC is a binary (0/1) moderator with no
continuous range to run a Johnson-Neyman sweep over; JN only applies to H7a's
continuous moderator (PDPL).

Method: refits the same H7a OLS model as `09_h7_ols_record.R`
(`TRU_mean ~ REL_mean + DISC_COND + INT_c * PDPL_c`) via `statsmodels`, then switches to
**HC3-robust covariance** (`get_robustcov_results(cov_type="HC3")`) for the conditional-
effect band specifically because Table 11 already found significant heteroscedasticity
in this exact model (Breusch-Pagan p<.001, White p<.001 on the full-N run) — a classical
homoscedastic SE band would understate the true uncertainty. The conditional effect
θ(W) = b_INT_c + b_inter×(W − mean(PDPL)) and its SE (from the HC3 covariance of
b_INT_c and the interaction term) are evaluated over a grid spanning the observed PDPL
range ±15%; the JN point is found where |θ/SE| crosses the two-tailed critical t-value,
located by linear interpolation between the two nearest grid points. At n=363: JN point
W≈5.18 — the conditional effect of INT on TRU is only significant (and negative,
consistent with the Dampening prediction) above that PDPL level; below it, the
confidence band includes zero.

## 22. Manuscript tables renumbered Table 2-15 (was Table 1-14), plus 2 restyled to match
reference tables Khai supplied ("An & Ngo") — 2026-09-23

Requested by Khai: shift every table number by +1 (freeing "Table 1" for something
outside this pipeline's scope — not specified, not built here), and restyle two tables
to match two reference images from a published paper's Table 2 and Table 6. All function
names, docstrings, and output CSV filenames in `10_final_results_table.py` were renamed
to match (`table1_...` -> `table2_...` etc., uniformly +1 through the old Table 14 ->
new Table 15); nothing in the underlying analysis changed, only labeling/formatting.

**New numbering:** Table 2 Demographic Profile (+ supplementary Table 2b, the LOC=5
city breakdown), Table 3 Cell Distribution, Table 4 Manipulation Check, Table 5
Reliability & Validity (restyled, see below), Table 6 Fornell-Larcker, Table 7 HTMT,
Table 8 Inner VIF (restyled, see below), Table 9 Path Coefficients, Table 10 R²/Q²predict,
Table 11 Indirect Effects, Table 12 Heteroscedasticity, Table 13 Moderation Results,
Table 14 Sensitivity Check, Table 15 Simple Slopes.

**Table 5 (reliability/validity) restyled** to match the reference "Table 2" image: per
construct, Cronbach's alpha / rho_A / CR / AVE are now printed only on that construct's
FIRST item row and left blank on the rows below it (was: repeated on every item row) —
matches the reference table's own layout of not restating construct-level numbers per
item. Also **added an Outer VIF column** (from `plssem_outer_vif_main.csv`, not
previously in this table), since the reference table has a per-item VIF column too.
rho_A and AVE are kept as extra columns beyond what the reference table itself shows —
the reference paper's table only has Loadings/alpha/CR/VIF, but TF's own reliability
thresholds require rho_A and AVE as well, so dropping them to match the reference
exactly would have lost information this project's own governing rules require.

**Table 8 (inner VIF) restyled** from a long `(to, from, vif)` list into a
**predictor × outcome matrix** to match the reference "Table 6" image: rows are every
construct that predicts something in the model (AIP, REL, INT, PDPL, DISC, TRU, ENG,
INT*PDPL, INT*DISC), columns are the 5 endogenous constructs (REL, INT, TRU, ENG, PI),
and a blank cell means that predictor doesn't appear in that outcome's own structural
equation (not a missing value) — same convention the reference table uses.

**Cross-checked against the Master Codebook, per Khai's request:** Table 2's demographic
categories (`_config.py::DEMOGRAPHIC_VALUE_LABELS`) were already transcribed directly
from Master Codebook v2.7/A-20 §4.8 in §20 — re-confirmed here, no changes needed.
Table 5's item list/counts per construct come from `_config.py::CONSTRUCT_ITEMS`, which
is itself the ratified register from §1 of this file (TF §C.4 / Codebook §4.7) — also
unchanged. AIP_COND/DISC_COND coding (0=Low/No, 1=High/With) used in Table 4's column
labels was confirmed against `_config.py`'s own `AIP_COND_COL`/`DISC_COL` constants
rather than re-derived from scratch.

**Not carried forward from the reference images:** the reference Table 2's specific
construct names (Perceived Personalization/Relevance/Trust/Usefulness, Purchase
Intention) are from an unrelated published paper, not this project's own constructs
(AIP/REL/INT/TRU/ENG/PDPL/PI per §0/§1) — only the table STYLE (layout, which stats
repeat vs. which don't, matrix format) was adopted, not its variable names or numbers.

**Follow-up same day:** Khai noticed the reference Table 2's "Items" column quotes the
full item statement, not just a code — Table 5's "Item" column now shows
`{CODE}: "{English wording}"` (e.g. `AIP1: "ShopWave can analyze my consumption
level."`). Added `_config.py::ITEM_WORDING_EN`, all 30 items (AIP1-5, REL1-4, INT1-5,
TRU1-6, ENG1-6, PI1-4, PDPL1-4) transcribed verbatim from Master Codebook v2.7/A-20's
own "Item (EN)" column for each block — the finalized main-collection wording
(`PROJ_MAIN_final_v2`), not the superseded pilot-stage text. DISC has no entry (never a
Likert item, §0).

## 23. 10th hard-drop step added: non-Vietnam respondents excluded — 2026-09-23

**Context for the triggering question.** Khai asked why `clean_main.csv` had "1 dữ liệu
không trọn vẹn" — investigated directly: `clean_main.csv` (n=367 at the time) has one
row (`ResponseId R_4smw8GeFt5DsaQN`) with all 9 `DEMOGRAPHIC_COLS` (AGE_BAND, GEN, LOC,
EDU, INC, FREQ, PLAT, PRIOR, REF) missing simultaneously, despite passing the
zero-tolerance 34-item missing-item filter (step 7) — a respondent who fully completed
the substantive battery but skipped the entire demographics block. This is not a bug:
`excess_missing_items` (§12 step 7) only checks the 34 reflective items, by design —
demographics were never part of that check, and a handful of other rows also have one
or two individual demographic fields missing (`AGE_BAND`/`GEN`/`LOC`/etc., each ~1 row)
for the same reason. Nothing was changed for this — it's expected behavior, not a defect.

**Then, a separate, actionable request in the same message:** restrict the sample to
Vietnam residents — drop any respondent who filled in `LOC=5` ("Khac/Other") with a
free-text answer naming a location outside Vietnam. Checked `Table2b_LOC_other_breakdown.csv`
(§22) for the full list of LOC=5 answers first: of ~26 distinct free-text answers, only
2 are actually foreign — "Wollongong" (Australia) and "L.A" (Los Angeles, USA); every
other answer is a genuine Vietnamese province/city name (Tây Ninh, Đắk Lắk, Nghệ An,
An Giang, etc.), and "Prefer not to say" / missing free text are non-answers, not foreign
claims, so neither was touched.

**Implemented as a 10th hard-drop step, `non_vietnam_location`** (`01_clean.py`,
inserted into `HARD_DROP_STEP_ORDER` right after `duplicate_response_pattern`, before
`straightlining_near_zero_sd`): drops a row only if `LOC == 5` **and** its
(stripped, casefolded) `LOC_5_TEXT` exactly matches an entry in the new
`_config.py::NON_VIETNAM_LOC5_TEXT` set (currently `{"wollongong", "l.a"}`). Every other
case — `LOC` in {1,2,3} (Ho Chi Minh/Ha Noi/Da Nang), a Vietnamese `LOC=5` answer, a
missing/blank `LOC_5_TEXT`, or `LOC` itself missing (pre-LOC-field rows, §9) — passes
through untouched. **This list is hand-maintained, not a geocoding lookup** — a future
raw-export respondent typing a new foreign place name will not be caught automatically;
add their (casefolded) answer to `NON_VIETNAM_LOC5_TEXT` after checking
`Table2b_LOC_other_breakdown.csv` again, the same way this pair was found. Symmetrically,
never add a genuine Vietnamese place name to this set no matter how it's spelled.

**Result on `pilot_real.csv` (1003 raw, 2026-09-23):** the new step drops exactly 2 rows
(confirmed: Wollongong and L.A, the only two matches) — pooled n 419→417, main n 367→365.
9-step hard-drop policy (§12) is now a **10-step policy**; `outputs/tables/pilot_exclusion_log.csv`
shows `non_vietnam_location` as its own funnel row between `duplicate_response_pattern`
and `straightlining_near_zero_sd`.

## 24. Raw file renamed to `raw_data.csv`; processed output collapsed from a 3-way
pilot/main/pooled split to exactly 2 files — 2026-09-24

**Trigger:** Khai renamed the live raw export from `data/raw/pilot_real.csv` to
`data/raw/raw_data.csv` (confirmed on disk — `pilot_real.csv` no longer exists,
`raw_data.csv` does) and asked that, after cleaning, there be **only two** processed
datasets: `pilot_clean_data` and `main_clean_data` — no pooled (pilot+main) file anymore.

**`01_clean.py` changed:** the previous write step produced `data/processed/{phase}_clean.csv`
(the pooled file, e.g. `pilot_clean.csv` under the historical `--phase pilot` usage) plus a
3-way split (`clean_pilot.csv`, `clean_main.csv`, `clean_pooled.csv`) and 3 SmartPLS exports
(`smartpls_input_{pilot,main,pooled}.csv`). Now it writes **only**:
- `data/processed/pilot_clean_data.csv`
- `data/processed/main_clean_data.csv`
- `smartpls_input_pilot.csv` / `smartpls_input_main.csv` (kept, pooled variant dropped)

The pooled write and the `clean_pooled.csv`/`{phase}_clean.csv` duplicate names are gone
entirely — there is no third combined file. `--input` is unaffected (still a plain CLI
argument, already pointed at whatever raw file is given: `python src/01_clean.py --input
data/raw/raw_data.csv --phase pilot`).

**Every downstream script's usage example / default-path comment** was updated from the
retired `data/processed/pilot_clean.csv` (the old pooled file, historically read with
`--sample-role {pilot,main}` for filtering) to point directly at
`data/processed/main_clean_data.csv` (or `pilot_clean_data.csv` where the pilot sample
specifically was meant): `02_descriptives.py`, `03_reliability_efa.py`,
`04_manipulation_check.py`, `06_power_analysis.py` (both usage lines and the `--input`
help text), `08_data_quality_robustness.py`, `09_h7_ols_record.R`, `run_plssem.py`, and
`10_final_results_table.py`'s actual `pd.read_csv(...)` call (not just a comment — this one
would have broken on the next run otherwise). The `--sample-role` flag in `03`/`04`/`06`/`05`/
`run_plssem.py` still works exactly as before (harmless no-op when the input file is already
single-role), it's just no longer *necessary* now that there's no pooled file to filter down
from. Historical/dated mentions of `pilot_real.csv` elsewhere (comments describing what was
verified on a specific date, e.g. `_config.py`'s TRU-count provenance notes) were left
untouched — they're dated facts about that session, not stale instructions.

**Cleanup:** deleted the now-orphaned old-named files from `data/processed/`:
`clean_main.csv`, `clean_pilot.csv`, `clean_pooled.csv`, `pilot_clean.csv`,
`smartpls_input_pooled.csv`. **Note:** `pilot_clean.csv` was, unlike the others, actually
git-tracked (pre-dates the `.gitignore` rule from §8, same historical gap) — its deletion
shows as `D data/processed/pilot_clean.csv` in `git status`; not staged or committed here,
left for Khai's own commit.

**Verified end-to-end on `raw_data.csv` (1043 raw, 2026-09-24):** `01_clean.py` →
`pilot_clean_data.csv` (n=52), `main_clean_data.csv` (n=381) → `09_h7_ols_record.R` →
`run_plssem.py --sample-role main` → `10_final_results_table.py` (all 15 tables + combined
`.xlsx`) — full chain runs clean with the new names. **n_main=381** at this checkpoint,
still below N_main=400 (TF §C.2.2) — INTERIM. H7a: supported (post hoc, Dampening) in both
the all-N and Cook's-D-trimmed runs at this n; H7b: not supported.

## 25. Standing rule: hold `run_plssem.py` until n>=395 — 2026-09-24

Khai deleted `outputs/tables/plssem_run_log.csv` (its running history of every past
`run_plssem.py` invocation, timestamp/input/n — see §24's "1. Có bị lưu lại lịch sử"
answer) and set a new policy: **do not run `run_plssem.py` again until
`main_clean_data.csv` reaches n>=395**, then run it and let the log start fresh from
there. Rationale (inferred, not stated explicitly): the log was getting cluttered with
many INTERIM checkpoint runs (§13 through §24) at n well under the 400 stopping rule;
starting the log over right before the confirmatory n>=400 window keeps it focused on
the runs that actually matter for the manuscript, rather than the whole growth history.

**Current count at the time of this rule (2026-09-24): n_main = 381** (from
`data/processed/main_clean_data.csv`) — 14 short of the n>=395 trigger. **Future
sessions: do not call `python src/run_plssem.py` for any reason (including a routine
"check current n" request) until n_main has been confirmed >=395 via `01_clean.py`'s
own funnel output** (checking `len(pd.read_csv("data/processed/main_clean_data.csv"))`
directly, or re-running `01_clean.py`, is fine and does not violate this rule — only
`run_plssem.py` itself is held back). Other scripts (`05_anova_h3.py`,
`09_h7_ols_record.R`, `10_final_results_table.py`, etc.) are NOT covered by this hold
unless Khai says otherwise — this rule is specific to `run_plssem.py` and its log.

**Still in force after §26**: §26 (TF reverted to A-21) made PLS-SEM the H7a/H7b
estimator of record, but that did NOT require re-running `run_plssem.py` — the
existing n=381 PLS-SEM outputs on disk were reused as-is; only `10_final_results_table.py`
was re-run to pick up the relabeling. This rule (hold `run_plssem.py` until n>=395)
remains the standing default.

## 26. TF reverted to v2.13/A-21 (Buffering restored, PLS-SEM single pooled model is the
H7a/H7b estimator of record); A-22/A-23 rescinded — 2026-09-24

**Discovery.** Khai asked to "update the project per the new TF." Checked `docs/` first,
per this file's own standing instruction to re-extract any higher/different-named TF
before trusting it: `docs/Theoretical_Foundations_v2_13_A22_main400_DRAFT (1).docx` (the
source of §17's A-22/A-23 changes) **no longer exists**. In its place:
`docs/Theoretical_Foundations_v2_13_A21_DRAFT.docx` — content-wise this is *earlier* in
the amendment lineage, not later: it absorbs only A-7 through A-21 (DRAFT, dated
20 Sep 2026, still pending ratification), and:
- **H7a/H7b predictions are the ORIGINAL Buffering direction**: β_M1 > 0, β_M2 > 0 (Table
  3/16's H7a/H7b rows both say "Prediction: β_M1/β_M2 [greater than] 0"). No mention of
  Dampening anywhere in the document (checked programmatically: 0 hits for "dampening",
  7 hits for "buffering").
- **§C.2 estimation is a single pooled two-stage PLS-SEM model** for H7a and H7b together
  (`"H7a and H7b are two independent second-order interactions on the same outcome. They
  are estimated in a single pooled model"`) — not two separate OLS/Hayes regressions.
- **Zero mentions of Holm, BCa (the abbreviation), PROCESS Model, or HC3** anywhere in the
  document (checked programmatically) — there is no OLS estimator described in this TF at
  all, of any kind.

**Confirmed with Khai (`AskUserQuestion`) before touching anything**, since this reverses
a large amount of §17's work: yes, treat this as the real, current governing TF — A-22 and
A-23 (Holm-Bonferroni removal, H7a/H7b re-signed to Dampening, the OLS Hayes PROCESS
Model 1 split promoted to "estimation of record") **are rescinded**. The document that
described them ratified is gone; whatever process produced it does not represent the
actual (still-unratified) TF lineage the team/faculty are tracking.

**Also confirmed with Khai:** keep running the OLS Hayes PROCESS Model 1 analysis exactly
as implemented (same regression specs, bootstrap, Cook's D sensitivity, HC3, Breusch-Pagan/
White) — it is **not deleted**, just demoted from "estimation of record" to a
**supplementary/exploratory sensitivity check**, since TF v2.13/A-21 designates the single
pooled PLS-SEM model as the actual estimator of record for H7a/H7b.

**Changes made:**
- **`09_h7_ols_record.R`**: header comment rewritten to describe its new supplementary
  status and the real current TF; **no computational change** to the regression formulas,
  bootstrap procedure, Cook's D, HC3, or heteroscedasticity tests, per Khai's explicit
  instruction. Only the "predicted direction" labels changed: `sign_all_N` and
  `supported_as_predicted_A21` (renamed from `..._A22_A23`) now read a **positive**
  coefficient as the predicted (Buffering) direction, the reverse of before.
- **`10_final_results_table.py`**:
  - Section E (PLS-SEM path table) — H7a/H7b predicted-sign label changed from
    `- (dampening, A-22)`/`- (dampening, A-23)` to `+ (buffering, A-21 DRAFT)` for both;
    this also flips the sign-match check used for "Supported" vs. "Significant, opposite
    sign" back to testing for a positive coefficient.
  - Section G (renamed from "OLS model of record" to "OLS Hayes PROCESS Model 1
    (SUPPLEMENTARY, not estimation of record)") — predicted-direction label and text
    updated to Buffering/A-21; no source-data change.
  - **Table 9 (Path Coefficients) now includes H7a and H7b rows**, sourced from the
    PLS-SEM bootstrap table (`plssem_bootstrap_paths_main.csv` + `plssem_f_squared_main.csv`,
    same source as every other path), predicted sign `+`, decision logic identical to every
    other hypothesis in that table. This is the first time H7a/H7b have appeared in Table 9
    — previously that table only covered H1-H6c/E1/E2, leaving H7a/H7b to be read solely
    from the (now-demoted) OLS Table 13.
  - Table 13/14/15 (Moderation Results / Sensitivity Check / Simple Slopes) docstrings
    updated to say explicitly they are the supplementary OLS check, not the record.
  - **Figure 1**: the H7a/H7b dashed-arrow labels now pull b/p from the PLS-SEM bootstrap
    table (`b`, the same source every other arrow already used) instead of the OLS table
    (`o`) — consistent with PLS-SEM being the actual estimator of record. Labels changed
    from "(Dampening)" to "(Buffering, A-21)". Title changed from "...H7a/H7b per Hayes
    PROCESS Model 1" to "...H1-H7b all PLS-SEM per TF A-21".
  - Figure 2 (interaction plot, OLS-based simple slopes) **left unchanged** — it's part of
    the supplementary OLS check Khai asked to keep running as-is; it does not claim to
    represent the estimation of record, just a visualization.
- **`07_plssem_bridge.R` / `run_plssem.py`**: no change needed — neither ever hardcoded a
  predicted sign or an "A-22/A-23" framing; they only estimate and report, so the single
  pooled H7a/H7b model they've had all along already matches A-21's requirement exactly.

**Result on `main_clean_data.csv` (n=381; `run_plssem.py` was NOT re-run for this --
§25's "hold until n>=395" rule stands, and no re-run was needed since neither
`07_plssem_bridge.R` nor `run_plssem.py` changed — only `10_final_results_table.py` was
re-run, reading the PLS-SEM outputs already on disk from the prior n=381 run):** under
the PLS-SEM estimator of record, **neither H7a nor H7b is supported** — H7a β_M1 = −0.110 (p=.098, wrong sign vs.
the Buffering prediction), H7b β_M2 = 0.004 (p=.998, correct sign but negligible and far
from significant). This is a materially different picture from the OLS Table 13's own
numbers at the same n (H7a b=−0.092, p=.047, CI excludes 0 — "supported" under the OLS
check's own non-directional rule, but note the OLS estimate's sign is *also* opposite the
Buffering prediction, so it would not be "supported as predicted" there either) — a
reminder that the two estimators can and do disagree, which is exactly why Section E/Table 9
(PLS-SEM) is the one that governs the manuscript's verdict now, with Table 13 reported
alongside as supplementary evidence, not a competing verdict.

**Not done / left open:** the TF docx itself was not edited (no changes were needed inside
it — it already correctly states A-21's content) unlike §17's edits to the old A-22 docx.
No amendment was added to acknowledge that A-22/A-23 were tried and rescinded — if Khai
wants that documented inside the TF for the manuscript's own amendment log, that would need
its own follow-up request (this session only reconciled the pipeline, not the document).

## 27. Correction to §26, same day: the OLS Hayes PROCESS Model 1 check keeps its OWN
Dampening prediction (beta_M < 0), independent of Table 9's Buffering — 2026-09-24

§26 changed the OLS supplementary check's predicted direction to match Table 9's Buffering
(beta_M > 0), reasoning that TF v2.13/A-21 is silent on any OLS estimator so there was no
independent prediction to preserve. **Khai corrected this the same day**: the OLS Hayes
PROCESS Model 1 check (`09_h7_ols_record.R`, Table 13/14/15) keeps its **own** predicted
direction, **beta_M1 < 0 and beta_M2 < 0 (Dampening)** — the Legal-Sensitization /
institutional-salience logic from the earlier (rescinded, §26) A-22/A-23 draft, which Khai
still holds as the correct theoretical prediction for this specific supplementary check,
even though that draft's TF status is gone. **This is now intentionally two different
directional predictions living side by side**:
- **Table 9 (PLS-SEM, estimator of record, TF v2.13/A-21)**: Buffering, beta_M > 0.
- **Table 13 (OLS Hayes PROCESS Model 1, supplementary)**: Dampening, beta_M < 0.

Do not "reconcile" these to match each other again without asking — both are deliberate,
independent, and belong to different tables. `09_h7_ols_record.R`'s header comment now says
this explicitly ("Do not 'fix' this to match Table 9's Buffering sign again without asking
first"), specifically to stop a future session from re-flipping it back per §26's reasoning.

**Changes made (reverting only the direction-label parts of §26, not the estimator-of-record
reassignment, which stands):**
- `09_h7_ols_record.R`: `sign_all_N`/`supported_as_predicted` (renamed back from
  `..._A21`) now read a **negative** coefficient as the predicted (Dampening) direction
  again; header comment explains why this differs from Table 9.
- `10_final_results_table.py` Section G: `pred=` label for the OLS rows changed from
  `"Buffering, beta_M > 0 (A-21 DRAFT)"` to `"Dampening, beta_M < 0 (this OLS check's own
  prediction, independent of Table 9's Buffering)"`.
- Table 9 / Section E / Figure 1 (PLS-SEM, estimator of record) are **untouched** — still
  Buffering, beta_M > 0, per A-21, exactly as §26 set them.

**Result on `main_clean_data.csv` (n=381, unchanged from §26 — no new data, no
`run_plssem.py` re-run per SS25):** under the OLS check's own (Dampening) prediction,
**H7a is "supported as predicted (Dampening)"** in both the all-N and Cook's-D-trimmed
runs (b=-0.092, p=.047 all-N; b=-0.072, p=.018 trimmed); H7b remains not supported
(b≈-0.002 to -0.038, p=.978/.612). This sits alongside, not in place of, Table 9's
official PLS-SEM verdict (§26: neither H7a nor H7b supported there).

## 28. Table 9 no longer includes H7a/H7b at all; OLS Hayes PROCESS Model 1 is THE test
for H7a/H7b, predicted Dampening (beta_M < 0) -- §26/§27 superseded further — 2026-09-24

Same day, Khai went one step further than §27: **remove H7a/H7b from Table 9 entirely**
("xoa phan lien quan den 2 bien dieu tiet o Table 9 di") -- H7a/H7b are not a PLS-SEM
path-table hypothesis at all; they are tested via the **OLS Hayes PROCESS Model 1 check**
(Table 13, `09_h7_ols_record.R`), full stop, with predicted direction **beta_M1 < 0 and
beta_M2 < 0 (Dampening)**. This effectively retires §26's "PLS-SEM is the H7a/H7b
estimator of record, Buffering" framing -- it stands only for §26's history, not as
current practice.

**Changes made:**
- **Table 9 (`table9_path_coefficients()`)**: the `hyp_labels`/`pred_sign` entries for
  H7a/H7b (added in §26) are removed -- Table 9 is back to exactly H1, H2, H4, H5, H6a,
  H6b, H6c, E1, E2, nothing else.
- **Section E** (the PLS-SEM path listing inside `FINAL_results_main_all.csv`): the
  `INT*PDPL -> TRU` / `INT*DISC -> TRU` rows are kept (PLS-SEM still estimates these
  paths as part of the same model, for transparency) but are now **reporting-only,
  no verdict** -- relabeled `"spec INT*PDPL->TRU (H7a tested via OLS Hayes PROCESS
  Model 1, Section G, not here)"` / same for H7b, `pred=""`, so no "Supported/Not
  supported" text is generated for them here (avoiding a second, conflicting verdict
  living next to Table 13's real one).
- **Figure 1**: the H7a/H7b dashed-arrow b/p values switched back from the PLS-SEM
  bootstrap table (`b`) to the OLS table (`o`, Section G) -- consistent with OLS Hayes
  being the actual test. Arrow labels now read "H7a (Dampening, OLS Hayes)" /
  "H7b (Dampening, OLS Hayes)". Title changed to "PLS-SEM for H1-H6c/E1/E2; H7a/H7b via
  OLS Hayes PROCESS Model 1".
- Table 13/14/15 and `09_h7_ols_record.R` are unchanged from §27 (already correct:
  Dampening prediction, supplementary-but-now-actually-primary role for H7a/H7b).

**Current state of record, as of this section (supersedes §26's framing):**
- H1-H6c, E1, E2: PLS-SEM two-stage (single pooled model), Table 9 / Section E / Figure 1.
- **H7a, H7b: OLS Hayes PROCESS Model 1 (`09_h7_ols_record.R`), Table 13, Figure 1 --
  predicted Dampening, beta_M < 0.** PLS-SEM still estimates `INT*PDPL -> TRU` /
  `INT*DISC -> TRU` as part of its own single pooled model (Section E, reporting only,
  no verdict) but that number is NOT the test of H7a/H7b.

**Result on `main_clean_data.csv` (n=381, figure/table regeneration only, no new
analysis run):** Figure 1 now shows H7a b=-0.092 (*, p=.047) and H7b b=-0.002 (n.s.) --
the OLS all-N numbers, both in the Dampening direction as predicted; H7a's asterisk
reflects it clearing p<.05 under the OLS check's own nominal rule (§ "not TF-mandated"
caveat from §26 still applies -- this is this check's own convention, not a rule fixed
by any TF version).

## 29. TF re-verified against docs/Theoretical_Foundations_v2_14.docx (a full version
bump, not a DRAFT) -- OLS Hayes PROCESS Model 1 IS confirmed the estimation of record
for H7a/H7b, predicted Dampening; model spec and verdict rule corrected — 2026-09-24

**Yet another docs/ change, re-verified per this file's own standing instruction.**
`docs/Theoretical_Foundations_v2_13_A21_DRAFT.docx` (§26/§27/§28's basis) is gone;
`docs/Theoretical_Foundations_v2_14.docx` is now the only TF file present -- a full
version bump (2.13 -> 2.14), not marked DRAFT. Extracted and read directly. It resolves
the Buffering/Dampening and PLS-SEM/OLS questions explicitly, with specific amendment
numbers this time (not the vague "A-21/22/23" churn of earlier sessions):

- **Amendment A-14**: "H7a supported, H7b not supported; H7a/H7b sign typo corrected...
  The predicted sign of both moderations is negative — β_M1 < 0 and β_M2 < 0 (dampening)
  — and the '> 0 / buffering' wording printed in earlier versions was a **typing error**,
  now corrected throughout." I.e. every prior version's "Buffering" framing (including
  what §26 read out of the since-superseded A-21 draft) is now declared, by the TF
  itself, to have been an error — Dampening was always the intended prediction.
- **Amendment A-15 (ratified, not "pending")**: "Estimation of record for H7a/H7b: OLS
  moderated regression on the main-only sample (N_main=400); Holm-Bonferroni correction
  removed; verdict from a 5,000-resample bootstrap 95% CI at nominal p<.05." — OLS,
  not PLS-SEM, is confirmed the estimator of record. §C.2's PLS-SEM two-stage model
  still estimates `INT*PDPL -> TRU`/`INT*DISC -> TRU` as part of its own equations, and
  is reported "next to" the OLS estimates for an agreement check, but does not carry
  the verdict.
- **Amendment A-16 (pending ratification, but already written as "Model of record" in
  SS C.2.2)**: two separate single-moderator OLS regressions, Hayes' PROCESS Model 1
  template, **without REL and without the other institutional carrier as a covariate**:
  `H7a: TRU = b0 + b1*INT_c + b2*PDPL_c + beta_M1*(INT_c x PDPL_c) + e`
  `H7b: TRU = b0 + b1*INT_c + b2*DISC_c + beta_M2*(INT_c x DISC_c) + e`
  This is DIFFERENT from what `09_h7_ols_record.R` had implemented since §17/§20/§26-28
  (which included REL and the cross-covariate in each equation, an assumption carried
  over from the earlier, since-defunct A-22/A-23 lineage that was never actually in any
  real TF text). The TF explicitly names the REL-including combined-equation form (from
  A-15's own original text) as a **sensitivity analysis**, not the model of record:
  `TRU = b0 + b1*REL + b2*INT_c + b3*PDPL_c + b4*DISC_c + beta_M1*(...) + beta_M2*(...) + e`
  (both interactions together in ONE pooled equation, mirroring H4's REL covariate).
- **Verdict rule (A-15) is DIRECTIONAL**, which `09_h7_ols_record.R` had never
  implemented correctly: "H7a (H7b) is supported if its 95% CI excludes zero **and the
  coefficient is negative, as predicted**... A significant positive coefficient would be
  reported as such and would **not** count as support." The script's verdict logic had
  been non-directional (CI-excludes-zero either way) since it was first written.

**`09_h7_ols_record.R` rewritten to match, all three corrections:**
1. Model-of-record formulas changed to drop REL and the cross-covariate:
   `f_H7a <- TRU_mean ~ INT_c + PDPL_c + INT_x_PDPL`,
   `f_H7b <- TRU_mean ~ INT_c + DISC_c + INT_x_DISC`.
2. Added the pooled-with-REL sensitivity model (`f_pooled`, both interactions together)
   as a third analysis per hypothesis, all-N only, clearly labeled
   `"pooled model with REL (A-15 form, sensitivity)"`.
3. `analyse()`'s bootstrap `stat()` function was generalized to look up the tested
   coefficient **by name** (`b[term]`) instead of assuming it's the last coefficient --
   necessary because the pooled sensitivity model has two interaction terms, so the one
   being tested is not always last.
4. Verdict logic (`ver <- ...`) changed from `(ci[1,1] > 0 | ci[1,2] < 0) && p<.05`
   (non-directional) to `ci[1,2] < 0 && p<.05` (CI entirely negative AND p<.05) --
   directional, matching A-15's actual rule. Labels changed from
   `"supported (post hoc, non-directional)"` to `"supported (as predicted, dampening)"`.
5. Output renamed `h7_ols_record_A22_A23_PROCESS_M1_INTERIM.csv` ->
   `h7_ols_record_A15_A16_PROCESS_M1_INTERIM.csv` (old file deleted); header comment
   rewritten to cite the real amendment numbers and formulas.

**`10_final_results_table.py` updated to match:** Section G relabeled "ESTIMATION OF
RECORD for H7a/H7b" (was "SUPPLEMENTARY"); all `h7_ols_record_...csv` filename
references updated; Table 13 (Moderation Results) and Table 15 (Simple Slopes) now
filter to just the two model-of-record rows (excluding the new pooled-with-REL
sensitivity rows); Table 14 (Sensitivity Check) extended to a 3-way pivot — Full
sample / Cook's-D-trimmed / Pooled with REL (A-15 form) — instead of 2-way, so the new
sensitivity variant has a home. Figure 1 and Table 9 needed no further change (§28
already had them right: Table 9 excludes H7a/H7b, Figure 1 sources H7a/H7b from the OLS
table, both already consistent with A-15/A-16).

**Result on `main_clean_data.csv` (n=381) under the corrected model-of-record
specification and directional verdict rule:**

| | H7a beta_M1 (all-N) | H7a (Cook's D-trimmed) | H7b beta_M2 (all-N) | H7b (trimmed) |
|---|---|---|---|---|
| b | -0.0899 | -0.1061 | -0.0418 | -0.0586 |
| BCa 95% CI | [-0.201, -0.007] | [-0.172, -0.037] | [-0.277, 0.192] | [-0.228, 0.106] |
| p (bootstrap) | .048 | .006 | .730 | .495 |
| Verdict | supported | supported | not supported | not supported |

**H7a: supported (as predicted, dampening) in BOTH the all-N and Cook's-D-trimmed
runs** -- CI entirely negative, p<.05 in both. **H7b: not supported** in either.
Sensitivity (pooled-with-REL, all-N): H7a b=-0.092, CI=[-0.204,-0.004] (excludes 0) but
p=.056 (misses the nominal .05 cutoff by a hair); H7b b=+0.009, n.s. -- broadly
consistent with the model-of-record verdict for both hypotheses, with H7a sitting right
at the edge under the alternate (REL-including) specification.

**Standing rule for future sessions**: OLS Hayes PROCESS Model 1
(`09_h7_ols_record.R`) is THE estimation of record for H7a/H7b -- not PLS-SEM, and not
"supplementary" as §26-§28 briefly had it. Predicted direction is Dampening
(beta_M1 < 0, beta_M2 < 0) per Amendment A-14 -- treat any TF text saying "Buffering"
as describing a pre-A-14 typo, not the current prediction. If `docs/` changes again,
re-extract before trusting any of this -- this project's TF file has now changed
content substantively 4 times in 3 days (§17, §26, §28, §29).

## 30. 11th hard-drop step added: `demographics_incomplete` (terminated at Flow Element
FL_51) — 2026-09-26

Khai spotted the same respondent §23 had flagged as "1 dữ liệu không trọn vẹn"
(ResponseId `R_4smw8GeFt5DsaQN`, all 9 `DEMOGRAPHIC_COLS` missing) again, this time
identified by its Qualtrics **Last Seen Flow Element ID = `FL_51`** (Finished=0,
Progress=79%), and asked to exclude it going forward via a real hard-drop step instead
of leaving it as a documented-but-tolerated edge case.

**Implemented as an 11th hard-drop step, `demographics_incomplete`** (`01_clean.py`,
inserted right after `non_vietnam_location`, before `straightlining_near_zero_sd`):
drops any row whose `"Last Seen Flow Element ID"` is in the new
`_config.py::DEMOGRAPHICS_INCOMPLETE_FLOW_ELEMENTS` set (currently `{"FL_51"}`). Checked
the raw export first: only 2 rows in the entire 1083-row raw file have ever landed on
`FL_51` (both `Finished=0`, `Progress=79%`), and only one of them (`R_4smw8GeFt5DsaQN`)
was still present in `main_clean_data.csv` before this fix — the other
(`R_4N8HL21e7cKDGwK`) had already been caught by an earlier step. **Hand-maintained, like
`NON_VIETNAM_LOC5_TEXT`** — if the Qualtrics survey flow is ever edited, a future
demographics-incomplete respondent may terminate at a different Flow Element ID that
won't be caught automatically; verify against a fresh raw row (its
`"Last Seen Flow Element ID"`, `Finished`, `Progress`, and which fields are all-NaN)
before adding a new ID to the set.

**Result on `raw_data.csv` (1083 raw, 2026-09-26):** the new step drops exactly 1 row as
expected (`R_4smw8GeFt5DsaQN`) — pooled 447→446, **main 395→394**. 10-step hard-drop
policy (§23) is now an **11-step policy**. `main_clean_data.csv` is now **1 short of the
n>=395 trigger** for re-running `run_plssem.py` (§25) and 6 short of N_main=400.

## 31. `HARD_DROP_STEP_ORDER` regrouped into 4 named categories, same day — 2026-09-26

Khai supplied an exact reordering of the 11 hard-drop steps into 4 labeled groups and
asked for the source to match it:
1. **Eligibility & Screening**: `consent_fail`, `screener_age_fail`, `screener_omni_fail`,
   `non_vietnam_location` (moved up here — a target-population eligibility criterion,
   grouped with the other screening checks rather than left with the technical/
   completeness steps where it originally sat).
2. **Attention & Comprehension**: `attention_check_fail`, `comprehension_check_fail`.
3. **Careless Responding**: `speeder_under_120s`, `straightlining_near_zero_sd` (moved
   up here, next to speeding, under one careless-responding umbrella — previously it
   was the very last step).
4. **Technical & Completeness**: `duplicate_response_pattern`, `excess_missing_items`,
   `demographics_incomplete`.

**Implemented exactly as given** in `01_clean.py::HARD_DROP_STEP_ORDER`, with the 4 group
headers kept as comments in the source for readability. `apply_exclusions()` already
iterates generically over `HARD_DROP_STEP_ORDER`, so no other code change was needed.
**Re-ordering changes only which step gets "credit" for dropping a respondent who fails
more than one criterion** (the printed funnel breakdown) — the final kept sample after
all 11 steps is identical regardless of order, since a respondent is dropped if ANY
step's mask is False. Confirmed on `raw_data.csv` (1083 raw): same final n (446 pooled,
394 main) as the previous step order, just redistributed across steps — e.g.
`straightlining_near_zero_sd` now shows 5 dropped (was 1) since it runs before
`duplicate_response_pattern` in the new order and so catches respondents the old order
would have let `duplicate_response_pattern` claim instead.

## 32. Manuscript tables renumbered into main body (Table 2-10) + appendix (Table A1-A5);
every remaining PLS-SEM trace of H7a/H7b removed; historical docstring clutter pruned
— 2026-09-26

Khai supplied an exact main-body/appendix split and asked `10_final_results_table.py`'s
output to match it, plus asked (separately, same message) to delete every remaining sign
that H7a/H7b were ever estimated via PLS-SEM — including reporting-only rows — now that
OLS Hayes PROCESS Model 1 is the sole estimator (§29).

**New numbering (supersedes §22/§28's Table 2-15 numbering):**

| Main body | Was | | Appendix | Was |
|---|---|---|---|---|
| Table 2 (+2b) | Table 2 (+2b) | | Table A1 | Table 6 (Fornell-Larcker) |
| Table 3 | Table 3 | | Table A2 | Table 8 (Inner VIF) |
| Table 4 | Table 4 | | Table A3 | Table 12 (Heteroscedasticity) |
| Table 5 | Table 5 | | Table A4 | Table 14 (Sensitivity check) |
| Table 6 (HTMT) | Table 7 | | Table A5 | Table 15 (Simple slopes) |
| Table 7 (Path coefficients) | Table 9 | | | |
| Table 8 (R2/Q2predict) | Table 10 | | | |
| Table 9 (Indirect effects) | Table 11 | | | |
| Table 10 (Moderation, H7a/H7b) | Table 13 | | | |

Function names in `10_final_results_table.py` are unchanged (`table6_fornell_larcker()`,
`table7_htmt()`, etc. still mean the same analysis they always did) — only each
function's `.to_csv()` output filename and docstring were updated to its new manuscript
number. The assembly section at the bottom of the script now defines `_MAIN_BODY_TABLES`
(Table2-Table10) and `_APPENDIX_TABLES` (TableA1-TableA5) as two explicit lists (Table2b
stays attached to Table2 in the main-body list, not given its own appendix slot), with
`_manuscript_tables = _MAIN_BODY_TABLES + _APPENDIX_TABLES` kept as the combined
build/write loop's input so `Manuscript_Results_Tables.xlsx` still gets all 15 sheets in
one file (main-body sheets first, appendix sheets after). `_MATRIX_TABLES` (the tables
whose row index should be written to Excel) updated from `("Table6","Table7","Table8")`
to `("Table6","TableA1","TableA2")` to track HTMT/Fornell-Larcker/Inner-VIF to their new
names. Old-numbered orphan CSVs in `outputs/tables/` (`Table6_fornell_larcker.csv`,
`Table7_htmt.csv`, `Table8_inner_vif.csv`, `Table9_path_coefficients.csv`,
`Table10_r2_q2predict.csv`, `Table11_indirect_effects.csv`,
`Table12_heteroscedasticity.csv`, `Table13_moderation_results.csv`,
`Table14_sensitivity_full_vs_trimmed.csv`, `Table15_simple_slopes_PDPL.csv`) were
deleted — none were git-tracked (same `outputs/tables/*.csv` `.gitignore` rule as §8).

**PLS-SEM/H7a/H7b traces removed:**
- `10_final_results_table.py` Section E's `paths` list (feeding
  `FINAL_results_main_all.csv`) previously still listed `INT*PDPL -> TRU` /
  `INT*DISC -> TRU` as reporting-only rows (no verdict, per §28). These two rows are now
  **deleted outright** — Section E no longer mentions H7a/H7b in any form, reporting or
  otherwise. Section E's remaining rows (H1/H2/H4/H5/H6a/H6b/H6c/E1/E2 plus the
  DISC->INT/DISC->TRU/PDPL->TRU specification terms) are unchanged.
- Table 7 (path coefficients, was Table 9)'s docstring and `table9_path_coefficients()`'s
  `hyp_labels` dict already excluded H7a/H7b since §28 — confirmed still correct, no
  change needed there beyond the renumbering above.
- Verified no other script (`07_plssem_bridge.R`, `run_plssem.py`, Figure 1/2 code) still
  sources H7a/H7b from a PLS-SEM table — Figure 1's H7a/H7b arrows already read from the
  OLS table (`o`) since §28, confirmed unchanged.

**Historical docstring/comment clutter removed** (Khai's second ask, same message):
- `10_final_results_table.py`'s module docstring no longer says "(renumbered 2026-09-23
  from 14_final_results_table.py after removing
  09_h7_supplementary.{py,R}/10_jn_micom.R/11_ols_model1_bootstrap.R/
  12_process_moderated_mediation.R)" — rewritten to a clean description of the script's
  current scope (PLS-SEM for H1-H6c/E1/E2 only; OLS Hayes PROCESS Model 1 is the sole
  H7a/H7b estimator, TF v2.14 §C.2.2, Amendments A-14/A-15/A-16).
- `09_h7_ols_record.R`'s header comment's opening line simplified to state its role
  directly ("THE ONLY ESTIMATION OF H7a/H7b in this pipeline — PLS-SEM never estimates or
  reports H7a/H7b, not even for reference") ahead of the existing TF-verification history
  (Amendments A-14/A-15/A-16 detail below it, unchanged) rather than leading with the
  renumbering/rewrite history.
- These are documentation/comment-only changes — no computation, formula, bootstrap
  procedure, or output value in either script changed.

**Verified end-to-end**: re-ran `10_final_results_table.py` on the current
`main_clean_data.csv`/PLS-SEM/OLS outputs (n=404 pooled funnel input, n=381 in the
H7a/H7b OLS record — §25's "hold `run_plssem.py` until n>=395" rule means the on-disk
PLS-SEM outputs are still from an earlier n; Section E's PLS-SEM numbers reflect
whatever `run_plssem.py` was last run against, not necessarily today's n=404 — this is
expected and unrelated to today's table-restructuring/cleanup work). All 15 tables (10
main body incl. 2b, 5 appendix) and `Manuscript_Results_Tables.xlsx` wrote successfully;
`FINAL_results_main_all.csv`'s Section E now has 12 PLS-SEM rows (was 14 — the two
H7a/H7b reporting-only rows are gone) and Section G's OLS Hayes rows are unchanged.
