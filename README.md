# 🛍️ Retail Sales Analytics & Demand Forecasting Platform

> A production-grade, end-to-end retail analytics platform built with **Python · Streamlit · scikit-learn · Plotly · SQLite**.  
> Upload any retail CSV/Excel dataset — the platform auto-detects columns and delivers EDA, KPIs, SQL reports, ML forecasting, and downloadable reports instantly.

---

## 🚀 Quick Start

```bash
# 1. Clone / navigate to the project
cd Retail_Analytics_Platform

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the dashboard
streamlit run app.py
```

Open your browser at **http://localhost:8501** and upload your dataset.

---

## 📁 Project Structure

```
Retail_Analytics_Platform/
│
├── app.py                        ← Main Streamlit dashboard
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py            ← File upload, parsing, column-type detection
│   ├── data_cleaner.py           ← Automated cleaning pipeline
│   ├── eda.py                    ← Dynamic Plotly EDA charts
│   ├── kpi.py                    ← KPI computation + business insights
│   ├── sql_engine.py             ← SQLite analytics engine
│   ├── ml_models.py              ← Linear Regression + Random Forest
│   └── report_generator.py      ← PDF, Excel, CSV report generation
│
├── data/                         ← Uploaded datasets & SQLite DB stored here
├── models/                       ← Trained model files (.pkl)
├── notebooks/
│   └── retail_analysis.ipynb    ← Full Jupyter notebook walkthrough
├── reports/                      ← Generated reports saved here
├── sql/
│   └── queries.sql               ← Pre-written SQL analytics scripts
│
├── requirements.txt
└── README.md
```

---

## ✨ Features

### 📁 Data Upload Module
- Upload **CSV or Excel** (.csv, .xlsx, .xls) files
- Auto-detects encodings (UTF-8, Latin-1, CP1252)
- Dataset preview, shape, dtypes, memory usage
- Missing value audit, duplicate count

### 🧹 Automated Data Cleaning
| Step | Method |
|------|--------|
| Date parsing | Heuristic detection + `pd.to_datetime` |
| Missing values | Numeric → median · Categorical → mode · Date → ffill/bfill |
| Duplicates | `drop_duplicates()` |
| Outliers | IQR-based capping (1.5×IQR) |
| Dtype conversion | Object → numeric where >90% parseable |

### 📊 Dynamic EDA
- Descriptive statistics with skewness & kurtosis
- Correlation heatmap
- Numeric distributions grid
- Sales & profit trend lines (monthly)
- Category / product / region bar charts + pie charts
- Box plots for distribution comparison
- Time heatmap (day-of-week × month)
- Area charts with category breakdown
- Custom scatter plot with trendline

### 📈 KPI Dashboard
| KPI | Description |
|-----|-------------|
| Total Revenue | Sum of sales column |
| Total Profit | Sum of profit column |
| Total Orders | Unique order count |
| Avg Order Value | Mean sales per row |
| Profit Margin % | Profit / Revenue × 100 |
| Best Product | Highest revenue product |
| Best Category | Highest revenue category |
| Best Region | Highest revenue region |
| Date Range | Min → Max order date |

### 🗄️ SQL Analytics (SQLite)
- Dataset auto-saved to SQLite on upload
- Pre-built reports: Revenue by Category, Region, Top Products, Profitability, Monthly Trend
- **Custom SQL editor** — write and run any query

### 🤖 Machine Learning Forecasting
- **Linear Regression** — fast baseline
- **Random Forest Regressor** — handles non-linearity
- Auto-engineered date features: year, month, day, day-of-week, quarter
- Label encoding for categorical features
- Configurable train/test split
- Metrics: **MAE, MSE, RMSE, R²**
- Visualizations: Actual vs Predicted, Residual plot, Feature Importance
- Best model saved as `models/best_model.pkl`

### 📥 Reports
| Report | Format | Contents |
|--------|--------|----------|
| PDF Report | `.pdf` | Overview, KPIs, insights, cleaning log, stats |
| Excel Report | `.xlsx` | Data, stats, KPIs, SQL results, quality sheet |
| CSV Summary | `.csv` | Descriptive stats + skewness/kurtosis |
| Cleaned Data | `.csv` | Full cleaned dataset |

---

## 🗂️ Supported Datasets

Any retail CSV/Excel with columns such as:

| Column Type | Example Names |
|-------------|---------------|
| Date | `Order Date`, `date`, `invoice_date` |
| Sales/Revenue | `Sales`, `revenue`, `amount`, `total` |
| Profit | `Profit`, `profit`, `margin` |
| Quantity | `Quantity`, `qty`, `units` |
| Product | `Product Name`, `product`, `item` |
| Category | `Category`, `segment`, `type` |
| Region | `Region`, `state`, `country`, `city` |
| Customer | `Customer Name`, `customer_id` |
| Order ID | `Order ID`, `transaction_id` |

**Popular datasets to try:**
- [Kaggle Superstore Sales](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
- [Online Retail II (UCI)](https://archive.ics.uci.edu/ml/datasets/Online+Retail+II)
- [Walmart Sales Forecasting](https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting)

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly Express, Seaborn, Matplotlib |
| Machine Learning | scikit-learn |
| Database | SQLite (via sqlite3) |
| Report Generation | fpdf2, openpyxl |
| Model Persistence | joblib |

---

## 📓 Jupyter Notebook

Run the full analysis pipeline in `notebooks/retail_analysis.ipynb`:

```bash
cd notebooks
jupyter notebook retail_analysis.ipynb
```

---

