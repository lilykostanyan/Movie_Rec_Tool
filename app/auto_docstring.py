import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get excluded directories from environment variable
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in os.getenv("EXCLUDE_DIRS") and not d.startswith(".")]
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            print(f"📄 Formatting: {path}")
            subprocess.run(
                ["pyment", "-w", "-o", "google", path],
                env={**os.environ, "PYTHONIOENCODING": "utf-8"}
            )