from loguru import logger
import os

# === LOGGING SETUP ===
# Define shared logs directory
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "shared_logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Determine which module is using this logger
LOG_FILE = os.getenv("LOG_FILE")  # Default to app.log

# Full path to the log file
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Remove default log handler
logger.remove()

# Log to file (rotates at 1MB, UTF-8 encoding)
logger.add(LOG_PATH, rotation="1 MB", encoding="utf-8")

# Also log to console (real-time)
logger.add(lambda msg: print(msg, end=""))

logger.info(f"* Logging initialized → {LOG_FILE}")