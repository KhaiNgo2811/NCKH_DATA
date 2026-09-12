"""
strip_pii.py - Removes personal-data columns from a raw Qualtrics export BEFORE it is
committed to git, even to a private repo.

Why this exists: the raw export contains IPAddress and precise LocationLatitude /
LocationLongitude for every respondent (confirmed present for all 75 rows in the
2026-08-26 real export) -- both are personal data under Law 91/2025/QH15 Art. 2, the
very statute this project studies. A private GitHub repo reduces exposure but is not
zero-risk (collaborator access changes, accidental visibility toggle, no audit trail).
None of these columns are used anywhere in the analysis pipeline (_config.py does not
reference them), so there is no analytical cost to removing them before commit.

This script does NOT touch the working file used for analysis -- run the pipeline
(01_clean.py etc.) on the original export as usual, from wherever you keep it locally
(outside git, e.g. an untracked data/raw/_local/ folder). Only the de-identified copy
this script produces should ever be committed.

Usage:
    python src/strip_pii.py --input <original_export.csv> --output data/raw/<name>.csv
"""
import argparse
import sys

import pandas as pd

sys.path.insert(0, "src")
from _config import PII_COLUMNS  # noqa: E402 -- single source of truth, shared with 01_clean.py


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Original raw Qualtrics export.")
    ap.add_argument("--output", required=True,
                     help="De-identified copy to commit (e.g. data/raw/pilot_deidentified.csv).")
    args = ap.parse_args()

    # Read the ENTIRE file as plain rows (header=0 only), so the 2nd row (question
    # text) and 3rd row (ImportId JSON) come along as ordinary data rows and get
    # written back out exactly as they were -- this keeps the file recognizable to
    # _qualtrics_io.is_raw_qualtrics_export(), which expects those two rows present.
    df = pd.read_csv(args.input, dtype=str, keep_default_na=False)

    found = [c for c in PII_COLUMNS if c in df.columns]
    if not found:
        print("No PII columns found by name -- file may already be de-identified, or "
              "column names have drifted. Do not assume it's safe without checking "
              "manually before committing.")
    else:
        print(f"Blanking columns: {found}")
        for c in found:
            # Blank every row's VALUE but keep the column (and its question-text /
            # ImportId header rows) so column positions and the raw-export detector
            # are undisturbed.
            df[c] = ""

    df.to_csv(args.output, index=False)
    n_data_rows = max(len(df) - 2, 0)
    print(f"\nWrote de-identified export to {args.output} ({n_data_rows} respondent rows)")
    print("Verify manually before committing -- this only blanks the named columns; "
          "it does not scan free-text fields (e.g. PLAT_5_TEXT) for incidentally "
          "identifying content.")


if __name__ == "__main__":
    main()
