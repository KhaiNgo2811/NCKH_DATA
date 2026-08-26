import argparse
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from _qualtrics_io import load_and_normalize, anchor_match  # noqa: E402
from _config import (  # noqa: E402
    ALL_ITEMS, CONSENT_COL, CONSENT_OK_ANCHOR, AGE_COL, AGE_OK_ANCHOR,
    OMNI_COL, OMNI_OK_ANCHOR, ATT1_COL, ATT1_CORRECT, ATT2_COL, ATT2_CORRECT,
    CC1_COL, CC2_COL,
    DURATION_COL, DISC_COL, AIP_COND_COL, CELL_COL,
    SPEEDING_MIN_SECONDS, STRAIGHTLINE_SD_THRESHOLD, MAX_MISSING_ITEM_PCT,
)

# CC1: người dùng phải nhận diện đúng điều kiện AIP mình được xem
#   AIP_COND = 0 (Low)  -> đáp án đúng CC1 = 1
#   AIP_COND = 1 (High) -> đáp án đúng CC1 = 2
# CC2: người dùng phải nhận diện đúng điều kiện DISC mình được xem
#   DISC_COND = 1 -> đáp án đúng CC2 = 1
#   DISC_COND != 1 -> đáp án đúng CC2 = 2
# Vì khảo sát Qualtrics đã tự động terminate khi CC sai, các dòng lọt vào
# đây mà vẫn sai CC coi như dữ liệu không hợp lệ -> loại cứng (hard drop).


def apply_exclusions(df):
    """Lọc bỏ các mẫu không hợp lệ (Hard drops)."""
    log_rows = []
    n0 = len(df)
    keep = pd.Series(True, index=df.index)

    def drop_step(mask_keep, reason):
        nonlocal keep
        n_before = keep.sum()
        mask_keep = pd.Series(mask_keep, index=df.index).fillna(False).astype(bool)
        newly_dropped = keep & ~mask_keep
        keep = keep & mask_keep
        log_rows.append({"step": reason, "n_before": int(n_before),
                          "n_dropped_this_step": int(newly_dropped.sum()),
                          "n_after": int(keep.sum())})

    if CONSENT_COL in df.columns:
        drop_step(anchor_match(df[CONSENT_COL], CONSENT_OK_ANCHOR), "consent_not_given")
    if AGE_COL in df.columns:
        drop_step(anchor_match(df[AGE_COL], AGE_OK_ANCHOR), "under_18")
    if OMNI_COL in df.columns:
        drop_step(anchor_match(df[OMNI_COL], OMNI_OK_ANCHOR), "not_omnichannel_screener")
    if ATT1_COL in df.columns:
        drop_step(pd.to_numeric(df[ATT1_COL], errors="coerce") == ATT1_CORRECT,
                   "failed_attention_check_ATT1")
    if ATT2_COL in df.columns:
        drop_step(pd.to_numeric(df[ATT2_COL], errors="coerce") == ATT2_CORRECT,
                   "failed_attention_check_ATT2")

    # Comprehension checks: sai CC1/CC2 nghĩa là khảo sát lẽ ra đã terminate.
    # Loại cứng các dòng còn sót lại mà đáp án sai (hoặc thiếu).
    if CC1_COL in df.columns and AIP_COND_COL in df.columns:
        cc1_val = pd.to_numeric(df[CC1_COL], errors="coerce")
        aip = pd.to_numeric(df[AIP_COND_COL], errors="coerce")
        expect_cc1 = np.where(aip == 1, 2, 1)
        drop_step(cc1_val == expect_cc1, "failed_comprehension_check_CC1")

    if CC2_COL in df.columns and DISC_COL in df.columns:
        cc2_val = pd.to_numeric(df[CC2_COL], errors="coerce")
        disc = pd.to_numeric(df[DISC_COL], errors="coerce")
        expect_cc2 = np.where(disc == 1, 1, 2)
        drop_step(cc2_val == expect_cc2, "failed_comprehension_check_CC2")

    if DURATION_COL in df.columns:
        dur = pd.to_numeric(df[DURATION_COL], errors="coerce")
        drop_step(dur >= SPEEDING_MIN_SECONDS, "speeding_below_threshold")

    present_items = [c for c in ALL_ITEMS if c in df.columns]
    if present_items:
        miss_pct = df[present_items].isna().mean(axis=1)
        drop_step(miss_pct <= MAX_MISSING_ITEM_PCT, "excess_missing_items")

    clean = df.loc[keep].copy()
    log = pd.DataFrame(log_rows)
    if len(log):
        log.loc[len(log)] = {"step": "TOTAL", "n_before": n0,
                              "n_dropped_this_step": n0 - len(clean), "n_after": len(clean)}
    return clean, log


def add_soft_flags(df):
    """Đánh dấu các mẫu nghi ngờ (Straightlining). CC1/CC2 đã được xử lý
    như hard-drop trong apply_exclusions nên không cần gắn cờ lại ở đây."""
    present_items = [c for c in ALL_ITEMS if c in df.columns]
    if present_items:
        df["flag_straightliner"] = df[present_items].std(axis=1, skipna=True) < STRAIGHTLINE_SD_THRESHOLD
    return df


def check_cell_consistency(df):
    if CELL_COL not in df.columns or AIP_COND_COL not in df.columns or DISC_COL not in df.columns:
        return df
    expected_cell = {(0, 0): 1, (0, 1): 2, (1, 0): 3, (1, 1): 4}
    aip = pd.to_numeric(df[AIP_COND_COL], errors="coerce")
    disc = pd.to_numeric(df[DISC_COL], errors="coerce")
    predicted = [expected_cell.get((a, d), np.nan) if pd.notna(a) and pd.notna(d) else np.nan
                 for a, d in zip(aip, disc)]
    df["flag_cell_mismatch"] = pd.to_numeric(df[CELL_COL], errors="coerce") != pd.Series(predicted, index=df.index)
    return df


def recode_cond(df):
    if AIP_COND_COL in df.columns:
        df[AIP_COND_COL] = pd.to_numeric(df[AIP_COND_COL], errors="coerce").round().astype("Int64")
    if DISC_COL in df.columns:
        df[DISC_COL] = pd.to_numeric(df[DISC_COL], errors="coerce").round().astype("Int64")
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--phase", choices=["pilot", "main"], required=True)
    args = ap.parse_args()

    df = load_and_normalize(args.input)
    df = check_cell_consistency(df)
    clean, log = apply_exclusions(df)
    clean = add_soft_flags(clean)
    clean = recode_cond(clean)

    out_csv = f"data/processed/{args.phase}_clean.csv"
    out_log = f"outputs/tables/{args.phase}_exclusion_log.csv"
    clean.to_csv(out_csv, index=False)
    log.to_csv(out_log, index=False)

    print(f"[01_clean] input={args.input} phase={args.phase}")
    print(log.to_string(index=False))
    print(f"[01_clean] wrote {out_csv} (n={len(clean)}) and {out_log}")


if __name__ == "__main__":
    main()