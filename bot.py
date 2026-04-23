import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers import (
    start,
    help_command,
    tema_command,
    temas_command,
    nuevo_command,
    document_handler,
    photo_handler,
    message_handler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tema", tema_command))
    app.add_handler(CommandHandler("temas", temas_command))
    app.add_handler(CommandHandler("nuevo", nuevo_command))

    # Documentos PDF
    app.add_handler(MessageHandler(filters.Document.PDF, document_handler))
    # Fotos / diapositivas
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    # Texto libre
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("Bot de Contabilidad Financiera iniciado. Presiona Ctrl+C para detener.")
    app.run_polling()


if __name__ == "__main__":
    main()
