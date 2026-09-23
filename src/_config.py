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

# English item wording (2026-09-23, requested by Khai for the manuscript's item-level
# reliability table, Table 5), transcribed verbatim from Master Codebook v2.7/A-20's
# "Item (EN)" column for each block (SS on AIP/REL/INT/TRU/ENG/PI/PDPL) -- the finalized
# main-collection text (PROJ_MAIN_final_v2), not the earlier pilot-stage wording. DISC
# has no item wording (it is a manipulated 0/1 dummy, never a Likert item, CLAUDE.md SS0).
ITEM_WORDING_EN = {
    "AIP1": "ShopWave can analyze my consumption level.",
    "AIP2": "ShopWave can analyze my personal characteristics (e.g., gender, age group, preferred style).",
    "AIP3": "ShopWave is able to identify my shopping habits and suggest products I may be interested in or need.",
    "AIP4": "Regardless of which channel I use (app or website), ShopWave gives me recommendations that reflect the same understanding of me.",
    "AIP5": "ShopWave's promotions and recommendations reflect my personal profile, regardless of which channel I am using.",
    "REL1": "The product list I just saw matches my current shopping needs.",
    "REL2": "The product list I saw was consistent with the type of product I was looking for.",
    "REL3": "The product list I saw was consistent with what I had previously searched for.",
    "REL4": "Overall, the product list I saw was useful to me.",
    "INT1": "I feel this product list interferes with my normal shopping experience.",
    "INT2": "I feel annoyed because this product list disrupts my shopping.",
    "INT3": "I feel this product list is intrusive and hard to ignore.",
    "INT4": "I feel this experience invades my privacy.",
    "INT5": "I feel the way products are shown to me is imposing, beyond my control.",
    "TRU1": "I believe ShopWave is competent enough to make good product recommendations.",
    "TRU2": "I believe ShopWave is honest in how it uses my information for personalisation.",
    "TRU3": "I believe ShopWave acts in my best interest, not just its own.",
    "TRU4": "I feel secure about relying on ShopWave for my shopping decisions.",
    "TRU5": "I feel comfortable about relying on ShopWave for my shopping decisions.",
    "TRU6": "I feel content about relying on ShopWave for my shopping decisions.",
    "ENG1": "Using the ShopWave platform gets me thinking about ShopWave.",
    "ENG2": "I pay close attention to content related to ShopWave's recommendations.",
    "ENG3": "I feel positive emotions when interacting with ShopWave.",
    "ENG4": "Among the online shopping platforms I use, ShopWave is the one I choose first.",
    "ENG5": "Compared with other shopping platforms, I spend more time using ShopWave.",
    "ENG6": "I feel enthusiastic when using ShopWave.",
    "PI1": "Given the opportunity, I intend to buy the products ShopWave recommends.",
    "PI2": "I think I will purchase on the ShopWave platform in the future.",
    "PI3": "Based on the scenario I just read, I am likely to continue shopping on ShopWave.",
    "PI4": "The likelihood that I would buy the products ShopWave recommends is high.",
    "PDPL1": "I am aware that Vietnam has a law regulating the protection of personal data.",
    "PDPL2": "I know that I have the right to request that a business delete my personal data or stop using it.",
    "PDPL3": "I understand that a business must obtain my consent before collecting my data for personalisation.",
    "PDPL4": "I know that I have the right to be informed about how my personal data is being processed.",
}

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
# LOC and REF (2026-09-14, requested by Khai) are two new demographic items
# added to the live Qualtrics instrument alongside the earlier LOC addition
# (see MAIN_DATA_START_TIMESTAMP note above):
#   LOC ("Bạn hiện đang sinh sống ở đâu?" / area of residence) -- has an
#     "other, please specify" companion column, LOC_TEXT_COL.
#   REF ("Bạn nhận khảo sát này từ ai?" / "Who did you receive this survey
#     from?" -- the referrer/recruitment-source item) -- values 1-5, no free-
#     text companion column in the raw export (unlike LOC/PLAT's _5_TEXT).
# Both are demographics/covariates only -- neither is part of the 34-item
# reflective battery (ALL_ITEMS above), so neither affects
# excess_missing_items, straightlining, or any exclusion rule.
LOC_COL = "LOC"
LOC_TEXT_COL = "LOC_5_TEXT"
REF_COL = "REF"
DEMOGRAPHIC_COLS = ["AGE_BAND", "GEN", "LOC", "EDU", "INC", "FREQ", "PLAT", "PRIOR", "REF"]

# REF value labels (2026-09-15, requested by Khai) -- REF tracks which team
# member's link/invite a respondent came through, not a respondent-level
# identity, so this is operational/team bookkeeping, not respondent PII.
# Used by 02_descriptives.py to show names instead of bare codes 1-5.
REF_LABELS = {
    1: "Hoàng Khải",
    2: "Tuấn Anh",
    3: "Đức Thiện",
    4: "Trọng Phúc",
    5: "Như Quỳnh",
}

# Demographic value labels (2026-09-23, requested by Khai, for the manuscript's
# Table 1 demographic-profile table), transcribed verbatim from Master Codebook
# v2.7/A-20 SS4.8's variable table, except LOC (see its own comment below).
DEMOGRAPHIC_VALUE_LABELS = {
    "AGE_BAND": {1: "18-24", 2: "25-34", 3: "35-44", 4: "45-54", 5: "55+"},
    "GEN": {1: "Nam / Male", 2: "Nữ / Female", 3: "Khác / Other"},
    "EDU": {1: "THPT trở xuống / High school or below", 2: "Trung cấp-Cao đẳng / Vocational-Associate",
            3: "Đại học / Bachelor's", 4: "Sau đại học / Postgraduate"},
    "INC": {1: "< 5tr VND", 2: "5-10tr VND", 3: ">10-20tr VND", 4: ">20-40tr VND", 5: ">40tr VND"},
    "FREQ": {1: "Rất ít khi / Rarely", 2: "Vài lần mỗi năm / A few times a year",
             3: "Khoảng mỗi tháng / About monthly", 4: "Khoảng mỗi tuần / About weekly",
             5: "Nhiều lần mỗi tuần / Several times a week"},
    "PLAT": {1: "Shopee", 2: "Lazada", 3: "TikTok Shop", 4: "Tiki", 5: "Khác / Other"},
    "PRIOR": {1: "< 6 tháng / months", 2: "6-12 tháng / months", 3: "1-3 năm / years",
              4: "> 3 năm / years"},
    # LOC (2026-09-23, supplied directly by Khai -- not documented anywhere in the
    # Master Codebook, which only says "choice numbers" for this item): 1/2/3 given
    # verbatim by Khai; code 4 has never appeared in the data and is left unlabeled
    # if it ever does; code 5 is inferred, not given directly -- the Codebook's own
    # LOC row says "LOC_5_TEXT carries the free-text 'other' answer", the same
    # 5="Khác/Other + free-text companion" pattern PLAT already uses above, so 5 is
    # labeled "Khac / Other" on that basis, not from a value Khai stated himself.
    "LOC": {1: "Hồ Chí Minh", 2: "Hà Nội", 3: "Đà Nẵng", 5: "Khác / Other"},
}

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

# ---- Pilot -> main administrative boundary (2026-09-13, requested by Khai) ----
# MAIN_DATA_START_TIMESTAMP marks the same moment the LOC demographic item was
# added to the live Qualtrics instrument (2026-09-12 02:15:56) -- reused here
# as the administrative cutoff between 'pilot' and 'main' sample_role labels.
# This is an ADMINISTRATIVE boundary (when a field was added), NOT a
# measurement-readiness boundary -- the manipulation-check gate
# (04_manipulation_check.py, |d| >= 0.50) has not cleared on data on either
# side of it as of 2026-09-13. See 01_clean.py's printed reminder and
# TF v2.10 / OD-12 (referenced in the request that added this; not otherwise
# present in this session's own records -- verify against the actual TF/OD
# text if you rely on the citation).
RECORDED_DATE_COL = "RecordedDate"
MAIN_DATA_START_TIMESTAMP = "2026-09-12 02:15:56"  # = LOC_ADDED_TIMESTAMP

# ---- Ngưỡng loại bỏ mẫu ----
# POLICY CHANGE (2026-09-16, requested by Khai): the 2026-09-11 narrowing to
# 3 criteria is superseded -- 01_clean.py's hard-drop pipeline is back to a
# 9-step policy (consent, age screener, omni screener, ATT1/ATT2, CC1/CC2,
# speeder floor, missing item, duplicate pattern, straightlining), in this
# exact order. SPEEDING_MIN_SECONDS below is back in active use (it was
# dead/unused between 2026-09-11 and 2026-09-16).
#
# The ONE thing NOT reverted: MC_AIP/MC_DISC are still NOT a hard-drop filter.
# The ITT rationale (Montgomery, Nyhan & Torres, 2018 -- filtering on a
# post-treatment variable biases the causal estimate of AIP_COND) stands
# regardless of how many other criteria exist. MC_AIP/MC_DISC now feed
# 01_clean.py::manipulation_check_sensitivity() (multi-scenario robustness
# reporting) instead of report_manipulation_check() alone.
#
# The pilot/main sample_role split is explicitly KEPT as the
# MAIN_DATA_START_TIMESTAMP/RecordedDate boundary (Amendment A-19, verified
# against the real docs -- see CLAUDE.md SS9/SS11) -- NOT reverted to a
# hardcoded row index, which would silently break on every re-export of this
# still-growing file.
SPEEDING_MIN_SECONDS = 120
STRAIGHTLINE_SD_THRESHOLD = 0.5   # old soft-flag threshold, no longer used by 01_clean.py
MAX_MISSING_ITEM_PCT = 0.10       # kept, but the missing-item step now uses MISSING_ITEM_TOLERANCE instead

# POLICY CHANGE (2026-09-16): zero-tolerance missing-item rule, overriding the
# previous <=10% (MAX_MISSING_ITEM_PCT) threshold. A respondent missing ANY of
# the 34 fielded items is dropped. MAX_MISSING_ITEM_PCT is left defined in
# case a future amendment reverts to a percentage-based tolerance.
MISSING_ITEM_TOLERANCE = 0

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
# this many of the fielded items (0 = exact match only), AND they have at
# least DUPLICATE_MIN_OVERLAP_ITEMS items both jointly answered. O(n^2)
# pairwise comparison in 01_clean.py::flag_duplicate_response_pattern -- fine
# at pilot n, but will need a vectorized/hashing approach before main
# collection (n>=400, ~80k pairs) if it becomes a runtime bottleneck.
DUPLICATE_MAX_DIFFERING_ITEMS = 2

# BUGFIX 2026-09-15: without a minimum-overlap requirement, two respondents
# who both have heavy missingness (e.g. 3 answered items each, most of the
# battery blank) could match by chance on those few shared items and get
# flagged as "duplicates" even though the match is noise, not real content
# overlap -- ndiff<=2 is trivially satisfied when there are only 3-5 jointly-
# answered items. Verified against pilot_real.csv (2026-09-14, n=289/323/409
# checkpoints) that this had NOT yet produced a false positive -- both
# genuinely-flagged pairs had full 34/34 item overlap -- but the gap was
# real and this constant closes it before it can bite at larger n.
DUPLICATE_MIN_OVERLAP_ITEMS = 15
