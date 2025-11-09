import os, yaml
from app.utils.event_logger import log_event

def safe_read_yaml(path: str) -> dict:
    """Safely load a YAML file. Returns {} if missing or invalid."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            log_event("config.load.success", {"path": path, "keys": list(data.keys())})
            return data
    except FileNotFoundError:
        log_event("config.load.missing", {"path": path})
    except yaml.YAMLError as e:
        log_event("config.load.invalid", {"path": path, "error": str(e)})
    except Exception as e:
        log_event("config.load.error", {"path": path, "error": str(e)})
    return {}


def load_config(folder_path: str, extensions=(".yaml", ".yml")) -> dict:
    """
    Loads all YAML files in the given folder and returns {name: content}.
    Example:
        {
          "llm": { "provider": "openai", "model": "gpt-4o-mini" },
          "ui": { "theme": "dark" }
        }
    """
    configs = {}
    try:
        if not os.path.exists(folder_path):
            log_event("config.folder.missing", {"folder_path": folder_path})
            return configs

        for fname in sorted(os.listdir(folder_path)):
            if fname.endswith(extensions):
                name, _ = os.path.splitext(fname)
                path = os.path.join(folder_path, fname)
                data = safe_read_yaml(path)
                if data:
                    configs[name] = data
                else:
                    log_event("config.file.unreadable", {"file": fname})

        log_event("config.folder.load.complete", {
            "folder": folder_path,
            "loaded": list(configs.keys()),
            "count": len(configs)
        })
    except Exception as e:
        log_event("config.folder.load.error", {"folder": folder_path, "error": str(e)})

    return configs
