import os
import yaml

def safe_read_yaml(path: str) -> dict:
    """Safely load a YAML file. Returns {} if missing or invalid."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"[WARN] Config file not found: {path}")
    except yaml.YAMLError as e:
        print(f"[ERROR] Invalid YAML format in {path}: {e}")
    except Exception as e:
        print(f"[ERROR] Failed to read {path}: {e}")
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

    if not os.path.exists(folder_path):
        print(f"[WARN] Config folder not found: {folder_path}")
        return configs

    for fname in sorted(os.listdir(folder_path)):
        if fname.endswith(extensions):
            name, _ = os.path.splitext(fname)
            path = os.path.join(folder_path, fname)
            data = safe_read_yaml(path)
            if data:
                configs[name] = data
            else:
                print(f"[WARN] Empty or unreadable config: {fname}")

    return configs
