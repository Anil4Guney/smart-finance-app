"""
Business logic services (e.g. AI receipt scanning).
"""
import json
from django.conf import settings
import re
from io import BytesIO

import google.generativeai as genai
from PIL import Image


RECEIPT_PROMPT = """Analyze this receipt image. Extract: Total Amount, Currency, Date (YYYY-MM-DD), Merchant Name (use as Title), and suggest a Category (Food, Transport, etc.). Return ONLY valid JSON.

Use these exact keys in the JSON:
- "title": string - Merchant/store name
- "amount": number - Total amount in the receipt's own currency (e.g. 25.99)
- "currency": string - ISO 4217 code of that currency (e.g. TRY, EUR, USD, GBP, PLN). Infer it from symbols (₺, TL, €, $, £, zł) or the country of the shop
- "date": string - YYYY-MM-DD
- "category": string - One of: Food, Rent, Salary, Freelance, Entertainment, Transport, Other

If a value is not found, use empty string for title, 0 for amount, empty string for currency, today for date, "Other" for category. No markdown, no code block—only the JSON object."""


def analyze_receipt(image_file) -> dict:
    """
    Use Gemini to extract receipt data from an image.
    Returns dict with keys: title, amount, currency, date, category.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("AI service is not configured (GEMINI_API_KEY is missing).")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)

    # Support Django UploadedFile or file-like object
    if hasattr(image_file, "read"):
        image_file.seek(0)
        raw = image_file.read()
    else:
        raw = image_file

    image = Image.open(BytesIO(raw))
    # Convert to RGB if necessary (e.g. RGBA, P)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    response = model.generate_content([RECEIPT_PROMPT, image], request_options={'timeout': 60})
    text = (response.text or "").strip()

    # Remove optional markdown code fence if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    data = json.loads(text)

    # Normalize keys and types
    title = str(data.get("title") or "").strip() or "Receipt"
    amount = float(data.get("amount") or 0)
    date_str = str(data.get("date") or "").strip()
    category = str(data.get("category") or "Other").strip()
    currency = str(data.get("currency") or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", currency):
        currency = ""
    if category not in (
        "Food",
        "Rent",
        "Salary",
        "Freelance",
        "Entertainment",
        "Transport",
        "Other",
    ):
        category = "Other"

    return {
        "title": title,
        "amount": round(amount, 2),
        "currency": currency,
        "date": date_str,
        "category": category,
    }


def describe_ai_error(exc: Exception, fallback: str = "The AI assistant is unavailable right now. Please try again later.") -> tuple[int, str]:
    """Turn a Gemini/AI failure into an HTTP status and a message the user can act on."""
    from google.api_core import exceptions as google_errors

    text = str(exc).lower()
    if isinstance(exc, google_errors.ResourceExhausted) or "quota" in text or "rate limit" in text:
        return 503, "The AI service has reached its usage limit for now. Please try again in a few minutes."
    if isinstance(exc, (google_errors.PermissionDenied, google_errors.Unauthenticated)) or "api key" in text:
        return 503, "The AI service key is invalid or expired. The app owner needs to update GEMINI_API_KEY."
    if isinstance(exc, google_errors.NotFound):
        return 503, "The configured AI model is not available. The app owner needs to update GEMINI_MODEL."
    if isinstance(exc, (google_errors.DeadlineExceeded, google_errors.ServiceUnavailable, google_errors.InternalServerError)):
        return 503, "The AI service is busy right now. Please try again in a moment."
    if isinstance(exc, ValueError) and "not configured" in text:
        return 503, "AI service is not configured."
    return 502, fallback
