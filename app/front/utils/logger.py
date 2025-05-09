from loguru import logger

# Configure logger to write to a file
logger.add("logs/front.log", rotation="1 MB", retention="7 days", compression="zip")

# Also log to console (real-time)
logger.add(lambda msg: print(msg, end=""))

logger.info(f"* Logging initialized → front.log")