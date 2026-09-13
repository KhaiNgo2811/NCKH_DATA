import argparse
import sys
import numpy as np
import pandas as pd
import pingouin as pg

sys.path.insert(0, "src")
from _qualtrics_io import load_and_normalize  # noqa: E402
from _config import (  # noqa: E402
    FIELDED_ITEMS, CONSTRUCT_ITEMS, DISC_COL, AIP_COND_COL, CELL_COL,
    MC_AIP_COL, MC_DISC_COL, MC_MIDPOINT,
    STRAIGHTLINE_HARD_SD_THRESHOLD, DUPLICATE_MAX_DIFFERING_ITEMS,
    MAX_MISSING_ITEM_PCT,
    DEMOGRAPHIC_PNTS_CODE, DEMOGRAPHIC_PNTS_COLS,
    PII_COLUMNS,
    RECORDED_DATE_COL, MAIN_DATA_START_TIMESTAMP,
)

# ---------------------------------------------------------------------------
# POLICY CHANGE (2026-09-11, requested by Khai): the sample-filtering criteria
# were narrowed to exactly four checks (superseding the earlier 9-step
# consent/age/screener/ATT/CC/speeding set from before that):
#   1. Missing data
#   2. Duplicate response pattern
#   3. Straightlining
#   (a 4th, manipulation-check-based individual exclusion, was added then
#    immediately identified as a problem -- see the next policy change below)
#
# AMENDMENT (2026-09-11, same day, requested by Khai): the individual-level
# manipulation-check filter on MC_AIP is REMOVED. Dropping respondents based
# on MC_AIP -- a variable measured AFTER the AIP_COND treatment was
# administered -- is post-treatment conditioning: it can introduce selection
# bias into the causal estimate of AIP_COND's effect, because "how someone
# answered MC_AIP" is itself partly a consequence of the treatment (Montgomery,
# Nyhan & Torres, 2018, AJPS). The project now follows an
# Intention-to-Treat (ITT) design for this check:
#   - MC_AIP is NEVER used to drop individual rows.
#   - report_manipulation_check() reports group-level manipulation strength
#     (Welch's t-test + Cohen's d comparing MC_AIP across AIP_COND) AFTER
#     filtering, for diagnostic/manuscript purposes only -- it excludes no one.
#   - flag_extreme_reversers() marks (does not drop) respondents who show a
#     flatly reversed reading of their assigned condition, for a separate
#     robustness check (e.g. re-running H2/H3/H7 with/without this group) in
#     03_reliability_efa.py or a later analysis script -- never in this script.
#   - A respondent who quit before reaching the MC block (MC_AIP is NaN) is
#     still excluded, but via the ordinary missing-data screen on the
#     substantive item battery (since the MC block sits after all 34 items in
#     the instrument, a genuine mid-survey dropout already fails that screen
#     on its own merits) -- not via a "manipulation check fail" label, since
#     that mislabels dropout as miscomprehension.
# ---------------------------------------------------------------------------


def breakdown_mc_groups(df, mc_col=MC_AIP_COL, cond_col=AIP_COND_COL, midpoint=MC_MIDPOINT):
    """Split respondents into the two groups that were previously conflated
    under one 'manipulation_check_fail' label:
      (a) answered MC_AIP, but on the wrong side of the midpoint for their
          assigned AIP_COND (genuine miscomprehension / reversed reading)
      (b) MC_AIP is missing -- did not reach that point in the survey
          (dropout, not miscomprehension)
    Returns (table, mask_a, mask_b) -- table is a small summary DataFrame,
    the masks are boolean Series aligned to df.index for further inspection.
    """
    mc = pd.to_numeric(df[mc_col], errors="coerce")
    cond = pd.to_numeric(df[cond_col], errors="coerce")

    missing_mc = mc.isna()
    wrong_direction = pd.Series(False, index=df.index)
    wrong_direction |= (cond == 1) & (mc <= midpoint)
    wrong_direction |= (cond == 0) & (mc >= midpoint)

    mask_b = missing_mc
    mask_a = wrong_direction & ~missing_mc
    mask_correct = (~missing_mc) & (~wrong_direction)

    table = pd.DataFrame([
        {"group": "(a) answered, wrong direction (miscomprehension)", "n": int(mask_a.sum())},
        {"group": "(b) missing MC_AIP (dropout, never reached it)", "n": int(mask_b.sum())},
        {"group": "correct direction", "n": int(mask_correct.sum())},
        {"group": "TOTAL", "n": len(df)},
    ])
    return table, mask_a, mask_b


def flag_duplicate_response_pattern(df, items):
    """Flag every respondent who has another respondent with an identical or
    near-identical (<= DUPLICATE_MAX_DIFFERING_ITEMS items differing, over the
    items both answered) response pattern across the full item battery."""
    mat = df[items].to_numpy(dtype=float)
    n = len(df)
    is_dup = np.zeros(n, dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            row_i, row_j = mat[i], mat[j]
            valid = ~(np.isnan(row_i) | np.isnan(row_j))
            if valid.sum() == 0:
                continue
            n_diff = np.sum(row_i[valid] != row_j[valid])
            if n_diff <= DUPLICATE_MAX_DIFFERING_ITEMS:
                is_dup[i] = True
                is_dup[j] = True
    return pd.Series(is_dup, index=df.index)


def apply_exclusions(df):
    """Lọc bỏ các mẫu không hợp lệ (Hard drops) -- 3 tiêu chí. MC_AIP không
    còn được dùng để loại cá nhân nào (xem policy note ở đầu file)."""
    log_rows = []
    n0 = len(df)
    keep = pd.Series(True, index=df.index)

    def drop_step(mask_keep, reason):
        nonlocal keep
        n_before = keep.sum()
        mask_keep = pd.Series(mask_keep, index=df.index).fillna(False).astype(bool)
        newly_dropped = keep & ~mask_keep
        keep = keep & mask_keep
        log_rows.append({"step": reason, "n_before": int(n_before),
                          "n_dropped_this_step": int(newly_dropped.sum()),
                          "n_after": int(keep.sum())})

    present_items = [c for c in FIELDED_ITEMS if c in df.columns]

    # 1. Missing data (also catches MC-block dropouts -- MC sits after all 34
    #    items in the instrument, see policy note)
    if present_items:
        miss_pct = df[present_items].isna().mean(axis=1)
        drop_step(miss_pct <= MAX_MISSING_ITEM_PCT, "excess_missing_items")

    # 2. Duplicate / near-duplicate response pattern
    if present_items:
        dup_flag = flag_duplicate_response_pattern(df, present_items)
        drop_step(~dup_flag, "duplicate_response_pattern")

    # 3. Straightlining (hard drop -- SD ~ 0 across the full item battery)
    if present_items:
        sd = df[present_items].std(axis=1, skipna=True)
        drop_step(sd >= STRAIGHTLINE_HARD_SD_THRESHOLD, "straightlining_near_zero_sd")

    clean = df.loc[keep].copy()
    log = pd.DataFrame(log_rows)
    if len(log):
        log.loc[len(log)] = {"step": "TOTAL", "n_before": n0,
                              "n_dropped_this_step": n0 - len(clean), "n_after": len(clean)}
    return clean, log


def report_manipulation_check(df, mc_col=MC_AIP_COL, cond_col=AIP_COND_COL):
    """Group-level ITT evidence for the manipulation check (Welch's t-test +
    Cohen's d), run AFTER filtering. REPORTS ONLY -- excludes no observations.
    Returns a dict with the test statistics (None if it couldn't be computed)."""
    if mc_col not in df.columns or cond_col not in df.columns:
        return None
    cond = pd.to_numeric(df[cond_col], errors="coerce")
    mc = pd.to_numeric(df[mc_col], errors="coerce")
    g0 = mc[cond == 0].dropna()
    g1 = mc[cond == 1].dropna()
    if len(g0) < 2 or len(g1) < 2:
        return None
    res = pg.ttest(g1, g0, correction=True)  # Welch's t (unequal variances)
    d = pg.compute_effsize(g1, g0, eftype="cohen")
    p_col = "p_val" if "p_val" in res.columns else "p-val"
    result = {
        "mc_column": mc_col, "cond_column": cond_col,
        "n_group0": len(g0), "n_group1": len(g1),
        "mean_group0": round(g0.mean(), 3), "mean_group1": round(g1.mean(), 3),
        "t_welch": round(res["T"].iloc[0], 3), "p": round(res[p_col].iloc[0], 4),
        "cohens_d": round(d, 3), "flag_d_below_0.50": bool(abs(d) < 0.50),
    }
    print(f"\n[report_manipulation_check] {mc_col} by {cond_col} (Welch's t-test, group-level ITT evidence, n_excluded=0)")
    print(f"    n0={result['n_group0']} mean0={result['mean_group0']}  "
          f"n1={result['n_group1']} mean1={result['mean_group1']}")
    print(f"    Welch t={result['t_welch']}  p={result['p']}  Cohen's d={result['cohens_d']}")
    if result["flag_d_below_0.50"]:
        print(f"    !! WARNING: |d| < 0.50 -- manipulation may be weak for {mc_col}.")
    return result


def report_manipulation_check_composite(df, cond_col=AIP_COND_COL):
    """SUPPLEMENTARY (2026-09-11, requested by Khai): additional group-level ITT
    evidence using the AIP_mean composite (all fielded AIP items, currently
    AIP1-AIP5) instead of the single MC_AIP item. Same Welch's t + Cohen's d
    design as report_manipulation_check(), report-only, excludes no one.

    Rationale / caveat: AIP_mean is less noisy than the single-item MC_AIP (5
    items vs 1), so it's a reasonable SUPPLEMENTARY corroboration -- if AIP_mean
    and MC_AIP tell different stories, that's itself informative (e.g. a weak
    single-item MC_AIP reading next to a clean AIP_mean split would suggest the
    MC item itself is the noisy part, not the manipulation). But AIP_mean is
    also the measured construct that feeds H1/H2 as a predictor -- it is NOT a
    substitute for the pre-registered MC_AIP manipulation check (TF/Codebook
    §4.6), and should never be reported as "the" manipulation check in the
    manuscript. Keep both numbers side by side, don't let this one replace the
    other."""
    aip_items = [c for c in CONSTRUCT_ITEMS["AIP"] if c in df.columns]
    if not aip_items or cond_col not in df.columns:
        return None
    df["AIP_mean"] = df[aip_items].mean(axis=1)
    cond = pd.to_numeric(df[cond_col], errors="coerce")
    low = df.loc[cond == 0, "AIP_mean"].dropna()
    high = df.loc[cond == 1, "AIP_mean"].dropna()
    if len(low) < 2 or len(high) < 2:
        return None
    res = pg.ttest(high, low, correction=True)  # Welch's t (unequal variances)
    d = pg.compute_effsize(high, low, eftype="cohen")
    p_col = "p_val" if "p_val" in res.columns else "p-val"
    result = {
        "n_items": len(aip_items), "n_low": len(low), "n_high": len(high),
        "mean_low": round(low.mean(), 3), "mean_high": round(high.mean(), 3),
        "t_welch": round(res["T"].iloc[0], 3), "p": round(res[p_col].iloc[0], 4),
        "cohens_d": round(d, 3), "flag_d_below_0.50": bool(abs(d) < 0.50),
    }
    print(f"\n[report_manipulation_check_composite] AIP_mean ({result['n_items']} items) "
          f"by {cond_col} (Welch's t-test, SUPPLEMENTARY ITT evidence, n_excluded=0)")
    print(f"    n_low={result['n_low']} mean_low={result['mean_low']}  "
          f"n_high={result['n_high']} mean_high={result['mean_high']}")
    print(f"    Welch t={result['t_welch']}  p={result['p']}  Cohen's d={result['cohens_d']}")
    if result["flag_d_below_0.50"]:
        print("    !! WARNING: |d| < 0.50 on the AIP_mean composite check too.")
    return result


def flag_extreme_reversers(df, mc_col=MC_AIP_COL, cond_col=AIP_COND_COL,
                            high_reverse_thresh=3, low_reverse_thresh=5):
    """Flag (does not drop) respondents who show a flatly reversed reading of
    their assigned condition: AIP High but MC_AIP <= high_reverse_thresh, or
    AIP Low but MC_AIP >= low_reverse_thresh. For a separate robustness check
    only (e.g. re-run H2/H3/H7 with/without this group) -- never a filter."""
    if mc_col not in df.columns or cond_col not in df.columns:
        df["flag_extreme_reverser"] = False
        return df
    cond = pd.to_numeric(df[cond_col], errors="coerce")
    mc = pd.to_numeric(df[mc_col], errors="coerce")
    reversed_high = (cond == 1) & (mc <= high_reverse_thresh)
    reversed_low = (cond == 0) & (mc >= low_reverse_thresh)
    df["flag_extreme_reverser"] = (reversed_high | reversed_low).fillna(False)
    return df


def compute_collection_phase(df):
    """Adds two parallel columns, both derived from the same
    MAIN_DATA_START_TIMESTAMP cutoff compared against RECORDED_DATE_COL
    (never row order/index -- unstable across re-exports of a growing survey):

      - 'collection_phase': 'pre_LOC' / 'post_LOC' -- the technical marker
        (whether the LOC demographic item existed yet when this response was
        recorded). Kept for technical traceability.
      - 'sample_role': 'pilot' / 'main' -- the OFFICIAL administrative label
        (2026-09-13, requested by Khai) built on the same cutoff. This is an
        administrative boundary (when a field was added), NOT a
        measurement-readiness boundary -- see the printed reminder in main()
        and the note in _config.py. 04_manipulation_check.py's gate logic is
        UNCHANGED by this label and must not be loosened just because a
        'main' bucket now exists.

    Both columns are 'unknown' if RecordedDate can't be parsed."""
    if RECORDED_DATE_COL not in df.columns:
        df["collection_phase"] = "unknown"
        df["sample_role"] = "unknown"
        return df
    recorded = pd.to_datetime(df[RECORDED_DATE_COL], errors="coerce")
    cutoff = pd.to_datetime(MAIN_DATA_START_TIMESTAMP)
    df["collection_phase"] = np.where(recorded.isna(), "unknown",
                                       np.where(recorded >= cutoff, "post_LOC", "pre_LOC"))
    df["sample_role"] = np.where(recorded.isna(), "unknown",
                                  np.where(recorded < cutoff, "pilot", "main"))
    return df


def collection_checkpoint_log(df):
    """Checkpoint table keyed by sample_role (with collection_phase carried
    along for cross-reference): n per role, n/pct by AIP_COND within each
    role (differential-attrition tracking). Diagnostic only -- filters
    nobody. Always written to outputs/tables/collection_checkpoint_log.csv
    (one shared file, not per --phase) so pilot/main can be filtered out of
    it directly regardless of which --phase this run used."""
    rows = []
    if "sample_role" in df.columns:
        group_cols = ["sample_role"] + (["collection_phase"] if "collection_phase" in df.columns else [])
        for keys, sub in df.groupby(group_cols):
            keys = keys if isinstance(keys, tuple) else (keys,)
            row = dict(zip(group_cols, keys))
            row["n"] = len(sub)
            if AIP_COND_COL in df.columns:
                aip = pd.to_numeric(sub[AIP_COND_COL], errors="coerce")
                row["n_AIP_low_0"] = int((aip == 0).sum())
                row["n_AIP_high_1"] = int((aip == 1).sum())
                row["pct_AIP_high"] = round((aip == 1).mean() * 100, 1) if len(aip.dropna()) else None
            rows.append(row)
    return pd.DataFrame(rows)


def check_cell_consistency(df):
    """Diagnostic only -- does not drop anyone. Flags CELL vs AIP_COND x
    DISC_COND disagreement (Survey-Flow integrity signal)."""
    if CELL_COL not in df.columns or AIP_COND_COL not in df.columns or DISC_COL not in df.columns:
        return df
    expected_cell = {(0, 0): 1, (0, 1): 2, (1, 0): 3, (1, 1): 4}
    aip = pd.to_numeric(df[AIP_COND_COL], errors="coerce")
    disc = pd.to_numeric(df[DISC_COL], errors="coerce")
    predicted = [expected_cell.get((a, d), np.nan) if pd.notna(a) and pd.notna(d) else np.nan
                 for a, d in zip(aip, disc)]
    df["flag_cell_mismatch"] = pd.to_numeric(df[CELL_COL], errors="coerce") != pd.Series(predicted, index=df.index)
    return df


def recode_pnts(df):
    """Recode the -98 'prefer not to say' sentinel to missing (Master Codebook
    v2.6 SS4.8 / standing prohibition: no -98 in a computed statistic)."""
    for col in DEMOGRAPHIC_PNTS_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").replace(
                DEMOGRAPHIC_PNTS_CODE, np.nan)
    return df


def strip_pii(df):
    """Drop PII columns (Law 91/2025/QH15 Art. 2) before writing the processed
    output. strip_pii.py only de-identifies the RAW export before commit; this
    is the equivalent safeguard for the CLEANED output, since data/processed/
    has been found tracked in git despite .gitignore's intent (see CLAUDE.md
    SS0 / README "Data handling") -- belt and suspenders, not a substitute for
    also fixing the git tracking state."""
    return df.drop(columns=[c for c in PII_COLUMNS if c in df.columns], errors="ignore")


def compute_construct_scores(df):
    """Add one unweighted-mean column per construct (AIP_mean, REL_mean, ...)
    to the cleaned output, so downstream scripts/analysts don't each
    reimplement this (05_anova_h3.py currently computes INT_mean inline and
    doesn't persist it; report_manipulation_check_composite() needs AIP_mean).
    ENG_mean is still the sole structural-model input for ENG (pooled, per
    Amendment A-12) -- this does not add per-dimension ENG scores; use
    _config.py::ENG_DIMENSIONS directly if those are needed."""
    for construct, items in CONSTRUCT_ITEMS.items():
        present = [c for c in items if c in df.columns]
        if present:
            df[f"{construct}_mean"] = df[present].mean(axis=1)
    return df


def recode_cond(df):
    if AIP_COND_COL in df.columns:
        df[AIP_COND_COL] = pd.to_numeric(df[AIP_COND_COL], errors="coerce").round().astype("Int64")
    if DISC_COL in df.columns:
        df[DISC_COL] = pd.to_numeric(df[DISC_COL], errors="coerce").round().astype("Int64")
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--phase", choices=["pilot", "main"], required=True)
    args = ap.parse_args()

    df = load_and_normalize(args.input)
    df = check_cell_consistency(df)

    # Step 1: breakdown BEFORE filtering -- (a) miscomprehension vs (b) dropout,
    # previously conflated under one "manipulation_check_fail" label.
    mc_table, _, _ = breakdown_mc_groups(df)
    print("[01_clean] MC_AIP breakdown BEFORE filtering (diagnostic only, not a filter step):")
    print(mc_table.to_string(index=False))

    clean, log = apply_exclusions(df)
    clean = recode_cond(clean)
    clean = recode_pnts(clean)
    clean = compute_construct_scores(clean)
    clean = compute_collection_phase(clean)

    print("\nNOTE: sample_role boundary is administrative (LOC field added), "
          "not a measurement-readiness boundary. Manipulation-check gate "
          "(04_manipulation_check.py) has not cleared d>=0.50 as of the most "
          "recent batch on this side of the boundary either. See TF v2.10, OD-12.")

    checkpoint = collection_checkpoint_log(clean)
    print("\n[collection_checkpoint_log] n by sample_role (pilot/main) and collection_phase, "
          "with AIP_COND breakdown:")
    print(checkpoint.to_string(index=False) if len(checkpoint) else "(no data)")
    checkpoint_path = "outputs/tables/collection_checkpoint_log.csv"
    checkpoint.to_csv(checkpoint_path, index=False)

    # Group-level ITT evidence (report only, n_excluded=0) -- run AFTER filtering.
    mc_result = report_manipulation_check(clean, MC_AIP_COL, AIP_COND_COL)
    disc_result = report_manipulation_check(clean, MC_DISC_COL, DISC_COL)
    composite_result = report_manipulation_check_composite(clean, AIP_COND_COL)

    if mc_result is not None:
        log.loc[len(log)] = {
            "step": f"manipulation_check_group_evidence (report only, n_excluded=0, "
                    f"d={mc_result['cohens_d']}, p={mc_result['p']})",
            "n_before": len(clean), "n_dropped_this_step": 0, "n_after": len(clean),
        }
    if composite_result is not None:
        log.loc[len(log)] = {
            "step": f"manipulation_check_composite_evidence (report only, n_excluded=0, "
                    f"AIP_mean d={composite_result['cohens_d']}, p={composite_result['p']})",
            "n_before": len(clean), "n_dropped_this_step": 0, "n_after": len(clean),
        }

    # Extreme-reverser flag (for a separate robustness check -- not a filter).
    clean = flag_extreme_reversers(clean)
    n_reversers = int(clean["flag_extreme_reverser"].sum())
    print(f"\n[flag_extreme_reversers] flagged (not dropped): {n_reversers} / {len(clean)}")

    clean = strip_pii(clean)

    out_csv = f"data/processed/{args.phase}_clean.csv"
    out_log = f"outputs/tables/{args.phase}_exclusion_log.csv"
    clean.to_csv(out_csv, index=False)
    log.to_csv(out_log, index=False)

    print(f"\n[01_clean] input={args.input} phase={args.phase}")
    print(log.to_string(index=False))
    print(f"[01_clean] wrote {out_csv} (n={len(clean)}), {out_log}, and {checkpoint_path}")


if __name__ == "__main__":
    main()
