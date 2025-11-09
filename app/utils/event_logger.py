# app/utils/event_logger.py
import json, time

def log_event(event: str, payload=None, agent=None, stage=None, version=None):
    """Centralized structured event logger."""
    print(json.dumps({
        "timestamp": time.time(),
        "agent": agent or "system",
        "stage": stage,
        "version": version or "n/a",
        "event": event,
        "payload": payload,
    }, ensure_ascii=False))
