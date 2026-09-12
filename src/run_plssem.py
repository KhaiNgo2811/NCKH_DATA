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

    # 07_plssem_bridge.R's run_plssem() returns a named list with 7 elements
    # (loadings, weights, reliability, path_coefficients, f_squared, htmt,
    # boot_paths) -- pull and save all of them, not just 2. Previously this
    # script silently dropped reliability/f_squared/htmt/loadings/weights,
    # forcing a manual re-extraction from the R session for anything beyond
    # path coefficients.
    r_result_names = {
        "loadings": "plssem_outer_loadings.csv",
        "weights": "plssem_outer_weights.csv",
        "reliability": "plssem_reliability.csv",
        "path_coefficients": "plssem_path_coefficients.csv",
        "f_squared": "plssem_f_squared.csv",
        "htmt": "plssem_htmt.csv",
        "boot_paths": "plssem_bootstrap_paths.csv",
    }

    dfs = {}
    with localconverter(ro.default_converter + pandas2ri.converter):
        for r_name, out_filename in r_result_names.items():
            try:
                r_obj = result.rx2(r_name)
            except Exception as e:
                print(f"!! WARNING: could not extract '{r_name}' from the R result: {e}")
                continue
            py_df = pd.DataFrame(ro.conversion.rpy2py(r_obj))
            dfs[r_name] = py_df
            py_df.to_csv(f"outputs/tables/{out_filename}")

    print("--- PLS-SEM path coefficients (structural model) ---")
    if "path_coefficients" in dfs:
        print(dfs["path_coefficients"])
    print("\n--- Bootstrap CIs (10,000 resamples) ---")
    if "boot_paths" in dfs:
        print(dfs["boot_paths"])
    print("\n--- Reliability (alpha, rhoC, AVE, rhoA per construct) ---")
    if "reliability" in dfs:
        print(dfs["reliability"])
    print("\n--- f-squared (incl. beta_M1/beta_M2 individual effect sizes) ---")
    if "f_squared" in dfs:
        print(dfs["f_squared"])
    print("\n--- HTMT (discriminant validity) ---")
    if "htmt" in dfs:
        print(dfs["htmt"])

    written = [f"outputs/tables/{r_result_names[name]}" for name in dfs]
    print(f"\n[run_plssem] wrote: {', '.join(written)}")
    print("\n!! Cross-validate all numbers against SmartPLS 4 before manuscript use "
          "(CLAUDE.md SS5, 07_plssem_bridge.R rule).")


if __name__ == "__main__":
    main()
