"""
02_descriptives.py - demographics summary + 2x2 cell balance check + soft-flag sensitivity.
Usage:
    python src/02_descriptives.py --input data/processed/pilot_clean.csv --phase pilot
"""
import argparse
import sys

import pandas as pd

sys.path.insert(0, "src")
from _config import DEMOGRAPHIC_COLS, AIP_COND_COL, DISC_COL  # noqa: E402


def cell_balance(df):
    if AIP_COND_COL not in df.columns or DISC_COL not in df.columns:
        return pd.DataFrame()
    tab = df.groupby([AIP_COND_COL, DISC_COL]).size().reset_index(name="n")
    total = tab["n"].sum()
    if total == 0:
        return tab
    tab["pct"] = (tab["n"] / total * 100).round(1)
    min_expected_pct = 100 / 4 * 0.20  # flag if a cell is <20% of an even quarter share
    tab["flag_underfilled"] = tab["pct"] < min_expected_pct
    return tab


def demographic_summary(df):
    rows = []
    for col in DEMOGRAPHIC_COLS:
        target = col if col in df.columns else None
        if target is None:
            continue
        vc = df[target].value_counts(dropna=False)
        for val, cnt in vc.items():
            rows.append({"variable": col, "value": val, "n": cnt,
                         "pct": round(cnt / len(df) * 100, 1)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--phase", choices=["pilot", "main"], required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.input)

    balance = cell_balance(df)
    profile = demographic_summary(df)

    balance.to_csv(f"outputs/tables/{args.phase}_cell_balance.csv", index=False)
    profile.to_csv(f"outputs/tables/{args.phase}_sample_profile.csv", index=False)

    print(f"[02_descriptives] n={len(df)}")
    print("--- 2x2 cell balance (AIP_COND x DISC_COND) ---")
    print(balance.to_string(index=False) if len(balance) else "(no data / columns missing)")
    if len(balance) and balance.get("flag_underfilled", pd.Series(dtype=bool)).any():
        print("!! WARNING: at least one cell is underfilled (<20% of even quarter share). "
              "Check Qualtrics Randomizer 'Evenly Present Elements' setting.")
    if "flag_straightliner" in df.columns:
        print(f"Straightliners flagged (not dropped): {int(df['flag_straightliner'].sum())}")
    if "flag_cc1_wrong" in df.columns:
        print(f"CC1 wrong (not dropped): {int(df['flag_cc1_wrong'].sum())}")
    if "flag_cc2_wrong" in df.columns:
        print(f"CC2 wrong (not dropped): {int(df['flag_cc2_wrong'].sum())}")
    print(f"[02_descriptives] wrote outputs/tables/{args.phase}_cell_balance.csv "
          f"and outputs/tables/{args.phase}_sample_profile.csv")


if __name__ == "__main__":
    main()
