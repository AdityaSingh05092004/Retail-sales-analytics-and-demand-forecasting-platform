"""
app.py — Retail Sales Analytics & Demand Forecasting Platform
Run: streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ── utils ──────────────────────────────────────────────────────────────────────
from utils.data_loader       import load_dataframe, get_dataset_info, detect_column_types, auto_detect_col_map
from utils.data_cleaner      import full_clean_pipeline
from utils.eda               import (descriptive_stats, correlation_heatmap, numeric_distributions,
                                     categorical_bar, sales_trend, top_n_bar, pie_chart,
                                     scatter_plot, box_plot, time_heatmap, area_chart)
from utils.kpi               import compute_kpis, generate_insights
from utils.sql_engine        import build_sql_reports, SQL_SCRIPTS
from utils.ml_models         import run_forecasting_pipeline
from utils.report_generator  import generate_csv_summary, generate_excel_report, generate_pdf_report

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Retail Analytics Platform",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: #f1f5f9;
}
section[data-testid="stSidebar"] * { color: #f1f5f9 !important; }

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    margin: 6px 0;
    box-shadow: 0 4px 16px rgba(0,0,0,.3);
}
.kpi-label { font-size: .78rem; color: #94a3b8; text-transform: uppercase; letter-spacing: .06em; }
.kpi-value { font-size: 1.9rem; font-weight: 700; color: #38bdf8; margin: 6px 0 0; line-height:1; }
.kpi-sub   { font-size: .72rem; color: #64748b; margin-top: 4px; }

/* Section headers */
.section-hdr {
    font-size: 1.1rem; font-weight: 700; color: #38bdf8;
    border-left: 4px solid #38bdf8; padding-left: 10px;
    margin: 28px 0 14px;
}

/* Insight cards */
.insight {
    background: #1e293b; border-left: 3px solid #38bdf8;
    border-radius: 8px; padding: 10px 16px; margin: 6px 0;
    font-size: .9rem; color: #e2e8f0;
}

/* Top banner */
.banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    border: 1px solid #334155; border-radius: 14px;
    padding: 32px 40px; margin-bottom: 28px;
    text-align: center;
}
.banner h1 { font-size: 2rem; color: #38bdf8; margin: 0; font-weight: 700; }
.banner p  { color: #94a3b8; margin: 8px 0 0; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def kpi_card(label, value, sub=""):
    val_html = f"{value}" if value is not None else "N/A"
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{val_html}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""


def fmt_currency(v):
    if v is None: return "N/A"
    if abs(v) >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000:     return f"${v/1_000:.1f}K"
    return f"${v:,.2f}"


def show_fig(fig, key=None):
    if fig: st.plotly_chart(fig, use_container_width=True, key=key)
    else:   st.info("Not enough data / columns to generate this chart.")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🛍️ Retail Analytics")
    st.markdown("---")
    st.markdown("### 📁 Upload Dataset")
    uploaded = st.file_uploader("CSV or Excel file", type=["csv","xlsx","xls"],
                                 label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    sections = ["🏠 Overview","🔍 Data Preview","🧹 Data Cleaning",
                "📊 EDA","📈 KPI Dashboard","🗄️ SQL Analytics",
                "🤖 ML Forecasting","📥 Download Reports"]
    active = st.radio("Go to:", sections, label_visibility="collapsed")
    st.markdown("---")
    st.caption("Built with Streamlit · scikit-learn · Plotly")
    st.caption(f"© {datetime.now().year} Retail Analytics Platform")


# ══════════════════════════════════════════════════════════════════════════════
# LANDING — no file uploaded
# ══════════════════════════════════════════════════════════════════════════════
if uploaded is None:
    st.markdown("""
    <div class="banner">
        <h1>🛍️ Retail Sales Analytics & Demand Forecasting Platform</h1>
        <p>Upload your retail CSV or Excel dataset to unlock full analytics, KPIs, ML forecasting, and reports.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 📊 Automated EDA")
        st.write("Correlation heatmaps, distributions, trends, and category breakdowns — generated instantly.")
    with col2:
        st.markdown("#### 📈 KPI Dashboard")
        st.write("Revenue, profit, best product, best region, and MoM growth — all computed automatically.")
    with col3:
        st.markdown("#### 🤖 ML Forecasting")
        st.write("Linear Regression & Random Forest models with MAE, RMSE, and R² comparison.")

    st.markdown("---")
    st.info("👈 Upload your dataset from the sidebar to begin.")

    st.markdown("#### 💡 Supported Dataset Formats")
    st.markdown("""
    Your CSV/Excel can have **any** column names. The platform auto-detects:
    - **Date columns** — for trend analysis  
    - **Monetary columns** (sales, revenue, profit…) — for KPIs  
    - **Categorical columns** (category, region, product…) — for grouping  
    - **Numeric columns** — for ML features  
    
    Popular demo datasets: **Kaggle Superstore**, **Online Retail II**, **Walmart Sales**.
    """)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# LOAD & CACHE DATA
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Loading and cleaning dataset…")
def load_and_clean(file_bytes, file_name):
    import io
    fake = io.BytesIO(file_bytes)
    fake.name = file_name
    df_raw = load_dataframe(fake)
    df_clean, log = full_clean_pipeline(df_raw)
    return df_raw, df_clean, log


file_bytes = uploaded.read()
df_raw, df, cleaning_log = load_and_clean(file_bytes, uploaded.name)

# Auto-detect column mapping
col_map = auto_detect_col_map(df)
col_types = detect_column_types(df)
info_raw  = get_dataset_info(df_raw)
info_clean= get_dataset_info(df)

# Allow user overrides in sidebar
with st.sidebar:
    st.markdown("### 🗺️ Column Mapping")
    st.caption("Override auto-detected columns")
    all_cols   = [None] + list(df.columns)
    num_cols   = [None] + df.select_dtypes(include=np.number).columns.tolist()
    date_cols  = [None] + [c for c,t in col_types.items() if t=="date"]

    col_map["sales_col"]    = st.selectbox("💰 Sales/Revenue",    all_cols, index=all_cols.index(col_map["sales_col"])    if col_map["sales_col"]    in all_cols else 0)
    col_map["profit_col"]   = st.selectbox("📊 Profit",           all_cols, index=all_cols.index(col_map["profit_col"])   if col_map["profit_col"]   in all_cols else 0)
    col_map["quantity_col"] = st.selectbox("📦 Quantity",         all_cols, index=all_cols.index(col_map["quantity_col"]) if col_map["quantity_col"] in all_cols else 0)
    col_map["date_col"]     = st.selectbox("📅 Date",             all_cols, index=all_cols.index(col_map["date_col"])     if col_map["date_col"]     in all_cols else 0)
    col_map["product_col"]  = st.selectbox("🏷️ Product",         all_cols, index=all_cols.index(col_map["product_col"])  if col_map["product_col"]  in all_cols else 0)
    col_map["category_col"] = st.selectbox("🗂️ Category",        all_cols, index=all_cols.index(col_map["category_col"]) if col_map["category_col"] in all_cols else 0)
    col_map["region_col"]   = st.selectbox("🌍 Region",           all_cols, index=all_cols.index(col_map["region_col"])   if col_map["region_col"]   in all_cols else 0)
    col_map["order_id_col"] = st.selectbox("🔢 Order ID",         all_cols, index=all_cols.index(col_map["order_id_col"]) if col_map["order_id_col"] in all_cols else 0)

# Compute KPIs + insights
kpis     = compute_kpis(df, col_map)
insights = generate_insights(df, col_map, kpis)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION ROUTER
# ══════════════════════════════════════════════════════════════════════════════

# ── 🏠 Overview ───────────────────────────────────────────────────────────────
if active == "🏠 Overview":
    st.markdown("""
    <div class="banner">
        <h1>🛍️ Retail Analytics Platform</h1>
        <p>Your dataset is loaded and ready for analysis.</p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Total Rows",    f"{info_raw['rows']:,}","raw"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Columns",        f"{info_raw['columns']}",""), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Duplicates",     f"{info_raw['duplicates']:,}","detected"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Memory",         f"{info_raw['memory_kb']:.0f} KB","raw"), unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">📝 Business Insights</div>', unsafe_allow_html=True)
    for ins in insights:
        st.markdown(f'<div class="insight">{ins}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">🗂️ Column Types Detected</div>', unsafe_allow_html=True)
    ct_df = pd.DataFrame({"Column": list(col_types.keys()),
                           "Detected Type": list(col_types.values()),
                           "Pandas Dtype": df.dtypes.astype(str).values})
    st.dataframe(ct_df, use_container_width=True, hide_index=True)


# ── 🔍 Data Preview ────────────────────────────────────────────────────────────
elif active == "🔍 Data Preview":
    st.markdown('<div class="section-hdr">🔍 Dataset Preview</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Data Table", "ℹ️ Info", "📊 Raw Stats"])

    with tab1:
        n = st.slider("Rows to preview", 10, min(500, len(df)), 50)
        st.dataframe(df.head(n), use_container_width=True)

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Dataset Dimensions**")
            st.write(f"- Rows (cleaned): **{info_clean['rows']:,}**")
            st.write(f"- Columns: **{info_clean['columns']}**")
            st.write(f"- Memory: **{info_clean['memory_kb']:.1f} KB**")
        with col_b:
            st.markdown("**Missing Values**")
            miss_df = pd.DataFrame({
                "Column":   df.columns,
                "Missing":  df.isnull().sum().values,
                "Missing%": (df.isnull().mean()*100).round(2).values,
                "Dtype":    df.dtypes.astype(str).values,
            })
            st.dataframe(miss_df[miss_df["Missing"]>0] if miss_df["Missing"].sum() > 0 else miss_df,
                         use_container_width=True, hide_index=True)

    with tab3:
        st.dataframe(df.describe(include="all").T, use_container_width=True)


# ── 🧹 Data Cleaning ───────────────────────────────────────────────────────────
elif active == "🧹 Data Cleaning":
    st.markdown('<div class="section-hdr">🧹 Automated Data Cleaning Report</div>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Rows Before", f"{info_raw['rows']:,}")
    with c2: st.metric("Rows After",  f"{info_clean['rows']:,}",
                       delta=f"-{info_raw['rows']-info_clean['rows']}")
    with c3: st.metric("Duplicates Removed", f"{cleaning_log.get('duplicates_removed',0):,}")

    tab1,tab2,tab3,tab4 = st.tabs(["📅 Date Parsing","🔢 Type Conversions","🩹 Missing Values","📉 Outliers"])

    with tab1:
        dp = cleaning_log.get("date_columns_parsed",[])
        if dp:
            st.success(f"✅ Parsed {len(dp)} date column(s): **{', '.join(dp)}**")
        else:
            st.info("No date columns detected or parsed.")

    with tab2:
        dc = cleaning_log.get("dtype_conversions",{})
        if dc:
            st.dataframe(pd.DataFrame(dc.items(),columns=["Column","Conversion"]),
                         hide_index=True, use_container_width=True)
        else:
            st.info("No dtype conversions needed.")

    with tab3:
        mv = cleaning_log.get("missing_value_treatment",{})
        rows_drop = mv.pop("rows_dropped_high_missing", 0)
        st.write(f"Rows dropped (>50% missing): **{rows_drop}**")
        if mv:
            st.dataframe(pd.DataFrame(mv.items(),columns=["Column","Action"]),
                         hide_index=True, use_container_width=True)
        else:
            st.info("No missing values treated.")

    with tab4:
        oc = cleaning_log.get("outlier_capping",{})
        if oc:
            oc_rows = [{"Column":col,"Capped":v["outliers_capped"],"Lower":v["lower"],"Upper":v["upper"]}
                       for col,v in oc.items()]
            st.dataframe(pd.DataFrame(oc_rows), hide_index=True, use_container_width=True)
        else:
            st.info("No outliers detected via IQR method.")


# ── 📊 EDA ─────────────────────────────────────────────────────────────────────
elif active == "📊 EDA":
    st.markdown('<div class="section-hdr">📊 Exploratory Data Analysis</div>', unsafe_allow_html=True)

    tabs = st.tabs(["📈 Distributions","🔥 Correlation","📅 Trends","🏷️ Categories",
                    "📦 Products","🌍 Regions","🕐 Time Heatmap","🔍 Custom Scatter"])

    # Distributions
    with tabs[0]:
        st.subheader("Numeric Distributions")
        show_fig(numeric_distributions(df), "num_dist")
        st.subheader("Descriptive Statistics")
        st.dataframe(descriptive_stats(df), use_container_width=True)

    # Correlation
    with tabs[1]:
        show_fig(correlation_heatmap(df), "corr")

    # Trends
    with tabs[2]:
        dc = col_map.get("date_col")
        sc = col_map.get("sales_col")
        pc = col_map.get("profit_col")
        if dc and sc:
            col_a, col_b = st.columns(2)
            with col_a:
                show_fig(sales_trend(df, dc, sc), "trend_sales")
            with col_b:
                if pc:
                    show_fig(sales_trend(df, dc, pc), "trend_profit")
            show_fig(area_chart(df, dc, sc, col_map.get("category_col")), "area")
            show_fig(time_heatmap(df, dc, sc), "heatmap")
        else:
            st.warning("Set Date and Sales columns in the sidebar to generate trend charts.")

    # Categories
    with tabs[3]:
        cc = col_map.get("category_col")
        sc = col_map.get("sales_col")
        if cc and sc:
            col_a, col_b = st.columns(2)
            with col_a: show_fig(top_n_bar(df, cc, sc, title=f"Revenue by {cc}"), "cat_bar")
            with col_b: show_fig(pie_chart(df, cc, sc), "cat_pie")
            if col_map.get("profit_col"):
                show_fig(box_plot(df, cc, col_map["profit_col"]), "cat_box")
        else:
            st.warning("Set Category and Sales columns in the sidebar.")
        # Also show bar for any categorical
        st.markdown("#### All Categorical Columns")
        cat_cols = [c for c,t in col_types.items() if t in ("category","categorical","region","product")]
        chosen = st.selectbox("Pick column", cat_cols) if cat_cols else None
        if chosen:
            show_fig(categorical_bar(df, chosen), "cat_chosen")

    # Products
    with tabs[4]:
        prc = col_map.get("product_col")
        sc  = col_map.get("sales_col")
        if prc and sc:
            col_a, col_b = st.columns(2)
            with col_a: show_fig(top_n_bar(df, prc, sc, n=12, title="Top 12 Products by Revenue"), "prod_bar")
            with col_b: show_fig(pie_chart(df, prc, sc, n=8), "prod_pie")
        else:
            st.warning("Set Product and Sales columns in the sidebar.")

    # Regions
    with tabs[5]:
        rc = col_map.get("region_col")
        sc = col_map.get("sales_col")
        if rc and sc:
            col_a, col_b = st.columns(2)
            with col_a: show_fig(top_n_bar(df, rc, sc, title=f"Revenue by {rc}"), "reg_bar")
            with col_b: show_fig(pie_chart(df, rc, sc), "reg_pie")
            if col_map.get("profit_col"):
                show_fig(box_plot(df, rc, col_map["profit_col"]), "reg_box")
        else:
            st.warning("Set Region and Sales columns in the sidebar.")

    # Time Heatmap
    with tabs[6]:
        dc = col_map.get("date_col")
        sc = col_map.get("sales_col")
        if dc and sc:
            show_fig(time_heatmap(df, dc, sc), "time_heat")
        else:
            st.warning("Set Date and Sales columns.")

    # Custom Scatter
    with tabs[7]:
        num_cols_list = df.select_dtypes(include=np.number).columns.tolist()
        cat_cols_list = [c for c,t in col_types.items() if t in ("category","categorical","region")] or [None]
        if len(num_cols_list) >= 2:
            c1,c2,c3 = st.columns(3)
            x_c = c1.selectbox("X axis", num_cols_list, key="sc_x")
            y_c = c2.selectbox("Y axis", num_cols_list, index=min(1,len(num_cols_list)-1), key="sc_y")
            col_c = c3.selectbox("Color by (optional)", [None]+cat_cols_list, key="sc_col")
            show_fig(scatter_plot(df, x_c, y_c, col_c), "custom_scatter")
        else:
            st.info("Need at least 2 numeric columns for scatter plot.")


# ── 📈 KPI Dashboard ───────────────────────────────────────────────────────────
elif active == "📈 KPI Dashboard":
    st.markdown('<div class="section-hdr">📈 KPI Dashboard</div>', unsafe_allow_html=True)

    # Row 1
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Total Revenue",    fmt_currency(kpis.get("total_revenue")),
                                   f"Max order: {fmt_currency(kpis.get('max_sale'))}"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Total Profit",     fmt_currency(kpis.get("total_profit")),
                                   f"Margin: {kpis.get('profit_margin_pct','N/A')}%"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Total Orders",     f"{kpis.get('total_orders','N/A'):,}" if kpis.get('total_orders') else "N/A",
                                   "unique transactions"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Avg Order Value",  fmt_currency(kpis.get("avg_order_value")),
                                   "per order"), unsafe_allow_html=True)

    st.markdown("")
    # Row 2
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi_card("🏆 Best Product",  str(kpis.get("best_product") or "N/A")[:30], "top by revenue"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("📦 Best Category", str(kpis.get("best_category") or "N/A")[:30],"top by revenue"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("🌍 Best Region",   str(kpis.get("best_region") or "N/A")[:30],  "top by revenue"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("📅 Date Range",
                                   f"{kpis.get('date_range_start','?')}",
                                   f"to {kpis.get('date_range_end','?')}"), unsafe_allow_html=True)

    if kpis.get("total_units_sold"):
        st.markdown("")
        c1,_,_,_ = st.columns(4)
        with c1: st.markdown(kpi_card("📦 Units Sold", f"{kpis['total_units_sold']:,}","total quantity"), unsafe_allow_html=True)

    # Insight cards
    st.markdown('<div class="section-hdr">💡 Auto-Generated Insights</div>', unsafe_allow_html=True)
    for ins in insights:
        st.markdown(f'<div class="insight">{ins}</div>', unsafe_allow_html=True)

    # Mini charts row
    st.markdown('<div class="section-hdr">📊 Supporting Charts</div>', unsafe_allow_html=True)
    sc = col_map.get("sales_col")
    cc = col_map.get("category_col")
    rc = col_map.get("region_col")
    dc = col_map.get("date_col")
    col_a, col_b = st.columns(2)
    with col_a:
        if cc and sc: show_fig(pie_chart(df, cc, sc), "kpi_cat_pie")
    with col_b:
        if rc and sc: show_fig(pie_chart(df, rc, sc), "kpi_reg_pie")
    if dc and sc:
        show_fig(sales_trend(df, dc, sc), "kpi_trend")


# ── 🗄️ SQL Analytics ─────────────────────────────────────────────────────────
elif active == "🗄️ SQL Analytics":
    st.markdown('<div class="section-hdr">🗄️ SQL Analytics</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊 Pre-built Reports","✍️ Custom SQL"])

    with tab1:
        with st.spinner("Running SQL queries…"):
            sql_reports = build_sql_reports(df, col_map)

        if not sql_reports:
            st.warning("No SQL reports generated. Map at least Sales + one grouping column.")
        else:
            for report_name, rdf in sql_reports.items():
                st.markdown(f"**{report_name}**")
                st.dataframe(rdf, use_container_width=True, hide_index=True)
                st.markdown("")

    with tab2:
        st.info("The dataset is stored as table **`sales_data`** in SQLite.")
        st.code(SQL_SCRIPTS, language="sql")
        user_sql = st.text_area("Write your own SQL:", height=120,
                                 placeholder="SELECT * FROM sales_data LIMIT 10")
        if st.button("▶️ Run Query") and user_sql.strip():
            try:
                from utils.sql_engine import run_query
                result = run_query(user_sql)
                st.dataframe(result, use_container_width=True)
            except Exception as e:
                st.error(f"SQL Error: {e}")


# ── 🤖 ML Forecasting ─────────────────────────────────────────────────────────
elif active == "🤖 ML Forecasting":
    st.markdown('<div class="section-hdr">🤖 Machine Learning Forecasting</div>', unsafe_allow_html=True)

    num_cols_for_target = df.select_dtypes(include=np.number).columns.tolist()
    if not num_cols_for_target:
        st.error("No numeric columns found for ML. Check your dataset.")
        st.stop()

    c1,c2,c3 = st.columns(3)
    with c1:
        target_col = st.selectbox("🎯 Target Column (predict)",
                                   num_cols_for_target,
                                   index=num_cols_for_target.index(col_map["sales_col"])
                                         if col_map["sales_col"] in num_cols_for_target else 0)
    with c2:
        date_col_ml = st.selectbox("📅 Date Column (feature)",
                                    [None]+[c for c,t in col_types.items() if t=="date"])
    with c3:
        test_size = st.slider("Test Split %", 10, 40, 20) / 100

    run_btn = st.button("🚀 Train Models", type="primary")

    if run_btn:
        with st.spinner("Training Linear Regression & Random Forest…"):
            results = run_forecasting_pipeline(
                df, target_col, date_col_ml, test_size,
                save_dir=os.path.join(os.path.dirname(__file__), "models"),
            )

        if "error" in results:
            st.error(results["error"])
            st.stop()

        st.success(f"✅ Training complete! Best model: **{results['best_model']}**")
        st.write(f"Train size: **{results['train_size']:,}**   |   Test size: **{results['test_size_n']:,}**")

        # Metrics comparison
        st.markdown('<div class="section-hdr">📊 Model Performance Comparison</div>', unsafe_allow_html=True)
        metrics_data = []
        for model_name in ["Linear Regression","Random Forest"]:
            row = {"Model": model_name}
            row.update(results[model_name]["metrics"])
            metrics_data.append(row)
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df.style.highlight_max(subset=["R²"], color="#22c55e")
                                      .highlight_min(subset=["MAE","MSE","RMSE"], color="#22c55e"),
                     use_container_width=True, hide_index=True)

        # Bar chart comparison
        fig_cmp = px.bar(metrics_df.melt(id_vars="Model", value_vars=["MAE","RMSE","R²"]),
                         x="variable", y="value", color="Model", barmode="group",
                         title="Model Metrics Comparison",
                         color_discrete_sequence=px.colors.qualitative.Bold)
        fig_cmp.update_layout(template="plotly_dark", height=380)
        st.plotly_chart(fig_cmp, use_container_width=True)

        # Actual vs Predicted
        st.markdown('<div class="section-hdr">📈 Actual vs Predicted</div>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        for idx, model_name in enumerate(["Linear Regression","Random Forest"]):
            preds = results[model_name]["predictions"]
            y_test = results["y_test"]
            fig_ap = go.Figure()
            fig_ap.add_trace(go.Scatter(y=y_test[:150], mode="lines", name="Actual",
                                         line=dict(color="#38bdf8", width=2)))
            fig_ap.add_trace(go.Scatter(y=preds[:150], mode="lines", name="Predicted",
                                         line=dict(color="#f97316", width=2, dash="dash")))
            fig_ap.update_layout(template="plotly_dark", title=model_name,
                                  height=350, xaxis_title="Sample", yaxis_title=target_col)
            if idx == 0: col_a.plotly_chart(fig_ap, use_container_width=True)
            else:         col_b.plotly_chart(fig_ap, use_container_width=True)

        # Feature Importance
        fi = results["Random Forest"]["feature_importance"]
        if not fi.empty:
            st.markdown('<div class="section-hdr">🌟 Feature Importance (Random Forest)</div>', unsafe_allow_html=True)
            fi_fig = px.bar(fi.head(15), x="Importance", y="Feature", orientation="h",
                             title="Top 15 Features", color="Importance",
                             color_continuous_scale="Plasma")
            fi_fig.update_layout(template="plotly_dark", height=420,
                                  yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(fi_fig, use_container_width=True)

        # Residual plot
        st.markdown('<div class="section-hdr">📉 Residual Analysis</div>', unsafe_allow_html=True)
        best_preds = results[results["best_model"]]["predictions"]
        residuals  = results["y_test"] - best_preds
        fig_res = px.scatter(x=best_preds, y=residuals,
                             labels={"x":"Predicted","y":"Residual"},
                             title=f"Residuals — {results['best_model']}",
                             color_discrete_sequence=["#f97316"])
        fig_res.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
        fig_res.update_layout(template="plotly_dark", height=380)
        st.plotly_chart(fig_res, use_container_width=True)


# ── 📥 Download Reports ────────────────────────────────────────────────────────
elif active == "📥 Download Reports":
    st.markdown('<div class="section-hdr">📥 Download Reports</div>', unsafe_allow_html=True)

    st.info("All reports are generated from the **cleaned** dataset.")

    # Generate SQL reports for Excel
    with st.spinner("Preparing reports…"):
        sql_reports = build_sql_reports(df, col_map)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📄 PDF Report")
        st.write("Comprehensive report: overview, KPIs, insights, cleaning summary, stats.")
        pdf_bytes = generate_pdf_report(df, kpis, insights, cleaning_log)
        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_bytes,
            file_name=f"retail_analytics_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with col2:
        st.markdown("#### 📊 Excel Report")
        st.write("Multi-sheet: raw data, stats, KPIs, SQL reports, data quality.")
        xl_bytes = generate_excel_report(df, kpis, col_map, sql_reports)
        st.download_button(
            label="⬇️ Download Excel",
            data=xl_bytes,
            file_name=f"retail_analytics_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col3:
        st.markdown("#### 📋 CSV Summary")
        st.write("Descriptive statistics, skewness, kurtosis, and missing value counts.")
        csv_bytes = generate_csv_summary(df)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_bytes,
            file_name=f"stats_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("#### 📋 Cleaned Dataset")
    clean_csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Cleaned Dataset (CSV)",
        data=clean_csv,
        file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
