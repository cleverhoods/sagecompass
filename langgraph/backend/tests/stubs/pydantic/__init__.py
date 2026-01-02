"""Lightweight pydantic stubs for offline testing.

These stubs only implement the minimal surface needed by the tests and
application helpers in this repository. They are **not** feature-complete.
"""

from __future__ import annotations

from typing import Any, Callable, Dict


class ValidationError(Exception):
    """Stub validation error."""


class _FieldSpec:
    def __init__(self, default: Any = ..., default_factory: Callable[[], Any] | None = None) -> None:
        self.default = default
        self.default_factory = default_factory


def Field(default: Any = ..., *, default_factory: Callable[[], Any] | None = None, **_: Any) -> Any:
    """Return a placeholder used to declare model fields."""
    return _FieldSpec(default=default, default_factory=default_factory)


class _PrivateAttrSpec:
    def __init__(self, default: Any = None, default_factory: Callable[[], Any] | None = None) -> None:
        self.default = default
        self.default_factory = default_factory


def PrivateAttr(default: Any = None, default_factory: Callable[[], Any] | None = None) -> Any:
    """Stub for pydantic PrivateAttr used to hold internal data."""
    return _PrivateAttrSpec(default=default, default_factory=default_factory)


class BaseModel:
    """Minimal BaseModel compatible with the expectations in tests."""

    def __init__(self, **data: Any) -> None:
        # Populate defaults declared via Field(...)
        for name, spec in self.__class__.__dict__.items():
            if isinstance(spec, _FieldSpec):
                if spec.default_factory is not None:
                    value = spec.default_factory()
                elif spec.default is not ...:
                    value = spec.default
                else:
                    value = None
                setattr(self, name, value)
            elif isinstance(spec, _PrivateAttrSpec):
                if spec.default_factory is not None:
                    value = spec.default_factory()
                else:
                    value = spec.default
                setattr(self, name, value)

        self.__dict__.update(data)

    @classmethod
    def model_validate(cls, value: Any) -> "BaseModel":
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls(**value)
        raise ValidationError(f"Cannot validate value of type {type(value)!r}")

    def model_dump(self) -> Dict[str, Any]:
        return dict(self.__dict__)

    def model_copy(self, *, update: Dict[str, Any] | None = None) -> "BaseModel":
        data = self.model_dump()
        if update:
            data.update(update)
        return self.__class__(**data)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        args = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({args})"
