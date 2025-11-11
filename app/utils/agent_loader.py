import os
from app.utils.file_loader import FileLoader
from app.utils.logger import log


class AgentLoader:
    """Aggregates all files belonging to an agent into a structured package."""

    @classmethod
    def load_agent(cls, agent_name: str):
        """
        Loads all configuration, schema, and prompts for a given agent.
        Always includes the global system prompt from _core.
        Returns a dict with:
          - name
          - config (agent.yaml)
          - schema (schema.json)
          - core_system_prompt (_core/core.prompt)
          - agent_system_prompt (agent/system.prompt)
        """
        base = FileLoader.BASE_DIR
        agent_dir = os.path.join(base, "agents", agent_name)

        if not os.path.isdir(agent_dir):
            msg = f"Agent folder not found: {agent_dir}"
            log("agent.load.error", {"agent": agent_name, "error": msg})
            raise RuntimeError(msg)

        # --- Load required assets ---
        config = FileLoader.load_agent_config(agent_name)
        schema = FileLoader.load_schema(agent_name, "schema")
        agent_prompt = FileLoader.load_prompt(agent_name, 'system')
        core_prompt = FileLoader.load_prompt('_core', 'core')

        # --- Validate existence ---
        if not core_prompt:
            raise RuntimeError("Critical: _core/core.prompt missing")
        if not agent_prompt:
            log("agent.prompt.missing", {"agent": agent_name})
        if not schema:
            log("agent.schema.missing", {"agent": agent_name})
        if not config:
            log("agent.config.missing", {"agent": agent_name})

        agent_data = {
            "name": agent_name,
            "config": config or {},
            "schema": schema or {},
            "agent_system_prompt": agent_prompt or "",
            "core_system_prompt": core_prompt or "",
        }

        log(
            "agent.load.success"
        )

        return agent_data
