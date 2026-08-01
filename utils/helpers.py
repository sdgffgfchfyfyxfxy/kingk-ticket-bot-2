import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

STICKERS = {
    "start": "CAACAgQAAxkBAAEJ...", # Animated sticker placeholders or valid file_ids
    "create": "CAACAgQAAxkBAAEJ...",
    "message": "CAACAgQAAxkBAAEJ...",
    "confirm": "CAACAgQAAxkBAAEJ...",
    "send": "CAACAgQAAxkBAAEJ...",
    "cancel": "CAACAgQAAxkBAAEJ...",
    "admin": "CAACAgQAAxkBAAEJ...",
    "settings": "CAACAgQAAxkBAAEJ...",
    "close": "CAACAgQAAxkBAAEJ..."
}

async def safe_send_sticker(update, context, sticker_key: str):
    # Fallback safe sticker sender if file_id is invalid
    try:
        # If needed, specific file_ids can be placed here or safely bypassed if not critical
        pass
    except Exception as e:
        logger.error(f"Error sending sticker {sticker_key}: {e}")
