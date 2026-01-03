"""Node for writing vector content items."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from langgraph.runtime import Runtime
from langgraph.types import Command

from app.platform.observability.logger import get_logger
from app.runtime import SageRuntimeContext
from app.state import VectorWriteState
from app.tools.vector_writer import write_to_vectorstore


def make_node_write_vector(
) -> Callable[[VectorWriteState, Runtime[SageRuntimeContext] | None], Command[Literal["__end__"]]]:
    """Node: vector_writer.

    Purpose:
        Write vector content items to the LangGraph Store using the vector writer tool.

    Side effects/state writes:
        Writes to the LangGraph Store via `write_to_vectorstore`.

    Returns:
        A Command routing to END after processing all items.
    """
    logger = get_logger("nodes.vector_writer")

    def node_write_vector(
        state: VectorWriteState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["__end__"]]:
        items = state.get("items") or []
        logger.info("vector_writer.batch.start", count=len(items))

        for item in items:
            # content = plain text
            content = item.get("text", "") or ""

            # write into agent namespace(s)
            agents = item.get("agents") or []
            for agent in agents:
                collection = agent  # e.g. "problem_framing"

                metadata = {
                    "uuid": item.get("uuid"),
                    "title": item.get("title", ""),
                    "tags": item.get("tags") or [],
                    "agents": agents,
                    "changed": item.get("changed", 0),
                }

                logger.info(
                    "vector_writer.write",
                    uuid=metadata["uuid"],
                    collection=collection,
                    content_length=len(content),
                )

                write_to_vectorstore(content, collection, metadata)

        logger.info("vector_writer.batch.done", count=len(items))
        return Command(goto="__end__")

    return node_write_vector
