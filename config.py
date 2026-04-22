import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# BOT_TOKEN sólo se valida al arrancar el bot de Telegram (bot.py), no aquí.
# ANTHROPIC_API_KEY es leído directamente por el SDK de Anthropic desde el entorno.
