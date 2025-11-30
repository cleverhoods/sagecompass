import json, time
from app.utils.paths import LOG_DIR

LOG_FILE = LOG_DIR / "sagecompass.log"
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
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
