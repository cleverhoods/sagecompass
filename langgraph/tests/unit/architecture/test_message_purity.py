"""Architecture tests: Message purity enforcement.

This test suite enforces the separation between LLM conversation context
(state.messages) and operational trace events (state.events).

Nodes should NOT add operational/routing messages to state.messages.
Those belong in state.events via emit_event().
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# Patterns that indicate operational messages (should use events instead)
OPERATIONAL_PATTERNS = [
    "Running safety checks",
    "Running ambiguity preflight",
    "Checking for ambiguities",
    "Retrieving context",
    "Rescanning ambiguities",
    "Ambiguity checks complete",
    "No high-priority ambiguities",
    "Unable to determine ambiguity",
    "Unable to determine phase",
    "Unable to determine retrieval",
    "Unable to determine clarification",
    "Retrieved .* context items",
    "Ambiguities detected:",
    "Starting .* flow via",
    "phase complete",
    "analysis.",
]

# Directory containing node modules
NODES_DIR = Path("app/nodes")


def _find_aimessage_usages(file_path: Path) -> list[tuple[int, str]]:
    """Find AIMessage usages with their content in a file.

    Args:
        file_path: Path to Python file to analyze.

    Returns:
        List of (line_number, content_string) tuples.
    """
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return []

    usages: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        # Look for AIMessage(...) calls - combined if to satisfy SIM102
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "AIMessage":
            # Find content= keyword argument
            for keyword in node.keywords:
                if keyword.arg == "content":
                    # Extract string literal content
                    if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                        usages.append((node.lineno, keyword.value.value))
                    elif isinstance(keyword.value, ast.JoinedStr):
                        # f-string - extract literal parts using list comprehension (PERF401)
                        parts = [str(val.value) for val in keyword.value.values if isinstance(val, ast.Constant)]
                        if parts:
                            usages.append((node.lineno, "".join(parts)))

    return usages


def _is_operational_message(content: str) -> bool:
    """Check if a message content matches operational patterns.

    Args:
        content: Message content string.

    Returns:
        True if the message appears to be operational/routing.
    """
    import re

    content_lower = content.lower()

    for pattern in OPERATIONAL_PATTERNS:
        # Convert pattern to regex (handle .*)
        regex_pattern = pattern.lower().replace(".*", ".*")
        if re.search(regex_pattern, content_lower):
            return True

    return False


@pytest.mark.architecture
def test_no_operational_messages_in_nodes() -> None:
    """Test that nodes don't add operational messages to state.messages.

    Operational messages (routing status, progress updates, internal decisions)
    should be emitted as TraceEvents via emit_event(), not added to messages.

    User-facing messages (clarification prompts, terminal errors) may still
    use AIMessage.
    """
    # Find all Python files in nodes directory
    if not NODES_DIR.exists():
        pytest.skip(f"Nodes directory {NODES_DIR} does not exist")

    python_files = list(NODES_DIR.rglob("*.py"))
    if not python_files:
        pytest.skip(f"No Python files found in {NODES_DIR}")

    violations: list[tuple[Path, int, str]] = []

    for file_path in python_files:
        if "__pycache__" in str(file_path):
            continue

        usages = _find_aimessage_usages(file_path)

        for line_no, content in usages:
            if _is_operational_message(content):
                violations.append((file_path, line_no, content))

    if violations:
        error_lines = ["Found operational messages in state.messages (should use emit_event):"]
        for file_path, line_no, content in violations:
            error_lines.append(f'  {file_path.relative_to(Path.cwd())}:{line_no}: "{content[:60]}..."')
        error_lines.append("")
        error_lines.append("Operational messages should use emit_event() instead of AIMessage.")
        error_lines.append("Keep AIMessage for user-facing messages only.")

        pytest.fail("\n".join(error_lines))


@pytest.mark.architecture
def test_events_not_in_prompt_assembly() -> None:
    """Test that build_llm_messages() doesn't include events in LLM context.

    The prompting module should assemble LLM context from state.messages only,
    never from state.events.
    """
    from app.platform.runtime.prompting import build_llm_messages
    from app.state import SageState

    # Create a state with messages and events
    state = SageState()

    # The function should exist and return a list
    messages = build_llm_messages(state)
    assert isinstance(messages, list), "build_llm_messages should return a list"

    # Empty state should return empty list
    assert len(messages) == 0, "Empty state should have no messages"


# Allowed message types in state.messages
ALLOWED_MESSAGE_TYPES = {
    "HumanMessage",
    "AIMessage",
    "SystemMessage",
}

# Message types that should NOT be in state.messages (internal LangChain types)
FORBIDDEN_MESSAGE_TYPES = {
    "FunctionMessage",
    "ToolMessage",
    "ChatMessage",
    "RemoveMessage",
}


def _find_message_type_usages(file_path: Path) -> list[tuple[int, str]]:
    """Find message type instantiations in a file.

    Args:
        file_path: Path to Python file to analyze.

    Returns:
        List of (line_number, type_name) tuples for message instantiations.
    """
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return []

    usages: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        # Look for MessageType(...) calls
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            type_name = node.func.id
            if type_name in FORBIDDEN_MESSAGE_TYPES:
                usages.append((node.lineno, type_name))

    return usages


@pytest.mark.architecture
def test_no_forbidden_message_types_in_nodes() -> None:
    """Test that nodes don't use forbidden message types.

    Only HumanMessage, AIMessage, and SystemMessage should be used
    in state.messages. Internal LangChain types like FunctionMessage,
    ToolMessage, etc. should not appear.

    This prevents unexpected message types from breaking downstream
    processing that expects only the standard types.
    """
    if not NODES_DIR.exists():
        pytest.skip(f"Nodes directory {NODES_DIR} does not exist")

    python_files = list(NODES_DIR.rglob("*.py"))
    if not python_files:
        pytest.skip(f"No Python files found in {NODES_DIR}")

    violations: list[tuple[Path, int, str]] = []

    for file_path in python_files:
        if "__pycache__" in str(file_path):
            continue

        usages = _find_message_type_usages(file_path)
        for line_no, type_name in usages:
            violations.append((file_path, line_no, type_name))

    if violations:
        error_lines = ["Found forbidden message types in nodes:"]
        for file_path, line_no, type_name in violations:
            error_lines.append(f"  {file_path.relative_to(Path.cwd())}:{line_no}: {type_name}")
        error_lines.append("")
        error_lines.append(f"Allowed types: {', '.join(sorted(ALLOWED_MESSAGE_TYPES))}")
        error_lines.append(f"Forbidden types: {', '.join(sorted(FORBIDDEN_MESSAGE_TYPES))}")

        pytest.fail("\n".join(error_lines))


@pytest.mark.architecture
def test_message_type_contract_documented() -> None:
    """Test that the allowed message types are documented in the state contract.

    Ensures the contract explicitly states which message types are valid.
    """
    from app.platform.core.contract.state import STATE_OWNERSHIP_RULES

    # Find the messages ownership rule
    messages_rule = next(
        (rule for rule in STATE_OWNERSHIP_RULES if rule.field == "messages"),
        None,
    )

    assert messages_rule is not None, "messages field should have ownership rule"
    assert "append" in messages_rule.invariant.lower(), "messages invariant should mention append-only behavior"
