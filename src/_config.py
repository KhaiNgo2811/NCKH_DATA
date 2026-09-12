# ---- Reflective measurement constructs ----
# Reconciled against TF v2.9/2.11 (consolidated reissue, absorbs A-7-A-17 + the
# post-B1.5 correction pass) and Master Codebook v2.5/2.6, cross-checked against
# the actual PROJ_MAIN raw export (pilot_real.csv, 47 responses, 10 Sep 2026).
#
# TRU = 6 items (TRU1-TRU6), NOT 5. This was genuinely ambiguous earlier: Amendment
# A-10 (26 Aug) had reduced TRU to 5 (TRU1-TRU5) to match what was fielded at the
# time. TF v2.11's amendment log carries an explicit superseding note under A-10:
# "the team and faculty advisor confirmed the current, correct standard is TRU = 6
# items (TRU1-TRU6: TRU1-3 cognitive; TRU4-6 affective -- secure, comfortable,
# content -- Komiak & Benbasat, 2006), as fielded in B1.5. This reverses A-10's
# 5-item reconciliation for TRU specifically." This matches pilot_real.csv exactly
# (TRU4/5/6 wording is "an toan/thoai mai/an long khi dua vao ShopWave..."). TRU=6
# is therefore the ratified, current state -- not an open item.
#
# REL4 is no longer excluded: Amendment A-9's REL4-exclusion logic applied only
# to the old (Tam & Ho, 2006) REL4 item, which has been removed from the
# instrument entirely. The current REL4 (Yin, Qiu & Wang, 2025) is a different,
# unrelated item and is fully analysed alongside REL1-REL3.
CONSTRUCT_ITEMS = {
    "AIP": [f"AIP{i}" for i in range(1, 6)],    # 5 items (was 6; self-reference item dropped)
    "REL": [f"REL{i}" for i in range(1, 5)],    # 4 items, all analysed (REL4 no longer excluded)
    "INT": [f"INT{i}" for i in range(1, 6)],    # 5 items
    "TRU": [f"TRU{i}" for i in range(1, 7)],    # 6 items -- see TRU note above
    "ENG": [f"ENG{i}" for i in range(1, 7)],    # 6 items
    "PI": [f"PI{i}" for i in range(1, 5)],      # 4 items (was 3; PI4 added from Dodds et al. 1991)
    "PDPL": [f"PDPL{i}" for i in range(1, 5)],  # 4 items
}
ALL_ITEMS = [it for items in CONSTRUCT_ITEMS.values() for it in items]

# ENG dimension structure (Amendment A-12, TF v2.6/v2.9). ENG1-ENG6 still enter the
# structural model (H5, H6b, E1, E2) as ONE pooled reflective composite via ENG_mean
# / CONSTRUCT_ITEMS["ENG"] -- that is unchanged. But per the standing prohibition
# "no pooled reliability across all six ENG items", Cronbach's alpha, item-rest
# correlation, and outer-loading diagnostics for ENG must be computed WITHIN
# dimension in 03_reliability_efa.py, never pooled across all six.
ENG_DIMENSIONS = {
    "ENG_cog": ["ENG1", "ENG2"],   # Cognitive Processing
    "ENG_aff": ["ENG3", "ENG6"],   # Affection
    "ENG_act": ["ENG4", "ENG5"],   # Activation
}

# Item-count constants. As of the current instrument, every fielded item is also
# analysed (no fielded-but-excluded items remain -- that situation was specific to
# the old REL4, now retired). FIELDED_ITEM_COUNT and ANALYSED_ITEM_COUNT are
# therefore identical; both names are kept so downstream scripts (01_clean.py)
# don't need to change which constant they import.
FIELDED_ITEM_COUNT = len(ALL_ITEMS)
ANALYSED_ITEM_COUNT = len(ALL_ITEMS)
FIELDED_ITEMS = ALL_ITEMS

# Likert columns
LIKERT_TEXT_COLS = ALL_ITEMS + ["ATT1", "ATT2", "MC_AIP", "MC_DISC", "CC1", "CC2"]

DISC_COL = "DISC_COND"
AIP_COND_COL = "AIP_COND"   # 0=Low / 1=High
CELL_COL = "CELL"           # 1-4

# ---- Exclusion-rule columns (Numeric Anchors) ----
CONSENT_COL = "CONSENT"
CONSENT_OK_ANCHOR = "1"     # 1 = Đồng ý

AGE_COL = "SCR_AGE"
AGE_OK_ANCHOR = "1"         # 1 = Đủ 18 tuổi

# Real fielded column name is SCR_OMNI (not SCR1 -- SCR1 was a stale assumption
# from an earlier scaffold draft; confirmed against pilot_real.csv, 10 Sep 2026).
OMNI_COL = "SCR_OMNI"
OMNI_OK_ANCHOR = "1"        # 1 = Có đa kênh

ATT1_COL, ATT1_CORRECT = "ATT1", 5
ATT2_COL, ATT2_CORRECT = "ATT2", 2

# Comprehension checks (CC)
CC1_COL, CC2_COL = "CC1", "CC2"
CC1_PLATFORM_ANCHOR = "1"
CC1_PERSONALIZED_ANCHOR = "2"
CC2_YES_ANCHOR = "1"
CC2_NO_ANCHOR = "2"

# Manipulation checks
MC_AIP_COL = "MC_AIP"
MC_DISC_COL = "MC_DISC"

# Timing
VIG_TIME_BASE_COLS = ["VIG_TIME_First Click", "VIG_TIME_Last Click",
                       "VIG_TIME_Page Submit", "VIG_TIME_Click Count"]

DURATION_COL = "Duration (in seconds)"

# Demographics
DEMOGRAPHIC_COLS = ["AGE_BAND", "GEN", "EDU", "INC", "FREQ", "PLAT", "PRIOR"]
CHAN_COL = "CHAN"
CHAN_CODES = ["CHAN_APP", "CHAN_WEB", "CHAN_LIVE", "CHAN_STORE", "CHAN_SOC"]

# Demographic "prefer not to say" sentinel (Master Codebook v2.5 SS4.8). Applies to
# every demographic item except FREQ, PLAT and PRIOR. Must be recoded to missing
# before any statistic is computed -- treating it as a valid ordinal value would
# place "prefer not to say" below the lowest substantive category.
DEMOGRAPHIC_PNTS_CODE = -98
DEMOGRAPHIC_PNTS_COLS = ["AGE_BAND", "GEN", "EDU", "INC"]

RESPONSE_ID_COL = "ResponseId"

# PII columns (Law 91/2025/QH15 Art. 2). Single source of truth shared by
# strip_pii.py (raw export, before commit) AND 01_clean.py (processed output,
# before to_csv) -- both must strip the same list. RecipientEmail/FirstName/
# LastName/ExternalReference are typically empty for anonymous-link
# distributions but are stripped regardless -- never assume they're empty.
PII_COLUMNS = [
    "IPAddress",
    "LocationLatitude",
    "LocationLongitude",
    "RecipientEmail",
    "RecipientFirstName",
    "RecipientLastName",
    "ExternalReference",
]

# ---- Ngưỡng loại bỏ mẫu ----
# POLICY CHANGE (2026-09-11, requested by Khai, amended same day): 01_clean.py's
# hard-drop pipeline uses ONLY 3 criteria -- missing data, duplicate response
# pattern, straightlining. Manipulation check (MC_AIP/MC_DISC) is NOT a filter
# -- it was briefly a 4th individual-level drop criterion, then removed the same
# day after being identified as post-treatment conditioning (see CLAUDE.md
# SS6.1); it is now report-only (Welch's t + Cohen's d, group-level ITT
# evidence) via 01_clean.py::report_manipulation_check(). The original
# consent/age/omni/ATT1/ATT2/CC1/CC2/speeding hard drops (pre-2026-09-11) are
# also no longer applied (constants below kept, unused, in case reinstated).
SPEEDING_MIN_SECONDS = 120
STRAIGHTLINE_SD_THRESHOLD = 0.5   # old soft-flag threshold, no longer used by 01_clean.py
MAX_MISSING_ITEM_PCT = 0.10

# Manipulation-check midpoint -- NOT used as a filter (see policy note above).
# Used only by 01_clean.py::breakdown_mc_groups()/report_manipulation_check()/
# flag_extreme_reversers() to classify direction, on a 1-7 Likert scale.
MC_MIDPOINT = 4

# Straightlining (per-respondent hard drop). Much stricter than the old
# STRAIGHTLINE_SD_THRESHOLD soft flag -- meant to catch responses that are
# (near-)identical across the whole battery (SD ~= 0), not merely low-variance
# responding.
STRAIGHTLINE_HARD_SD_THRESHOLD = 0.10

# Duplicate / near-duplicate response pattern (per-respondent hard drop). Two
# respondents are treated as duplicates if their answers differ on at most
# this many of the fielded items (0 = exact match only). O(n^2) pairwise
# comparison in 01_clean.py::flag_duplicate_response_pattern -- fine at pilot
# n, but will need a vectorized/hashing approach before main collection
# (n>=400, ~80k pairs) if it becomes a runtime bottleneck.
DUPLICATE_MAX_DIFFERING_ITEMS = 2
