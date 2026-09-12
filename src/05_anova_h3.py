"""
05_anova_h3.py - Two-way ANOVA: INT ~ AIP_COND * DISC_COND.
The Disclosure main effect on INT is the SOLE confirmatory test of H3 (Amendment A-5,
carried forward unchanged by Amendment A-7 - only the study label changed, not the test).
AIP main effect = experimental replication of H1/H2 (not itself H-numbered).
AIP x DISC interaction = exploratory only. Do NOT label it H-anything without a logged
team decision in TF v2.2.

Usage:
    python src/05_anova_h3.py --input data/processed/main_clean.csv
"""
import argparse
import sys

import pandas as pd
import pingouin as pg

sys.path.insert(0, "src")
from _config import CONSTRUCT_ITEMS, AIP_COND_COL, DISC_COL  # noqa: E402


def score_int(df):
    items = [c for c in CONSTRUCT_ITEMS["INT"] if c in df.columns]
    return df[items].mean(axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()
    df = pd.read_csv(args.input)

    df = df.copy()
    df["INT_mean"] = score_int(df)
    df["DISC_label"] = df[DISC_COL].map({0: "No Disclosure", 1: "With Disclosure"})
    aip_col = AIP_COND_COL if AIP_COND_COL in df.columns else "AIP_COND"

    aov = pg.anova(data=df, dv="INT_mean", between=[aip_col, "DISC_label"],
                    detailed=True, effsize="np2")
    aov.to_csv("outputs/tables/H3_anova_disclosure_main_effect.csv", index=False)
    print("--- Two-way ANOVA: INT ~ AIP_COND * DISC_COND ---")
    print(aov.to_string(index=False))

    disc_row = aov[aov["Source"] == "DISC_label"]
    aip_row = aov[aov["Source"] == aip_col]
    inter_row = aov[aov["Source"].str.contains("\\*", na=False)]

    # pingouin >=0.6 renamed the p-value column from 'p-unc' to 'p_unc' - support both
    p_col = "p_unc" if "p_unc" in aov.columns else "p-unc"
    print("\n=== H3 test (Disclosure main effect on INT) ===")
    if not disc_row.empty:
        p = disc_row[p_col].iloc[0]
        print(f"p = {p:.4f}  ->  {'SUPPORTED' if p < 0.05 else 'NOT SUPPORTED'} "
              f"at alpha=.05 (report regardless of outcome - TF v2.2 reporting-integrity rule)")
    print("\n=== AIP main effect (H1/H2 experimental replication, not itself H-numbered) ===")
    if not aip_row.empty:
        print(aip_row.to_string(index=False))
    print("\n=== AIP x DISC interaction (EXPLORATORY ONLY - do not label H-anything) ===")
    if not inter_row.empty:
        print(inter_row.to_string(index=False))


if __name__ == "__main__":
    main()
