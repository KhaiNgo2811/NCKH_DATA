"""
06_power_analysis.py - OD-2 (CLOSED by Amendment A-8 / TF v2.3). A priori power for
the two independent two-way interaction terms beta_M1 (INT x PDPL -> TRU, H7a) and
beta_M2 (INT x DISC -> TRU, H7b). The three-way term beta_M4 is retired and no longer
estimated anywhere in this project.

Uses the standard Cohen (1988) / G*Power noncentrality convention for an F-test of a
single added predictor in multiple regression:
    ncp = f2 * (df_num + df_denom + 1),  df_num = 1 (the term being tested),
    df_denom = n - k - 1  (k = total predictor terms in the full model)
Power = 1 - F_noncentral.cdf(F_critical(alpha, df_num, df_denom), df_num, df_denom, ncp)

An earlier version of this script used statsmodels.stats.power.FTestPower.power(),
whose `effect_size` parameter does NOT follow this convention for this use case - it
returned power stuck at ~alpha regardless of n. Validated by hand against the known
TF v2.2 target (f2=0.02, k=8 -> n~402) before use; see CLAUDE.md SS5 for the check.

This is the Python cross-check ONLY. Must be reconciled against the R-side pwr/WebPower
check (PLS-specific power can differ from this OLS-regression analogue) before the
Qualtrics quota is frozen - see CLAUDE.md SS5.

Usage:
    python src/06_power_analysis.py
    python src/06_power_analysis.py --f2 0.02 0.009 --k 8 --alpha 0.05 --power 0.80
"""
import argparse

import pandas as pd
from scipy.stats import f as fdist
from scipy.stats import ncf


def power_at_n(f2, n, k, alpha=0.05):
    df_num, df_denom = 1, n - k - 1
    if df_denom <= 0:
        return 0.0
    ncp = f2 * (df_num + df_denom + 1)
    f_crit = fdist.ppf(1 - alpha, df_num, df_denom)
    return float(1 - ncf.cdf(f_crit, df_num, df_denom, ncp))


def required_n(f2, k, alpha=0.05, target_power=0.80, n_max=5000):
    for n in range(k + 5, n_max):
        p = power_at_n(f2, n, k, alpha)
        if p >= target_power:
            return n, p
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--f2", nargs="+", type=float, default=[0.02, 0.009],
                     help="effect sizes to evaluate (default: TF target + Aguinis risk band)")
    ap.add_argument("--k", type=int, default=6,
                     help="total predictor terms in the full model (INT, PDPL, DISC, "
                          "INTxPDPL, INTxDISC, +1). PDPLxDISC and INTxPDPLxDISC are "
                          "retired - no longer part of the model (Amendment A-8).")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.80)
    args = ap.parse_args()

    labels = {0.02: "a priori target (TF v2.3 SS C.2)",
              0.009: "conservative risk band (Aguinis et al. 2005 median)"}
    rows = []
    for f2 in args.f2:
        n, achieved = required_n(f2, args.k, args.alpha, args.power)
        rows.append({
            "scenario": labels.get(f2, f"f2={f2}"), "f2": f2, "k": args.k,
            "alpha": args.alpha, "target_power": args.power,
            "required_n": n, "achieved_power_at_n": round(achieved, 4) if achieved else None,
        })

    out = pd.DataFrame(rows)
    out.to_csv("outputs/tables/OD2_power_analysis_beta_M1_M2.csv", index=False)
    print("--- OD-2: Power analysis for beta_M1 (INT x PDPL -> TRU) / "
          "beta_M2 (INT x DISC -> TRU) ---")
    print("NOTE: beta_M1 and beta_M2 are independent two-way terms estimated in the "
          "same model with the same k, so the required_n below applies identically to "
          "both terms - this is not a calculation for just one of them.")
    print(out.to_string(index=False))
    print("\nNOTE: cross-validate against the R-side pwr::pwr.f2.test() / WebPower check "
          "before freezing the Qualtrics quota (CLAUDE.md SS5). This is an OLS-regression "
          "analogue, not a PLS-SEM-specific power calc - use it as a sanity bound.")


if __name__ == "__main__":
    main()
