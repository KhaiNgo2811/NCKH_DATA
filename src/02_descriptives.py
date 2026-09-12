"""
02_descriptives.py - demographics summary + 2x2 cell balance check + construct
descriptives + soft-flag sensitivity.
Usage:
    python src/02_descriptives.py --input data/processed/pilot_clean.csv --phase pilot
"""
import argparse
import sys

import pandas as pd

sys.path.insert(0, "src")
from _config import DEMOGRAPHIC_COLS, AIP_COND_COL, DISC_COL, CONSTRUCT_ITEMS  # noqa: E402


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


def construct_descriptives(df):
    """Mean/SD per construct score. Uses the {construct}_mean columns
    01_clean.py::compute_construct_scores() persists; falls back to computing
    them on the fly (e.g. for an older *_clean.csv predating that step)."""
    rows = []
    for construct, items in CONSTRUCT_ITEMS.items():
        col = f"{construct}_mean"
        if col in df.columns:
            series = df[col]
        else:
            present = [c for c in items if c in df.columns]
            if not present:
                continue
            series = df[present].mean(axis=1)
        series = series.dropna()
        if series.empty:
            continue
        rows.append({"construct": construct, "n_items": len(items), "n_obs": len(series),
                     "mean": round(series.mean(), 3), "sd": round(series.std(), 3),
                     "min": round(series.min(), 3), "max": round(series.max(), 3)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--phase", choices=["pilot", "main"], required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.input)

    balance = cell_balance(df)
    profile = demographic_summary(df)
    construct_desc = construct_descriptives(df)

    balance.to_csv(f"outputs/tables/{args.phase}_cell_balance.csv", index=False)
    profile.to_csv(f"outputs/tables/{args.phase}_sample_profile.csv", index=False)
    construct_desc.to_csv(f"outputs/tables/{args.phase}_construct_descriptives.csv", index=False)

    print(f"[02_descriptives] n={len(df)}")
    print("--- 2x2 cell balance (AIP_COND x DISC_COND) ---")
    print(balance.to_string(index=False) if len(balance) else "(no data / columns missing)")
    if len(balance) and balance.get("flag_underfilled", pd.Series(dtype=bool)).any():
        print("!! WARNING: at least one cell is underfilled (<20% of even quarter share). "
              "Check Qualtrics Randomizer 'Evenly Present Elements' setting.")

    print("\n--- Construct descriptives (mean/SD) ---")
    print(construct_desc.to_string(index=False) if len(construct_desc) else "(no data)")

    # Soft flags actually produced by 01_clean.py (flag_straightliner/flag_cc1_wrong/
    # flag_cc2_wrong predate the 2026-09-11 policy change and no longer exist).
    if "flag_cell_mismatch" in df.columns:
        print(f"\nCELL vs AIP_COND x DISC_COND mismatches (not dropped): "
              f"{int(df['flag_cell_mismatch'].sum())}")
    if "flag_extreme_reverser" in df.columns:
        print(f"Extreme MC reversers (not dropped, robustness-check only): "
              f"{int(df['flag_extreme_reverser'].sum())}")

    print(f"\n[02_descriptives] wrote outputs/tables/{args.phase}_cell_balance.csv, "
          f"outputs/tables/{args.phase}_sample_profile.csv, and "
          f"outputs/tables/{args.phase}_construct_descriptives.csv")


if __name__ == "__main__":
    main()
