import os
from pathlib import Path
from app.utils.event_logger import log_event

def safe_read_file(path: str) -> str:
    """Safely read a text file. Returns empty string if missing or unreadable."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            log_event("prompt.load.success", {"path": path, "length": len(content)})
            return content
    except FileNotFoundError:
        log_event("prompt.load.missing", {"path": path})
    except PermissionError:
        log_event("prompt.load.denied", {"path": path})
    except Exception as e:
        log_event("prompt.load.error", {"path": path, "error": str(e)})
    return ""

def load_prompt(prompt_file_name: str) -> str"
  """Load a prompt file."""
  content = self.safe_read_file()

def load_prompts(folder_path: str, extensions=(".prompt", ".txt")) -> dict:
    """
    Loads all prompt files in the given folder and returns {name: content}.
    Example:
        {
          "glossary": "<SYSTEM>...</SYSTEM>",
          "reasoning-flow": "<STAGE>...</STAGE>"
        }
    """
    prompts = {}
    try:
        if not os.path.exists(folder_path):
            log_event("prompt.folder.missing", {"folder_path": folder_path})
            return prompts

        for fname in sorted(os.listdir(folder_path)):
            if fname.endswith(extensions):
                name, _ = os.path.splitext(fname)
                path = os.path.join(folder_path, fname)
                content = safe_read_file(path)
                if content:
                    prompts[name] = content
                else:
                    log_event("prompt.file.unreadable", {"file": fname})

        log_event("prompt.folder.load.complete", {
            "folder": folder_path,
            "loaded": list(prompts.keys()),
            "count": len(prompts)
        })
    except Exception as e:
        log_event("prompt.folder.load.error", {"folder": folder_path, "error": str(e)})

    return prompts
