"""
run_plssem.py - rpy2 bridge orchestrator. Reads the cleaned main-collection CSV, passes
it to R via rpy2, calls 07_plssem_bridge.R's run_plssem(), and pulls results back as
pandas DataFrames.

ONLY for n>=400 main collection. NEVER run this on pilot (n=30) data for confirmatory
purposes - pilot is reliability/EFA/manipulation-check only (TF v2.2 SS C.3 mandatory
pilot gate). See CLAUDE.md SS5.

Usage:
    python src/run_plssem.py --input data/processed/main_clean.csv
"""
import argparse
import sys

import pandas as pd

try:
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.conversion import localconverter
    RPY2_AVAILABLE = True
except ImportError:
    RPY2_AVAILABLE = False

sys.path.insert(0, "src")
from _config import CONSTRUCT_ITEMS, DISC_COL  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()

    if not RPY2_AVAILABLE:
        print("rpy2 is not installed / R environment not configured.")
        print("Install: pip install rpy2  (and R packages: seminr, cSEM, pwr - see "
              "CLAUDE.md SS3 requirements.txt)")
        sys.exit(1)

    df = pd.read_csv(args.input)
    needed_cols = [c for items in CONSTRUCT_ITEMS.values() for c in items] + [DISC_COL]
    missing = [c for c in needed_cols if c not in df.columns]
    if missing:
        print(f"ERROR: input is missing required columns: {missing}")
        sys.exit(1)

    ro.r("source('src/07_plssem_bridge.R')")
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_df = ro.conversion.py2rpy(df[needed_cols].dropna())

    ro.globalenv["input_data"] = r_df
    result = ro.r("run_plssem(input_data)")

    with localconverter(ro.default_converter + pandas2ri.converter):
        path_coef = ro.conversion.rpy2py(result.rx2("path_coefficients"))
        boot_paths = ro.conversion.rpy2py(result.rx2("boot_paths"))

    path_coef_df = pd.DataFrame(path_coef)
    boot_paths_df = pd.DataFrame(boot_paths)

    path_coef_df.to_csv("outputs/tables/plssem_path_coefficients.csv")
    boot_paths_df.to_csv("outputs/tables/plssem_bootstrap_paths.csv")

    print("--- PLS-SEM path coefficients (structural model) ---")
    print(path_coef_df)
    print("\n--- Bootstrap CIs (10,000 resamples) ---")
    print(boot_paths_df)
    print("\n!! Cross-validate all numbers against SmartPLS 4 before manuscript use "
          "(CLAUDE.md SS5, 07_plssem_bridge.R rule).")


if __name__ == "__main__":
    main()
