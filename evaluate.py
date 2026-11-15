"""Measures extraction accuracy on samples/labels.csv. Put these numbers in your submission.
Works from any folder. Needs a real API key (Gemini or Anthropic) set as an environment variable."""
import csv, os, time
from extract import extract_bill, has_key

BASE = os.path.dirname(os.path.abspath(__file__))
labels = os.path.join(BASE, "samples", "labels.csv")
if not os.path.exists(labels):
    raise SystemExit("samples/labels.csv not found. Run:  python make_samples.py   first.")
if not has_key():
    print("WARNING: no API key found, so demo mode is used and scores are meaningless.\n"
          "Set GEMINI_API_KEY (reopen the terminal after setx) and run again.\n")

ok_kind = ok_qty = ok_month = n = errors = 0
for r in csv.DictReader(open(labels, encoding="utf-8")):
    path = os.path.join(BASE, r["file"])
    try:
        out = extract_bill(open(path, "rb").read(), "image/png")
    except Exception as e:
        errors += 1; print(f"  {r['file']}: failed ({str(e)[:80]})"); time.sleep(10); continue
    n += 1
    k = out.get("kind") == r["kind"]
    q = out.get("quantity") is not None and abs(float(out["quantity"]) - float(r["quantity"])) < 0.5
    m = out.get("month") == r["month"]
    ok_kind += k; ok_qty += q; ok_month += m
    print(f"  {os.path.basename(path)}: type {'OK' if k else 'X'}, qty {'OK' if q else 'X'}, month {'OK' if m else 'X'}")
    time.sleep(6)   # stay under free-tier rate limits (about 10 requests/minute)
if n:
    print(f"\nBills read: {n} (failed: {errors})\nType accuracy:     {ok_kind / n:.0%}"
          f"\nQuantity accuracy: {ok_qty / n:.0%}\nMonth accuracy:    {ok_month / n:.0%}")