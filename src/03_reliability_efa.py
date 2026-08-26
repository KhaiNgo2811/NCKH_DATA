"""
03_reliability_efa.py - PILOT ONLY

Purpose:
    1. Cronbach's alpha per reflective construct.
    2. 2-factor EFA for AIP + REL.
    3. Cross-loading diagnostic for AIP/REL items.

Important governance rules:
    - DISC is a 0/1 dummy (DISC_COND), NOT a reflective construct.
      Never include DISC in Cronbach's alpha or EFA.
    - TRU/ENG item counts follow the actual fielded instrument:
        TRU = 5 items
        ENG = 6 items
      Do not silently add/drop items here.
    - This script is for PILOT data only.

Usage:
    python src/03_reliability_efa.py --input data/processed/pilot_clean.csv

Outputs:
    outputs/tables/pilot_reliability.csv
    outputs/tables/pilot_efa_aip_rel_crossloadings.csv
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import pingouin as pg
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import (
    calculate_bartlett_sphericity,
    calculate_kmo,
)

sys.path.insert(0, "src")
from _config import CONSTRUCT_ITEMS  # noqa: E402


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

ALPHA_THRESHOLD = 0.70
CROSS_LOADING_THRESHOLD = 0.30
MIN_EFA_EXTRA_OBS = 3

EFA_CONSTRUCTS = ("AIP", "REL")

OUTPUT_DIR = Path("outputs/tables")


# ---------------------------------------------------------------------
# Reliability
# ---------------------------------------------------------------------

def reliability_table(df):
    """
    Calculate Cronbach's alpha for every reflective construct
    defined in CONSTRUCT_ITEMS.

    DISC is not present in CONSTRUCT_ITEMS and therefore is never
    analyzed here.

    Returns
    -------
    pandas.DataFrame
        One row per construct.
    """
    rows = []

    for construct, items in CONSTRUCT_ITEMS.items():
        present = [item for item in items if item in df.columns]

        # Need at least 2 items to calculate Cronbach's alpha.
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

        # Need observations before attempting alpha.
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


# ---------------------------------------------------------------------
# EFA / Cross-loading
# ---------------------------------------------------------------------

def efa_cross_loading_check(df, focal=EFA_CONSTRUCTS):
    """
    Run a 2-factor EFA on the AIP + REL item set.

    Cross-loading rule:
        An item is flagged when its absolute loading is > 0.30
        on BOTH factors.

    Parameters
    ----------
    df : pandas.DataFrame
        Clean pilot dataset.

    focal : tuple[str, ...]
        Constructs included in the EFA.

    Returns
    -------
    loadings : pandas.DataFrame
        Factor loadings and cross-loading flags.

    diag : str
        KMO/Bartlett diagnostic text.
    """

    # Collect items in the configured construct order.
    items = []

    for construct in focal:
        if construct not in CONSTRUCT_ITEMS:
            continue

        items.extend(
            item
            for item in CONSTRUCT_ITEMS[construct]
            if item in df.columns
        )

    # Remove accidental duplicates while preserving order.
    items = list(dict.fromkeys(items))

    if len(items) < 2:
        return (
            pd.DataFrame(),
            "insufficient items present for EFA",
        )

    sub = df[items].dropna()

    # Conservative minimum-N check retained from original pipeline.
    if len(sub) < len(items) + MIN_EFA_EXTRA_OBS:
        return (
            pd.DataFrame(),
            f"insufficient n for EFA "
            f"(need n > n_items + {MIN_EFA_EXTRA_OBS}; "
            f"n={len(sub)}, n_items={len(items)})",
        )

    # -------------------------------------------------------------
    # Sampling adequacy / factorability diagnostics
    # -------------------------------------------------------------

    kmo_all, kmo_model = calculate_kmo(sub)
    chi2, p = calculate_bartlett_sphericity(sub)

    # -------------------------------------------------------------
    # Two-factor EFA
    # -------------------------------------------------------------

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

    # -------------------------------------------------------------
    # Cross-loading diagnostic
    # -------------------------------------------------------------

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
            "Pilot reliability and AIP/REL EFA "
            "cross-loading diagnostic."
        )
    )

    ap.add_argument(
        "--input",
        required=True,
        help="Path to the cleaned pilot CSV.",
    )

    args = ap.parse_args()

    input_path = Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    # -------------------------------------------------------------
    # Load data
    # -------------------------------------------------------------

    df = pd.read_csv(input_path)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # 1. Cronbach's alpha
    # -------------------------------------------------------------

    rel_tab = reliability_table(df)

    reliability_path = OUTPUT_DIR / "pilot_reliability.csv"
    rel_tab.to_csv(reliability_path, index=False)

    print("--- Cronbach's alpha per construct (pilot) ---")
    print(rel_tab.to_string(index=False))

    if (
        "flag_below_0.70" in rel_tab.columns
        and rel_tab["flag_below_0.70"]
        .fillna(False)
        .any()
    ):
        print(
            "!! WARNING: at least one construct "
            "has alpha < 0.70 at pilot."
        )

    # -------------------------------------------------------------
    # 2. EFA AIP + REL
    # -------------------------------------------------------------

    loadings, diag = efa_cross_loading_check(df)

    print(
        f"\n--- EFA AIP-REL cross-loading check "
        f"({diag}) ---"
    )

    if loadings.empty:
        print(diag)
        return

    efa_path = (
        OUTPUT_DIR
        / "pilot_efa_aip_rel_crossloadings.csv"
    )

    loadings.round(3).to_csv(efa_path)

    print(loadings.round(3).to_string())

    # -------------------------------------------------------------
    # 3. Cross-loading warning
    # -------------------------------------------------------------

    flagged_items = loadings.index[
        loadings["cross_loading_risk"]
    ].tolist()

    if flagged_items:
        print(
            "!! WARNING: cross-loading items detected: "
            + ", ".join(flagged_items)
        )
        print(
            f"    Rule: absolute loading > "
            f"{CROSS_LOADING_THRESHOLD:.2f} "
            f"on both factors."
        )
    else:
        print(
            "OK: no cross-loading items detected "
            f"under the >{CROSS_LOADING_THRESHOLD:.2f} rule."
        )

    # -------------------------------------------------------------
    # 4. Output confirmation
    # -------------------------------------------------------------

    print(
        "\n[03_reliability_efa] wrote:"
    )
    print(f"  - {reliability_path}")
    print(f"  - {efa_path}")


if __name__ == "__main__":
    main()