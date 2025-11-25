import os, sys
from pathlib import Path
from dotenv import load_dotenv

# --- Ensure project root in sys.path ---
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# --- Load environment variables ---
base = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base.parent / ".env")

# --- Import core logic, graph picture generation and UI ---
from app.orchestrator import SageCompass
from app.ui import SageCompassUI

if __name__ == "__main__":
    app = SageCompass()
    ui = SageCompassUI(app)
    ui.launch()
