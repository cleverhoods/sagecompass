import os, sys

# Ensure project root.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.chain import SageCompass
from app.ui import SageCompassUI

if __name__ == "__main__":
    app = SageCompass()
    ui = SageCompassUI(app)
    ui.launch()
