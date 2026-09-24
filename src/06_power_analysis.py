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

k reduced from 8 to 6 by Amendment A-8: the full model is now INT, PDPL, DISC,
INTxPDPL, INTxDISC, +1 -- PDPLxDISC and INTxPDPLxDISC are retired, no longer part of
the model. Because beta_M1 and beta_M2 share the same k and the same formula, this
script's output applies identically to both terms -- it is not a calculation for just
one of them.

This is the Python cross-check ONLY. Must be reconciled against the R-side pwr/WebPower
check (PLS-specific power can differ from this OLS-regression analogue) before the
Qualtrics quota is frozen - see CLAUDE.md SS5.

OBSERVED f2 (2026-09-17, requested by Khai): --input lets this script also compute an
EMPIRICAL f2 from the real data, instead of only the two assumed scenarios (0.02/0.009)
above. compute_observed_f2() fits THREE PLS-SEM models via rpy2/seminr on the same
data -- a FULL model (with both INT*PDPL and INT*DISC, i.e. the actual
07_plssem_bridge.R structural model), a model WITHOUT INT*PDPL only (M1 dropped, M2
kept), and a model WITHOUT INT*DISC only (M2 dropped, M1 kept) -- and applies Cohen's
f2 SEPARATELY for each term: f2_M1 = (R2_full - R2_no_M1)/(1-R2_full), f2_M2 =
(R2_full - R2_no_M2)/(1-R2_full), both on R2(TRU) (the outcome both interaction terms
point to). This is the standard per-predictor f2 convention (each term's own
incremental R2, holding the other interaction term in the model) -- NOT the earlier
(pre-2026-09-17-refit) version, which dropped both interaction terms at once and
reported one joint f2 for "M1/M2 combined." Both f2_M1/f2_M2 are then run through the
SAME required_n()/power_at_n() functions as the two assumed scenarios, at the same
k=6/alpha=.05/power=.80, so all four numbers are directly comparable in one table.

PERCEIVED H7b f2 (2026-09-17, requested by Khai): the literal request asked to
substitute AIP_COND (assigned, binary) for MC_AIP (measured, continuous 1-7)
inside the H7a/H7b interaction term(s), to test whether misclassification
error in an assigned condition is suppressing the observed f2. Checked against
07_plssem_bridge.R's actual model first: AIP_COND isn't part of the PLS-SEM
model at all (ANOVA-only), H7a's moderator (PDPL) is already fully continuous
(nothing to swap), and H7b's moderator (DISC) wraps DISC_COND, not AIP_COND.
Confirmed with Khai and implemented as the closest valid analog:
compute_observed_f2_perceived() swaps DISC_COND for MC_DISC in the DISC
composite for H7b ONLY (--perceived-disc flag), leaving PDPL/H7a unchanged,
and the "Comparison" printout at the end of main() reports assigned vs.
perceived f2 for H7b directly.

Usage:
    python src/06_power_analysis.py
    python src/06_power_analysis.py --f2 0.02 0.009 --k 6 --alpha 0.05 --power 0.80
    python src/06_power_analysis.py --input data/processed/main_clean_data.csv
    python src/06_power_analysis.py --input data/processed/main_clean_data.csv --perceived-disc
"""
import argparse
import sys

import pandas as pd
from scipy.stats import f as fdist
from scipy.stats import ncf

try:
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.conversion import localconverter
    RPY2_AVAILABLE = True
except ImportError:
    RPY2_AVAILABLE = False

sys.path.insert(0, "src")
from _config import CONSTRUCT_ITEMS, DISC_COL, MC_DISC_COL  # noqa: E402


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


def f2_significance(f2, n, k):
    """Incremental F-test for a single added term's f2 (Cohen 1988): the same
    OLS-regression-analogue convention required_n()/power_at_n() already use,
    just run as a significance test instead of a power calc. F =
    f2 * df_denom / df_num, df_num=1 (the one term being tested), df_denom =
    n - k - 1, under the CENTRAL F distribution (H0: this term adds no
    incremental R2). Added 2026-09-17 (requested by Khai) alongside the
    per-term f2_M1/f2_M2 split -- an f2 number alone doesn't say whether that
    increment is distinguishable from zero at this n. Same OLS-analogue
    caveat as everywhere else in this script: this is NOT the actual
    PLS-SEM bootstrap p-value for beta_M1/beta_M2 (that comes from
    run_plssem.py's 10,000-resample bootstrap CIs) -- it is a power/sample-
    size-planning sanity check only."""
    df_num, df_denom = 1, n - k - 1
    if df_denom <= 0:
        return None, None
    f_stat = f2 * df_denom / df_num
    p_value = float(1 - fdist.cdf(f_stat, df_num, df_denom))
    return float(f_stat), p_value


# ---------------------------------------------------------------------------
# R model definitions duplicated (deliberately) from 07_plssem_bridge.R's
# measurement/structural model, rather than sourcing that file, because the
# REDUCED model here needs the two interaction_term()/paths() calls removed --
# a variant 07_plssem_bridge.R's run_plssem() doesn't parameterize for. Keep
# both in sync by hand if the base measurement/structural model ever changes
# (item ranges, added/removed paths) -- see CLAUDE.md SS13.
#
# The DISC composite's single item is a separate constant, not baked into
# _R_MEASUREMENT_COMMON, because compute_observed_f2_perceived() (2026-09-17,
# see its docstring) needs to swap it for MC_DISC while leaving every other
# construct (including PDPL/H7a) untouched.
# ---------------------------------------------------------------------------
_R_MEASUREMENT_COMMON = """
composite("AIP",  multi_items("AIP", 1:5)),
composite("REL",  multi_items("REL", 1:4)),
composite("INT",  multi_items("INT", 1:5)),
composite("TRU",  multi_items("TRU", 1:6)),
composite("ENG",  multi_items("ENG", 1:6)),
composite("PI",   multi_items("PI", 1:4)),
composite("PDPL", multi_items("PDPL", 1:4))
"""

_R_DISC_COMPOSITE_ASSIGNED = 'composite("DISC", single_item("DISC_COND"))'
_R_DISC_COMPOSITE_PERCEIVED = 'composite("DISC", single_item("MC_DISC"))'

_R_STRUCTURE_COMMON = """
paths(from = "AIP",  to = c("REL", "INT")),
paths(from = "REL",  to = c("TRU", "ENG")),
paths(from = "INT",  to = c("TRU", "ENG", "PI")),
paths(from = "TRU",  to = "ENG"),
paths(from = "ENG",  to = "PI"),
paths(from = "DISC", to = "INT"),
paths(from = "PDPL", to = "TRU"),
paths(from = "DISC", to = "TRU")
"""

_R_SCRIPT_TEMPLATE = """
library(seminr)

# fit_model(data, include_m1, include_m2) builds the measurement/structural model
# with either, both, or neither of the two interaction_term()/paths() pairs
# included -- used to isolate each term's OWN incremental R2(TRU), holding the
# other interaction term fixed in the model, per the standard PLS-SEM f2
# convention (Cohen 1988; Hair et al. 2022 SS "Effect size f2").
fit_model <- function(data, include_m1, include_m2) {{
  composites <- list(
    {measurement_common},
    {disc_composite}
  )
  interactions <- list()
  if (include_m1) {{
    interactions[[length(interactions) + 1]] <-
      interaction_term(iv = "INT", moderator = "PDPL", method = two_stage)
  }}
  if (include_m2) {{
    interactions[[length(interactions) + 1]] <-
      interaction_term(iv = "INT", moderator = "DISC", method = two_stage)
  }}
  measurements <- do.call(constructs, c(composites, interactions))

  base_paths <- list(
    {structure_common}
  )
  extra_paths <- list()
  if (include_m1) extra_paths[[length(extra_paths) + 1]] <- paths(from = "INT*PDPL", to = "TRU")
  if (include_m2) extra_paths[[length(extra_paths) + 1]] <- paths(from = "INT*DISC", to = "TRU")
  structure <- do.call(relationships, c(base_paths, extra_paths))

  estimate_pls(data = data, measurement_model = measurements,
               structural_model = structure, missing_value = NA)
}}

model_full  <- fit_model(input_data, TRUE,  TRUE)   # both M1, M2
model_no_m1 <- fit_model(input_data, FALSE, TRUE)   # M1 (INT*PDPL) dropped, M2 kept
model_no_m2 <- fit_model(input_data, TRUE,  FALSE)  # M2 (INT*DISC) dropped, M1 kept

c(r2_full  = model_full$rSquared["Rsq", "TRU"],
  r2_no_m1 = model_no_m1$rSquared["Rsq", "TRU"],
  r2_no_m2 = model_no_m2$rSquared["Rsq", "TRU"],
  beta_m1  = model_full$path_coef["INT*PDPL", "TRU"],
  beta_m2  = model_full$path_coef["INT*DISC", "TRU"],
  n = nrow(input_data))
"""


def compute_observed_f2(input_csv, sample_role="all", k=6):
    """Fit three PLS-SEM models on real data (full; without M1 only; without
    M2 only) and return Cohen's f2 SEPARATELY for each interaction term:
    f2_M1 = (R2_full - R2_no_M1) / (1 - R2_full), f2_M2 = (R2_full - R2_no_M2)
    / (1 - R2_full), both on R2(TRU) -- the construct both interaction terms
    point to. Each term's f2 isolates its OWN incremental R2, holding the
    other interaction term in the model (standard per-predictor f2
    convention), rather than the joint f2 an earlier version of this function
    reported for both terms dropped at once. Returns None (with a printed
    reason) if rpy2/R aren't available or the input is unusable; never raises
    on a missing R environment, since this is meant to be an optional
    addition to the two assumed-f2 scenarios, not a hard requirement to run
    this script at all."""
    if not RPY2_AVAILABLE:
        print("!! Cannot compute observed f2: rpy2 is not installed / R environment "
              "not configured. Falling back to the assumed-f2 scenarios only. "
              "See README.md Setup for installing R + seminr/cSEM/pwr.")
        return None

    df = pd.read_csv(input_csv)
    if sample_role != "all":
        if "sample_role" not in df.columns:
            print(f"!! WARNING: --sample-role={sample_role} requested but the input "
                  f"has no 'sample_role' column -- using the full input instead.")
        else:
            df = df[df["sample_role"] == sample_role].copy()

    needed_cols = [c for items in CONSTRUCT_ITEMS.values() for c in items] + [DISC_COL]
    missing = [c for c in needed_cols if c not in df.columns]
    if missing:
        print(f"!! Cannot compute observed f2: input is missing required columns: {missing}")
        return None
    df = df[needed_cols].dropna()
    if len(df) < 20:
        print(f"!! Cannot compute observed f2: only {len(df)} complete rows -- too few "
              f"for a stable PLS-SEM fit.")
        return None

    r_script = _R_SCRIPT_TEMPLATE.format(
        measurement_common=_R_MEASUREMENT_COMMON, structure_common=_R_STRUCTURE_COMMON,
        disc_composite=_R_DISC_COMPOSITE_ASSIGNED)

    with localconverter(ro.default_converter + pandas2ri.converter):
        r_df = ro.conversion.py2rpy(df)
    ro.globalenv["input_data"] = r_df

    result = ro.r(r_script)
    r2_full = float(result.rx2("r2_full")[0])
    r2_no_m1 = float(result.rx2("r2_no_m1")[0])
    r2_no_m2 = float(result.rx2("r2_no_m2")[0])
    beta_m1 = float(result.rx2("beta_m1")[0])
    beta_m2 = float(result.rx2("beta_m2")[0])
    n = int(result.rx2("n")[0])

    if r2_full >= 1.0:
        print("!! Cannot compute observed f2: R2_full >= 1.0 (degenerate model).")
        return None

    f2_m1 = (r2_full - r2_no_m1) / (1 - r2_full)
    f2_m2 = (r2_full - r2_no_m2) / (1 - r2_full)
    f_m1, p_m1 = f2_significance(f2_m1, n, k)
    f_m2, p_m2 = f2_significance(f2_m2, n, k)
    print(f"\n[compute_observed_f2] n={n}  R2(TRU) full={r2_full:.4f}  "
          f"R2(TRU) without M1(INT*PDPL)={r2_no_m1:.4f}  "
          f"R2(TRU) without M2(INT*DISC)={r2_no_m2:.4f}\n"
          f"    beta_M1 (H7a, INT*PDPL -> TRU, path coef. from the full model) = {beta_m1:.4f}\n"
          f"    f2_M1 (H7a, INT*PDPL) = ({r2_full:.4f} - {r2_no_m1:.4f}) / (1 - {r2_full:.4f}) "
          f"= {f2_m1:.4f}  (F={f_m1:.3f}, p={p_m1:.4f})\n"
          f"    beta_M2 (H7b, INT*DISC -> TRU, path coef. from the full model) = {beta_m2:.4f}\n"
          f"    f2_M2 (H7b, INT*DISC) = ({r2_full:.4f} - {r2_no_m2:.4f}) / (1 - {r2_full:.4f}) "
          f"= {f2_m2:.4f}  (F={f_m2:.3f}, p={p_m2:.4f})")
    return {"n": n, "r2_full": r2_full, "r2_no_m1": r2_no_m1, "r2_no_m2": r2_no_m2,
            "beta_m1": beta_m1, "beta_m2": beta_m2,
            "f2_m1": f2_m1, "f2_m2": f2_m2, "p_m1": p_m1, "p_m2": p_m2}


def compute_observed_f2_perceived(input_csv, sample_role="all", k=6):
    """"As-perceived" H7b variant (2026-09-17, requested by Khai). The literal
    request asked to swap AIP_COND (assigned) for MC_AIP (measured, 1-7) inside
    the H7a/H7b interaction term(s) "if applicable to the current design" -- to
    test whether misclassification error in an assigned condition is
    suppressing the observed f2. Checked against the actual
    07_plssem_bridge.R structural model first: AIP_COND does not appear
    anywhere in the PLS-SEM model at all (it's ANOVA-only, 05_anova_h3.py).
    H7a's moderator (PDPL) is already a full continuous multi-item construct
    -- there is no assigned/perceived distinction to test there. H7b's
    moderator (DISC) DOES wrap an assigned 0/1 dummy, but it's DISC_COND, not
    AIP_COND. Confirmed with Khai (AskUserQuestion) and implemented as the
    closest valid analog: swap DISC_COND for MC_DISC in the DISC composite
    ONLY, leaving PDPL/H7a completely unchanged, and compare f2_perceived
    (MC_DISC) against f2_observed/compute_observed_f2()'s DISC_COND-based
    result on the SAME rows. Keeps ALL n (no exclusion) other than the
    complete-case requirement compute_observed_f2() already applies -- MC_DISC
    is just one more required column here, not a filter.

    Same per-term (M1 held out / M2 held out) PLS-SEM / Cohen's f2 methodology
    as compute_observed_f2() (see that docstring) -- only the DISC composite's
    single item changes. f2_m1 is returned too (PDPL/H7a is unchanged here, so
    it should closely match compute_observed_f2()'s f2_m1 on the same rows --
    a built-in consistency check), but the headline number for this function
    is f2_m2 (H7b, perceived)."""
    if not RPY2_AVAILABLE:
        print("!! Cannot compute perceived f2: rpy2 is not installed / R environment "
              "not configured.")
        return None

    df = pd.read_csv(input_csv)
    if sample_role != "all":
        if "sample_role" not in df.columns:
            print(f"!! WARNING: --sample-role={sample_role} requested but the input "
                  f"has no 'sample_role' column -- using the full input instead.")
        else:
            df = df[df["sample_role"] == sample_role].copy()

    needed_cols = [c for items in CONSTRUCT_ITEMS.values() for c in items] + [DISC_COL, MC_DISC_COL]
    missing = [c for c in needed_cols if c not in df.columns]
    if missing:
        print(f"!! Cannot compute perceived f2: input is missing required columns: {missing}")
        return None
    df = df[needed_cols].dropna()
    if len(df) < 20:
        print(f"!! Cannot compute perceived f2: only {len(df)} complete rows -- too few "
              f"for a stable PLS-SEM fit.")
        return None

    r_script = _R_SCRIPT_TEMPLATE.format(
        measurement_common=_R_MEASUREMENT_COMMON, structure_common=_R_STRUCTURE_COMMON,
        disc_composite=_R_DISC_COMPOSITE_PERCEIVED)

    with localconverter(ro.default_converter + pandas2ri.converter):
        r_df = ro.conversion.py2rpy(df)
    ro.globalenv["input_data"] = r_df

    result = ro.r(r_script)
    r2_full = float(result.rx2("r2_full")[0])
    r2_no_m1 = float(result.rx2("r2_no_m1")[0])
    r2_no_m2 = float(result.rx2("r2_no_m2")[0])
    beta_m1 = float(result.rx2("beta_m1")[0])
    beta_m2_perceived = float(result.rx2("beta_m2")[0])
    n = int(result.rx2("n")[0])

    if r2_full >= 1.0:
        print("!! Cannot compute perceived f2: R2_full >= 1.0 (degenerate model).")
        return None

    f2_m1 = (r2_full - r2_no_m1) / (1 - r2_full)
    f2_m2_perceived = (r2_full - r2_no_m2) / (1 - r2_full)
    f_m1, p_m1 = f2_significance(f2_m1, n, k)
    f_m2, p_m2_perceived = f2_significance(f2_m2_perceived, n, k)
    print(f"\n[compute_observed_f2_perceived] n={n}  DISC=MC_DISC (perceived, continuous 1-7) "
          f"instead of DISC_COND (assigned) -- PDPL/H7a unchanged\n"
          f"    beta_M1 (H7a, INT*PDPL -> TRU, consistency check) = {beta_m1:.4f}\n"
          f"    f2_M1 (H7a, INT*PDPL, unchanged-model consistency check) = {f2_m1:.4f}  "
          f"(F={f_m1:.3f}, p={p_m1:.4f})\n"
          f"    beta_M2 (H7b, INT*DISC -> TRU, perceived/MC_DISC) = {beta_m2_perceived:.4f}\n"
          f"    f2_M2 (H7b, INT*DISC, perceived/MC_DISC) = {f2_m2_perceived:.4f}  "
          f"(F={f_m2:.3f}, p={p_m2_perceived:.4f})")
    return {"n": n, "r2_full": r2_full, "r2_no_m1": r2_no_m1, "r2_no_m2": r2_no_m2,
            "beta_m1": beta_m1, "beta_m2_perceived": beta_m2_perceived,
            "f2_m1": f2_m1, "f2_m2_perceived": f2_m2_perceived,
            "p_m1": p_m1, "p_m2_perceived": p_m2_perceived}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--f2", nargs="+", type=float, default=[0.02, 0.009],
                     help="effect sizes to evaluate (default: TF target + Aguinis risk band)")
    ap.add_argument("--k", type=int, default=6,
                     help="total predictor terms in the full model (INT, PDPL, DISC, "
                          "INTxPDPL, INTxDISC, +1). PDPLxDISC and INTxPDPLxDISC are "
                          "retired (Amendment A-8) -- no longer part of the model.")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.80)
    ap.add_argument("--input", default=None,
                     help="Optional: a cleaned CSV (e.g. data/processed/main_clean_data.csv). "
                          "If given, also fits the observed/empirical f2 via "
                          "compute_observed_f2() and adds it to the table. Omit to get "
                          "only the two assumed-f2 scenarios (original behavior).")
    ap.add_argument("--sample-role", choices=["pilot", "main", "all"], default="all",
                     help="Optional row filter on 'sample_role' when --input is given "
                          "(see CLAUDE.md SS9/SS12). Ignored without --input.")
    ap.add_argument("--perceived-disc", action="store_true",
                     help="Optional, requires --input: also fit "
                          "compute_observed_f2_perceived() -- the H7b DISC composite "
                          "uses MC_DISC (continuous, perceived) instead of DISC_COND "
                          "(assigned), PDPL/H7a unchanged -- and print it alongside "
                          "the DISC_COND-based f2 for comparison. Off by default "
                          "since it fits one more full/reduced PLS-SEM pair.")
    args = ap.parse_args()

    labels = {0.02: "a priori target (TF v2.3 SS C.2)",
              0.009: "conservative risk band (Aguinis et al. 2005 median)"}
    rows = []
    for f2 in args.f2:
        n, achieved = required_n(f2, args.k, args.alpha, args.power)
        rows.append({
            "scenario": labels.get(f2, f"f2={f2}"), "beta": None, "f2": f2, "k": args.k,
            "alpha": args.alpha, "target_power": args.power,
            "required_n": n, "achieved_power_at_n": round(achieved, 4) if achieved else None,
            "p_value": None,  # assumed scenarios aren't fit on real data -- no beta/p to report
        })

    observed = None
    if args.input:
        observed = compute_observed_f2(args.input, args.sample_role, args.k)
        if observed is not None:
            for label, beta_key, f2_key, p_key in (
                    ("H7a", "beta_m1", "f2_m1", "p_m1"), ("H7b", "beta_m2", "f2_m2", "p_m2")):
                f2 = observed[f2_key]
                n_req, achieved = required_n(f2, args.k, args.alpha, args.power)
                rows.append({
                    "scenario": f"observed {label} (empirical PLS-SEM, n={observed['n']})",
                    "beta": round(observed[beta_key], 4), "f2": round(f2, 4), "k": args.k,
                    "alpha": args.alpha, "target_power": args.power,
                    "required_n": n_req, "achieved_power_at_n": round(achieved, 4) if achieved else None,
                    "p_value": round(observed[p_key], 4) if observed[p_key] is not None else None,
                })

    perceived = None
    if args.perceived_disc:
        if not args.input:
            print("!! --perceived-disc requires --input -- skipping.")
        else:
            perceived = compute_observed_f2_perceived(args.input, args.sample_role, args.k)
            if perceived is not None:
                f2 = perceived["f2_m2_perceived"]
                n_req, achieved = required_n(f2, args.k, args.alpha, args.power)
                rows.append({
                    "scenario": f"perceived H7b (MC_DISC, n={perceived['n']})",
                    "beta": round(perceived["beta_m2_perceived"], 4), "f2": round(f2, 4), "k": args.k,
                    "alpha": args.alpha, "target_power": args.power,
                    "required_n": n_req, "achieved_power_at_n": round(achieved, 4) if achieved else None,
                    "p_value": round(perceived["p_m2_perceived"], 4)
                    if perceived["p_m2_perceived"] is not None else None,
                })

    out = pd.DataFrame(rows)
    out.to_csv("outputs/tables/OD2_power_analysis_beta_M1_M2.csv", index=False)
    print("--- OD-2 (CLOSED, Amendment A-8): Power analysis for beta_M1 (INT x PDPL -> TRU, "
          "H7a) and beta_M2 (INT x DISC -> TRU, H7b) ---")
    print("NOTE: the two assumed-f2 scenario rows (a priori/conservative) use the same "
          "k=6/formula for both terms by convention -- but the 'observed' rows (when "
          "--input is given) now fit f2_M1 and f2_M2 SEPARATELY, each term's own "
          "incremental R2(TRU) holding the other interaction term in the model. "
          "beta (new, 2026-09-17) is that term's own path coefficient (INT*PDPL->TRU / "
          "INT*DISC->TRU) from the FULL PLS-SEM model -- the actual seminr path_coef, "
          "not an OLS proxy. p_value is the incremental-F-test significance of that "
          "term's f2 (central F, df_num=1, df_denom=n-k-1) -- an OLS-analogue sanity "
          "check for whether the increment is distinguishable from zero at this n, "
          "NOT the actual PLS-SEM bootstrap p-value (that's run_plssem.py's 10,000-"
          "resample bootstrap CI on beta_M1/beta_M2 -- cross-validate against it).")
    print(out.to_string(index=False))
    if observed is not None:
        print(f"\nComparison -- assumed f2 vs. observed/empirical f2 vs. required n:")
        for _, r in out.iterrows():
            print(f"    {r['scenario']}: beta={r['beta']}, f2={r['f2']}, p={r['p_value']}, "
                  f"required_n={r['required_n']}")
    if perceived is not None and observed is not None:
        delta = perceived["f2_m2_perceived"] - observed["f2_m2"]
        direction = "HIGHER (misclassification may be suppressing observed f2)" if delta > 0 else \
                    "LOWER or unchanged (no evidence misclassification is suppressing observed f2)"
        print(f"\nH7b assigned (DISC_COND) vs. perceived (MC_DISC) f2: "
              f"{observed['f2_m2']:.4f} -> {perceived['f2_m2_perceived']:.4f} "
              f"(delta={delta:+.4f}) -- perceived is {direction}. "
              f"NOTE: H7a/PDPL is unaffected -- PDPL is already a full continuous "
              f"construct, there is no assigned/perceived distinction to test there.")
    print("\nNOTE: cross-validate against the R-side pwr::pwr.f2.test() / WebPower check "
          "before freezing the Qualtrics quota (CLAUDE.md SS5). This is an OLS-regression "
          "analogue, not a PLS-SEM-specific power calc - use it as a sanity bound.")


if __name__ == "__main__":
    main()
