import json, time, os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "sagecompass.log")

def log(event, payload=None, agent="system", stage=None, version="n/a"):
    entry = {
        "timestamp": time.time(),
        "event": event,
        "payload": payload or {},
        "agent": agent,
        "stage": stage,
        "version": version,
    }
    line = json.dumps(entry, ensure_ascii=False)
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
