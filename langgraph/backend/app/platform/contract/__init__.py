"""Public contract surface for backend invariants."""

from app.platform.contract.agents import validate_agent_schema
from app.platform.contract.artifacts import (
    ArtifactEnvelope,
    ArtifactProvenance,
    EvidencePointer,
)
from app.platform.contract.guardrails import evaluate_guardrails_contract
from app.platform.contract.namespaces import NamespaceParts, build_namespace
from app.platform.contract.phases import validate_phase_registry
from app.platform.contract.prompts import (
    PromptContract,
    validate_prompt_placeholders,
    validate_prompt_suffix_order,
)
from app.platform.contract.state import (
    PHASE_STATUS_VALUES,
    SAGESTATE_TOP_LEVEL_FIELDS,
    STATE_OWNERSHIP_RULES,
    StateOwnershipRule,
    validate_state_update,
)
from app.platform.contract.structured_output import (
    extract_structured_response,
    validate_structured_response,
)
from app.platform.contract.tools import (
    build_allowlist_contract,
    validate_allowlist_contains_schema,
)

__all__ = [
    "PHASE_STATUS_VALUES",
    "SAGESTATE_TOP_LEVEL_FIELDS",
    "STATE_OWNERSHIP_RULES",
    "ArtifactEnvelope",
    "ArtifactProvenance",
    "EvidencePointer",
    "NamespaceParts",
    "PromptContract",
    "StateOwnershipRule",
    "build_allowlist_contract",
    "build_namespace",
    "evaluate_guardrails_contract",
    "extract_structured_response",
    "validate_agent_schema",
    "validate_allowlist_contains_schema",
    "validate_phase_registry",
    "validate_prompt_placeholders",
    "validate_prompt_suffix_order",
    "validate_state_update",
    "validate_structured_response",
]
