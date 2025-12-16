from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from app.state import SageState


class TranslationService:
    """
    UI translation wrapper.

    - HU-only behavior for now.
    - Uses translator agent: invoke({"user_language": "...", "message": "..."}).
    - Caches translations (lang, text).
    """

    def __init__(self):
        self._translation_agent = None
        self._cache: Dict[Tuple[str, str], str] = {}

    def infer_user_lang(self, user_message: str) -> str:
        msg = (user_message or "").lower()
        if any(ch in msg for ch in "áéíóöőúüű"):
            return "hu"
        return "en"

    def _get_translation_agent(self):
        if self._translation_agent is None:
            from app.agents.translator.agent import build_agent as build_translation_agent
            self._translation_agent = build_translation_agent()
        return self._translation_agent

    def translate_text(self, state: SageState, text: str) -> str:
        user_lang = (state.get("user_lang") or "en").lower()
        if not user_lang.startswith("hu"):
            return text

        text = (text or "").strip()
        if not text:
            return text

        key = (user_lang, text)
        if key in self._cache:
            return self._cache[key]

        try:
            raw = self._get_translation_agent().invoke(
                {"user_language": user_lang, "message": text}
            )

            translated: Optional[str] = None
            if isinstance(raw, dict):
                translated = raw.get("translated_text")
            else:
                translated = getattr(raw, "translated_text", None)

            if not translated:
                translated = text

            self._cache[key] = translated
            return translated
        except Exception as e:
            (state.setdefault("errors", [])).append(f"ui_translation_error: {e}")
            return text

    def translate_hilp_request(self, state: SageState, req: Dict[str, Any]) -> Dict[str, Any]:
        user_lang = (state.get("user_lang") or "en").lower()
        if not user_lang.startswith("hu"):
            return req

        req2 = dict(req)
        req2["prompt"] = self.translate_text(state, req.get("prompt", ""))

        qs = []
        for q in (req.get("questions") or []):
            q2 = dict(q)
            q2["text"] = self.translate_text(state, q.get("text", ""))
            qs.append(q2)

        req2["questions"] = qs
        return req2
