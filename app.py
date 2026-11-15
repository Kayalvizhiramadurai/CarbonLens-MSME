"""CarbonLens MSME: Streamlit dashboard. Run: streamlit run app.py"""
import os, tempfile
import pandas as pd, streamlit as st
from engine import calculate
from extract import extract_bill, has_key
from validate import check
from recommend import recommend
from ml import sample_history, detect_anomalies, forecast_next, benchmark
from report import build_report

st.set_page_config(page_title="CarbonLens MSME", page_icon="🌱", layout="wide")
st.title("🌱 CarbonLens MSME")
st.caption("Upload your bills, get your carbon footprint and a plan that pays for itself.")

if "records" not in st.session_state:
    st.session_state.records = []

with st.sidebar:
    company = st.text_input("Business name", "Demo Textiles Pvt Ltd")
    key = st.text_input("API key (Gemini or Anthropic, optional)", type="password",
                        help="Free Gemini key from aistudio.google.com works. Leave empty for demo mode.")
    turnover = st.number_input("Monthly turnover (Rs lakh)", 1.0, 2000.0, 100.0)
    if st.button("Load 12-month sample data"):
        h = sample_history()
        st.session_state.records = [{"kind": "electricity", "quantity": float(r.kwh), "month": r.month,
                                     "confidence": 1.0} for r in h.itertuples()]
        st.session_state.records.append({"kind": "diesel", "quantity": 400.0, "month": "2026-10", "confidence": 1.0})
    if st.button("Clear all data"):
        st.session_state.records = []

t1, t2, t3, t4, t5 = st.tabs(["1. Upload bills", "2. Footprint", "3. Savings plan", "4. AI insights", "5. Report"])

with t1:
    files = st.file_uploader("Bill photos (PNG/JPG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    if files and st.button("Extract with AI"):
        for f in files:
            mt = "image/png" if f.name.lower().endswith("png") else "image/jpeg"
            with st.spinner(f"Reading {f.name}..."):
                try:
                    out = extract_bill(f.getvalue(), mt, key or None)
                except Exception as e:
                    st.error(f"{f.name}: extraction failed. {e}")
                    continue
            if out.get("kind") in ("electricity", "diesel", "petrol", "lpg", "steel", "cotton", "packaging"):
                st.session_state.records.append({"kind": out["kind"], "quantity": out.get("quantity"),
                                                 "month": out.get("month"), "confidence": out.get("confidence", 0)})
        if not has_key(key):
            st.warning("Demo mode: no API key, so a fixed sample was used.")
    if st.session_state.records:
        st.subheader("Review and correct (one-tap confirmation)")
        df = st.data_editor(pd.DataFrame(st.session_state.records), num_rows="dynamic", use_container_width=True)
        st.session_state.records = df.to_dict("records")
        for i, r in enumerate(st.session_state.records):
            for flag in check(r):
                st.warning(f"Row {i + 1} ({r.get('kind')}): {flag}")

recs = [r for r in st.session_state.records if r.get("quantity")]
totals, rows = calculate(recs)

with t2:
    if not recs:
        st.info("Add bills or load sample data first.")
    else:
        c = st.columns(4)
        c[0].metric("Scope 1 (t)", f"{totals[1]:.2f}"); c[1].metric("Scope 2 (t)", f"{totals[2]:.2f}")
        c[2].metric("Scope 3 (t)", f"{totals[3]:.2f}"); c[3].metric("Total tCO2e", f"{sum(totals.values()):.2f}")
        st.subheader("Every number is traceable")
        st.dataframe(pd.DataFrame(rows)[["month", "kind", "quantity", "unit", "factor", "tCO2e", "scope", "source"]],
                     use_container_width=True)

elec = sum(r["quantity"] for r in recs if r["kind"] == "electricity")
dsl = sum(r["quantity"] for r in recs if r["kind"] == "diesel")
n_m = max(1, len({r.get("month") for r in recs if r["kind"] == "electricity"}))
annual = {"electricity": elec / n_m * 12, "diesel": dsl / n_m * 12}
actions = recommend(annual)

with t3:
    if not recs:
        st.info("Add bills or load sample data first.")
    else:
        st.dataframe(pd.DataFrame(actions), use_container_width=True)
        st.success(f"Total potential saving: Rs {sum(a['Annual saving (Rs)'] for a in actions):,} per year, "
                   f"{sum(a['CO2e avoided (t/yr)'] for a in actions):.1f} tCO2e avoided per year (if all actions are done).")
        st.caption("Assumptions (tariff, capex, savings %) are illustrative: edit recommend.py.")

with t4:
    hist = pd.DataFrame([{"month": r["month"], "kwh": r["quantity"]} for r in recs
                         if r["kind"] == "electricity" and r.get("month")],
                        columns=["month", "kwh"]).sort_values("month").reset_index(drop=True)
    if len(hist) < 6:
        st.info("Need at least 6 months of electricity data. Use 'Load 12-month sample data'.")
    else:
        a = detect_anomalies(hist)
        st.subheader("Anomaly detection (Isolation Forest)")
        st.line_chart(a.set_index("month")["kwh"])
        for r in a[a.anomaly].itertuples():
            st.error(f"Unusual consumption (high or low) in {r.month}: {r.kwh:,.0f} kWh. Check for leaks, faulty machines or billing errors.")
        st.subheader("Next 3 months forecast (regression + seasonality)")
        st.dataframe(forecast_next(hist), use_container_width=True)
        st.subheader("Peer benchmark (ratio to sector median; above 1.0 = worse)")
        ratios, mine = benchmark(hist["kwh"].mean(), turnover)
        st.write(f"Your intensity: {mine} kWh per Rs 1000 turnover")
        st.bar_chart(pd.Series(ratios))

with t5:
    if not recs:
        st.info("Add data first.")
    elif st.button("Generate buyer-ready PDF"):
        p = os.path.join(tempfile.gettempdir(), "carbonlens_report.pdf")
        build_report(p, company, "Based on uploaded bills", totals, rows, actions)
        st.download_button("Download report", open(p, "rb"), "emissions_report.pdf", "application/pdf")