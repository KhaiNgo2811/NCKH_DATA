"""
00_generate_synthetic.py
Generates fake respondent-level CSVs already in the CLEAN NUMERIC shape that
_io.load_and_normalize() would produce from a real raw export - i.e. this script
emulates the OUTPUT of the loader, not Qualtrics's raw multi-header format. That
lets every downstream script (01-07) be written and smoke-tested end-to-end before
real data lands, without re-deriving the raw-export quirks (choice-text Likert,
duplicated VIG_TIME columns) twice.

Column names and value scheme confirmed against the real raw export
(1787112675195_PROJ_MAIN_August_18_2026_22_10.csv, checked 2026-08-19):
  - AIP_COND, DISC_COND arrive as NUMERIC 0/1 (not "Low"/"High" strings)
  - CELL (1-4) is a redundant cross-check field
  - CONSENT/SCR_AGE/SCR1/CC1/CC2 are choice text in the raw export, but 01_clean.py's
    anchor_match() only runs on raw exports - for synthetic data we skip straight to
    the ALREADY-DECODED numeric/boolean equivalents 01_clean.py needs downstream, EXCEPT
    Consent/Age18/Omnichannel2ch flags which we bake in as "always pass" (synthetic data
    only exists to prove code paths run, not to test the anchor-matching regex - that is
    tested against the real partial-pilot CSV directly, see CLAUDE.md SS7).

Item counts are the ACTUAL FIELDED counts, not the TF v2.2 Table 5 registered counts.
See CLAUDE.md SS1 for the open TRU/ENG discrepancy.
"""
import argparse
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from _config import CONSTRUCT_ITEMS, CHAN_CODES  # noqa: E402

ALL_ITEMS = [it for items in CONSTRUCT_ITEMS.values() for it in items]
CELL_MAP = {1: (0, 0), 2: (0, 1), 3: (1, 0), 4: (1, 1)}  # cell -> (AIP_COND, DISC_COND)


def _make_construct(n, mean, sd, n_items, corr=0.55, rng=None):
    rng = rng or np.random.default_rng()
    latent = rng.normal(0, 1, size=n)
    items = np.zeros((n, n_items))
    for j in range(n_items):
        noise = rng.normal(0, np.sqrt(1 - corr), size=n)
        raw = mean + sd * (np.sqrt(corr) * latent + noise)
        items[:, j] = np.clip(np.round(raw), 1, 7)
    return items, latent


def generate(n, seed, unbalanced_cells=False, inject_quality_issues=True):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(index=range(n))

    probs = [0.35, 0.35, 0.20, 0.10] if (unbalanced_cells and n >= 20) else [0.25] * 4
    cell = rng.choice([1, 2, 3, 4], size=n, p=probs)
    df["CELL"] = cell
    df["AIP_COND"] = [CELL_MAP[c][0] for c in cell]
    df["DISC_COND"] = [CELL_MAP[c][1] for c in cell]
    aip_high = df["AIP_COND"].values
    disc = df["DISC_COND"].values

    # --- Screener / consent (real Vietnamese diacritics, so anchor_match() in
    #     01_clean.py is genuinely smoke-tested here too, not bypassed) ---
    df["CONSENT"] = "Tôi đồng ý tham gia\nI agree to participate"
    df["SCR_AGE"] = "Có, tôi đã từ 18 tuổi trở lên\nYes, I am 18 or older"
    df["SCR_OMNI"] = "Có\nYes"  # real column name confirmed 2026-09-10; was SCR1 in an older draft

    # --- Comprehension check, numeric-coded directly (1/2/3) ---
    cc1_correct = np.where(aip_high == 1, 2, 1)
    cc2_correct = np.where(disc == 1, 1, 2)
    miss_rate = 0.10
    df["CC1"] = np.where(rng.random(n) < miss_rate, 3, cc1_correct)
    df["CC2"] = np.where(rng.random(n) < miss_rate, 3, cc2_correct)

    # --- Latent structural simulation (mild, just for pipeline smoke-testing) ---
    aip_items, aip_lat = _make_construct(n, mean=4.0 + 0.8 * aip_high, sd=1.3,
                                          n_items=len(CONSTRUCT_ITEMS["AIP"]), rng=rng)
    rel_items, rel_lat = _make_construct(n, mean=4.0 + 0.5 * aip_lat, sd=1.2,
                                          n_items=len(CONSTRUCT_ITEMS["REL"]), rng=rng)
    int_mean = 4.0 + 0.5 * aip_lat - 0.6 * disc
    int_items, int_lat = _make_construct(n, mean=int_mean, sd=1.2,
                                          n_items=len(CONSTRUCT_ITEMS["INT"]), rng=rng)
    tru_mean = 4.2 + 0.45 * rel_lat - 0.5 * int_lat
    tru_items, tru_lat = _make_construct(n, mean=tru_mean, sd=1.1,
                                          n_items=len(CONSTRUCT_ITEMS["TRU"]), rng=rng)
    eng_mean = 4.0 + 0.4 * rel_lat - 0.35 * int_lat + 0.3 * tru_lat
    eng_items, eng_lat = _make_construct(n, mean=eng_mean, sd=1.2,
                                          n_items=len(CONSTRUCT_ITEMS["ENG"]), rng=rng)
    pi_mean = 4.0 - 0.3 * int_lat + 0.4 * eng_lat
    pi_items, _ = _make_construct(n, mean=pi_mean, sd=1.2,
                                   n_items=len(CONSTRUCT_ITEMS["PI"]), rng=rng)
    pdpl_items, _ = _make_construct(n, mean=4.0, sd=1.4,
                                     n_items=len(CONSTRUCT_ITEMS["PDPL"]), rng=rng)

    for name, arr in [("AIP", aip_items), ("REL", rel_items), ("INT", int_items),
                       ("TRU", tru_items), ("ENG", eng_items), ("PI", pi_items),
                       ("PDPL", pdpl_items)]:
        for j, col in enumerate(CONSTRUCT_ITEMS[name]):
            df[col] = arr[:, j].astype(int)

    # --- Attention checks ---
    df["ATT1"] = 5
    df["ATT2"] = 2
    if inject_quality_issues and n >= 20:
        fail_idx = rng.choice(n, size=max(1, int(0.06 * n)), replace=False)
        df.loc[fail_idx, "ATT1"] = rng.integers(1, 7, size=len(fail_idx))

    # --- Manipulation checks (real fielded names: MC_AIP, MC_DISC) ---
    df["MC_AIP"] = np.clip(np.round(4.0 + 1.1 * aip_lat + rng.normal(0, 1, n)), 1, 7).astype(int)
    df["MC_DISC"] = np.clip(np.round(4.0 + 1.3 * disc + rng.normal(0, 1, n)), 1, 7).astype(int)

    # --- Timing (already coalesced, mirrors post-_io.py shape) ---
    df["VIG_TIME_First Click"] = rng.exponential(2.5, n).round(1)
    df["VIG_TIME_Last Click"] = df["VIG_TIME_First Click"] + rng.exponential(3, n).round(1)
    df["VIG_TIME_Page Submit"] = df["VIG_TIME_Last Click"] + rng.exponential(1, n).round(1)
    df["VIG_TIME_Click Count"] = rng.integers(1, 8, n)
    df["Duration (in seconds)"] = rng.normal(480, 120, n).clip(60).round().astype(int)
    if inject_quality_issues and n >= 20:
        speeders = rng.choice(n, size=max(1, int(0.05 * n)), replace=False)
        df.loc[speeders, "Duration (in seconds)"] = rng.integers(30, 90, len(speeders))

    # --- Demographics (real Qualtrics variable names) ---
    df["AGE_BAND"] = rng.choice(["18 - 24", "25 - 34", "35 - 44", "45 - 54", "55 tro len"],
                                 n, p=[0.35, 0.30, 0.18, 0.12, 0.05])
    df["GEN"] = rng.choice(["Nam", "Nu", "Khac"], n, p=[0.45, 0.50, 0.05])
    df["EDU"] = rng.choice(["THPT tro xuong", "Trung cap - Cao dang",
                             "Dai hoc", "Sau dai hoc"], n, p=[0.10, 0.20, 0.55, 0.15])
    df["INC"] = rng.choice(["Duoi 5 trieu", "5 - 10 trieu", "Tren 10 - 20 trieu",
                             "Tren 20 - 40 trieu", "Tren 40 trieu"], n)
    df["FREQ"] = rng.choice(["Vai lan moi nam", "Khoang moi thang",
                              "Khoang moi tuan", "Nhieu lan moi tuan"], n)
    df["PLAT"] = rng.choice(["Shopee", "Lazada", "TikTok Shop", "Tiki"], n,
                             p=[0.5, 0.2, 0.25, 0.05])
    df["PRIOR"] = rng.choice(["Duoi 6 thang", "Tu 6 den 12 thang",
                               "Tu 1 den 3 nam", "Tren 3 nam"], n)
    chan_combos = ["CHAN_APP", "CHAN_APP,CHAN_WEB", "CHAN_APP,CHAN_LIVE",
                   "CHAN_WEB,CHAN_STORE", "CHAN_APP,CHAN_WEB,CHAN_LIVE,CHAN_SOC"]
    df["CHAN"] = rng.choice(chan_combos, n)
    for code in CHAN_CODES:
        df[code] = df["CHAN"].str.contains(code)  # code already e.g. "CHAN_APP"

    # --- Missingness injection ---
    if inject_quality_issues and n >= 20:
        for col in rng.choice(ALL_ITEMS, size=3, replace=False):
            miss_idx = rng.choice(n, size=max(1, int(0.04 * n)), replace=False)
            df.loc[miss_idx, col] = np.nan

    df.insert(0, "ResponseId", [f"R_{seed}_{i:04d}" for i in range(n)])
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="data/raw")
    args = ap.parse_args()

    pilot = generate(n=30, seed=1, unbalanced_cells=True, inject_quality_issues=True)
    main = generate(n=420, seed=2, unbalanced_cells=False, inject_quality_issues=True)

    pilot.to_csv(f"{args.out_dir}/pilot_n30_synthetic.csv", index=False)
    main.to_csv(f"{args.out_dir}/main_n400_synthetic.csv", index=False)
    print(f"Wrote {args.out_dir}/pilot_n30_synthetic.csv  (n={len(pilot)})")
    print(f"Wrote {args.out_dir}/main_n400_synthetic.csv  (n={len(main)})")
