-- ══════════════════════════════════════════════════════════════
-- Retail Analytics SQL Scripts
-- Table name: sales_data (auto-created when you upload a dataset)
-- Replace column names to match your actual dataset columns
-- ══════════════════════════════════════════════════════════════

-- 1. REVENUE BY CATEGORY
SELECT   Category,
         ROUND(SUM(Sales), 2)                   AS TotalRevenue,
         ROUND(AVG(Sales), 2)                   AS AvgOrderValue,
         COUNT(*)                               AS OrderCount
FROM     sales_data
GROUP BY Category
ORDER BY TotalRevenue DESC;

-- ──────────────────────────────────────────────────────────────

-- 2. TOP 10 PRODUCTS BY REVENUE
SELECT   "Product Name",
         ROUND(SUM(Sales), 2)                   AS Revenue,
         COUNT(*)                               AS TimesSold
FROM     sales_data
GROUP BY "Product Name"
ORDER BY Revenue DESC
LIMIT    10;

-- ──────────────────────────────────────────────────────────────

-- 3. MONTHLY REVENUE TREND
SELECT   SUBSTR("Order Date", 1, 7)             AS YearMonth,
         ROUND(SUM(Sales), 2)                   AS MonthlyRevenue,
         COUNT(*)                               AS Orders
FROM     sales_data
GROUP BY YearMonth
ORDER BY YearMonth;

-- ──────────────────────────────────────────────────────────────

-- 4. PROFITABILITY BY CATEGORY
SELECT   Category,
         ROUND(SUM(Sales),  2)                  AS Revenue,
         ROUND(SUM(Profit), 2)                  AS Profit,
         ROUND(SUM(Profit)*100.0
               / NULLIF(SUM(Sales), 0), 2)      AS MarginPct
FROM     sales_data
GROUP BY Category
ORDER BY MarginPct DESC;

-- ──────────────────────────────────────────────────────────────

-- 5. REGION PERFORMANCE
SELECT   Region,
         ROUND(SUM(Sales),  2)                  AS TotalRevenue,
         ROUND(AVG(Sales),  2)                  AS AvgOrder,
         ROUND(SUM(Profit), 2)                  AS TotalProfit,
         COUNT(*)                               AS Orders
FROM     sales_data
GROUP BY Region
ORDER BY TotalRevenue DESC;

-- ──────────────────────────────────────────────────────────────

-- 6. YEAR-OVER-YEAR COMPARISON
SELECT   SUBSTR("Order Date", 1, 4)             AS Year,
         ROUND(SUM(Sales),  2)                  AS Revenue,
         ROUND(SUM(Profit), 2)                  AS Profit,
         COUNT(*)                               AS Orders
FROM     sales_data
GROUP BY Year
ORDER BY Year;

-- ──────────────────────────────────────────────────────────────

-- 7. CUSTOMER SEGMENT ANALYSIS
SELECT   Segment,
         ROUND(SUM(Sales),  2)                  AS Revenue,
         ROUND(AVG(Sales),  2)                  AS AvgOrderValue,
         COUNT(DISTINCT "Customer ID")          AS UniqueCustomers
FROM     sales_data
GROUP BY Segment
ORDER BY Revenue DESC;

-- ──────────────────────────────────────────────────────────────

-- 8. TOP CUSTOMERS BY REVENUE
SELECT   "Customer Name",
         Segment,
         Region,
         ROUND(SUM(Sales),  2)                  AS TotalSpend,
         COUNT(DISTINCT "Order ID")             AS OrderCount
FROM     sales_data
GROUP BY "Customer Name", Segment, Region
ORDER BY TotalSpend DESC
LIMIT    20;

-- ──────────────────────────────────────────────────────────────

-- 9. SUB-CATEGORY DRILL-DOWN
SELECT   Category,
         "Sub-Category",
         ROUND(SUM(Sales),  2)                  AS Revenue,
         ROUND(SUM(Profit), 2)                  AS Profit,
         ROUND(SUM(Profit)*100.0
               / NULLIF(SUM(Sales), 0), 2)      AS MarginPct
FROM     sales_data
GROUP BY Category, "Sub-Category"
ORDER BY Revenue DESC;

-- ──────────────────────────────────────────────────────────────

-- 10. SHIPPING MODE ANALYSIS
SELECT   "Ship Mode",
         ROUND(SUM(Sales),  2)                  AS Revenue,
         COUNT(*)                               AS Orders,
         ROUND(AVG(Sales),  2)                  AS AvgOrderValue
FROM     sales_data
GROUP BY "Ship Mode"
ORDER BY Revenue DESC;
