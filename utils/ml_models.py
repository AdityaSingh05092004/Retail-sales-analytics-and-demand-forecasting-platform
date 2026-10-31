"""
ml_models.py — Linear Regression & Random Forest forecasting pipeline.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib, os


def prepare_features(df: pd.DataFrame, target_col: str,
                     date_col: Optional[str] = None) -> Tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df["_year"]      = df[date_col].dt.year
        df["_month"]     = df[date_col].dt.month
        df["_day"]       = df[date_col].dt.day
        df["_dayofweek"] = df[date_col].dt.dayofweek
        df["_quarter"]   = df[date_col].dt.quarter
        df = df.drop(columns=[date_col])
    # Drop all remaining datetime cols
    dt_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()
    df = df.drop(columns=dt_cols, errors="ignore")

    y = df[target_col].copy()
    X = df.drop(columns=[target_col])
    le = LabelEncoder()
    for col in X.select_dtypes(include=["object", "string"]).columns:
        X[col] = le.fit_transform(X[col].astype(str))
    X = X.select_dtypes(include=np.number).fillna(X.select_dtypes(include=np.number).median())
    y = pd.to_numeric(y, errors="coerce").fillna(y.median() if y.dropna().shape[0] else 0)
    return X, y


def _metrics(y_true, y_pred) -> Dict[str, float]:
    mae  = mean_absolute_error(y_true, y_pred)
    mse  = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2   = r2_score(y_true, y_pred)
    return {"MAE": round(mae,4), "MSE": round(mse,4),
            "RMSE": round(rmse,4), "R²": round(r2,4)}


def run_forecasting_pipeline(df: pd.DataFrame, target_col: str,
                              date_col: Optional[str] = None,
                              test_size: float = 0.2,
                              save_dir: Optional[str] = None) -> Dict[str, Any]:
    if len(df) < 20:
        return {"error": "Need at least 20 rows to train models."}

    X, y = prepare_features(df, target_col, date_col)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=test_size, random_state=42)

    results: Dict[str, Any] = {}

    # ── Linear Regression ──────────────────────────────────────────
    lr = LinearRegression()
    lr.fit(X_tr, y_tr)
    lr_pred = lr.predict(X_te)
    results["Linear Regression"] = {
        "metrics": _metrics(y_te, lr_pred),
        "predictions": lr_pred,
        "model": lr,
        "feature_importance": pd.DataFrame(),
    }

    # ── Random Forest ──────────────────────────────────────────────
    rf = RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=-1)
    rf.fit(X_tr, y_tr)
    rf_pred = rf.predict(X_te)
    fi = pd.DataFrame({"Feature": X.columns, "Importance": rf.feature_importances_})\
           .sort_values("Importance", ascending=False)
    results["Random Forest"] = {
        "metrics": _metrics(y_te, rf_pred),
        "predictions": rf_pred,
        "model": rf,
        "feature_importance": fi,
    }

    results["y_test"]       = y_te.values
    results["feature_names"]= list(X.columns)
    results["train_size"]   = len(X_tr)
    results["test_size_n"]  = len(X_te)

    best = max(["Linear Regression","Random Forest"],
               key=lambda m: results[m]["metrics"]["R²"])
    results["best_model"] = best

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        joblib.dump(results[best]["model"],
                    os.path.join(save_dir, "best_model.pkl"))

    return results
