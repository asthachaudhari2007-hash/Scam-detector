# -*- coding: utf-8 -*-
"""
gemini_assistant.py

Optional AI companion for Digital Sathi: understands plain-language
requests from users (e.g. "I want to listen to a song") and either
resolves them directly — song requests become a YouTube search link —
or asks Google's Gemini model for a short, simple, safety-scoped reply.

Song/YouTube-link requests work even without a Gemini key. Full chat
replies require the GEMINI_API_KEY environment variable to be set.
"""

import logging
import os
import re
from urllib.parse import quote_plus

# Load variables from a local .env file (e.g. GEMINI_API_KEY=...) into
# the process environment. Safe to call even if no .env file exists —
# it just does nothing in that case. Requires: pip install python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; env vars set another way still work

logger = logging.getLogger("digital_sathi.assistant")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Models to try, in order. If the first is overloaded (503) or otherwise
# fails, we fall back to the next one. Override with GEMINI_MODEL_NAME to
# pin a single model instead.
_env_model = os.environ.get("GEMINI_MODEL_NAME")
GEMINI_MODEL_CANDIDATES = (
    [_env_model] if _env_model else
    ["gemini-3.5-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash"]
)

_gemini_client = None

try:
    from google import genai

    if GEMINI_API_KEY:
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini assistant configured successfully")
    else:
        logger.warning(
            "GEMINI_API_KEY not set — assistant chat replies are disabled; "
            "song/YouTube link requests will still work."
        )

except Exception:
    logger.exception("Could not initialize Gemini — assistant chat replies disabled")
    _gemini_client = None


# ============================================================
# SONG / MUSIC REQUEST DETECTION
# ============================================================

SONG_TRIGGER_PATTERNS = [
    r"\bplay\b",
    r"\blisten to\b",
    r"\bsong\b",
    r"\bmusic\b",
    r"\bgaana\b",
    r"\bgana\b",
    r"\bsunna\b",
    r"\bsunao\b",
    r"\bbajao\b",
    r"गाना",
    r"गीत",
    r"संगीत",
]

_SONG_TRIGGER_RE = re.compile("|".join(SONG_TRIGGER_PATTERNS), re.IGNORECASE)

# Words stripped out of the request so only the song/artist name remains
_STRIP_WORDS_RE = re.compile(
    r"\b(play|listen to|i want to listen to|can you play|a song|song|"
    r"music|gaana|gana|sunna hai|sunao|bajao|please)\b"
    r"|मुझे|सुनना|है|गाना|बजाओ|कृपया",
    re.IGNORECASE,
)


def is_song_request(text: str) -> bool:
    """Return True if `text` looks like a request to hear a song."""

    return bool(_SONG_TRIGGER_RE.search(text))


def extract_song_query(text: str) -> str:
    """Strip common trigger phrases from `text`, leaving the likely
    song/artist name behind. Falls back to the original text if
    stripping would leave nothing usable.
    """

    cleaned = _STRIP_WORDS_RE.sub("", text).strip(" .,!?-")
    return cleaned if cleaned else text.strip()


def get_youtube_search_link(query: str) -> str:
    """Build a YouTube search-results link for `query`.

    Uses a plain search URL (no YouTube API key required) rather than
    guessing a specific video, so the user sees real results and
    picks one themselves.
    """

    return "https://www.youtube.com/results?search_query=" + quote_plus(query)


# ============================================================
# GEMINI CHAT (general requests)
# ============================================================

_SYSTEM_INSTRUCTION_EN = (
    "You are a warm, patient digital companion for a senior citizen in "
    "India who may not be very comfortable with technology. Answer in "
    "short, simple sentences with no jargon. Do not give financial, "
    "medical, or legal advice, and never ask for OTPs, PINs, passwords, "
    "or banking details. If a request could involve money or personal "
    "data, gently suggest they verify with a trusted family member first."
)

_SYSTEM_INSTRUCTION_HI = (
    "आप भारत में एक वरिष्ठ नागरिक के लिए एक विनम्र, धैर्यवान डिजिटल साथी हैं, "
    "जो तकनीक में सहज नहीं हो सकते। सरल और छोटे वाक्यों में हिंदी में उत्तर दें। "
    "वित्तीय, चिकित्सा या कानूनी सलाह न दें, और कभी भी OTP, PIN, पासवर्ड या "
    "बैंकिंग विवरण न मांगें। यदि अनुरोध पैसे या व्यक्तिगत जानकारी से जुड़ा हो, तो "
    "पहले किसी विश्वसनीय परिवार के सदस्य से पुष्टि करने का सुझाव दें।"
)


def get_assistant_reply(message: str, lang: str = "en") -> dict:
    """Handle one assistant message.

    Song/music requests are resolved directly to a YouTube search link
    without needing Gemini. Everything else is passed to Gemini (if
    configured) for a short, safe, senior-friendly reply.

    Args:
        message: The user's free-text request.
        lang: "en" or "hi" — controls the reply language.

    Returns:
        A dict with:
          - type: "youtube" | "chat" | "unavailable"
          - reply: str shown to the user
          - youtube_link: str or None
    """

    message = (message or "").strip()
    lang = lang if lang in ("en", "hi") else "en"

    if not message:

        reply = (
            "कृपया मुझे बताएं कि आपको किस चीज़ में मदद चाहिए।"
            if lang == "hi" else
            "Please tell me what you'd like help with."
        )

        return {"type": "chat", "reply": reply, "youtube_link": None}

    # --------------------------------------------------------
    # Song / music requests — handled directly, no Gemini needed
    # --------------------------------------------------------

    if is_song_request(message):

        query = extract_song_query(message)
        link = get_youtube_search_link(query)

        reply = (
            f"यह रहा \"{query}\" के लिए YouTube पर खोज परिणाम:"
            if lang == "hi" else
            f"Here's a YouTube search for \"{query}\":"
        )

        return {"type": "youtube", "reply": reply, "youtube_link": link}

    # --------------------------------------------------------
    # Everything else — ask Gemini, if configured
    # --------------------------------------------------------

    if _gemini_client is None:

        reply = (
            "अभी AI सहायक उपलब्ध नहीं है। कृपया बाद में पुनः प्रयास करें।"
            if lang == "hi" else
            "The AI assistant isn't available right now. Please try again later."
        )

        return {"type": "unavailable", "reply": reply, "youtube_link": None}

    try:

        system_instruction = (
            _SYSTEM_INSTRUCTION_HI if lang == "hi" else _SYSTEM_INSTRUCTION_EN
        )

        prompt = f"{system_instruction}\n\nUser: {message}"

        reply_text = ""
        last_error = None

        for model_name in GEMINI_MODEL_CANDIDATES:
            try:
                response = _gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                reply_text = (getattr(response, "text", "") or "").strip()
                if reply_text:
                    break
            except Exception as model_error:
                last_error = model_error
                logger.warning(
                    "Gemini model %s failed, trying next candidate: %s",
                    model_name, model_error,
                )

        if not reply_text:
            raise last_error or ValueError("Empty response from Gemini")

        return {"type": "chat", "reply": reply_text, "youtube_link": None}

    except Exception:

        logger.exception("Gemini assistant request failed")

        reply = (
            "माफ़ कीजिए, अभी मैं इसका उत्तर नहीं दे पाया। कृपया फिर से कोशिश करें।"
            if lang == "hi" else
            "Sorry, I couldn't answer that just now. Please try again."
        )

        return {"type": "unavailable", "reply": reply, "youtube_link": None}