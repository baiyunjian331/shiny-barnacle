import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
_default_token_path = os.path.join(os.getcwd(), "token.json")
GOOGLE_TOKEN_FILE = os.path.abspath(os.getenv("GOOGLE_TOKEN_FILE", _default_token_path))

if not all([TELEGRAM_BOT_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DRIVE_FOLDER_ID]):
    raise EnvironmentError("❌ 缺少必要的环境变量，请检查 .env 文件。")
