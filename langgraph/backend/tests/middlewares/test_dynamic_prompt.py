from app.middlewares.dynamic_prompt import _apply_placeholders_to_string


def test_apply_placeholders_to_string_replaces_known_keys_only():
    template = (
        "Input: {user_query}\n"
        "Output: {\"business_domain\": \"Retail\", \"note\": \"keep braces {braces}\"}\n"
        "{format_instructions}"
    )
    values = {
        "user_query": "How do we reduce churn?",
        "format_instructions": "Return JSON.",
    }

    rendered = _apply_placeholders_to_string(template, values, ["user_query", "format_instructions"])

    assert "How do we reduce churn?" in rendered
    assert "Return JSON." in rendered
    assert "{\"business_domain\": \"Retail\", \"note\": \"keep braces {braces}\"}" in rendered
    assert "{braces}" in rendered  # unrelated braces are preserved
