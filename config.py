import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8804710278:AAH6M2IRM6Yh0_dU9bJu_iJOvU_teX6KdS4")
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "0").split(",")]
SECRET = os.environ.get("SECRET", "change-me")
APP_URL = os.environ.get("APP_URL", "http://localhost:5000")
