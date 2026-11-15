"""Rule-based validation of extracted bill data."""
LIMITS = {  # plausible monthly range for a small MSME
    "electricity": (100, 200000), "diesel": (5, 20000), "petrol": (5, 5000), "lpg": (1, 5000),
}

def check(rec):
    flags = []
    q = rec.get("quantity")
    if q is None or q <= 0:
        flags.append("Missing or non-positive quantity")
    lo_hi = LIMITS.get(rec.get("kind"))
    if q and lo_hi and not (lo_hi[0] <= q <= lo_hi[1]):
        flags.append(f"Quantity {q} outside plausible range {lo_hi}")
    if rec.get("confidence", 1) < 0.7:
        flags.append("Low extraction confidence: please confirm")
    if not rec.get("month"):
        flags.append("Billing month missing")
    return flags
