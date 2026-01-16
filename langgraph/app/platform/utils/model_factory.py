"""Model factory helpers for agent models."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from app.platform.utils.provider_config import ProviderFactory


def get_model_for_agent(agent_name: str) -> BaseChatModel:
    """Return a configured model instance for a given agent.

    Uses the existing ProviderFactory.for_agent(agent_name) which
    reads config/provider/*.yaml (or env) and returns a (instance, params) pair.
    """
    instance, _params = ProviderFactory.for_agent(agent_name)
    return instance
