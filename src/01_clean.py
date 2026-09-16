import argparse
import sys
import numpy as np
import pandas as pd
import pingouin as pg

sys.path.insert(0, "src")
from _qualtrics_io import load_and_normalize, anchor_match  # noqa: E402
from _config import (  # noqa: E402
    FIELDED_ITEMS, CONSTRUCT_ITEMS, DISC_COL, AIP_COND_COL, CELL_COL,
    MC_AIP_COL, MC_DISC_COL, MC_MIDPOINT,
    STRAIGHTLINE_HARD_SD_THRESHOLD, DUPLICATE_MAX_DIFFERING_ITEMS, DUPLICATE_MIN_OVERLAP_ITEMS,
    MISSING_ITEM_TOLERANCE,
    DEMOGRAPHIC_PNTS_CODE, DEMOGRAPHIC_PNTS_COLS,
    PII_COLUMNS,
    RECORDED_DATE_COL, MAIN_DATA_START_TIMESTAMP,
    CONSENT_COL, CONSENT_OK_ANCHOR, AGE_COL, AGE_OK_ANCHOR, OMNI_COL, OMNI_OK_ANCHOR,
    ATT1_COL, ATT1_CORRECT, ATT2_COL, ATT2_CORRECT,
    CC1_COL, CC2_COL, CC1_PLATFORM_ANCHOR, CC1_PERSONALIZED_ANCHOR, CC2_YES_ANCHOR, CC2_NO_ANCHOR,
    SPEEDING_MIN_SECONDS, DURATION_COL,
)

# ---------------------------------------------------------------------------
# POLICY HISTORY:
#   2026-09-11: narrowed from the original 9-step hard-drop set (consent, age,
#     omni, ATT1/ATT2, CC1/CC2, speeding) down to 3 (missing data, duplicate
#     pattern, straightlining), and removed individual-level MC_AIP filtering
#     (ITT redesign, see below).
#   2026-09-16 (requested by Khai, this policy is CURRENT): reinstated the
#     9-step hard-drop set, in this order: consent -> age screener -> omni
#     screener -> attention checks (ATT1/ATT2) -> comprehension checks
#     (CC1/CC2) -> speeder floor -> missing item (now ZERO tolerance, not
#     <=10%) -> duplicate response pattern -> straightlining. See
#     build_hard_drop_masks() / HARD_DROP_STEP_ORDER below and CLAUDE.md SS12.
#
# NOT reverted by the 2026-09-16 change -- the ITT rationale for manipulation
# checks stands independently of how many other hard-drop criteria exist:
#   The individual-level manipulation-check filter on MC_AIP/MC_DISC is
#   REMOVED and stays removed. Dropping respondents based on MC_AIP -- a
#   variable measured AFTER the AIP_COND treatment was administered -- is
#   post-treatment conditioning: it can introduce selection bias into the
#   causal estimate of AIP_COND's effect, because "how someone answered
#   MC_AIP" is itself partly a consequence of the treatment (Montgomery,
#   Nyhan & Torres, 2018, AJPS). The project follows an
#   Intention-to-Treat (ITT) design for this check:
#   - MC_AIP/MC_DISC are NEVER used to drop individual rows.
#   - report_manipulation_check() reports group-level manipulation strength
#     (Welch's t-test + Cohen's d) AFTER filtering -- diagnostic only.
#   - manipulation_check_sensitivity() (2026-09-16) extends this to several
#     sample definitions at once (full sample, without the new speeder floor,
#     by collection_phase, excluding extreme reversers) -- still report-only,
#     the mechanism for resolving OD-12, not a new exclusion gate.
#   - flag_extreme_reversers() marks (does not drop) respondents who show a
#     flatly reversed reading of their assigned condition.
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


def breakdown_attention_groups(df, att1_col=ATT1_COL, att2_col=ATT2_COL,
                                att1_correct=ATT1_CORRECT, att2_correct=ATT2_CORRECT):
    """Same idea as breakdown_mc_groups(), applied to step 4
    (attention_check_fail): split respondents into the two groups the raw
    funnel count conflates under one label:
      (a) answered BOTH ATT1 and ATT2, but got at least one wrong (genuine
          inattention -- a real reason to drop)
      (b) missing ATT1 and/or ATT2 -- did not reach/finish that point in the
          survey (dropout, not inattention -- a different reason to drop)
    ATT2 sits after the ENG block, well past ATT1 (after INT), so a
    respondent who quit partway through can be missing one, the other, or
    both -- 'missing' here means missing on either.
    Returns (table, mask_a, mask_b) -- table is a small summary DataFrame,
    the masks are boolean Series aligned to df.index for further inspection.
    """
    att1 = pd.to_numeric(df[att1_col], errors="coerce") if att1_col in df.columns else pd.Series(np.nan, index=df.index)
    att2 = pd.to_numeric(df[att2_col], errors="coerce") if att2_col in df.columns else pd.Series(np.nan, index=df.index)

    missing_either = att1.isna() | att2.isna()
    wrong_answer = (~missing_either) & ((att1 != att1_correct) | (att2 != att2_correct))
    mask_b = missing_either
    mask_a = wrong_answer
    mask_correct = (~missing_either) & (~wrong_answer)

    table = pd.DataFrame([
        {"group": "(a) answered both, at least one wrong (genuine inattention)", "n": int(mask_a.sum())},
        {"group": "(b) missing ATT1 and/or ATT2 (dropout, never reached/finished it)", "n": int(mask_b.sum())},
        {"group": "correct on both", "n": int(mask_correct.sum())},
        {"group": "TOTAL", "n": len(df)},
    ])
    return table, mask_a, mask_b


def flag_duplicate_response_pattern(df, items):
    """Flag every respondent who has another respondent with an identical or
    near-identical (<= DUPLICATE_MAX_DIFFERING_ITEMS items differing, over the
    items both answered) response pattern across the full item battery.

    Requires >= DUPLICATE_MIN_OVERLAP_ITEMS jointly-answered items before a
    pair is even considered (see _config.py note) -- otherwise two heavily
    incomplete responses could match by chance on a handful of shared items
    and get flagged as duplicates for no real content-overlap reason."""
    mat = df[items].to_numpy(dtype=float)
    n = len(df)
    is_dup = np.zeros(n, dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            row_i, row_j = mat[i], mat[j]
            valid = ~(np.isnan(row_i) | np.isnan(row_j))
            if valid.sum() < DUPLICATE_MIN_OVERLAP_ITEMS:
                continue
            n_diff = np.sum(row_i[valid] != row_j[valid])
            if n_diff <= DUPLICATE_MAX_DIFFERING_ITEMS:
                is_dup[i] = True
                is_dup[j] = True
    return pd.Series(is_dup, index=df.index)


# Execution order for the 9-step hard-drop policy (2026-09-16). This governs
# both apply_exclusions()'s funnel table AND which masks
# manipulation_check_sensitivity() can recombine (e.g. "all steps except the
# speeder floor") -- see build_hard_drop_masks().
HARD_DROP_STEP_ORDER = [
    "consent_fail",
    "screener_age_fail",
    "screener_omni_fail",
    "attention_check_fail",
    "comprehension_check_fail",
    "speeder_under_120s",
    "excess_missing_items",
    "duplicate_response_pattern",
    "straightlining_near_zero_sd",
]


def build_hard_drop_masks(df, present_items):
    """Build one boolean 'keep' mask per hard-drop step (True = passes this
    step), keyed by the same names as HARD_DROP_STEP_ORDER. Split out from
    apply_exclusions() so manipulation_check_sensitivity() can recombine a
    SUBSET of these steps (e.g. every step except the speeder floor) without
    duplicating the per-step logic."""
    masks = {}

    if CONSENT_COL in df.columns:
        masks["consent_fail"] = anchor_match(df[CONSENT_COL], CONSENT_OK_ANCHOR)
    if AGE_COL in df.columns:
        masks["screener_age_fail"] = anchor_match(df[AGE_COL], AGE_OK_ANCHOR)
    if OMNI_COL in df.columns:
        masks["screener_omni_fail"] = anchor_match(df[OMNI_COL], OMNI_OK_ANCHOR)

    if ATT1_COL in df.columns and ATT2_COL in df.columns:
        att1_ok = pd.to_numeric(df[ATT1_COL], errors="coerce") == ATT1_CORRECT
        att2_ok = pd.to_numeric(df[ATT2_COL], errors="coerce") == ATT2_CORRECT
        masks["attention_check_fail"] = att1_ok & att2_ok

    # CC1/CC2: correct answer is conditional on the assigned cell (Master
    # Codebook SS4.4) -- CC1 depends on AIP_COND, CC2 depends on DISC_COND.
    if (CC1_COL in df.columns and CC2_COL in df.columns
            and AIP_COND_COL in df.columns and DISC_COL in df.columns):
        aip = pd.to_numeric(df[AIP_COND_COL], errors="coerce")
        disc = pd.to_numeric(df[DISC_COL], errors="coerce")
        cc1_val = pd.to_numeric(df[CC1_COL], errors="coerce")
        cc2_val = pd.to_numeric(df[CC2_COL], errors="coerce")
        expect_cc1 = np.where(aip == 1, float(CC1_PERSONALIZED_ANCHOR), float(CC1_PLATFORM_ANCHOR))
        expect_cc2 = np.where(disc == 1, float(CC2_YES_ANCHOR), float(CC2_NO_ANCHOR))
        masks["comprehension_check_fail"] = (cc1_val == expect_cc1) & (cc2_val == expect_cc2)

    if DURATION_COL in df.columns:
        dur = pd.to_numeric(df[DURATION_COL], errors="coerce")
        # Unparseable duration is NOT a drop on this criterion alone -- let
        # the other 8 steps catch a genuinely broken row instead.
        masks["speeder_under_120s"] = (dur >= SPEEDING_MIN_SECONDS) | dur.isna()

    if present_items:
        miss_pct = df[present_items].isna().mean(axis=1)
        # POLICY CHANGE (2026-09-15/16): zero-tolerance missing-item rule,
        # overriding the previous <=10% threshold. See Amendment A-21 (write-up
        # pending -- see CLAUDE.md SS12 governance note).
        masks["excess_missing_items"] = miss_pct <= MISSING_ITEM_TOLERANCE

    if present_items:
        dup_flag = flag_duplicate_response_pattern(df, present_items)
        masks["duplicate_response_pattern"] = ~dup_flag

    if present_items:
        sd = df[present_items].std(axis=1, skipna=True)
        masks["straightlining_near_zero_sd"] = sd >= STRAIGHTLINE_HARD_SD_THRESHOLD

    return masks


def apply_exclusions(df):
    """Lọc bỏ các mẫu không hợp lệ (Hard drops) -- 9 tiêu chí (2026-09-16 policy,
    see HARD_DROP_STEP_ORDER). MC_AIP/MC_DISC vẫn không được dùng để loại cá
    nhân (ITT design, xem policy note ở đầu file) -- xem
    manipulation_check_sensitivity() thay vào đó."""
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
    masks = build_hard_drop_masks(df, present_items)

    for step in HARD_DROP_STEP_ORDER:
        if step in masks:
            drop_step(masks[step], step)

    clean = df.loc[keep].copy()
    log = pd.DataFrame(log_rows)
    if len(log):
        log.loc[len(log)] = {"step": "TOTAL", "n_before": n0,
                              "n_dropped_this_step": n0 - len(clean), "n_after": len(clean)}
    return clean, log, masks


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


def _welch_d(sub_df, mc_col, cond_col):
    """Bare Welch's t-test + Cohen's d for one (mc_col, cond_col) pair on one
    sample -- no printing, no side effects. Shared by
    manipulation_check_sensitivity() across several sample definitions.
    Returns None if either group has fewer than 2 observations."""
    if mc_col not in sub_df.columns or cond_col not in sub_df.columns:
        return None
    cond = pd.to_numeric(sub_df[cond_col], errors="coerce")
    mc = pd.to_numeric(sub_df[mc_col], errors="coerce")
    g0 = mc[cond == 0].dropna()
    g1 = mc[cond == 1].dropna()
    if len(g0) < 2 or len(g1) < 2:
        return None
    res = pg.ttest(g1, g0, correction=True)
    d = pg.compute_effsize(g1, g0, eftype="cohen")
    p_col = "p_val" if "p_val" in res.columns else "p-val"
    return {
        "n_group0": len(g0), "n_group1": len(g1),
        "cohens_d": round(d, 3), "p": round(res[p_col].iloc[0], 4),
        "flag_d_below_0.50": bool(abs(d) < 0.50),
    }


def manipulation_check_sensitivity(df_raw, clean, masks):
    """Manipulation-check ROBUSTNESS reporting across several sample
    definitions (2026-09-16, requested by Khai) -- the mechanism for
    resolving OD-12, NOT a new exclusion gate. Drops nobody; MC_AIP/MC_DISC
    remain non-filters per the ITT design (see policy note at top of file).

    Scenarios:
      1. full_cleaned_sample        -- the final 9-step-cleaned sample (baseline)
      2. excluding_speeder_floor    -- re-adds the respondents the speeder-floor
                                        step (step 6) removed, all other 8 steps
                                        still applied, to show what that one
                                        step changes
      3. phase_pre_LOC / phase_post_LOC -- `clean` split by collection_phase
      4. excluding_extreme_reversers    -- `clean` minus flag_extreme_reverser rows

    `df_raw` is the post-load_and_normalize, pre-exclusion dataframe (needed
    for scenario 2, since rows the speeder floor alone removed aren't in
    `clean`). `masks` is build_hard_drop_masks()'s output on that same
    `df_raw`, reused here (not recomputed) to avoid duplicating the per-step
    logic.
    """
    rows = []

    def add_scenario(scenario_name, sub_df):
        for mc_col, cond_col in ((MC_AIP_COL, AIP_COND_COL), (MC_DISC_COL, DISC_COL)):
            res = _welch_d(sub_df, mc_col, cond_col) if sub_df is not None else None
            row = {"scenario": scenario_name, "mc_column": mc_col, "cond_column": cond_col}
            if res is None:
                row.update({"n_group0": None, "n_group1": None, "cohens_d": None,
                            "p": None, "flag_d_below_0.50": None})
            else:
                row.update(res)
            rows.append(row)

    # 1. Baseline -- full cleaned sample.
    add_scenario("full_cleaned_sample", clean)

    # 2. Excluding the speeder floor -- every OTHER step still applied, on the
    #    ORIGINAL (pre-exclusion) df_raw that `masks` was computed from.
    if "speeder_under_120s" in masks:
        other_steps = [s for s in HARD_DROP_STEP_ORDER if s != "speeder_under_120s" and s in masks]
        keep_without_speeder = pd.Series(True, index=df_raw.index)
        for step in other_steps:
            keep_without_speeder &= masks[step].reindex(df_raw.index).fillna(False)
        add_scenario("excluding_speeder_floor", df_raw.loc[keep_without_speeder])

    # 3. By collection_phase.
    if "collection_phase" in clean.columns:
        for phase_val in sorted(clean["collection_phase"].dropna().unique()):
            add_scenario(f"phase_{phase_val}", clean[clean["collection_phase"] == phase_val])

    # 4. Excluding extreme reversers.
    if "flag_extreme_reverser" in clean.columns:
        add_scenario("excluding_extreme_reversers", clean[~clean["flag_extreme_reverser"]])

    return pd.DataFrame(rows)


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

    # Same split for step 4 (attention_check_fail, 2026-09-16) -- the 665->296
    # run showed this step alone dropping 324 respondents; this breaks that
    # number down into genuine inattention vs. dropout, same reasoning as
    # breakdown_mc_groups() above.
    att_table, _, _ = breakdown_attention_groups(df)
    print("\n[01_clean] ATT1/ATT2 breakdown BEFORE filtering (diagnostic only, not a filter step):")
    print(att_table.to_string(index=False))

    clean, log, hard_drop_masks = apply_exclusions(df)
    clean = recode_cond(clean)
    clean = recode_pnts(clean)
    clean = compute_construct_scores(clean)
    clean = compute_collection_phase(clean)
    # Extreme-reverser flag computed here (moved up from later in this
    # function, 2026-09-16) so manipulation_check_sensitivity()'s
    # "excluding_extreme_reversers" scenario has the column available.
    clean = flag_extreme_reversers(clean)

    # Group-level ITT evidence (report only, n_excluded=0) -- run AFTER filtering,
    # and BEFORE the NOTE below so the note can reflect the actual result rather
    # than a canned line.
    mc_result = report_manipulation_check(clean, MC_AIP_COL, AIP_COND_COL)
    disc_result = report_manipulation_check(clean, MC_DISC_COL, DISC_COL)
    composite_result = report_manipulation_check_composite(clean, AIP_COND_COL)

    # BUGFIX 2026-09-15: this NOTE used to be a fixed string claiming the gate
    # "has not cleared" regardless of what the data actually showed -- it was
    # already stale by the time larger batches started passing. Now built from
    # mc_result/disc_result's own flag_d_below_0.50 (same |d|>=0.50 threshold
    # 04_manipulation_check.py's gate uses), so it always matches this run.
    gate_bits = []
    for label, res in (("MC_AIP", mc_result), ("MC_DISC", disc_result)):
        if res is None:
            gate_bits.append(f"{label}: not computed (insufficient n)")
        else:
            status = "FAIL" if res["flag_d_below_0.50"] else "PASS"
            gate_bits.append(f"{label} {status} (d={res['cohens_d']}, p={res['p']})")
    both_pass = (mc_result is not None and disc_result is not None
                 and not mc_result["flag_d_below_0.50"] and not disc_result["flag_d_below_0.50"])
    if both_pass:
        print(f"\nNOTE: manipulation-check gate CLEARS on this run -- {', '.join(gate_bits)}. "
              f"sample_role is still an administrative label (LOC field added, not a "
              f"measurement-readiness decision by itself) -- but the |d|>=0.50 gate "
              f"04_manipulation_check.py checks is, as of this run, actually met.")
    else:
        print(f"\nNOTE: manipulation-check gate does NOT clear on this run -- {', '.join(gate_bits)}. "
              f"sample_role boundary is administrative (LOC field added), not a "
              f"measurement-readiness boundary -- and per the above, gate readiness "
              f"still needs to be re-confirmed on whatever slice you're about to use.")

    # Manipulation-check sensitivity analysis (2026-09-16, requested by Khai) --
    # additive robustness evidence for OD-12, printed right after the gate
    # NOTE above, not a replacement for it.
    sensitivity_tab = manipulation_check_sensitivity(df, clean, hard_drop_masks)
    print("\n[manipulation_check_sensitivity] Welch's t + Cohen's d across sample definitions "
          "(report only, n_excluded=0 -- OD-12 robustness evidence, not a new gate):")
    print(sensitivity_tab.to_string(index=False) if len(sensitivity_tab) else "(no data)")
    sensitivity_path = f"outputs/tables/{args.phase}_manipulation_check_sensitivity.csv"
    sensitivity_tab.to_csv(sensitivity_path, index=False)

    checkpoint = collection_checkpoint_log(clean)
    print("\n[collection_checkpoint_log] n by sample_role (pilot/main) and collection_phase, "
          "with AIP_COND breakdown:")
    print(checkpoint.to_string(index=False) if len(checkpoint) else "(no data)")
    checkpoint_path = "outputs/tables/collection_checkpoint_log.csv"
    checkpoint.to_csv(checkpoint_path, index=False)

    if mc_result is not None:
        log.loc[len(log)] = {
            "step": f"manipulation_check_group_evidence_MC_AIP (report only, n_excluded=0, "
                    f"d={mc_result['cohens_d']}, p={mc_result['p']})",
            "n_before": len(clean), "n_dropped_this_step": 0, "n_after": len(clean),
        }
    if disc_result is not None:
        # BUGFIX 2026-09-15: MC_DISC was computed and printed but never logged --
        # only MC_AIP and the AIP_mean composite got a log row, so a reader of
        # pilot_exclusion_log.csv alone would see no trace of MC_DISC's d/p.
        log.loc[len(log)] = {
            "step": f"manipulation_check_group_evidence_MC_DISC (report only, n_excluded=0, "
                    f"d={disc_result['cohens_d']}, p={disc_result['p']})",
            "n_before": len(clean), "n_dropped_this_step": 0, "n_after": len(clean),
        }
    if composite_result is not None:
        log.loc[len(log)] = {
            "step": f"manipulation_check_composite_evidence (report only, n_excluded=0, "
                    f"AIP_mean d={composite_result['cohens_d']}, p={composite_result['p']})",
            "n_before": len(clean), "n_dropped_this_step": 0, "n_after": len(clean),
        }

    n_reversers = int(clean["flag_extreme_reverser"].sum())
    print(f"\n[flag_extreme_reversers] flagged (not dropped): {n_reversers} / {len(clean)}")

    clean = strip_pii(clean)

    out_csv = f"data/processed/{args.phase}_clean.csv"
    out_log = f"outputs/tables/{args.phase}_exclusion_log.csv"
    clean.to_csv(out_csv, index=False)
    log.to_csv(out_log, index=False)

    print(f"\n[01_clean] input={args.input} phase={args.phase}")
    print(log.to_string(index=False))
    print(f"[01_clean] wrote {out_csv} (n={len(clean)}), {out_log}, {checkpoint_path}, "
          f"and {sensitivity_path}")


if __name__ == "__main__":
    main()
