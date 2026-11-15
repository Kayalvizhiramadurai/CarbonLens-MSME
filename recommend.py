"""Rule-based recommendation engine. All numbers are ILLUSTRATIVE assumptions: edit and cite real quotes."""
from engine import FACTORS

TARIFF_RS_PER_KWH = 8.0     # typical industrial tariff, adjust per state
DIESEL_RS_PER_LITRE = 90.0

# saving_pct of annual use, capex in Rs per unit of annual saving
ACTIONS = [
    {"name": "LED lighting retrofit",        "fuel": "electricity", "saving_pct": 0.06, "capex_per_unit": 6},
    {"name": "VFDs and load shifting",       "fuel": "electricity", "saving_pct": 0.05, "capex_per_unit": 10},
    {"name": "IE3 efficient motors",         "fuel": "electricity", "saving_pct": 0.08, "capex_per_unit": 18},
    {"name": "Rooftop solar (30% of use)",   "fuel": "electricity", "saving_pct": 0.30, "capex_per_unit": 32},
    {"name": "DG set tuning and maintenance","fuel": "diesel",      "saving_pct": 0.05, "capex_per_unit": 5},
]

def recommend(annual_use):
    """annual_use: {'electricity': kWh/yr, 'diesel': litres/yr}. Returns actions ranked by payback."""
    out = []
    for a in ACTIONS:
        use = annual_use.get(a["fuel"], 0)
        if use <= 0:
            continue
        saved_units = use * a["saving_pct"]
        price = TARIFF_RS_PER_KWH if a["fuel"] == "electricity" else DIESEL_RS_PER_LITRE
        rs_saved = saved_units * price
        capex = saved_units * a["capex_per_unit"]
        co2 = saved_units * FACTORS[a["fuel"]]["factor"] / 1000
        out.append({"Action": a["name"], "Capex (Rs)": round(capex), "Annual saving (Rs)": round(rs_saved),
                    "Payback (years)": round(capex / rs_saved, 1) if rs_saved else None,
                    "CO2e avoided (t/yr)": round(co2, 2)})
    return sorted(out, key=lambda r: r["Payback (years)"])
