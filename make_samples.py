"""Creates realistic FAKE bills (English + Hindi) and labels.csv for testing extraction.
Run: python make_samples.py   -> samples/*.png + samples/labels.csv"""
import csv, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

random.seed(11)
BASE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE, "samples"), exist_ok=True)
FONT_PATHS = ["/usr/share/fonts/truetype/freefont/FreeSans.ttf",            # Linux (supports Hindi)
              "C:/Windows/Fonts/Nirmala.ttf", "C:/Windows/Fonts/arial.ttf",  # Windows (Nirmala = Hindi)
              "/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc", # Mac
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
BOLD_PATHS = ["/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", "C:/Windows/Fonts/NirmalaB.ttf"] + FONT_PATHS
def font(size, bold=False):
    for p in (BOLD_PATHS if bold else FONT_PATHS):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

W, H = 900, 1100
def page(title, subtitle, color, hindi_title=None):
    img = Image.new("RGB", (W, H), "#FBFAF5"); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 120], fill=color)
    d.text((40, 22), title, fill="white", font=font(34, True))
    d.text((40, 70), hindi_title or subtitle, fill="white", font=font(24))
    d.rectangle([15, 135, W - 15, H - 15], outline="#999", width=2)
    return img, d

def rows(d, y, items, size=24, gap=52, x1=50, x2=520):
    for k, v in items:
        d.text((x1, y), k, fill="#333", font=font(size)); d.text((x2, y), str(v), fill="black", font=font(size, True))
        d.line([x1, y + gap - 12, W - 50, y + gap - 12], fill="#DDD"); y += gap
    return y

def footer(d):
    d.text((50, H - 70), "SAMPLE DOCUMENT - FICTIONAL DATA FOR TESTING ONLY", fill="#B00", font=font(18, True))

def degrade(img, angle, blur, noise):
    img = img.rotate(angle, fillcolor="#E9E6DC", expand=False)
    if blur: img = img.filter(ImageFilter.GaussianBlur(blur))
    if noise:
        px = img.load()
        for _ in range(noise):
            x, y = random.randrange(W), random.randrange(H); g = random.randint(90, 200); px[x, y] = (g, g, g)
    return img

def electricity(i, lang, month, kwh, messy):
    amt = int(kwh * 8.1 + 2400)
    if lang == "hi":
        img, d = page("RAJYA VIDYUT VITRAN NIGAM (SAMPLE)", "", "#B5651D", "बिजली बिल - औद्योगिक उपभोक्ता")
        L = [("उपभोक्ता का नाम", "श्री साई टेक्सटाइल्स"), ("उपभोक्ता क्रमांक", f"41{random.randint(100000,999999)}"),
             ("बिल माह", month), ("पिछली रीडिंग", f"{random.randint(40000,90000)}"),
             ("खपत इकाइयाँ (kWh)", kwh), ("स्वीकृत भार", "45 kW"), ("ऊर्जा शुल्क (₹)", int(kwh * 7.4)),
             ("कुल देय राशि (₹)", amt)]
    else:
        img, d = page("STATE POWER DISTRIBUTION CO. LTD. (SAMPLE)", "ELECTRICITY BILL - INDUSTRIAL CONSUMER", "#1F4E79")
        L = [("Consumer Name", "Sai Textiles Pvt Ltd"), ("Consumer No.", f"41{random.randint(100000,999999)}"),
             ("Billing Month", month), ("Previous Reading", f"{random.randint(40000,90000)}"),
             ("Units Consumed (kWh)", kwh), ("Sanctioned Load", "45 kW"), ("Energy Charges (Rs)", int(kwh * 7.4)),
             ("Total Amount Payable (Rs)", amt)]
    rows(d, 170, L); footer(d)
    return degrade(img, *messy), "electricity", kwh, month, amt

def fuel(i, lang, kind, month, qty, messy):
    price = 91.4 if kind == "diesel" else 103.9
    amt = round(qty * price, 2)
    name = "DIESEL" if kind == "diesel" else "PETROL"
    if lang == "hi":
        img, d = page("सागर फ्यूल स्टेशन (नमूना)", "", "#2E7D32", "ईंधन रसीद - " + ("डीज़ल" if kind == "diesel" else "पेट्रोल"))
        L = [("दिनांक", f"{month}-{random.randint(1,28):02d}"), ("उत्पाद", "डीज़ल" if kind == "diesel" else "पेट्रोल"),
             ("मात्रा (लीटर)", qty), ("दर (₹/लीटर)", price), ("कुल राशि (₹)", amt), ("वाहन/जनरेटर", "DG Set 62.5 kVA")]
    else:
        img, d = page("SAGAR FUEL STATION (SAMPLE)", f"FUEL RECEIPT - {name}", "#2E7D32")
        L = [("Date", f"{month}-{random.randint(1,28):02d}"), ("Product", name.title()), ("Quantity (Litres)", qty),
             ("Rate (Rs/Litre)", price), ("Total Amount (Rs)", amt), ("Vehicle / Equipment", "DG Set 62.5 kVA")]
    rows(d, 170, L); footer(d)
    return degrade(img, *messy), kind, qty, month, amt

def lpg(i, month, kg, messy):
    img, d = page("BHARAT GAS AGENCY (SAMPLE)", "COMMERCIAL LPG - CASH MEMO", "#C62828")
    cyl = kg // 19
    L = [("Date", f"{month}-12"), ("Item", "Commercial LPG Cylinder 19 kg"), ("No. of Cylinders", cyl),
         ("Total Weight (kg)", kg), ("Rate per Cylinder (Rs)", 1780), ("Total Amount (Rs)", cyl * 1780)]
    rows(d, 170, L); footer(d)
    return degrade(img, *messy), "lpg", kg, month, cyl * 1780

def invoice(i, kind, month, kg, messy):
    item, rate = {"steel": ("MS Steel Rods 12mm", 62), "cotton": ("Cotton Yarn 30s Combed", 245),
                  "packaging": ("Corrugated Packaging Boxes", 48)}[kind]
    img, d = page("PURCHASE INVOICE / TAX INVOICE (SAMPLE)", f"Supplier: Metro Traders, Indore", "#4A148C")
    L = [("Invoice Date", f"{month}-09"), ("Item Description", item), ("Quantity (kg)", kg),
         ("Rate (Rs/kg)", rate), ("Taxable Value (Rs)", kg * rate), ("GST 18% (Rs)", int(kg * rate * 0.18)),
         ("Invoice Total (Rs)", int(kg * rate * 1.18))]
    rows(d, 170, L); footer(d)
    return degrade(img, *messy), kind, kg, month, int(kg * rate * 1.18)

clean, tilt, rough = (0, 0, 0), (2.5, 0, 0), (-3, 1.2, 4000)
specs = [
    ("electricity", "en", "2026-04", 11840, clean), ("electricity", "en", "2026-06", 14250, tilt),
    ("electricity", "hi", "2026-07", 12975, clean), ("electricity", "hi", "2026-09", 15620, tilt),
    ("electricity", "en", "2026-08", 9480, rough),
    ("diesel", "en", "2026-05", 420, clean), ("diesel", "hi", "2026-08", 355, tilt),
    ("petrol", "en", "2026-06", 90, clean),
    ("lpg", None, "2026-07", 190, tilt),
    ("steel", None, "2026-05", 2400, clean), ("cotton", None, "2026-06", 1800, tilt),
    ("packaging", None, "2026-09", 650, rough),
]
labels = []
for i, (kind, lang, month, qty, messy) in enumerate(specs, 1):
    if kind == "electricity": img, k, q, m, a = electricity(i, lang, month, qty, messy)
    elif kind in ("diesel", "petrol"): img, k, q, m, a = fuel(i, lang, kind, month, qty, messy)
    elif kind == "lpg": img, k, q, m, a = lpg(i, month, qty, messy)
    else: img, k, q, m, a = invoice(i, kind, month, qty, messy)
    fn = f"samples/bill_{i:02d}_{k}_{lang or 'en'}.png"; img.save(os.path.join(BASE, fn))
    labels.append([fn, k, q, m, a])
with open(os.path.join(BASE, "samples", "labels.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["file", "kind", "quantity", "month", "amount_rs"]); w.writerows(labels)
print(f"Created {len(labels)} sample bills in samples/ with labels.csv")