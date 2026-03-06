"""
Business logic services (e.g. AI receipt scanning).
"""
import json
import os
import re
from io import BytesIO

import google.generativeai as genai
from PIL import Image


RECEIPT_PROMPT = """Analyze this receipt image. Extract: Total Amount, Date (YYYY-MM-DD), Merchant Name (use as Title), and suggest a Category (Food, Transport, etc.). Return ONLY valid JSON.

Use these exact keys in the JSON:
- "title": string - Merchant/store name
- "amount": number - Total amount (e.g. 25.99)
- "date": string - YYYY-MM-DD
- "category": string - One of: Food, Rent, Salary, Freelance, Entertainment, Transport, Other

If a value is not found, use empty string for title, 0 for amount, today for date, "Other" for category. No markdown, no code block—only the JSON object."""


def analyze_receipt(image_file) -> dict:
    """
    Use Gemini 1.5 Flash to extract receipt data from an image.
    Returns dict with keys: title, amount, date, category.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

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

    response = model.generate_content([RECEIPT_PROMPT, image])
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
        "date": date_str,
        "category": category,
    }
