"""Small ML layer: anomaly detection (Isolation Forest) + next-month forecast (regression with seasonality)."""
import numpy as np, pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

def sample_history(seed=7):
    """12 months of synthetic electricity use with one planted spike."""
    rng = np.random.default_rng(seed)
    months = pd.period_range("2025-11", periods=12, freq="M")
    base = 11000 + 1800 * np.sin(np.arange(12) / 12 * 2 * np.pi) + rng.normal(0, 400, 12)
    base[8] *= 1.45  # planted anomaly
    return pd.DataFrame({"month": months.astype(str), "kwh": base.round()})

def detect_anomalies(df):
    X = df[["kwh"]].values
    model = IsolationForest(contamination=0.08, random_state=0).fit(X)
    out = df.copy()
    out["anomaly"] = model.predict(X) == -1
    return out

def _features(idx):
    idx = np.asarray(idx)
    return np.column_stack([idx, np.sin(2 * np.pi * idx / 12), np.cos(2 * np.pi * idx / 12)])

def forecast_next(df, steps=3):
    """Fit on non-anomalous months, predict next `steps` months."""
    clean = detect_anomalies(df)
    clean = clean[~clean["anomaly"]]
    idx = np.array([df.index.get_loc(i) for i in clean.index])
    reg = LinearRegression().fit(_features(idx), clean["kwh"].values)
    future = np.arange(len(df), len(df) + steps)
    start = pd.Period(df["month"].iloc[-1], freq="M")
    return pd.DataFrame({"month": [(start + i + 1).strftime("%Y-%m") for i in range(steps)],
                         "forecast_kwh": reg.predict(_features(future)).round()})

def benchmark(kwh_per_month, turnover_lakh):
    """Simple peer benchmark (illustrative peer medians; replace with real cluster data)."""
    peers = {"Textile": 1.0, "Food processing": 0.8, "Foundry": 2.0}   # kWh per Rs 1000 of monthly turnover
    mine = kwh_per_month / (turnover_lakh * 100)
    return {s: round(mine / v, 2) for s, v in peers.items()}, round(mine, 2)
