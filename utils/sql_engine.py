"""
sql_engine.py — SQLite-backed analytics.
"""
import pandas as pd
import sqlite3, os
from typing import Dict, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "retail.db")


def _conn(path=DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return sqlite3.connect(path)


def save_to_db(df: pd.DataFrame, table: str = "sales_data", path=DB_PATH) -> str:
    con = _conn(path)
    df.to_sql(table, con, if_exists="replace", index=False)
    con.close()
    return f"✅ Saved {len(df):,} rows → table '{table}'"


def run_query(sql: str, path=DB_PATH) -> pd.DataFrame:
    con = _conn(path)
    try:
        return pd.read_sql_query(sql, con)
    finally:
        con.close()


def build_sql_reports(df: pd.DataFrame,
                      col_map: Dict[str, Optional[str]],
                      path=DB_PATH) -> Dict[str, pd.DataFrame]:
    save_to_db(df, path=path)
    reports: Dict[str, pd.DataFrame] = {}

    sc  = col_map.get("sales_col")
    pc  = col_map.get("profit_col")
    cc  = col_map.get("category_col")
    rc  = col_map.get("region_col")
    prc = col_map.get("product_col")
    dc  = col_map.get("date_col")

    def safe(q, label):
        try:
            reports[label] = run_query(q, path)
        except Exception as e:
            reports[label] = pd.DataFrame({"error": [str(e)]})

    if cc and sc:
        safe(f'SELECT "{cc}", ROUND(SUM("{sc}"),2) AS revenue, COUNT(*) AS orders '
             f'FROM sales_data GROUP BY "{cc}" ORDER BY revenue DESC', "Revenue by Category")

    if rc and sc:
        safe(f'SELECT "{rc}", ROUND(SUM("{sc}"),2) AS revenue '
             f'FROM sales_data GROUP BY "{rc}" ORDER BY revenue DESC', "Revenue by Region")

    if prc and sc:
        safe(f'SELECT "{prc}", ROUND(SUM("{sc}"),2) AS revenue '
             f'FROM sales_data GROUP BY "{prc}" ORDER BY revenue DESC LIMIT 15', "Top Products")

    if pc and sc and cc:
        safe(f'SELECT "{cc}", ROUND(SUM("{sc}"),2) AS revenue, '
             f'ROUND(SUM("{pc}"),2) AS profit, '
             f'ROUND(SUM("{pc}")*100.0/NULLIF(SUM("{sc}"),0),2) AS margin_pct '
             f'FROM sales_data GROUP BY "{cc}" ORDER BY margin_pct DESC', "Profitability")

    if dc and sc:
        safe(f'SELECT SUBSTR("{dc}",1,7) AS ym, '
             f'ROUND(SUM("{sc}"),2) AS revenue, COUNT(*) AS orders '
             f'FROM sales_data GROUP BY ym ORDER BY ym', "Monthly Revenue")

    return reports


SQL_SCRIPTS = '''-- ══════════════════════════════════════════════════════
-- Retail Analytics SQL Scripts
-- Replace column names to match your dataset
-- ══════════════════════════════════════════════════════

-- 1. Revenue by Category
SELECT   Category,
         ROUND(SUM(Sales), 2)  AS TotalRevenue,
         COUNT(*)              AS Orders
FROM     sales_data
GROUP BY Category
ORDER BY TotalRevenue DESC;

-- 2. Top 10 Products
SELECT   Product,
         ROUND(SUM(Sales), 2)  AS Revenue
FROM     sales_data
GROUP BY Product
ORDER BY Revenue DESC
LIMIT    10;

-- 3. Monthly Revenue Trend
SELECT   SUBSTR(OrderDate, 1, 7) AS YearMonth,
         ROUND(SUM(Sales), 2)    AS MonthlyRevenue
FROM     sales_data
GROUP BY YearMonth
ORDER BY YearMonth;

-- 4. Profitability by Category
SELECT   Category,
         ROUND(SUM(Sales),  2)                                   AS Revenue,
         ROUND(SUM(Profit), 2)                                   AS Profit,
         ROUND(SUM(Profit)*100.0 / NULLIF(SUM(Sales),0), 2)     AS MarginPct
FROM     sales_data
GROUP BY Category
ORDER BY MarginPct DESC;

-- 5. Region Performance
SELECT   Region,
         ROUND(SUM(Sales),  2)  AS Revenue,
         ROUND(AVG(Sales),  2)  AS AvgOrder,
         COUNT(*)               AS Orders
FROM     sales_data
GROUP BY Region
ORDER BY Revenue DESC;

-- 6. Year-over-Year Comparison
SELECT   SUBSTR(OrderDate,1,4)  AS Year,
         ROUND(SUM(Sales), 2)   AS Revenue
FROM     sales_data
GROUP BY Year
ORDER BY Year;
'''
