"""Emission engine: activity data x emission factor. Plain maths, fully auditable.
VERIFY these factors against the latest CEA / IPCC / GHG Protocol sources before submitting."""

FACTORS = {  # kg CO2e per unit
    "electricity": {"factor": 0.71, "unit": "kWh",   "scope": 2, "source": "CEA CO2 Baseline Database (India grid, approx.)"},
    "diesel":      {"factor": 2.68, "unit": "litre", "scope": 1, "source": "IPCC / GHG Protocol"},
    "petrol":      {"factor": 2.31, "unit": "litre", "scope": 1, "source": "IPCC / GHG Protocol"},
    "lpg":         {"factor": 2.98, "unit": "kg",    "scope": 1, "source": "IPCC / GHG Protocol"},
    "steel":       {"factor": 2.00, "unit": "kg",    "scope": 3, "source": "Indicative purchased-goods factor"},
    "cotton":      {"factor": 1.80, "unit": "kg",    "scope": 3, "source": "Indicative purchased-goods factor"},
    "packaging":   {"factor": 1.50, "unit": "kg",    "scope": 3, "source": "Indicative purchased-goods factor"},
}

def calculate(records):
    """records: list of dicts with keys kind, quantity. Returns (totals_by_scope_in_tonnes, detail_rows)."""
    totals = {1: 0.0, 2: 0.0, 3: 0.0}
    rows = []
    for r in records:
        f = FACTORS.get(r["kind"])
        if not f:
            continue
        t = float(r["quantity"]) * f["factor"] / 1000
        totals[f["scope"]] += t
        rows.append({**r, "scope": f["scope"], "factor": f["factor"], "unit": f["unit"],
                     "tCO2e": round(t, 3), "source": f["source"]})
    return totals, rows

if __name__ == "__main__":
    print(calculate([{"kind": "electricity", "quantity": 12000}, {"kind": "diesel", "quantity": 400}]))
