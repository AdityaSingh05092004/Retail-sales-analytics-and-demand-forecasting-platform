"""
data_cleaner.py — Automated cleaning pipeline.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple


def auto_parse_dates(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    df = df.copy()
    converted = []
    for col in df.select_dtypes(include=["object", "string"]).columns:
        sample = df[col].dropna().head(40)
        hits = sum(1 for v in sample if _is_date(str(v)))
        if hits / max(len(sample), 1) > 0.65:
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().sum() / max(len(df), 1) > 0.5:
                    df[col] = parsed
                    converted.append(col)
            except Exception:
                pass
    return df, converted


def _is_date(val: str) -> bool:
    try:
        pd.to_datetime(val)
        return True
    except Exception:
        return False


def handle_missing_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    df = df.copy()
    report: Dict[str, Any] = {}

    # Drop rows >50% missing
    thresh = int(len(df.columns) * 0.5)
    before = len(df)
    df = df.dropna(thresh=thresh)
    report["rows_dropped_high_missing"] = before - len(df)

    for col in df.columns:
        n_miss = int(df[col].isnull().sum())
        if n_miss == 0:
            continue
        dtype = str(df[col].dtype)
        if "datetime" in dtype:
            df[col] = df[col].ffill().bfill()
            report[col] = f"Date: ffill+bfill ({n_miss} filled)"
        elif df[col].dtype in [np.float64, np.int64, float, int] or "float" in dtype or "int" in dtype:
            med = df[col].median()
            df[col] = df[col].fillna(med)
            report[col] = f"Numeric: median={med:.4f} ({n_miss} filled)"
        else:
            mode_s = df[col].mode()
            fill = mode_s.iloc[0] if len(mode_s) else "Unknown"
            df[col] = df[col].fillna(fill)
            report[col] = f"Categorical: mode='{fill}' ({n_miss} filled)"
    return df, report


def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    before = len(df)
    df = df.drop_duplicates()
    return df, before - len(df)


def detect_and_cap_outliers(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    df = df.copy()
    report: Dict[str, Any] = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            continue
        lo, hi = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        n_out = int(((df[col] < lo) | (df[col] > hi)).sum())
        if n_out:
            df[col] = df[col].clip(lo, hi)
            report[col] = {"outliers_capped": n_out, "lower": round(lo, 4), "upper": round(hi, 4)}
    return df, report


def convert_dtypes(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    df = df.copy()
    report: Dict[str, str] = {}
    for col in df.select_dtypes(include=["object", "string"]).columns:
        num = pd.to_numeric(df[col], errors="coerce")
        if num.notna().sum() / max(len(df), 1) > 0.9:
            df[col] = num
            report[col] = "object → numeric"
    return df, report


def full_clean_pipeline(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    log: Dict[str, Any] = {}
    df, log["date_columns_parsed"] = auto_parse_dates(df)
    df, log["dtype_conversions"] = convert_dtypes(df)
    df, log["duplicates_removed"] = remove_duplicates(df)
    df, log["missing_value_treatment"] = handle_missing_values(df)
    df, log["outlier_capping"] = detect_and_cap_outliers(df)
    return df, log
