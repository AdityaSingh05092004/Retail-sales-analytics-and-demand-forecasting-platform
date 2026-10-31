"""
data_loader.py — File upload, parsing, and column-type detection.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List


def load_dataframe(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        for enc in ("utf-8", "latin-1", "cp1252"):
            try:
                df = pd.read_csv(uploaded_file, encoding=enc)
                uploaded_file.seek(0)
                return df
            except UnicodeDecodeError:
                uploaded_file.seek(0)
        raise ValueError("Could not decode CSV. Try saving as UTF-8.")
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    raise ValueError("Unsupported format. Upload .csv or .xlsx/.xls")


def get_dataset_info(df: pd.DataFrame) -> Dict[str, Any]:
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().mean() * 100).round(2).to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "memory_kb": round(df.memory_usage(deep=True).sum() / 1024, 2),
    }


def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    col_types = {}
    for col in df.columns:
        cl = col.lower().replace(" ", "_").replace("-", "_")
        dtype = str(df[col].dtype)
        if "datetime" in dtype:
            col_types[col] = "date"
        elif df[col].dtype in [np.float64, np.int64, float, int]:
            if any(k in cl for k in ["sales","revenue","amount","price","profit","cost","income","total","spend"]):
                col_types[col] = "monetary"
            elif any(k in cl for k in ["qty","quantity","units","count","orders","demand"]):
                col_types[col] = "quantity"
            else:
                col_types[col] = "numeric"
        elif pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
            # Date sniff
            sample = df[col].dropna().head(30)
            hits = sum(1 for v in sample if _is_date(str(v)))
            if hits / max(len(sample), 1) > 0.65:
                col_types[col] = "date"
            elif any(k in cl for k in ["region","state","country","city","location","zone","area","territory"]):
                col_types[col] = "region"
            elif any(k in cl for k in ["category","segment","type","class","group","dept","department"]):
                col_types[col] = "category"
            elif any(k in cl for k in ["customer","client","user","buyer","cust","member"]):
                col_types[col] = "customer"
            elif any(k in cl for k in ["product","item","sku","name","description","sub_category"]):
                col_types[col] = "product"
            elif any(k in cl for k in ["order","invoice","transaction","id"]):
                col_types[col] = "order_id"
            else:
                col_types[col] = "categorical"
        else:
            col_types[col] = "other"
    return col_types


def _is_date(val: str) -> bool:
    try:
        pd.to_datetime(val)
        return True
    except Exception:
        return False


def auto_detect_col_map(df: pd.DataFrame) -> Dict[str, str]:
    """Best-guess column mapping for KPI/EDA functions."""
    ct = detect_column_types(df)
    reverse: Dict[str, List[str]] = {}
    for col, t in ct.items():
        reverse.setdefault(t, []).append(col)

    def first(type_key):
        return reverse.get(type_key, [None])[0]

    return {
        "sales_col":     first("monetary"),
        "profit_col":    _find_profit_col(reverse.get("monetary", [])),
        "quantity_col":  first("quantity"),
        "date_col":      first("date"),
        "product_col":   first("product"),
        "category_col":  first("category"),
        "region_col":    first("region"),
        "order_id_col":  first("order_id"),
        "customer_col":  first("customer"),
    }


def _find_profit_col(monetary_cols):
    for c in monetary_cols:
        if "profit" in c.lower():
            return c
    return None
