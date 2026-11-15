# CarbonLens MSME: Build Guide (beginner friendly)

## What is in this folder
| File | What it does |
|---|---|
| `engine.py` | Emission maths: usage x factor (no AI, fully auditable) |
| `extract.py` | AI step: a vision LLM reads a bill photo and returns JSON |
| `validate.py` | Rules that flag odd or low-confidence values |
| `recommend.py` | Ranks savings actions by payback |
| `ml.py` | Anomaly detection, 3-month forecast, peer benchmark |
| `report.py` | Buyer-ready PDF report |
| `app.py` | The Streamlit dashboard (your demo) |
| `make_samples.py` | Creates 24 fake bills + answer sheet |
| `evaluate.py` | Measures extraction accuracy |

## Step 1: Setup (15 min)
1. Install Python 3.10+ (tick "Add to PATH") and VS Code.
2. Open this folder in VS Code, open a terminal, run:
   `pip install -r requirements.txt`

## Step 2: Test the engine (2 min)
`python engine.py`  -> Scope 1 = 1.072 t, Scope 2 = 8.52 t.

## Step 3: Run the app in demo mode (5 min)
`streamlit run app.py`
In the sidebar click **Load 12-month sample data**, then explore all 5 tabs.

## Step 4: Turn on the real AI (10 min)
1. Get an API key from console.anthropic.com.
2. Paste it in the sidebar box, or set it once:
   - Windows: `setx ANTHROPIC_API_KEY "your-key"` (reopen terminal)
   - Mac/Linux: `export ANTHROPIC_API_KEY="your-key"`
3. Run `python make_samples.py` to create test bills, then upload some in tab 1.

## Step 5: Measure accuracy (your headline number)
`python evaluate.py` (with the API key set). Without a key it only runs the
fixed demo output, so the score will be low and meaningless.
Report type, quantity and month accuracy in your submission. Then add 10 real
or realistic bills (blur, tilt, Hindi) to `samples/` and add rows to `labels.csv`.

## Step 6: Make it yours (days 3 to 5)
- Verify every emission factor in `engine.py` against the latest CEA and IPCC sources and cite them.
- Replace the illustrative assumptions in `recommend.py` (tariff, capex, savings %) with real quotes or BEE data.
- Replace peer medians in `ml.py` with real sector data if you can find it.
- Add your sector profiles (textile, food, foundry) as 3 saved demo cases.

## Step 7: Demo script (3 minutes)
1. Problem: a buyer demands emissions data; the owner has only paper bills.
2. Upload 2 to 3 bill photos (one in Hindi) -> AI extracts -> one-tap correction.
3. Footprint tab: Scope 1/2/3 with the source of every number.
4. Savings plan: payback, rupees and CO2 saved.
5. AI insights: anomaly flagged, forecast, benchmark.
6. Download the PDF report. Close with accuracy %, pricing and scale plan.

## Honest limits (say these to the judges)
- Scope 3 is a basic estimate using indicative factors.
- Savings figures are planning estimates, not guarantees.
- The anomaly and forecast models are trained on small data; they are demonstrations of the method.
- Pre-trained vision LLM does the reading; the novelty is the pipeline, validation and decision layer.

## Optional: put it online
Push the folder to GitHub and deploy free on Streamlit Community Cloud.
Add ANTHROPIC_API_KEY under the app's Secrets.
