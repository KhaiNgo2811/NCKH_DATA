"""
03_reliability_efa.py - PILOT ONLY

Purpose:
    1. Cronbach's alpha per reflective construct.
    2. Per-construct single-factor loadings + CR + AVE.
    3. HTMT (discriminant validity) between all reflective constructs.
    4. 2-factor EFA for AIP + REL (legacy diagnostic).
    5. Cross-loading diagnostic for AIP/REL items.

Important governance rules:
    - DISC is a 0/1 dummy (DISC_COND), NOT a reflective construct.
      Never include DISC in Cronbach's alpha, loadings, CR/AVE, HTMT, or EFA.
    - Item counts follow the actual fielded instrument (Master Codebook v2.5 /
      TF v2.9, 8 Sep 2026, cross-checked against pilot_real.csv):
        AIP = 5, REL = 4 (all analysed), INT = 5, TRU = 6 (see _config.py note),
        ENG = 6, PI = 4, PDPL = 4.
      Do not silently add/drop items here.
    - ENG standing prohibition (Amendment A-12): no pooled Cronbach's alpha,
      item-rest correlation, or outer-loading diagnostic across all six ENG
      items. ENG is EXCLUDED from the pooled reliability/loadings/CR-AVE tables
      below and instead gets its own within-dimension reliability table
      (Cognitive Processing: ENG1,ENG2; Affection: ENG3,ENG6; Activation:
      ENG4,ENG5). ENG_mean (pooled) remains the sole structural-model input --
      unaffected, computed elsewhere (this script does not compute construct
      scores).
    - This script is for PILOT data only.

Usage:
    python src/03_reliability_efa.py --input data/processed/pilot_clean.csv

Outputs:
    outputs/tables/pilot_reliability.csv
    outputs/tables/pilot_outer_loadings.csv
    outputs/tables/pilot_cr_ave.csv
    outputs/tables/pilot_htmt.csv
    outputs/tables/pilot_eng_dimension_reliability.csv
    outputs/tables/pilot_efa_aip_rel_crossloadings.csv
"""

import argparse
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pingouin as pg
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import (
    calculate_bartlett_sphericity,
    calculate_kmo,
)

sys.path.insert(0, "src")
from _config import CONSTRUCT_ITEMS, ENG_DIMENSIONS  # noqa: E402

# Constructs entering the pooled per-construct reliability/loadings/CR-AVE tables.
# ENG is excluded (Amendment A-12 -- see module docstring); it gets its own
# within-dimension table instead.
POOLED_CONSTRUCTS = {k: v for k, v in CONSTRUCT_ITEMS.items() if k != "ENG"}


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

ALPHA_THRESHOLD = 0.70
LOADING_THRESHOLD = 0.60          # NEW: item-level outer loading cutoff
CR_THRESHOLD = 0.70               # NEW
AVE_THRESHOLD = 0.50              # NEW
HTMT_THRESHOLD = 0.85             # NEW
CROSS_LOADING_THRESHOLD = 0.30
MIN_EFA_EXTRA_OBS = 3

EFA_CONSTRUCTS = ("AIP", "REL")

OUTPUT_DIR = Path("outputs/tables")


# ---------------------------------------------------------------------
# Reliability (unchanged)
# ---------------------------------------------------------------------

def reliability_table(df):
    """
    Calculate Cronbach's alpha for every reflective construct
    defined in CONSTRUCT_ITEMS.

    DISC is not present in CONSTRUCT_ITEMS and therefore is never
    analyzed here.
    """
    rows = []

    for construct, items in POOLED_CONSTRUCTS.items():
        present = [item for item in items if item in df.columns]

        if len(present) < 2:
            rows.append(
                {
                    "construct": construct,
                    "n_items": len(present),
                    "n_obs": 0,
                    "alpha": None,
                    "flag_below_0.70": None,
                    "note": "insufficient items present",
                }
            )
            continue

        sub = df[present].dropna()

        if len(sub) == 0:
            rows.append(
                {
                    "construct": construct,
                    "n_items": len(present),
                    "n_obs": 0,
                    "alpha": None,
                    "flag_below_0.70": None,
                    "note": "no complete observations",
                }
            )
            continue

        alpha, _ = pg.cronbach_alpha(data=sub)

        rows.append(
            {
                "construct": construct,
                "n_items": len(present),
                "n_obs": len(sub),
                "alpha": round(alpha, 3),
                "flag_below_0.70": bool(alpha < ALPHA_THRESHOLD),
                "note": "",
            }
        )

    return pd.DataFrame(rows)


def eng_dimension_reliability_table(df):
    """Within-dimension Cronbach's alpha for ENG (Amendment A-12). Pooling
    across all six ENG items is prohibited -- see module docstring."""
    rows = []
    for dim, items in ENG_DIMENSIONS.items():
        present = [item for item in items if item in df.columns]
        if len(present) < 2:
            rows.append({"dimension": dim, "n_items": len(present), "n_obs": 0,
                         "r_or_alpha": None, "note": "insufficient items present"})
            continue
        sub = df[present].dropna()
        if len(sub) == 0:
            rows.append({"dimension": dim, "n_items": len(present), "n_obs": 0,
                         "r_or_alpha": None, "note": "no complete observations"})
            continue
        alpha, _ = pg.cronbach_alpha(data=sub)
        rows.append({"dimension": dim, "n_items": len(present), "n_obs": len(sub),
                     "r_or_alpha": round(alpha, 3), "note": ""})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# NEW: Per-construct outer loadings (single-factor extraction)
# ---------------------------------------------------------------------

def construct_outer_loadings(df, construct, items):
    """
    Extract a single-factor (1-factor PCA) loading for each item within
    ONE construct. This approximates the "outer loading" reported in
    SmartPLS's reflective measurement model (PLS uses a different
    estimator than PCA, so treat these as an approximation, not a
    substitute for a real PLS-SEM run).

    Returns
    -------
    pandas.DataFrame or None
        Columns: construct, item, loading, flag_below_0.60
        None if insufficient items/observations.
    """
    present = [item for item in items if item in df.columns]

    if len(present) < 2:
        return None

    sub = df[present].dropna()

    if len(sub) < len(present) + MIN_EFA_EXTRA_OBS:
        return None

    fa = FactorAnalyzer(n_factors=1, rotation=None, method="principal")
    fa.fit(sub)

    loadings = fa.loadings_.flatten()

    out = pd.DataFrame(
        {
            "construct": construct,
            "item": present,
            "loading": np.round(loadings, 3),
        }
    )
    out["flag_below_0.60"] = out["loading"].abs() < LOADING_THRESHOLD

    return out


def all_outer_loadings(df):
    """Run construct_outer_loadings for every construct in POOLED_CONSTRUCTS
    (ENG excluded -- see module docstring)."""
    frames = []

    for construct, items in POOLED_CONSTRUCTS.items():
        result = construct_outer_loadings(df, construct, items)
        if result is not None:
            frames.append(result)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------
# NEW: Composite Reliability (CR) and AVE, from outer loadings
# ---------------------------------------------------------------------

def cr_ave_table(loadings_df):
    """
    Compute Composite Reliability (CR) and Average Variance Extracted
    (AVE) per construct from standardized single-factor loadings.

        CR  = (Σλ)^2 / [ (Σλ)^2 + Σ(1 - λ^2) ]
        AVE = Σ(λ^2) / n_items

    Parameters
    ----------
    loadings_df : pandas.DataFrame
        Output of all_outer_loadings(df).

    Returns
    -------
    pandas.DataFrame
        One row per construct with CR, AVE, and threshold flags.
    """
    if loadings_df.empty:
        return pd.DataFrame()

    rows = []

    for construct, group in loadings_df.groupby("construct"):
        lam = group["loading"].to_numpy(dtype=float)

        sum_lam = lam.sum()
        sum_lam_sq = (lam ** 2).sum()
        sum_error = (1 - lam ** 2).sum()

        cr = (sum_lam ** 2) / ((sum_lam ** 2) + sum_error)
        ave = sum_lam_sq / len(lam)

        rows.append(
            {
                "construct": construct,
                "n_items": len(lam),
                "CR": round(cr, 3),
                "AVE": round(ave, 3),
                "flag_cr_below_0.70": bool(cr < CR_THRESHOLD),
                "flag_ave_below_0.50": bool(ave < AVE_THRESHOLD),
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# NEW: HTMT (Heterotrait-Monotrait Ratio of Correlations)
# ---------------------------------------------------------------------

def htmt_pair(df, items_a, items_b):
    """
    HTMT between two constructs' item sets.

        HTMT = mean(heterotrait correlations)
               / sqrt( mean(monotrait_a) * mean(monotrait_b) )

    Monotrait correlations = off-diagonal correlations within each
    construct's own items. Heterotrait correlations = all
    cross-construct item-pair correlations.
    """
    corr = df[items_a + items_b].corr().abs()

    hetero = corr.loc[items_a, items_b].to_numpy().flatten()
    hetero_mean = hetero.mean()

    def mono_mean(items):
        if len(items) < 2:
            return np.nan
        sub_corr = corr.loc[items, items].to_numpy()
        iu = np.triu_indices(len(items), k=1)
        return sub_corr[iu].mean()

    mono_a = mono_mean(items_a)
    mono_b = mono_mean(items_b)

    if np.isnan(mono_a) or np.isnan(mono_b) or mono_a <= 0 or mono_b <= 0:
        return np.nan

    return hetero_mean / np.sqrt(mono_a * mono_b)


def htmt_table(df):
    """
    Compute HTMT for every pair of reflective constructs in
    CONSTRUCT_ITEMS (DISC is excluded automatically since it is not
    a key in CONSTRUCT_ITEMS).

    NOTE: this deliberately uses CONSTRUCT_ITEMS, not POOLED_CONSTRUCTS -- ENG
    IS included here as a pooled 6-item construct, unlike reliability_table()/
    all_outer_loadings() above. The Amendment A-12 "no pooled reliability
    across all six ENG items" prohibition targets ITEM-RETENTION diagnostics
    (alpha, item-rest correlation, outer loadings) used to decide whether to
    drop an ENG item -- it does not forbid using ENG's full item set for
    discriminant validity against OTHER constructs, which is a different
    question (does ENG as a whole overlap with AIP/REL/etc, not "which ENG
    item is weak"). Dropping ENG from this table would silently lose HTMT(ENG,
    other) coverage with no governance basis for doing so.

    Returns
    -------
    pandas.DataFrame
        One row per construct pair with HTMT and threshold flag.
    """
    constructs = list(CONSTRUCT_ITEMS.keys())
    rows = []

    for c1, c2 in itertools.combinations(constructs, 2):
        items_a = [i for i in CONSTRUCT_ITEMS[c1] if i in df.columns]
        items_b = [i for i in CONSTRUCT_ITEMS[c2] if i in df.columns]

        if len(items_a) < 2 or len(items_b) < 2:
            rows.append(
                {
                    "construct_1": c1,
                    "construct_2": c2,
                    "htmt": None,
                    "flag_above_0.85": None,
                    "note": "insufficient items present",
                }
            )
            continue

        sub = df[items_a + items_b].dropna()

        if len(sub) < 3:
            rows.append(
                {
                    "construct_1": c1,
                    "construct_2": c2,
                    "htmt": None,
                    "flag_above_0.85": None,
                    "note": "insufficient observations",
                }
            )
            continue

        value = htmt_pair(sub, items_a, items_b)

        if np.isnan(value):
            rows.append(
                {
                    "construct_1": c1,
                    "construct_2": c2,
                    "htmt": None,
                    "flag_above_0.85": None,
                    "note": "degenerate monotrait correlation (<=0)",
                }
            )
            continue

        rows.append(
            {
                "construct_1": c1,
                "construct_2": c2,
                "htmt": round(value, 3),
                "flag_above_0.85": bool(value > HTMT_THRESHOLD),
                "note": "",
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# EFA / Cross-loading (unchanged)
# ---------------------------------------------------------------------

def efa_cross_loading_check(df, focal=EFA_CONSTRUCTS):
    """
    Run a 2-factor EFA on the AIP + REL item set.

    Cross-loading rule:
        An item is flagged when its absolute loading is > 0.30
        on BOTH factors.
    """
    items = []

    for construct in focal:
        if construct not in CONSTRUCT_ITEMS:
            continue

        items.extend(
            item
            for item in CONSTRUCT_ITEMS[construct]
            if item in df.columns
        )

    items = list(dict.fromkeys(items))

    if len(items) < 2:
        return (
            pd.DataFrame(),
            "insufficient items present for EFA",
        )

    sub = df[items].dropna()

    if len(sub) < len(items) + MIN_EFA_EXTRA_OBS:
        return (
            pd.DataFrame(),
            f"insufficient n for EFA "
            f"(need n > n_items + {MIN_EFA_EXTRA_OBS}; "
            f"n={len(sub)}, n_items={len(items)})",
        )

    kmo_all, kmo_model = calculate_kmo(sub)
    chi2, p = calculate_bartlett_sphericity(sub)

    fa = FactorAnalyzer(
        n_factors=2,
        rotation="oblimin",
        method="principal",
    )

    fa.fit(sub)

    loadings = pd.DataFrame(
        fa.loadings_,
        index=items,
        columns=["Factor1", "Factor2"],
    )

    loading_abs = loadings.abs()

    loadings["cross_loading_risk"] = (
        (loading_abs > CROSS_LOADING_THRESHOLD)
        .sum(axis=1)
        > 1
    )

    diag = (
        f"KMO={kmo_model:.3f}, "
        f"Bartlett chi2={chi2:.1f} "
        f"(p={p:.4f})"
    )

    return loadings, diag


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=(
            "Pilot reliability, outer loadings, CR/AVE, HTMT, "
            "and AIP/REL EFA cross-loading diagnostic."
        )
    )

    ap.add_argument(
        "--input",
        required=True,
        help="Path to the cleaned pilot CSV.",
    )
    ap.add_argument(
        "--sample-role",
        choices=["pilot", "main", "all"],
        default="all",
        help="Optional row filter on the 'sample_role' column "
             "(01_clean.py::compute_collection_phase(), an ADMINISTRATIVE "
             "pilot/main label, see CLAUDE.md SS9 -- not a measurement-readiness "
             "boundary). Default 'all' preserves the original behavior (no "
             "filtering) exactly -- this does not change any threshold or formula "
             "below, only which rows are analysed.",
    )

    args = ap.parse_args()

    input_path = Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    df = pd.read_csv(input_path)

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
            print(f"[03_reliability_efa] --sample-role={args.sample_role}: "
                  f"{n_before} -> {len(df)} rows")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # 1. Cronbach's alpha
    # -------------------------------------------------------------

    rel_tab = reliability_table(df)
    reliability_path = OUTPUT_DIR / "pilot_reliability{}.csv".format(role_suffix)
    rel_tab.to_csv(reliability_path, index=False)

    print("--- Cronbach's alpha per construct (pilot) ---")
    print(rel_tab.to_string(index=False))

    if (
        "flag_below_0.70" in rel_tab.columns
        and rel_tab["flag_below_0.70"].fillna(False).any()
    ):
        print("!! WARNING: at least one construct has alpha < 0.70 at pilot.")

    # -------------------------------------------------------------
    # 1b. ENG within-dimension reliability (Amendment A-12 -- ENG is excluded
    #     from the pooled table above; pooling across all six items is
    #     prohibited)
    # -------------------------------------------------------------

    eng_dim_tab = eng_dimension_reliability_table(df)
    eng_dim_path = OUTPUT_DIR / "pilot_eng_dimension_reliability{}.csv".format(role_suffix)
    eng_dim_tab.to_csv(eng_dim_path, index=False)

    print("\n--- ENG within-dimension reliability (Amendment A-12, not pooled) ---")
    print(eng_dim_tab.to_string(index=False))

    # -------------------------------------------------------------
    # 2. NEW: Outer loadings per construct
    # -------------------------------------------------------------

    loadings_tab = all_outer_loadings(df)
    loadings_path = OUTPUT_DIR / "pilot_outer_loadings{}.csv".format(role_suffix)
    loadings_tab.to_csv(loadings_path, index=False)

    print("\n--- Outer loadings (single-factor per construct) ---")
    if loadings_tab.empty:
        print("insufficient data for outer loadings")
    else:
        print(loadings_tab.to_string(index=False))
        low = loadings_tab[loadings_tab["flag_below_0.60"]]
        if not low.empty:
            print("!! WARNING: items with loading < 0.60 (candidates for removal):")
            for _, r in low.iterrows():
                print(f"    {r['construct']}.{r['item']} = {r['loading']}")
        else:
            print("OK: no items below the 0.60 loading threshold.")

    # -------------------------------------------------------------
    # 3. NEW: CR / AVE
    # -------------------------------------------------------------

    cr_ave_tab = cr_ave_table(loadings_tab)
    cr_ave_path = OUTPUT_DIR / "pilot_cr_ave{}.csv".format(role_suffix)
    cr_ave_tab.to_csv(cr_ave_path, index=False)

    print("\n--- Composite Reliability (CR) and AVE ---")
    if cr_ave_tab.empty:
        print("insufficient data for CR/AVE")
    else:
        print(cr_ave_tab.to_string(index=False))
        bad_ave = cr_ave_tab[cr_ave_tab["flag_ave_below_0.50"]]
        bad_cr = cr_ave_tab[cr_ave_tab["flag_cr_below_0.70"]]
        if not bad_ave.empty:
            print(
                "!! WARNING: AVE < 0.50 for: "
                + ", ".join(bad_ave["construct"].tolist())
            )
        if not bad_cr.empty:
            print(
                "!! WARNING: CR < 0.70 for: "
                + ", ".join(bad_cr["construct"].tolist())
            )

    # -------------------------------------------------------------
    # 4. NEW: HTMT
    # -------------------------------------------------------------

    htmt_tab = htmt_table(df)
    htmt_path = OUTPUT_DIR / "pilot_htmt{}.csv".format(role_suffix)
    htmt_tab.to_csv(htmt_path, index=False)

    print("\n--- HTMT (discriminant validity) ---")
    if htmt_tab.empty:
        print("insufficient data for HTMT")
    else:
        print(htmt_tab.to_string(index=False))
        flagged = htmt_tab[htmt_tab["flag_above_0.85"] == True]  # noqa: E712
        if not flagged.empty:
            print("!! WARNING: HTMT > 0.85 for pairs:")
            for _, r in flagged.iterrows():
                print(f"    {r['construct_1']} <-> {r['construct_2']} = {r['htmt']}")
        else:
            print("OK: no construct pair exceeds the 0.85 HTMT threshold.")

    # -------------------------------------------------------------
    # 5. EFA AIP + REL (legacy diagnostic, kept as-is)
    # -------------------------------------------------------------

    efa_loadings, diag = efa_cross_loading_check(df)

    print(f"\n--- EFA AIP-REL cross-loading check ({diag}) ---")

    efa_path = OUTPUT_DIR / "pilot_efa_aip_rel_crossloadings{}.csv".format(role_suffix)

    if efa_loadings.empty:
        print(diag)
    else:
        efa_loadings.round(3).to_csv(efa_path)
        print(efa_loadings.round(3).to_string())

        flagged_items = efa_loadings.index[
            efa_loadings["cross_loading_risk"]
        ].tolist()

        if flagged_items:
            print(
                "!! WARNING: cross-loading items detected: "
                + ", ".join(flagged_items)
            )
            print(
                f"    Rule: absolute loading > "
                f"{CROSS_LOADING_THRESHOLD:.2f} on both factors."
            )
        else:
            print(
                "OK: no cross-loading items detected "
                f"under the >{CROSS_LOADING_THRESHOLD:.2f} rule."
            )

    # -------------------------------------------------------------
    # 6. Output confirmation
    # -------------------------------------------------------------

    print("\n[03_reliability_efa] wrote:")
    print(f"  - {reliability_path}")
    print(f"  - {eng_dim_path}")
    print(f"  - {loadings_path}")
    print(f"  - {cr_ave_path}")
    print(f"  - {htmt_path}")
    if not efa_loadings.empty:
        print(f"  - {efa_path}")


if __name__ == "__main__":
    main()