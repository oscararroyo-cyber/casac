from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Hola, {user.mention_html()}!\n\nSoy tu bot. Usa /help para ver los comandos disponibles."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto = (
        "Comandos disponibles:\n"
        "/start - Iniciar el bot\n"
        "/help  - Mostrar esta ayuda\n\n"
        "También puedes enviarme cualquier mensaje y te lo repetiré."
    )
    await update.message.reply_text(texto)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)
