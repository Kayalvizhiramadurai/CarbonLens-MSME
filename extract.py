"""AI extraction: a vision LLM reads a bill image and returns structured JSON.
Works with a FREE Google Gemini key (starts with 'AIza') or an Anthropic key (starts with 'sk-ant-').
Key can be pasted in the app sidebar, or set as GEMINI_API_KEY / ANTHROPIC_API_KEY.
No key at all = demo mode (fixed sample output)."""
import base64, hashlib, json, os, re, time

PROMPT = """You read Indian business bills (English or Hindi). Return ONLY JSON, no other text:
{"kind": "electricity|diesel|petrol|lpg|steel|cotton|packaging|other",
 "quantity": <number>, "unit": "<kWh|litre|kg>", "month": "YYYY-MM",
 "amount_rs": <number or null>, "confidence": <0 to 1>}
For electricity use units consumed (kWh). If a field is unreadable use null and lower confidence."""

# Model names change over time. If you get a 'model not found' error, check the model list in
# Google AI Studio and set GEMINI_MODEL to a current Flash model.
GEMINI_MODELS = [m for m in [os.getenv("GEMINI_MODEL"), "gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash"] if m]
CLAUDE_MODEL = "claude-sonnet-5-5"

BASE = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE, ".extract_cache.json")

class QuotaError(RuntimeError):
    pass

def _cache_load():
    try:
        return json.load(open(CACHE_FILE, encoding="utf-8"))
    except Exception:
        return {}

def _cache_save(c):
    try:
        json.dump(c, open(CACHE_FILE, "w", encoding="utf-8"))
    except Exception:
        pass

DEMO = {"kind": "electricity", "quantity": 12000, "unit": "kWh", "month": "2026-10",
        "amount_rs": 96000, "confidence": 0.5, "demo": True}

def has_key(key=None):
    return bool(key or os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))

def _parse(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    return json.loads(m.group(0)) if m else {"kind": "other", "quantity": None, "confidence": 0.0}

def _discover_flash_models(client):
    """Ask the API which Flash models this key can use (newest first)."""
    try:
        names = [m.name.replace("models/", "") for m in client.models.list()]
    except Exception:
        return []
    bad = ("image", "tts", "live", "audio", "embedding", "lite", "native")
    flash = [n for n in names if "flash" in n and not any(b in n for b in bad)]
    return sorted(flash, reverse=True)[:4]

def _gemini(image_bytes, media_type, key):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=key)
    errors = []
    tried = set()

    def attempt(models):
        for model in models:
            if model in tried:
                continue
            tried.add(model)
            for retry in (0, 1):
                try:
                    r = client.models.generate_content(
                        model=model,
                        contents=[types.Part.from_bytes(data=image_bytes, mime_type=media_type), PROMPT],
                        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0))
                    return _parse(r.text)
                except Exception as e:
                    msg = str(e)
                    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                        if retry == 0:
                            time.sleep(25)      # per-minute limit: wait once and retry
                            continue
                        raise QuotaError(
                            "Gemini free quota is used up for now. Per-minute limits clear in about a minute. "
                            "Daily limits reset at midnight Pacific time (about 1:30 PM IST); check the usage page "
                            "in Google AI Studio. Bills you already extracted are cached and will not use quota again.")
                    errors.append(f"{model}: {msg[:120]}")
                    break
        return None

    out = attempt(GEMINI_MODELS)
    if out is None:                       # all hard-coded names failed: discover current models
        out = attempt(_discover_flash_models(client))
    if out is None:
        raise RuntimeError("Gemini call failed. " + " | ".join(errors))
    return out

def _claude(image_bytes, media_type, key):
    import anthropic
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=400,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type,
                                         "data": base64.b64encode(image_bytes).decode()}},
            {"type": "text", "text": PROMPT}]}])
    return _parse("".join(b.text for b in msg.content if b.type == "text"))

def extract_bill(image_bytes, media_type="image/jpeg", api_key=None):
    key = (api_key or "").strip() or None
    if key is None:  # fall back to environment variables
        key = os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return dict(DEMO)
    h = hashlib.sha256(image_bytes).hexdigest()
    cache = _cache_load()
    if h in cache:
        return {**cache[h], "cached": True}
    out = _claude(image_bytes, media_type, key) if key.startswith("sk-ant") else _gemini(image_bytes, media_type, key)
    if out.get("quantity") is not None:
        cache[h] = out
        _cache_save(cache)
    return out