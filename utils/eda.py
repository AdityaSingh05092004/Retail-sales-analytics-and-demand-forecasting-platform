"""
eda.py — Dynamic EDA charts using Plotly.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional, List

PALETTE  = px.colors.qualitative.Bold
SEQ      = px.colors.sequential.Plasma
TEMPLATE = "plotly_dark"


def descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    num = df.select_dtypes(include=np.number)
    if num.empty:
        return pd.DataFrame()
    d = num.describe().T
    d["skewness"]    = num.skew()
    d["kurtosis"]    = num.kurt()
    d["missing"]     = num.isnull().sum()
    d["missing_pct"] = (num.isnull().mean() * 100).round(2)
    return d.round(4)


def correlation_heatmap(df: pd.DataFrame) -> Optional[go.Figure]:
    num = df.select_dtypes(include=np.number)
    if len(num.columns) < 2:
        return None
    corr = num.corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                    title="Correlation Heatmap", aspect="auto")
    fig.update_layout(template=TEMPLATE, height=520)
    return fig


def numeric_distributions(df: pd.DataFrame) -> Optional[go.Figure]:
    cols = df.select_dtypes(include=np.number).columns.tolist()
    if not cols:
        return None
    ncols = min(3, len(cols))
    nrows = -(-len(cols) // ncols)
    fig = make_subplots(rows=nrows, cols=ncols, subplot_titles=cols)
    for i, col in enumerate(cols):
        r, c = divmod(i, ncols)
        fig.add_trace(
            go.Histogram(x=df[col].dropna(), name=col,
                         marker_color=PALETTE[i % len(PALETTE)], showlegend=False),
            row=r + 1, col=c + 1,
        )
    fig.update_layout(template=TEMPLATE, title="Numeric Distributions",
                      height=300 * nrows, showlegend=False)
    return fig


def categorical_bar(df: pd.DataFrame, col: str, top_n: int = 15) -> Optional[go.Figure]:
    vc = df[col].value_counts().head(top_n)
    if len(vc) < 2:
        return None
    fig = px.bar(x=vc.index, y=vc.values,
                 labels={"x": col, "y": "Count"},
                 title=f"Top {top_n} — {col}",
                 color=vc.values, color_continuous_scale=SEQ)
    fig.update_layout(template=TEMPLATE, height=420, showlegend=False,
                      coloraxis_showscale=False)
    return fig


def sales_trend(df: pd.DataFrame, date_col: str, value_col: str,
                freq: str = "ME") -> Optional[go.Figure]:
    try:
        tmp = df[[date_col, value_col]].copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
        tmp = tmp.dropna(subset=[date_col])
        agg = tmp.set_index(date_col).resample(freq)[value_col].sum().reset_index()
        fig = px.line(agg, x=date_col, y=value_col,
                      title=f"Monthly {value_col} Trend",
                      markers=True, color_discrete_sequence=[PALETTE[0]])
        fig.update_layout(template=TEMPLATE, height=420)
        return fig
    except Exception:
        return None


def top_n_bar(df: pd.DataFrame, group_col: str, value_col: str,
              n: int = 10, title: str = "") -> Optional[go.Figure]:
    try:
        grp = df.groupby(group_col)[value_col].sum().nlargest(n).reset_index()
        fig = px.bar(grp, x=value_col, y=group_col, orientation="h",
                     title=title or f"Top {n} {group_col} by {value_col}",
                     color=value_col, color_continuous_scale=SEQ)
        fig.update_layout(template=TEMPLATE, height=420,
                          yaxis={"categoryorder": "total ascending"},
                          coloraxis_showscale=False)
        return fig
    except Exception:
        return None


def pie_chart(df: pd.DataFrame, group_col: str, value_col: str,
              n: int = 8) -> Optional[go.Figure]:
    try:
        grp = df.groupby(group_col)[value_col].sum().nlargest(n).reset_index()
        fig = px.pie(grp, names=group_col, values=value_col,
                     title=f"{value_col} Share by {group_col}",
                     color_discrete_sequence=PALETTE)
        fig.update_layout(template=TEMPLATE, height=440)
        return fig
    except Exception:
        return None


def scatter_plot(df: pd.DataFrame, x_col: str, y_col: str,
                 color_col: Optional[str] = None) -> Optional[go.Figure]:
    try:
        kw = dict(color=color_col, color_discrete_sequence=PALETTE) if color_col else {}
        fig = px.scatter(df, x=x_col, y=y_col,
                         title=f"{x_col}  vs  {y_col}", trendline="ols", **kw)
        fig.update_layout(template=TEMPLATE, height=460)
        return fig
    except Exception:
        return None


def box_plot(df: pd.DataFrame, x_col: str, y_col: str) -> Optional[go.Figure]:
    try:
        top_cats = df[x_col].value_counts().head(12).index
        filt = df[df[x_col].isin(top_cats)]
        fig = px.box(filt, x=x_col, y=y_col,
                     title=f"{y_col} Distribution by {x_col}",
                     color=x_col, color_discrete_sequence=PALETTE)
        fig.update_layout(template=TEMPLATE, height=460, showlegend=False)
        return fig
    except Exception:
        return None


def time_heatmap(df: pd.DataFrame, date_col: str,
                 value_col: str) -> Optional[go.Figure]:
    try:
        tmp = df[[date_col, value_col]].copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
        tmp = tmp.dropna(subset=[date_col])
        tmp["month"]  = tmp[date_col].dt.month_name()
        tmp["dow"]    = tmp[date_col].dt.day_name()
        pivot = tmp.groupby(["dow", "month"])[value_col].sum().unstack(fill_value=0)
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        pivot = pivot.reindex([d for d in day_order if d in pivot.index])
        fig = px.imshow(pivot, color_continuous_scale=SEQ,
                        title=f"{value_col} Intensity (Day × Month)", aspect="auto")
        fig.update_layout(template=TEMPLATE, height=420)
        return fig
    except Exception:
        return None


def area_chart(df: pd.DataFrame, date_col: str, value_col: str,
               group_col: Optional[str] = None) -> Optional[go.Figure]:
    try:
        tmp = df.copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
        tmp = tmp.dropna(subset=[date_col])
        if group_col and group_col in df.columns:
            top_cats = tmp[group_col].value_counts().head(6).index
            tmp = tmp[tmp[group_col].isin(top_cats)]
            agg = tmp.groupby([pd.Grouper(key=date_col, freq="ME"), group_col])[value_col].sum().reset_index()
            fig = px.area(agg, x=date_col, y=value_col, color=group_col,
                          title=f"{value_col} Over Time by {group_col}",
                          color_discrete_sequence=PALETTE)
        else:
            agg = tmp.set_index(date_col).resample("ME")[value_col].sum().reset_index()
            fig = px.area(agg, x=date_col, y=value_col,
                          title=f"{value_col} Area Chart",
                          color_discrete_sequence=[PALETTE[2]])
        fig.update_layout(template=TEMPLATE, height=440)
        return fig
    except Exception:
        return None
