import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8819952536:AAEqtGS4OvPqU-m-fmmSPq43M76Onq8Jh6E")
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "0").split(",")]
SECRET = os.environ.get("SECRET", "change-me")
APP_URL = os.environ.get("APP_URL", "http://localhost:5000")
