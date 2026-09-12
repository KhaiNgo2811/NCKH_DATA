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
    ap.add_argument("--phase", choices=["pilot", "main"], default="pilot",
                     help="Controls the output filename -- defaults to 'pilot' for "
                          "backward compatibility, but pass --phase main when running "
                          "against main-collection data or you will silently overwrite "
                          "the pilot results file.")
    args = ap.parse_args()
    df = pd.read_csv(args.input)

    results = []
    aip_col = AIP_COND_COL if AIP_COND_COL in df.columns else "AIP_COND"
    # BUGFIX 2026-08-26: AIP_COND is numeric 0/1 in the real export (CLAUDE.md SS4:
    # "AIP_COND, DISC_COND arrive as NUMERIC 0/1, not Low/High strings"), not text
    # labels. The previous ("Low", "High") group_labels matched zero rows, so
    # mc_test() silently returned None and MC_AIP was dropped from the results
    # table entirely -- the printed "PASS...for all checks" message was reporting
    # on 1 of 2 checks without saying so. Fixed to match the real coding.
    r1 = mc_test(df, MC_AIP_COL, aip_col, (0, 1))
    if r1:
        results.append(r1)
    else:
        print(f"!! WARNING: MC_AIP check could not be computed (insufficient n per "
              f"group in column '{aip_col}') -- NOT included in the gate verdict below.")
    r2 = mc_test(df, MC_DISC_COL, DISC_COL, (0, 1))
    if r2:
        results.append(r2)
    else:
        print(f"!! WARNING: MC_DISC check could not be computed (insufficient n per "
              f"group in column '{DISC_COL}') -- NOT included in the gate verdict below.")

    out = pd.DataFrame(results)
    out_path = f"outputs/tables/{args.phase}_manipulation_check.csv"
    out.to_csv(out_path, index=False)
    print("--- Manipulation check t-tests (gate: |d| >= 0.50) ---")
    print(out.to_string(index=False))

    if not out.empty:
        gate_pass = out["gate_pass_d>=0.50"].all()
        print(f"\n{'PASS' if gate_pass else 'FAIL'}: overall manipulation-check gate "
              f"{'clears' if gate_pass else 'does NOT clear'} d >= 0.50 for all checks.")
        if not gate_pass:
            print(">> Per TF v2.2 SS C.3 / Amendment A-7: vignettes must be revised "
                  "(task B2.10) and pilot re-run before main collection opens.")
    print(f"\n[04_manipulation_check] wrote {out_path}")


if __name__ == "__main__":
    main()
