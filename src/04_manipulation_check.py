"""
04_manipulation_check.py - t-tests + Cohen's d for the manipulation checks.
GATE: d must be >= 0.50 for BOTH checks before main collection can open (TF v2.2 SS C.3,
Amendment A-7 replacement bullet 2). If not met, vignettes go back to task B2.10 for rewrite.

Real fielded column names are MC_AIP and MC_DISC (NOT MC1/MC2 - see CLAUDE.md SS1).

Usage:
    python src/04_manipulation_check.py --input data/processed/pilot_clean.csv
"""
import argparse
import sys

import pandas as pd
import pingouin as pg

sys.path.insert(0, "src")
from _config import MC_AIP_COL, MC_DISC_COL, AIP_COND_COL, DISC_COL  # noqa: E402

GATE_D = 0.50


def mc_test(df, mc_col, group_col, group_labels):
    g1 = df.loc[df[group_col] == group_labels[0], mc_col].dropna()
    g2 = df.loc[df[group_col] == group_labels[1], mc_col].dropna()
    if len(g1) < 2 or len(g2) < 2:
        return None
    res = pg.ttest(g2, g1)  # g2 (High/With) - g1 (Low/No) direction
    d = pg.compute_effsize(g2, g1, eftype="cohen")
    # pingouin >=0.6 renamed the p-value column from 'p-val' to 'p_val' - support both
    p_col = "p_val" if "p_val" in res.columns else "p-val"
    return {
        "mc_column": mc_col, "group_col": group_col,
        "n_low_or_no": len(g1), "n_high_or_with": len(g2),
        "mean_low_or_no": round(g1.mean(), 2), "mean_high_or_with": round(g2.mean(), 2),
        "t": round(res["T"].iloc[0], 3), "p": round(res[p_col].iloc[0], 4),
        "cohens_d": round(d, 3), "gate_pass_d>=0.50": abs(d) >= GATE_D,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()
    df = pd.read_csv(args.input)

    results = []
    aip_col = AIP_COND_COL if AIP_COND_COL in df.columns else "AIP_COND"
    r1 = mc_test(df, MC_AIP_COL, aip_col, ("Low", "High"))
    if r1:
        results.append(r1)
    r2 = mc_test(df, MC_DISC_COL, DISC_COL, (0, 1))
    if r2:
        results.append(r2)

    out = pd.DataFrame(results)
    out.to_csv("outputs/tables/pilot_manipulation_check.csv", index=False)
    print("--- Manipulation check t-tests (gate: |d| >= 0.50) ---")
    print(out.to_string(index=False))

    if not out.empty:
        gate_pass = out["gate_pass_d>=0.50"].all()
        print(f"\n{'PASS' if gate_pass else 'FAIL'}: overall manipulation-check gate "
              f"{'clears' if gate_pass else 'does NOT clear'} d >= 0.50 for all checks.")
        if not gate_pass:
            print(">> Per TF v2.2 SS C.3 / Amendment A-7: vignettes must be revised "
                  "(task B2.10) and pilot re-run before main collection opens.")


if __name__ == "__main__":
    main()
