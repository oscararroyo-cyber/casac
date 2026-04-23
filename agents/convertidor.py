import base64
import anthropic
from pathlib import Path

EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

SYSTEM_EXTRACTOR = """\
Eres un experto en extracción y estructuración de contenido académico de Contabilidad Financiera.

Convierte el material proporcionado en Markdown estructurado siguiendo estas normas:

JERARQUÍA:
  # Título principal
  ## Capítulo / Bloque temático
  ### Sección
  #### Subsección

FORMATO:
  - **negrita** para términos técnicos y conceptos clave
  - `(XXX) Nombre cuenta` para cuentas del PGC (siempre con número y nombre)
  - > blockquote para definiciones normativas (PGC, NRV, NIIF/NIC)
  - Bloques de cálculo para fórmulas matemáticas

ASIENTOS CONTABLES (formato obligatorio):
  | Cuenta | Debe | Haber |
  |--------|------|-------|
  | `(XXX) Nombre` | importe | |
  | `(XXX) Nombre` | | importe |

CONTENIDO A PRESERVAR:
  Todas las definiciones, normas, ejemplos numéricos, tablas, esquemas y fórmulas.
  No omitas nada relevante aunque parezca redundante.

Responde ÚNICAMENTE con el Markdown resultante, sin texto introductorio ni explicaciones."""


def _cliente() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def convertir_pdf(ruta: str | Path, titulo: str = "") -> str:
    """Extrae y estructura en Markdown el contenido de un PDF académico."""
    ruta = Path(ruta)
    datos = base64.standard_b64encode(ruta.read_bytes()).decode()

    nota = f" titulado «{titulo}»" if titulo else ""
    prompt = (
        f"Extrae y estructura en Markdown todo el contenido de este documento académico{nota}. "
        "Preserva definiciones, normas contables (PGC/NRV/NIIF), fórmulas, tablas y ejemplos numéricos."
    )

    resp = _cliente().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=SYSTEM_EXTRACTOR,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": datos,
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return resp.content[0].text


def convertir_imagen(ruta: str | Path, numero: int = 0, contexto: str = "") -> str:
    """Extrae el contenido de una diapositiva o imagen a Markdown."""
    ruta = Path(ruta)
    media_type = MEDIA_TYPES.get(ruta.suffix.lower(), "image/jpeg")
    datos = base64.standard_b64encode(ruta.read_bytes()).decode()

    num_str = f" (diapositiva {numero})" if numero else ""
    ctx_str = f"\nContexto del tema: {contexto}" if contexto else ""

    prompt = (
        f"Esta es una diapositiva de Contabilidad Financiera Superior{num_str}.{ctx_str}\n"
        "Extrae en Markdown todo el contenido visible: textos, tablas, fórmulas, "
        "esquemas, asientos contables y cualquier dato numérico."
    )

    resp = _cliente().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_EXTRACTOR,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": datos,
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return resp.content[0].text


def convertir_directorio_imagenes(
    directorio: str | Path,
    contexto: str = "",
    patron: str = "*",
) -> str:
    """Convierte todas las imágenes de un directorio a un único bloque Markdown."""
    dir_path = Path(directorio)
    imagenes = sorted(
        f for f in dir_path.glob(patron)
        if f.suffix.lower() in EXTENSIONES_IMAGEN
    )

    if not imagenes:
        return ""

    secciones: list[str] = []
    for i, img in enumerate(imagenes, 1):
        print(f"  [{i}/{len(imagenes)}] {img.name}")
        md = convertir_imagen(img, numero=i, contexto=contexto)
        secciones.append(f"### Diapositiva {i} — `{img.name}`\n\n{md}")

    return "\n\n---\n\n".join(secciones)
