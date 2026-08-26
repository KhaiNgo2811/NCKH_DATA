# ---- Reflective measurement constructs ----
CONSTRUCT_ITEMS = {
    "AIP": [f"AIP{i}" for i in range(1, 7)],    # 6 items
    "REL": [f"REL{i}" for i in range(1, 5)],    # 4 items
    "INT": [f"INT{i}" for i in range(1, 6)],    # 5 items
    "TRU": [f"TRU{i}" for i in range(1, 6)],    # 5 items
    "ENG": [f"ENG{i}" for i in range(1, 7)],    # 6 items
    "PI": [f"PI{i}" for i in range(1, 4)],      # 3 items
    "PDPL": [f"PDPL{i}" for i in range(1, 5)],  # 4 items
}
ALL_ITEMS = [it for items in CONSTRUCT_ITEMS.values() for it in items]

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

OMNI_COL = "SCR1"
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

RESPONSE_ID_COL = "ResponseId"

# ---- Ngưỡng loại bỏ mẫu ----
SPEEDING_MIN_SECONDS = 120
STRAIGHTLINE_SD_THRESHOLD = 0.5
MAX_MISSING_ITEM_PCT = 0.10