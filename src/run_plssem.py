"""
run_plssem.py - rpy2 bridge orchestrator. Reads the cleaned main-collection CSV, passes
it to R via rpy2, calls 07_plssem_bridge.R's run_plssem(), and pulls results back as
pandas DataFrames.

ONLY for n>=400 main collection. NEVER run this on pilot (n=30) data for confirmatory
purposes - pilot is reliability/EFA/manipulation-check only (TF v2.2 SS C.3 mandatory
pilot gate). See CLAUDE.md SS5.

BOOTSTRAP P-VALUE METHOD (context-honesty note, 2026-09-17): a request asked this
script to switch to "real percentile bootstrap p-values, not an OLS-analogue" for
every path. Checked against seminr's actual source (seminr:::parse_boot_array,
installed seminr 2.5.0) before changing anything: the "Bootstrap P Val" column this
script has already been extracting and printing all along is
`2 * min(mean(boot_array <= 0), mean(boot_array > 0))` -- the standard EMPIRICAL
PERCENTILE bootstrap p-value (proportion of the 10,000 resampled path estimates on
each side of zero, doubled for two-sided), computed directly from the resample
distribution. It has never been an OLS/t-distribution analogue (that phrase only
applies to 06_power_analysis.py's separate, clearly-labeled f2_significance() sanity
check, added the same day for a different purpose -- picking a sample-size target,
not testing significance of an already-estimated model). No change was needed here;
this note just makes the fact explicit and citable, since the file itself never
spelled out the formula before.

RUN LOG (2026-09-17, requested by Khai): every run appends one row (timestamp, input
file, --sample-role, n before the PLS-SEM complete-case filter, final n actually
estimated) to outputs/tables/plssem_run_log.csv, so repeated runs on a growing
pilot_real.csv can be told apart instead of only ever showing the latest numbers.

Usage:
    python src/run_plssem.py --input data/processed/main_clean.csv
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

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
    ap.add_argument("--sample-role", choices=["pilot", "main", "all"], default="all",
                     help="Optional row filter on the 'sample_role' column "
                          "(01_clean.py::compute_collection_phase(), an ADMINISTRATIVE "
                          "pilot/main label, see CLAUDE.md SS9/SS12 -- not a "
                          "measurement-readiness boundary, and not a substitute for "
                          "the real n>=400 confirmatory-run gate). Default 'all' "
                          "preserves the original behavior (no filtering) exactly; "
                          "'main' or 'pilot' filters rows and appends _{role} to every "
                          "output filename so a filtered run never overwrites the "
                          "unfiltered one.")
    ap.add_argument("--tag", default="",
                     help="Optional extra suffix for every output filename (e.g. "
                          "'smartpls_main'), so a run on a different input file never "
                          "overwrites the default plssem_*.csv results.")
    args = ap.parse_args()

    if not RPY2_AVAILABLE:
        print("rpy2 is not installed / R environment not configured.")
        print("Install: pip install rpy2  (and R packages: seminr, cSEM, pwr - see "
              "CLAUDE.md SS3 requirements.txt)")
        sys.exit(1)

    df = pd.read_csv(args.input)

    role_suffix = ""
    if args.sample_role != "all":
        if "sample_role" not in df.columns:
            print(f"!! WARNING: --sample-role={args.sample_role} requested but the "
                  f"input has no 'sample_role' column (only present after "
                  f"01_clean.py's 2026-09-13 sample_role labeling) -- running on "
                  f"the full input instead.")
        else:
            n_before = len(df)
            df = df[df["sample_role"] == args.sample_role].copy()
            role_suffix = f"_{args.sample_role}"
            print(f"[run_plssem] --sample-role={args.sample_role}: {n_before} -> {len(df)} rows")
            if args.sample_role == "main" and len(df) < 400:
                print(f"!! WARNING: n={len(df)} is below the n>=400 main-collection "
                      f"target -- per CLAUDE.md SS5, do NOT treat this as a "
                      f"confirmatory PLS-SEM run. sample_role='main' is an "
                      f"administrative label (Amendment A-19), not a sign that main "
                      f"collection has actually reached its target n.")

    if args.tag:
        role_suffix += f"_{args.tag}"

    needed_cols = [c for items in CONSTRUCT_ITEMS.values() for c in items] + [DISC_COL]
    missing = [c for c in needed_cols if c not in df.columns]
    if missing:
        print(f"ERROR: input is missing required columns: {missing}")
        sys.exit(1)

    n_before_complete_case = len(df)
    complete_df = df[needed_cols].dropna()
    n_final = len(complete_df)
    print(f"[run_plssem] n going into PLS-SEM: {n_final} "
          f"(input after --sample-role filter had {n_before_complete_case} rows; "
          f"{n_before_complete_case - n_final} more dropped for missing values in "
          f"one of the {len(needed_cols)} PLS-SEM item/DISC columns).")
    if n_before_complete_case != n_final:
        print(f"!! NOTE: {n_before_complete_case - n_final} row(s) had a missing "
              f"value in a PLS-SEM column despite passing 01_clean.py's "
              f"zero-tolerance missing-item hard-drop (CLAUDE.md SS12 step 7) -- "
              f"this can happen if DISC_COND itself (Embedded Data, not one of the "
              f"34 fielded items) is missing on some row. Investigate if this "
              f"count is large.")

    ro.r("source('src/07_plssem_bridge.R')")
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_df = ro.conversion.py2rpy(complete_df)

    ro.globalenv["input_data"] = r_df
    result = ro.r("run_plssem(input_data)")

    log_path = Path("outputs/tables/plssem_run_log.csv")
    log_row = pd.DataFrame([{
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input_file": args.input,
        "sample_role": args.sample_role,
        "n_after_role_filter": n_before_complete_case,
        "n_final_into_plssem": n_final,
    }])
    log_row.to_csv(log_path, mode="a", header=not log_path.exists(), index=False)
    print(f"[run_plssem] logged this run to {log_path} (n_final_into_plssem={n_final})")

    # 07_plssem_bridge.R's run_plssem() returns a named list with 7 elements
    # (loadings, weights, reliability, path_coefficients, f_squared, htmt,
    # boot_paths) -- pull and save all of them, not just 2. Previously this
    # script silently dropped reliability/f_squared/htmt/loadings/weights,
    # forcing a manual re-extraction from the R session for anything beyond
    # path coefficients.
    r_result_names = {
        "loadings": f"plssem_outer_loadings{role_suffix}.csv",
        "weights": f"plssem_outer_weights{role_suffix}.csv",
        "reliability": f"plssem_reliability{role_suffix}.csv",
        "path_coefficients": f"plssem_path_coefficients{role_suffix}.csv",
        "f_squared": f"plssem_f_squared{role_suffix}.csv",
        "htmt": f"plssem_htmt{role_suffix}.csv",
        "vif": f"plssem_inner_vif{role_suffix}.csv",
        "indirect": f"plssem_indirect_effects{role_suffix}.csv",
        "fornell_larcker": f"plssem_fornell_larcker{role_suffix}.csv",
        "outer_vif": f"plssem_outer_vif{role_suffix}.csv",
        "boot_paths": f"plssem_bootstrap_paths{role_suffix}.csv",
        "rsquared": f"plssem_rsquared{role_suffix}.csv",
        "q2predict": f"plssem_q2predict{role_suffix}.csv",
    }

    def _to_named_df(r_obj):
        """Convert an R matrix/data.frame to a pandas DataFrame, preserving R's
        rownames/colnames when present.

        BUGFIX (2026-09-17, first real end-to-end run once R/rpy2 finally
        worked): rpy2's default matrix->numpy conversion drops dimnames, so
        `pd.DataFrame(ro.conversion.rpy2py(r_obj))` silently produced bare
        integer row/column labels (0,1,2,...) for every one of these 7
        tables -- e.g. a 10x10 path-coefficient matrix with no way to tell
        which row was AIP vs. REL vs. INT*PDPL. This was never caught earlier
        because run_plssem.py had never actually executed successfully
        before (no R/Rtools in any prior environment). Rownames/colnames are
        fetched separately via R's own rownames()/colnames() and reapplied."""
        with localconverter(ro.default_converter + pandas2ri.converter):
            arr = ro.conversion.rpy2py(r_obj)
        df = pd.DataFrame(arr)
        try:
            rn = ro.r["rownames"](r_obj)
            if rn is not ro.NULL and len(rn) == len(df.index):
                df.index = list(rn)
        except Exception:
            pass
        try:
            cn = ro.r["colnames"](r_obj)
            if cn is not ro.NULL and len(cn) == len(df.columns):
                df.columns = list(cn)
        except Exception:
            pass
        return df

    dfs = {}
    for r_name, out_filename in r_result_names.items():
        try:
            r_obj = result.rx2(r_name)
        except Exception as e:
            print(f"!! WARNING: could not extract '{r_name}' from the R result: {e}")
            continue
        py_df = _to_named_df(r_obj)
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
    print("\n--- R^2 / Adjusted R^2 (endogenous constructs) ---")
    if "rsquared" in dfs:
        print(dfs["rsquared"].to_string(index=False))
    print("\n--- Q2predict (Shmueli et al. 2019 PLSpredict, 10-fold x 10 rep, seed 123) ---")
    if "q2predict" in dfs:
        print(dfs["q2predict"].to_string(index=False))
    print("\n--- HTMT (discriminant validity) ---")
    if "htmt" in dfs:
        print(dfs["htmt"])
    print("\n--- Inner VIF (collinearity / common method bias, Kock 2015 convention: "
          "flag > 3.3, and > 5 on the generic-multicollinearity threshold) ---")
    if "vif" in dfs:
        vif_df = dfs["vif"]
        print(vif_df.to_string(index=False))
        flagged = vif_df[vif_df["vif"] > 3.3]
        if not flagged.empty:
            print("!! WARNING: inner VIF > 3.3 (possible CMB / collinearity) for:")
            for _, r in flagged.iterrows():
                print(f"    {r['from']} -> {r['to']} : VIF={r['vif']:.3f}")
        else:
            print("OK: no inner VIF exceeds 3.3.")

    print("\n--- Indirect effects (percentile bootstrap, same 10,000 resamples as the "
          "path table) + Zhao, Lynch & Chen (2010) classification ---")
    if "indirect" in dfs and "boot_paths" in dfs:
        ind, bp = dfs["indirect"], dfs["boot_paths"]
        # direct_of maps an indirect-effect chain to the ultimate from->to direct path
        # IN THE MODEL, for Zhao/Lynch/Chen (2010) classification. Not every chain has
        # one: REL->PI is never estimated as a direct path (only INT->PI, H6c, is) --
        # those chains report the indirect effect itself but skip classification rather
        # than compare against a path that doesn't exist.
        direct_of = {
            "REL->TRU->ENG": "REL  ->  ENG", "INT->TRU->ENG": "INT  ->  ENG",
            "INT->ENG->PI": "INT  ->  PI", "INT->TRU->ENG->PI": "INT  ->  PI",
        }
        out_rows = []
        for _, r in ind.iterrows():
            key = direct_of.get(r["effect"])
            ind_sig = (r["ci_low"] > 0) or (r["ci_high"] < 0)
            if key is None:
                out_rows.append({**r.to_dict(), "direct_beta": None, "direct_p": None,
                                 "ci_excludes_0": ind_sig,
                                 "classification": "N/A (no direct path in model)"})
                continue
            d = bp.loc[key]
            dir_sig = d["Bootstrap P Val"] < 0.05
            if ind_sig and not dir_sig:
                cls = "Indirect-only mediation (full)"
            elif ind_sig and dir_sig:
                same = (r["estimate"] * d["Original Est."]) > 0
                cls = "Complementary (partial)" if same else "Competitive (partial)"
            elif dir_sig:
                cls = "Direct-only (no mediation)"
            else:
                cls = "No effect (no mediation)"
            out_rows.append({**r.to_dict(), "direct_beta": d["Original Est."],
                             "direct_p": d["Bootstrap P Val"],
                             "ci_excludes_0": ind_sig, "classification": cls})
        ind_out = pd.DataFrame(out_rows)
        print(ind_out.round(4).to_string(index=False))
        ind_out.to_csv(f"outputs/tables/{r_result_names['indirect']}", index=False)

    print("\n--- Fornell-Larcker criterion (diagonal = sqrt(AVE), lower triangle = "
          "construct correlations; 7 reflective constructs only) ---")
    if "fornell_larcker" in dfs:
        fl = dfs["fornell_larcker"]
        print(fl.round(3).to_string())
        import numpy as np
        m = fl.to_numpy(dtype=float)
        sym = np.where(np.isnan(m), m.T, m)  # mirror lower triangle
        fl_bad = []
        for i, c in enumerate(fl.index):
            others = np.delete(np.abs(sym[i]), i)
            if np.nanmax(others) >= sym[i, i]:
                fl_bad.append(c)
        if fl_bad:
            print(f"!! WARNING: Fornell-Larcker violated for: {fl_bad}")
        else:
            print("OK: sqrt(AVE) exceeds every inter-construct correlation for all 7 constructs.")
    print("\n--- Outer VIF (item-level collinearity within construct; flag > 5, "
          "> 3.3 stricter) ---")
    if "outer_vif" in dfs:
        ov = dfs["outer_vif"]
        print(ov.to_string(index=False))
        hi = ov[ov["vif"] > 3.3]
        if hi.empty:
            print("OK: no outer VIF exceeds 3.3.")
        else:
            print("!! outer VIF > 3.3 (>5 = problematic):")
            for _, r in hi.iterrows():
                print(f"    {r['construct']}/{r['item']}: {r['vif']:.3f}")

    written = [f"outputs/tables/{r_result_names[name]}" for name in dfs]
    print(f"\n[run_plssem] wrote: {', '.join(written)}")
    print("\n!! Cross-validate all numbers against SmartPLS 4 before manuscript use "
          "(CLAUDE.md SS5, 07_plssem_bridge.R rule).")


if __name__ == "__main__":
    main()
