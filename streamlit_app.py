import os
import sys
from pathlib import Path

# Add the current directory to sys.path so 'app' can be imported
root_path = str(Path(__file__).parent)
if root_path not in sys.path:
    sys.path.append(root_path)

# Import the dashboard
from app.frontend.dashboard import main

if __name__ == "__main__":
    main()
