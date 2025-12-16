from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def build_hilp_markdown(req: Dict[str, Any], answers: Dict[str, str]) -> str:
    user_prompt = (req.get("prompt") or "").strip()
    questions: List[Dict[str, Any]] = req.get("questions") or []

    lines: List[str] = []
    lines.append("### Clarification (HILP)\n")

    if user_prompt:
        lines.append("**We’re refining your request:**")
        lines.append("")
        lines.append(f"> {user_prompt}")
        lines.append("")

    if not questions:
        lines.append("_No clarification questions defined._")
        return "\n".join(lines)

    lines.append("**Please answer each question with Yes, No, or “I’m not sure”:**")
    lines.append("")

    all_answered = True

    for idx, q in enumerate(questions, start=1):
        qid = q.get("id", f"q{idx}")
        qtext = q.get("text", "")

        answer_str = answers.get(qid)
        if answer_str is None:
            all_answered = False
            answer_label = "Not answered yet"
        else:
            if answer_str == "yes":
                answer_label = "Yes"
            elif answer_str == "no":
                answer_label = "No"
            else:
                answer_label = "I’m not sure"

        lines.append(f"- **Q{idx} (`{qid}`)**: {qtext}")
        lines.append(f"  - Answered: **{answer_label}**")

    if all_answered:
        lines.append("")
        lines.append(
            "**All questions are answered. Click “Run with these clarifications” "
            "to continue.**"
        )

    return "\n".join(lines)


def question_dropdown_choices(
    req: Dict[str, Any],
    answers: Dict[str, str],
    *,
    status_labels: Optional[Dict[str, str]] = None,
) -> List[Tuple[str, str]]:
    questions: List[Dict[str, Any]] = req.get("questions") or []
    choices: List[Tuple[str, str]] = []

    status_labels = status_labels or {"answered": "answered", "not_answered": "not answered"}

    for idx, q in enumerate(questions, start=1):
        qid = q.get("id", f"q{idx}")
        qtext = q.get("text", "")
        is_answered = qid in answers
        status = status_labels["answered"] if is_answered else status_labels["not_answered"]
        label = f"Q{idx} ({qid}) – {qtext} [{status}]"
        choices.append((label, qid))

    return choices


def pick_next_unanswered_question(req: Dict[str, Any], answers: Dict[str, str]) -> Optional[str]:
    questions: List[Dict[str, Any]] = req.get("questions") or []

    for q in questions:
        qid = q.get("id")
        if qid and qid not in answers:
            return qid

    if questions:
        return questions[-1].get("id")

    return None


def status_labels_for_lang(user_lang: str) -> Dict[str, str]:
    lang = (user_lang or "en").lower()
    if lang.startswith("hu"):
        return {"answered": "megválaszolva", "not_answered": "nincs megválaszolva"}
    return {"answered": "answered", "not_answered": "not answered"}
