#file _qualtrics_io.py
import re
import numpy as np
import pandas as pd

from _config import (
    LIKERT_TEXT_COLS, VIG_TIME_BASE_COLS, CHAN_COL, CHAN_CODES,
    CONSENT_COL, AGE_COL, OMNI_COL, CC1_COL, CC2_COL,
)

_LIKERT_RE = re.compile(r"^\s*(\d+)\s*-")


def is_raw_qualtrics_export(path):
    """Kiểm tra xem có phải file Qualtrics gốc (3 dòng header) không."""
    import csv
    try:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            row2 = next(reader)
            row3 = next(reader)
        row2_joined = " ".join(row2)
        row3_joined = " ".join(row3)
        return "ImportId" in row3_joined
    except:
        return False


def parse_likert_text(series):
    """Chuyển '7 - Strongly Agree' hoặc '7' thành số 7."""
    def _one(v):
        if pd.isna(v) or v == "":
            return np.nan
        v_str = str(v).strip()
        # Trường hợp 1: "7 - Hoàn toàn đồng ý"
        m = _LIKERT_RE.match(v_str)
        if m:
            return int(m.group(1))
        # Trường hợp 2: Đã là số "7" hoặc "7.0"
        try:
            return int(float(v_str))
        except ValueError:
            return np.nan
    return series.map(_one).astype("Int64")


def anchor_match(series, anchor):
    """So khớp an toàn cho cả text và số.

    Chấp nhận các dạng giá trị Qualtrics khác nhau cho cùng một lựa chọn:
      - số thuần: "1"
      - số kèm nhãn: "1 - Đủ 18 tuổi trở lên"
      - đúng bằng nhãn text (fallback nếu anchor không phải số)
    So khớp dựa trên MÃ SỐ dẫn đầu (nếu có) trước, rồi mới fallback so
    khớp toàn chuỗi (để không phá vỡ các anchor dạng text thuần).
    """
    clean_anchor = str(anchor).strip().casefold()
    anchor_num_match = _LIKERT_RE.match(str(anchor).strip()) or re.match(r"^\s*(\d+)\s*$", str(anchor).strip())
    anchor_num = anchor_num_match.group(1) if anchor_num_match else None

    def _match(val):
        if pd.isna(val):
            return False
        raw = str(val).split('\n')[0].split('\r')[0].strip()
        clean_val = raw.casefold()

        # 1) So khớp theo mã số dẫn đầu, ví dụ "1 - Đủ 18 tuổi" -> "1"
        if anchor_num is not None:
            val_num_match = _LIKERT_RE.match(raw) or re.match(r"^\s*(\d+)\s*$", raw)
            if val_num_match and val_num_match.group(1) == anchor_num:
                return True
            # 1b) Giá trị dạng số thực do pandas suy ra kiểu, vd 1.0, 1.00
            try:
                if float(raw) == float(anchor_num):
                    return True
            except ValueError:
                pass

        # 2) Fallback: so khớp toàn chuỗi (áp dụng cho anchor dạng text)
        return clean_val == clean_anchor

    return series.apply(_match)


def _coalesce_duplicate_columns(df, base_name):
    """Gộp các cột bị trùng tên (do Qualtrics chia block) như X, X.1, X.2..."""
    variants = [c for c in df.columns if c == base_name or c.startswith(base_name + ".")]
    if not variants:
        return pd.Series(np.nan, index=df.index)
    out = df[variants[0]].copy()
    for c in variants[1:]:
        out = out.combine_first(df[c])
    return out


def load_and_normalize(path):
    """Hàm chính để đọc và chuẩn hóa dữ liệu."""
    if not is_raw_qualtrics_export(path):
        return pd.read_csv(path)

    # Đọc file, bỏ qua dòng 2 và 3 (text câu hỏi và ImportId)
    df = pd.read_csv(path, header=0, skiprows=[1, 2])

    # 1. Gộp các cột Timing (VIG_TIME_*)
    for base in VIG_TIME_BASE_COLS:
        df[base] = _coalesce_duplicate_columns(df, base)

    # Xoá các cột rác .1, .2...
    drop_cols = [c for c in df.columns if any(c.startswith(b + ".") for b in VIG_TIME_BASE_COLS)]
    df = df.drop(columns=drop_cols)

    # 2. Parse các cột Likert/Check sang số
    for col in LIKERT_TEXT_COLS:
        if col in df.columns:
            df[col] = parse_likert_text(df[col])

    # 3. Giải mã cột CHAN (Đa kênh)
    if CHAN_COL in df.columns:
        chan_series = df[CHAN_COL].fillna("").astype(str)
        for i, code in enumerate(CHAN_CODES):
            choice_num = str(i + 1)
            df[code] = chan_series.apply(lambda x: choice_num in [s.strip() for s in x.split(',')])

    return df