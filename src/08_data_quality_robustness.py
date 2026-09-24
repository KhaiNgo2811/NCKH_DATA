"""
08_data_quality_robustness.py - DIAGNOSTIC / ROBUSTNESS ONLY (requested by Khai, 2026-09-19).

Flags two kinds of data-quality outliers and re-runs the SAME PLS-SEM
(07_plssem_bridge.R, 10,000 percentile-bootstrap resamples) on three samples,
reported side by side:
    (a) full sample
    (b) excluding extreme response duration
    (c) excluding Mahalanobis multivariate outliers

Thresholds are FIXED here, once, and must not be re-tuned after looking at
(b)/(c) -- changing a cutoff because a result was "not as hoped" would turn a
robustness check into a search for the preferred answer:
    - extreme duration: log(Duration) > Q3 + 3*IQR (Tukey far-out fence on the
      log scale, since duration is right-skewed)
    - Mahalanobis: D^2 over the 34 fielded items > chi-square(df=34) at p<.001

No version is designated "official" by this script. Neither flag is a hard-drop
step in 01_clean.py and neither is used by the main pipeline. Caveat worth
stating when reporting (c): D^2 is computed on the same items PLS-SEM models, so
excluding on it also trims the extremes of the outcomes -- it can mechanically
shrink variances and shift coefficients, which is a reason to read (c) as a
sensitivity check rather than a cleaner sample.

Usage:
    python src/08_data_quality_robustness.py --input data/processed/main_clean_data.csv
Writes (never touches the main plssem_*.csv files):
    outputs/tables/robustness_dq_flags.csv
    outputs/tables/robustness_dq_paths_{a_full,b_no_extreme_duration,c_no_mahalanobis}.csv
    outputs/tables/robustness_dq_side_by_side.csv
"""
import argparse
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, "src")
from _config import ALL_ITEMS, CONSTRUCT_ITEMS, DISC_COL, DURATION_COL  # noqa: E402

DURATION_IQR_MULT = 3.0
MAHALANOBIS_ALPHA = 0.001
NBOOT_NOTE = "10,000 (set in 07_plssem_bridge.R)"

PATH_LABELS = {
    "AIP  ->  REL": "H1", "AIP  ->  INT": "H2", "REL  ->  TRU": "H4",
    "REL  ->  ENG": "H5", "INT  ->  TRU": "H6a", "INT  ->  ENG": "H6b",
    "INT  ->  PI": "H6c", "TRU  ->  ENG": "E1", "ENG  ->  PI": "E2",
    "DISC  ->  INT": "spec DISC->INT", "DISC  ->  TRU": "spec DISC->TRU",
    "PDPL  ->  TRU": "spec PDPL->TRU", "INT*PDPL  ->  TRU": "H7a (beta_M1)",
    "INT*DISC  ->  TRU": "H7b (beta_M2)",
}


def flag_extreme_duration(df, duration_col=DURATION_COL, iqr_mult=DURATION_IQR_MULT):
    """Diagnostic only -- drops nobody. True where log(Duration) exceeds
    Q3 + iqr_mult*IQR of log-duration."""
    dur = pd.to_numeric(df[duration_col], errors="coerce")
    ld = np.log(dur.where(dur > 0))
    q1, q3 = ld.quantile([0.25, 0.75])
    fence = q3 + iqr_mult * (q3 - q1)
    return (ld > fence).fillna(False), float(np.exp(fence))


def flag_mahalanobis_outliers(df, items=ALL_ITEMS, alpha=MAHALANOBIS_ALPHA):
    """Diagnostic only -- drops nobody. Squared Mahalanobis distance over the
    item battery vs chi-square(df=n_items) at p<alpha. Returns (flag, D2, cutoff)."""
    items = [c for c in items if c in df.columns]
    X = df[items].astype(float)
    ok = X.notna().all(axis=1)
    Xc = X[ok].to_numpy()
    diff = Xc - Xc.mean(axis=0)
    d2 = np.einsum("ij,jk,ik->i", diff, np.linalg.pinv(np.cov(Xc, rowvar=False)), diff)
    cutoff = float(stats.chi2.ppf(1 - alpha, df=len(items)))
    d2_full = pd.Series(np.nan, index=df.index)
    d2_full[ok] = d2
    return (d2_full > cutoff).fillna(False), d2_full, cutoff


def run_plssem_paths(df):
    """Fit 07_plssem_bridge.R's model on df; return bootstrap path table with
    R's row/col names restored (rpy2 drops dimnames)."""
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.conversion import localconverter

    cols = [c for items in CONSTRUCT_ITEMS.values() for c in items] + [DISC_COL]
    data = df[cols].dropna()
    ro.r("source('src/07_plssem_bridge.R')")
    with localconverter(ro.default_converter + pandas2ri.converter):
        ro.globalenv["input_data"] = ro.conversion.py2rpy(data)
    res = ro.r("run_plssem(input_data)")
    boot = res.rx2("boot_paths")
    with localconverter(ro.default_converter + pandas2ri.converter):
        out = pd.DataFrame(ro.conversion.rpy2py(boot))
    out.index = list(ro.r["rownames"](boot))
    out.columns = list(ro.r["colnames"](boot))
    return out, len(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    n_full = len(df)

    dur_flag, dur_fence_sec = flag_extreme_duration(df)
    mah_flag, d2, mah_cut = flag_mahalanobis_outliers(df)
    print(f"[08] n={n_full}")
    print(f"[08] extreme duration (log-Tukey 3*IQR, fence={dur_fence_sec:.0f}s): "
          f"{int(dur_flag.sum())} flagged")
    print(f"[08] Mahalanobis (chi2 df={len(ALL_ITEMS)}, p<{MAHALANOBIS_ALPHA}, "
          f"D2>{mah_cut:.2f}): {int(mah_flag.sum())} flagged")
    print(f"[08] overlap of the two flags: {int((dur_flag & mah_flag).sum())}")
    print("[08] thresholds are fixed; each version is run ONCE, none is designated official.")

    pd.DataFrame({"extreme_duration": dur_flag, "mahalanobis_outlier": mah_flag,
                  "mahalanobis_D2": d2.round(3)}).to_csv(
        "outputs/tables/robustness_dq_flags.csv", index_label="row")

    versions = {
        "a_full": df,
        "b_no_extreme_duration": df[~dur_flag],
        "c_no_mahalanobis": df[~mah_flag],
    }
    tables, ns = {}, {}
    for name, sub in versions.items():
        print(f"\n[08] running PLS-SEM, version {name} (n={len(sub)}) ...", flush=True)
        t, n_used = run_plssem_paths(sub)
        t.to_csv(f"outputs/tables/robustness_dq_paths_{name}.csv")
        tables[name], ns[name] = t, n_used

    rows = []
    for path, lab in PATH_LABELS.items():
        row = {"Hypothesis": lab, "Path": path.replace("  ->  ", "->")}
        for name in versions:
            t = tables[name]
            row[f"beta_{name[0]}"] = round(t.loc[path, "Original Est."], 3)
            row[f"p_{name[0]}"] = round(t.loc[path, "Bootstrap P Val"], 4)
        sig = [row[f"p_{k}"] < 0.05 for k in "abc"]
        row["sig_stable"] = "yes" if len(set(sig)) == 1 else "NO - flips"
        rows.append(row)
    side = pd.DataFrame(rows)
    side.to_csv("outputs/tables/robustness_dq_side_by_side.csv", index=False)

    print(f"\n[08] side by side (a: full n={ns['a_full']}, "
          f"b: no extreme duration n={ns['b_no_extreme_duration']}, "
          f"c: no Mahalanobis n={ns['c_no_mahalanobis']}); "
          f"bootstrap {NBOOT_NOTE}")
    print(side.to_string(index=False))


if __name__ == "__main__":
    main()
