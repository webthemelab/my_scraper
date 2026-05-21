# utils/logger.py
# ─────────────────────────────────────────────────────────────
# Sets up a logger that:
#   • Prints coloured output to your terminal
#   • Saves everything to logs/scraper.log
#   • Rotates to a new file every day
#   • Deletes log files older than 7 days automatically
# ─────────────────────────────────────────────────────────────

from loguru import logger
import sys

# Remove the default loguru handler so we can set our own format
logger.remove()

# 1. Print to terminal (INFO and above)
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    colorize=True,
)

# 2. Save to file (DEBUG and above — captures everything)
logger.add(
    "logs/scraper.log",
    level="DEBUG",
    rotation="1 day",       # new file every day
    retention="7 days",     # delete files older than 7 days
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
)
