from __future__ import annotations

from typing import Optional

# Placeholder – you can swap this for a real detector (fastText, cld3, or a small LLM)
def simple_lang_guess(text: str) -> str:
    """
    Super dumb detector stub.
    Replace this with a proper library or a cheap LLM call.
    Always returns a lower-case ISO-ish code like 'en', 'hu'.
    """
    # Example: if it contains obvious Hungarian characters:
    lowered = text.lower()
    if any(ch in lowered for ch in "őűáéíóöü"):
        return "hu"
    return "en"

def detect_user_lang(current_lang: Optional[str], user_query: str) -> str:
    """
    Only detect once. If we already have a user_lang, keep it.
    """
    if current_lang:
        return current_lang
    if not user_query.strip():
        return "en"
    return simple_lang_guess(user_query)
