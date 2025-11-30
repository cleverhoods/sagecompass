import sys
from dotenv import load_dotenv
from app.utils.paths import PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# --- Import core logic, graph picture generation and UI ---
from app.runtime.orchestrator import SageCompass
from app.runtime.ui import SageCompassUI

if __name__ == "__main__":
    app = SageCompass()
    ui = SageCompassUI(app)
    ui.launch()
