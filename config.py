import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID_STR = os.getenv("ADMIN_ID")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing in Environment Variables!")

if not ADMIN_ID_STR:
    raise ValueError("❌ ADMIN_ID is missing in Environment Variables!")

ADMIN_ID = int(ADMIN_ID_STR)

# Bot Status Config (Can be toggled via Admin Panel)
BOT_ACTIVE = True