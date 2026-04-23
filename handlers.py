import io
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from study_session import SesionContabilidad

# Sesiones por usuario (chat_id → SesionContabilidad)
_sesiones: dict[int, SesionContabilidad] = {}
# Tema activo por usuario (mientras esperamos material o preguntas)
_temas: dict[int, str] = {}


def _get_sesion(chat_id: int) -> SesionContabilidad:
    if chat_id not in _sesiones:
        _sesiones[chat_id] = SesionContabilidad()
    return _sesiones[chat_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Hola, {user.mention_html()}!\n\n"
        "Soy tu asistente de <b>Contabilidad Financiera Superior</b>.\n\n"
        "Puedes:\n"
        "• Enviarme un <b>PDF</b> del manual → lo convierto a apuntes\n"
        "• Enviarme <b>imágenes</b> de las diapositivas → las proceso\n"
        "• Escribirme cualquier pregunta sobre contabilidad\n\n"
        "Usa /help para ver todos los comandos."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto = (
        "Comandos disponibles:\n"
        "/start        — Iniciar el bot\n"
        "/help         — Mostrar esta ayuda\n"
        "/tema NOMBRE  — Establecer el tema activo (ej: /tema Leasing)\n"
        "/temas        — Ver temas tratados en esta sesión\n"
        "/nuevo        — Empezar una sesión nueva\n\n"
        "También puedes:\n"
        "• Enviar un PDF → se convierte y el Profesor redacta apuntes\n"
        "• Enviar imágenes → se extraen y añaden al contexto\n"
        "• Escribir cualquier pregunta de contabilidad\n"
    )
    await update.message.reply_text(texto)


async def tema_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args
    if not args:
        tema_actual = _temas.get(chat_id, "no establecido")
        await update.message.reply_text(f"Tema activo: {tema_actual}\nUsa /tema NOMBRE para cambiarlo.")
        return
    nuevo_tema = " ".join(args)
    _temas[chat_id] = nuevo_tema
    await update.message.reply_text(f"Tema establecido: «{nuevo_tema}»")


async def temas_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    sesion = _get_sesion(chat_id)
    if sesion.temas_tratados:
        lista = "\n".join(f"  • {t}" for t in sesion.temas_tratados)
        await update.message.reply_text(f"Temas tratados:\n{lista}")
    else:
        await update.message.reply_text("Todavía no se ha tratado ningún tema en esta sesión.")


async def nuevo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    _sesiones[chat_id] = SesionContabilidad()
    _temas.pop(chat_id, None)
    await update.message.reply_text("Sesión reiniciada. ¿Qué tema quieres estudiar?")


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa PDFs enviados por el usuario."""
    doc = update.message.document
    if not doc.mime_type == "application/pdf":
        await update.message.reply_text("Solo proceso PDFs. Para imágenes, envíalas como foto.")
        return

    chat_id = update.effective_chat.id
    tema = _temas.get(chat_id, doc.file_name.replace(".pdf", ""))

    await update.message.reply_text(
        f"Recibido PDF: {doc.file_name}\nTema: «{tema}»\n\n"
        "Extrayendo contenido y generando apuntes… (puede tardar 1-2 minutos)"
    )

    try:
        from agents.convertidor import convertir_pdf

        # Descargar el PDF a un archivo temporal
        tg_file = await context.bot.get_file(doc.file_id)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            await tg_file.download_to_drive(tmp.name)
            tmp_path = Path(tmp.name)

        pdf_md = convertir_pdf(tmp_path, titulo=tema)
        tmp_path.unlink(missing_ok=True)

        sesion = _get_sesion(chat_id)
        sesion.cargar_material(pdf_md=pdf_md, tema=tema)

        respuesta = sesion.enviar_mensaje(
            f"Acabo de subir el manual del tema «{tema}». "
            "Redacta los apuntes completos basándote en ese material."
        )

        # Telegram limita a 4096 caracteres por mensaje
        for chunk in _dividir_texto(respuesta, 4000):
            await update.message.reply_text(chunk, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"Error al procesar el PDF: {e}")


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa imágenes (diapositivas) enviadas por el usuario."""
    chat_id = update.effective_chat.id
    tema = _temas.get(chat_id, "")

    await update.message.reply_text("Procesando imagen de diapositiva…")

    try:
        from agents.convertidor import convertir_imagen

        foto = update.message.photo[-1]  # mayor resolución disponible
        tg_file = await context.bot.get_file(foto.file_id)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            await tg_file.download_to_drive(tmp.name)
            tmp_path = Path(tmp.name)

        imagen_md = convertir_imagen(tmp_path, contexto=tema)
        tmp_path.unlink(missing_ok=True)

        sesion = _get_sesion(chat_id)
        sesion.cargar_material(imagenes_md=imagen_md, tema=tema)

        respuesta = sesion.enviar_mensaje(
            "He subido una diapositiva de la presentación. "
            "Incorpora su contenido a los apuntes y explica lo más relevante."
        )

        for chunk in _dividir_texto(respuesta, 4000):
            await update.message.reply_text(chunk, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"Error al procesar la imagen: {e}")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde preguntas de texto libre sobre contabilidad."""
    chat_id = update.effective_chat.id
    sesion = _get_sesion(chat_id)

    await update.message.reply_text("El Catedrático está coordinando la respuesta…")

    try:
        respuesta = sesion.enviar_mensaje(update.message.text)
        for chunk in _dividir_texto(respuesta, 4000):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error al generar la respuesta: {e}")


def _dividir_texto(texto: str, max_chars: int) -> list[str]:
    """Divide un texto largo en fragmentos respetando los límites de Telegram."""
    if len(texto) <= max_chars:
        return [texto]
    fragmentos = []
    while texto:
        if len(texto) <= max_chars:
            fragmentos.append(texto)
            break
        corte = texto.rfind("\n", 0, max_chars)
        if corte == -1:
            corte = max_chars
        fragmentos.append(texto[:corte])
        texto = texto[corte:].lstrip("\n")
    return fragmentos
