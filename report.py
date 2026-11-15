"""Buyer-ready PDF emissions report."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def build_report(path, company, period, totals, rows, actions):
    st = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=A4, title="Emissions Report")
    S = [Paragraph(f"Emissions Report: {company}", st["Title"]),
         Paragraph(f"Period: {period} | Method: GHG Protocol, activity data x emission factor", st["Normal"]),
         Spacer(1, 12), Paragraph("Summary (tonnes CO<sub>2</sub>e)", st["Heading2"])]
    t = Table([["Scope 1", "Scope 2", "Scope 3 (basic)", "Total"],
               [f"{totals[1]:.2f}", f"{totals[2]:.2f}", f"{totals[3]:.2f}", f"{sum(totals.values()):.2f}"]])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B5E3F")),
                           ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
    S += [t, Spacer(1, 12), Paragraph("Calculation detail (auditable)", st["Heading2"])]
    d = [["Month", "Source", "Qty", "Factor", "tCO2e", "Scope"]] + \
        [[r.get("month", ""), r["kind"], f'{r["quantity"]:g} {r["unit"]}', r["factor"], r["tCO2e"], r["scope"]] for r in rows]
    t2 = Table(d, repeatRows=1)
    t2.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 8)]))
    S += [t2, Spacer(1, 12), Paragraph("Recommended reduction actions", st["Heading2"])]
    if actions:
        a = [["Action", "Capex (Rs)", "Saving (Rs/yr)", "Payback (yrs)", "tCO2e avoided/yr"]] + \
            [[x["Action"], x["Capex (Rs)"], x["Annual saving (Rs)"], x["Payback (years)"], x["CO2e avoided (t/yr)"]] for x in actions]
        t3 = Table(a, repeatRows=1)
        t3.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 8)]))
        S.append(t3)
    S += [Spacer(1, 10), Paragraph("Emission factors: CEA CO<sub>2</sub> Baseline Database, IPCC, GHG Protocol. "
                                   "Savings are estimates for planning, not guarantees.", st["Italic"])]
    doc.build(S)
