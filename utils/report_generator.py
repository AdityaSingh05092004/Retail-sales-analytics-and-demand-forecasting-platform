"""
report_generator.py — PDF, CSV, and Excel report generation.
"""
import pandas as pd
import numpy as np
import io
from typing import Dict, Any, Optional
from datetime import datetime


def generate_csv_summary(df: pd.DataFrame) -> bytes:
    num = df.select_dtypes(include=np.number)
    if num.empty:
        summary = df.describe(include="all").T
    else:
        summary = num.describe().T
        summary["skewness"] = num.skew()
        summary["kurtosis"] = num.kurt()
        summary["missing"]  = num.isnull().sum()
    buf = io.StringIO()
    summary.to_csv(buf)
    return buf.getvalue().encode("utf-8")


def generate_excel_report(df: pd.DataFrame, kpis: Dict[str, Any],
                           col_map: Dict[str, Optional[str]],
                           sql_reports: Optional[Dict[str, pd.DataFrame]] = None) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.head(1000).to_excel(writer, sheet_name="Data (Top 1000)", index=False)

        num = df.select_dtypes(include=np.number)
        if not num.empty:
            stats = num.describe().T
            stats["skewness"] = num.skew()
            stats.to_excel(writer, sheet_name="Descriptive Stats")

        kpi_df = pd.DataFrame([(k, v) for k, v in kpis.items() if v is not None],
                               columns=["KPI", "Value"])
        kpi_df.to_excel(writer, sheet_name="KPIs", index=False)

        if sql_reports:
            for name, rdf in sql_reports.items():
                rdf.to_excel(writer, sheet_name=name[:31], index=False)

        quality = pd.DataFrame({
            "Column":       df.columns,
            "Dtype":        df.dtypes.astype(str).values,
            "Missing Count":df.isnull().sum().values,
            "Missing %":    (df.isnull().mean()*100).round(2).values,
            "Unique Values":df.nunique().values,
        })
        quality.to_excel(writer, sheet_name="Data Quality", index=False)
    return buf.getvalue()


def generate_pdf_report(df: pd.DataFrame, kpis: Dict[str, Any],
                         insights: list, cleaning_log: Dict[str, Any]) -> bytes:
    try:
        from fpdf import FPDF

        class PDF(FPDF):
            def header(self):
                self.set_fill_color(15, 23, 42)
                self.set_text_color(255, 255, 255)
                self.set_font("Helvetica", "B", 15)
                self.cell(0, 13, "Retail Sales Analytics Report", ln=True, fill=True, align="C")
                self.set_text_color(0, 0, 0)
                self.ln(3)

            def footer(self):
                self.set_y(-14)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(120)
                self.cell(0, 8,
                    f"Page {self.page_no()}  |  Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    align="C")

        def section(pdf, title):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_fill_color(226, 232, 240)
            pdf.cell(0, 8, f"  {title}", border="B", ln=True, fill=True)
            pdf.ln(2)

        def body(pdf, text):
            pdf.set_font("Helvetica", size=9)
            safe = ''.join(c if ord(c) < 128 else '-' for c in text)
            pdf.multi_cell(0, 5.5, safe)
            pdf.ln(0.5)

        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica","I",9)
        pdf.cell(0,5,f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",ln=True,align="R")
        pdf.ln(3)

        # 1. Overview
        section(pdf, "1. Dataset Overview")
        body(pdf, f"Rows: {len(df):,}    Columns: {len(df.columns)}")
        body(pdf, f"Columns: {', '.join(df.columns[:15].tolist())}")
        body(pdf, f"Date Range: {kpis.get('date_range_start','N/A')}  to  {kpis.get('date_range_end','N/A')}")

        # 2. KPIs
        section(pdf, "2. Key Performance Indicators")
        labels = {
            "total_revenue":"Total Revenue","total_profit":"Total Profit",
            "total_orders":"Total Orders","avg_order_value":"Avg Order Value",
            "profit_margin_pct":"Profit Margin %","total_units_sold":"Units Sold",
            "best_product":"Best Product","best_category":"Best Category",
            "best_region":"Best Region",
        }
        for k, lbl in labels.items():
            v = kpis.get(k)
            if v is None: continue
            if isinstance(v, float): body(pdf, f"  {lbl}: {v:,.2f}")
            elif isinstance(v, int):  body(pdf, f"  {lbl}: {v:,}")
            else:                     body(pdf, f"  {lbl}: {v}")

        # 3. Insights
        section(pdf, "3. Business Insights")
        for ins in insights:
            clean = ins.replace("**","").replace("📈","UP").replace("📉","DOWN")
            clean = clean.replace("💰","").replace("📊","").replace("🏆","").replace("📦","")
            clean = clean.replace("🌍","").replace("🛒","").replace("⚠️","[!]").replace("✅","[OK]")
            body(pdf, f"  * {clean}")

        # 4. Cleaning
        section(pdf, "4. Data Cleaning Summary")
        body(pdf, f"Duplicates removed: {cleaning_log.get('duplicates_removed', 0)}")
        dparsed = cleaning_log.get("date_columns_parsed",[])
        body(pdf, f"Date columns parsed: {', '.join(dparsed) if dparsed else 'None'}")
        for col, action in list(cleaning_log.get("missing_value_treatment",{}).items())[:8]:
            if col != "rows_dropped_high_missing":
                body(pdf, f"  {col}: {action}")

        # 5. Stats
        section(pdf, "5. Descriptive Statistics")
        num = df.select_dtypes(include=np.number)
        if not num.empty:
            for col, row in num.describe().T[["mean","std","min","max"]].iterrows():
                body(pdf, f"  {col}: mean={row['mean']:.2f}  std={row['std']:.2f}"
                          f"  min={row['min']:.2f}  max={row['max']:.2f}")

        return bytes(pdf.output())

    except ImportError:
        lines = [f"RETAIL ANALYTICS REPORT — {datetime.now()}",
                 "="*50, f"Rows: {len(df):,}  Columns: {len(df.columns)}",
                 "\nKPIs:"]
        for k, v in kpis.items():
            if v is not None: lines.append(f"  {k}: {v}")
        lines.append("\nInsights:")
        lines += [f"  {i}" for i in insights]
        return "\n".join(lines).encode("utf-8")
