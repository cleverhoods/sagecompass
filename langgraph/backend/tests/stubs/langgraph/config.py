from __future__ import annotations


class _NullStore:
    def get(self, *_args, **_kwargs):
        return None


def get_store() -> _NullStore:
    """
    Minimal stub for langgraph.config.get_store used in offline test lane.
    """
    return _NullStore()
