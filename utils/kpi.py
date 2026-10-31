"""
kpi.py — Dynamic KPI computation and business insight generation.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def compute_kpis(df: pd.DataFrame, col_map: Dict[str, Optional[str]]) -> Dict[str, Any]:
    k: Dict[str, Any] = {}
    sc  = col_map.get("sales_col")
    pc  = col_map.get("profit_col")
    qc  = col_map.get("quantity_col")
    dc  = col_map.get("date_col")
    prc = col_map.get("product_col")
    cc  = col_map.get("category_col")
    rc  = col_map.get("region_col")
    oc  = col_map.get("order_id_col")

    def col(c): return c if c and c in df.columns else None

    if col(sc):
        k["total_revenue"]   = round(float(df[sc].sum()), 2)
        k["avg_order_value"] = round(float(df[sc].mean()), 2)
        k["max_sale"]        = round(float(df[sc].max()), 2)
    else:
        k["total_revenue"] = k["avg_order_value"] = None

    if col(pc):
        k["total_profit"] = round(float(df[pc].sum()), 2)
        if k.get("total_revenue"):
            k["profit_margin_pct"] = round(k["total_profit"] / k["total_revenue"] * 100, 2)
        else:
            k["profit_margin_pct"] = None
    else:
        k["total_profit"] = k["profit_margin_pct"] = None

    k["total_orders"]    = int(df[oc].nunique()) if col(oc) else len(df)
    k["total_units_sold"]= int(df[qc].sum())     if col(qc) else None

    if col(prc) and col(sc):
        k["best_product"]  = df.groupby(prc)[sc].sum().idxmax()
    else:
        k["best_product"]  = None

    if col(cc) and col(sc):
        k["best_category"] = df.groupby(cc)[sc].sum().idxmax()
    else:
        k["best_category"] = None

    if col(rc) and col(sc):
        k["best_region"]   = df.groupby(rc)[sc].sum().idxmax()
    else:
        k["best_region"]   = None

    if col(dc):
        dates = pd.to_datetime(df[dc], errors="coerce").dropna()
        if len(dates):
            k["date_range_start"] = str(dates.min().date())
            k["date_range_end"]   = str(dates.max().date())
        else:
            k["date_range_start"] = k["date_range_end"] = None
    else:
        k["date_range_start"] = k["date_range_end"] = None

    return k


def generate_insights(df: pd.DataFrame,
                       col_map: Dict[str, Optional[str]],
                       kpis: Dict[str, Any]) -> list:
    ins = []
    sc = col_map.get("sales_col")
    pc = col_map.get("profit_col")
    cc = col_map.get("category_col")
    dc = col_map.get("date_col")

    if kpis.get("total_revenue"):
        ins.append(f"💰 **Total Revenue:** ${kpis['total_revenue']:,.2f} across {kpis['total_orders']:,} orders.")

    if kpis.get("profit_margin_pct") is not None:
        m = kpis["profit_margin_pct"]
        tag = "✅ healthy margin" if m > 15 else "⚠️ below 15% — consider cost optimisation"
        ins.append(f"📊 **Profit Margin:** {m:.1f}% — {tag}.")

    for kpi, label in [("best_product","🏆 Best Product"),
                        ("best_category","📦 Top Category"),
                        ("best_region","🌍 Top Region")]:
        if kpis.get(kpi):
            ins.append(f"{label}: **{kpis[kpi]}**")

    if kpis.get("avg_order_value"):
        ins.append(f"🛒 **Avg Order Value:** ${kpis['avg_order_value']:,.2f}")

    # Concentration warning
    if cc and sc and cc in df.columns and sc in df.columns:
        shares = df.groupby(cc)[sc].sum()
        top_pct = shares.max() / shares.sum() * 100
        if top_pct > 50:
            ins.append(f"⚠️ Revenue is concentrated — top category holds **{top_pct:.1f}%**. Consider diversification.")

    # MoM growth
    if dc and sc and dc in df.columns and sc in df.columns:
        try:
            tmp = df[[dc, sc]].copy()
            tmp[dc] = pd.to_datetime(tmp[dc], errors="coerce")
            monthly = tmp.dropna(subset=[dc]).set_index(dc).resample("ME")[sc].sum()
            if len(monthly) >= 2:
                growth = (monthly.iloc[-1] - monthly.iloc[-2]) / max(monthly.iloc[-2], 1) * 100
                arrow = "📈" if growth > 0 else "📉"
                ins.append(f"{arrow} **Month-over-Month Growth:** {growth:+.1f}% in the latest period.")
        except Exception:
            pass

    if not ins:
        ins.append("ℹ️ Map sales, profit, category, region columns for richer insights.")
    return ins
