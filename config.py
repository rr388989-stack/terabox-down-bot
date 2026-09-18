import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables fetch kar rahe hain aur integer casting ensure kar rahe hain
try:
    API_ID = int(os.getenv("API_ID", "0"))
except ValueError:
    logger.error("API_ID must be a valid integer number!")
    API_ID = 0

API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Optional: Terabox API cookies ya tokens agar use karne ho
TERABOX_COOKIE = os.getenv("COOKIE", "")
