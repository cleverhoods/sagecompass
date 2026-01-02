"""
Minimal LangChain core stubs to allow offline testing without installing
external dependencies.
"""

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.chat_models import GenericFakeChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    FewShotPromptWithTemplates,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.tools import BaseTool, tool

__all__ = [
    "AnyMessage",
    "BaseChatModel",
    "BaseMessage",
    "HumanMessage",
    "SystemMessage",
    "GenericFakeChatModel",
    "PydanticOutputParser",
    "PromptTemplate",
    "FewShotPromptWithTemplates",
    "BasePromptTemplate",
    "ChatPromptTemplate",
    "SystemMessagePromptTemplate",
    "BaseTool",
    "tool",
]
