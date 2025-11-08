import os

def safe_read_file(path: str) -> str:
    """Safely read a text file. Returns empty string if missing or unreadable."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"[WARN] File not found: {path}")
    except Exception as e:
        print(f"[ERROR] Failed to read {path}: {e}")
    return ""


def load_prompts(folder_path: str, extensions=(".prompt", ".txt")) -> dict:
    """
    Loads all prompt files in the given folder and returns a dict of {name: content}.

    Example output:
        {
          "glossary": "<SYSTEM>...</SYSTEM>",
          "reasoning-flow": "<STAGE>...</STAGE>",
        }
    """
    prompts = {}

    if not os.path.exists(folder_path):
        print(f"[WARN] Folder not found: {folder_path}")
        return prompts

    for fname in sorted(os.listdir(folder_path)):
        if fname.endswith(extensions):
            name, _ = os.path.splitext(fname)
            path = os.path.join(folder_path, fname)
            content = safe_read_file(path)
            if content:
                prompts[name] = content
            else:
                print(f"[WARN] Empty or unreadable: {fname}")

    return prompts
