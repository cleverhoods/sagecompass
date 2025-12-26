from __future__ import annotations

from types import SimpleNamespace
from typing import Any, List, Optional, Tuple


class Update(SimpleNamespace):
    """
    Lightweight stand-in for gradio.Update.
    Stores whatever kwargs are provided so tests can inspect visibility/values.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        # mirror common attributes
        self.visible = kwargs.get("visible")
        self.value = kwargs.get("value")
        self.choices = kwargs.get("choices")


def update(**kwargs: Any) -> Update:
    return Update(**kwargs)


class Blocks:
    def __init__(self, *args: Any, **kwargs: Any):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc: Any):
        return False

    def launch(self, *args: Any, **kwargs: Any):
        return None


class Markdown:
    def __init__(self, value: str | None = None, visible: bool | None = None, *args: Any, **kwargs: Any):
        self.value = value
        self.visible = visible


class Chatbot:
    def __init__(self, *args: Any, **kwargs: Any):
        self.visible = kwargs.get("visible", None)
        self.label = kwargs.get("label", None)
        self.height = kwargs.get("height", None)


class State:
    def __init__(self, value: Any = None):
        self.value = value


class Textbox:
    def __init__(self, *args: Any, **kwargs: Any):
        self.visible = kwargs.get("visible", None)
        self.value = kwargs.get("value", None)
        self.label = kwargs.get("label", None)


class Button:
    def __init__(self, *args: Any, **kwargs: Any):
        self.visible = kwargs.get("visible", None)
        self.value = kwargs.get("value", None)
        self.variant = kwargs.get("variant", None)

    def click(self, *args: Any, **kwargs: Any):
        return None


class Dropdown:
    def __init__(self, *args: Any, **kwargs: Any):
        self.visible = kwargs.get("visible", None)
        self.choices = kwargs.get("choices", [])
        self.value = kwargs.get("value", None)

    def click(self, *args: Any, **kwargs: Any):
        return None
