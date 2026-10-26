"""
Gemini access for the whole app (chat and receipt reading).

- retries a busy model once, then falls back to the next model in the list
- stops waiting after AI_TOTAL_BUDGET_SECONDS (the web server kills slow requests)
- global daily call cap, so a flood of sign-ups cannot burn the API quota/bill
- turns every failure into an `AIUnavailable` with a message the user can act on
"""
import logging
import time
from datetime import date

from django.conf import settings
from django.core.cache import cache
from google import genai
from google.genai import errors, types

logger = logging.getLogger(__name__)

RETRYABLE_CODES = {500, 503, 504}


class AIUnavailable(Exception):
    """The AI could not answer. `status_code` and `message` are safe to show the user."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def describe_ai_error(exc: Exception, fallback: str = "Yapay zekâ asistanı şu an kullanılamıyor. Lütfen daha sonra tekrar dene.") -> tuple[int, str]:
    """Turn a Gemini/AI failure into an HTTP status and a message the user can act on."""
    if isinstance(exc, AIUnavailable):
        return exc.status_code, exc.message

    code = getattr(exc, 'code', None) if isinstance(exc, errors.APIError) else None
    text = str(exc).lower()
    if code == 429 or 'quota' in text or 'rate limit' in text:
        return 503, "Yapay zekâ servisinin kullanım sınırı şu an doldu. Birkaç dakika sonra tekrar dene."
    if code in (401, 403) or 'api key' in text:
        return 503, "Yapay zekâ servisinin anahtarı geçersiz veya süresi dolmuş. Uygulama sahibi GEMINI_API_KEY değerini güncellemeli."
    if code == 404:
        return 503, "Ayarlı yapay zekâ modeli kullanılamıyor. Uygulama sahibi GEMINI_MODEL değerini güncellemeli."
    if code in RETRYABLE_CODES or 'timeout' in text or 'timed out' in text or 'unavailable' in text:
        return 503, "Yapay zekâ servisi şu an yoğun. Biraz sonra tekrar dene."
    return 502, fallback


def _spend_daily_budget() -> None:
    limit = settings.AI_DAILY_CALL_LIMIT
    if not limit:
        return
    key = f"ai-calls:{date.today().isoformat()}"
    cache.add(key, 0, timeout=60 * 60 * 26)
    try:
        used = cache.incr(key)
    except ValueError:  # key expired between add and incr
        cache.set(key, 1, timeout=60 * 60 * 26)
        used = 1
    if used > limit:
        raise AIUnavailable(503, "Yapay zekâ asistanının bugünkü kullanım hakkı doldu. Yarın tekrar dene.")


def generate(contents, models: list[str]) -> str:
    """Return the model's text answer, trying each model in `models` in order."""
    if not settings.GEMINI_API_KEY:
        raise AIUnavailable(503, "Yapay zekâ servisi yapılandırılmamış.")
    _spend_daily_budget()

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=int(settings.AI_REQUEST_TIMEOUT_SECONDS * 1000)),
    )
    deadline = time.monotonic() + settings.AI_TOTAL_BUDGET_SECONDS
    last_error: Exception | None = None

    for model in dict.fromkeys(models):  # unique, order kept
        for attempt in range(2):
            if time.monotonic() > deadline:
                raise AIUnavailable(503, "Yapay zekâ servisi şu an yoğun. Biraz sonra tekrar dene.")
            try:
                response = client.models.generate_content(model=model, contents=contents)
                text = (response.text or '').strip()
                if not text:
                    raise AIUnavailable(502, "Yapay zekâ boş bir cevap döndürdü. Soruyu biraz değiştirip tekrar dene.")
                return text
            except AIUnavailable:
                raise
            except errors.APIError as exc:
                last_error = exc
                logger.warning("Gemini %s failed (attempt %s): %s", model, attempt + 1, exc.code)
                if exc.code in RETRYABLE_CODES and attempt == 0:
                    time.sleep(1)
                    continue
                break  # next model
            except Exception as exc:  # network errors and timeouts
                last_error = exc
                logger.warning("Gemini %s call error: %s", model, type(exc).__name__)
                break

    status_code, message = describe_ai_error(last_error or RuntimeError('no model'))
    raise AIUnavailable(status_code, message)
