from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from langchain_core.messages import SystemMessage


class BasePromptTemplate:
    def __init__(self, template: str) -> None:
        self.template = template

    def format(self, **kwargs: Any) -> str:
        return self.template.format(**kwargs)


class PromptTemplate(BasePromptTemplate):
    pass


class SystemMessagePromptTemplate(BasePromptTemplate):
    def format(self, **kwargs: Any) -> SystemMessage:
        return SystemMessage(content=self.template.format(**kwargs))


class ChatPromptTemplate(BasePromptTemplate):
    def format_messages(self, **kwargs: Any) -> list[SystemMessage]:
        return [SystemMessage(content=self.template.format(**kwargs))]


class FewShotPromptWithTemplates:
    """Placeholder to satisfy imports; not used in test assertions."""

    def __init__(
        self,
        examples: Sequence[Mapping[str, Any]] | None = None,
        *,
        example_prompt: BasePromptTemplate | None = None,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        self.examples = list(examples or [])
        self.example_prompt = example_prompt
        self.prefix = prefix
        self.suffix = suffix

    def format(self, **kwargs: Any) -> str:  # pragma: no cover - unused helper
        formatted: list[str] = [self.prefix] if self.prefix else []
        for ex in self.examples:
            tpl = self.example_prompt or BasePromptTemplate("{example}")
            formatted.append(tpl.format(**ex))
        if self.suffix:
            formatted.append(self.suffix.format(**kwargs) if isinstance(self.suffix, BasePromptTemplate) else str(self.suffix))
        return "\n".join(str(x) for x in formatted)
