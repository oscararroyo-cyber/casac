import tempfile
import os
from markitdown import MarkItDown
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
        "También puedes enviarme un PDF y te lo convierto a Markdown.\n"
        "También puedes enviarme cualquier mensaje y te lo repetiré."
    )
    await update.message.reply_text(texto)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


async def pdf_a_markdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    documento = update.message.document
    if documento.mime_type != "application/pdf":
        await update.message.reply_text("Solo acepto archivos PDF.")
        return

    await update.message.reply_text("Convirtiendo PDF a Markdown...")

    archivo = await documento.get_file()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        ruta_tmp = tmp.name

    try:
        await archivo.download_to_drive(ruta_tmp)
        md = MarkItDown()
        resultado = md.convert(ruta_tmp)
        texto_md = resultado.text_content

        if len(texto_md) > 4096:
            nombre_md = documento.file_name.replace(".pdf", ".md")
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            ) as f_md:
                f_md.write(texto_md)
                ruta_md = f_md.name
            try:
                await update.message.reply_document(
                    document=open(ruta_md, "rb"),
                    filename=nombre_md,
                    caption="Aquí tienes el Markdown generado.",
                )
            finally:
                os.unlink(ruta_md)
        else:
            await update.message.reply_text(f"```\n{texto_md}\n```", parse_mode="Markdown")
    finally:
        os.unlink(ruta_tmp)
