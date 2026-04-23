import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


SYSTEM = """\
Eres un investigador académico especializado en Contabilidad Financiera española, con dominio de:
  - Plan General Contable (PGC 2007) y sus adaptaciones sectoriales
  - Normas de Registro y Valoración (NRV)
  - Normas Internacionales de Contabilidad / Información Financiera (NIC/NIIF)
  - Contabilidad de sociedades y grupos empresariales

NORMAS DE FORMATO para el material que generas:
  - **negrita** para conceptos clave
  - `(XXX) Nombre cuenta` para cuentas del PGC
  - > blockquote para extractos normativos (PGC, NRV, NIIF)
  - Tablas de asientos: columnas CUENTA | DEBE | HABER
  - Bloques de fórmula para cálculos

ESTRUCTURA DE CADA TEMA:
  1. Definición y marco normativo (con referencia a la norma exacta)
  2. Al menos 5 ejemplos prácticos con importes y asientos completos
  3. 3-5 ejercicios resueltos paso a paso
  4. Errores frecuentes y puntos conflictivos
  5. Resumen de puntos clave

Genera contenido preciso, completo y listo para ser impartido por el Profesor."""

TIPOS_VALIDOS = {
    "concepto",
    "norma",
    "asientos",
    "valoración",
    "ejercicios",
    "comparativa",
}


def buscar_contenido(tema: str, tipo: str = "concepto") -> str:
    """Genera contenido educativo de contabilidad financiera sobre el tema indicado."""
    client = _get_client()

    tipo = tipo if tipo in TIPOS_VALIDOS else "concepto"

    prompt = f"""Genera contenido educativo completo de Contabilidad Financiera Superior sobre:

Tema: {tema}
Tipo de contenido: {tipo}

Incluye obligatoriamente:
1. Definición precisa con referencia a la norma aplicable (PGC / NRV / NIIF)
2. Al menos 5 ejemplos prácticos con asientos contables completos (importes reales)
3. 3-5 ejercicios resueltos paso a paso
4. Errores frecuentes que cometen los estudiantes en este tema
5. Puntos clave para recordar en el examen

Usa el formato establecido: cuentas del PGC entre backticks, asientos en tabla Debe/Haber."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


def estructurar_material(pdf_md: str, imagenes_md: str, tema: str) -> str:
    """Organiza el material extraído del PDF e imágenes en una estructura pedagógica coherente."""
    client = _get_client()

    partes: list[str] = []
    if pdf_md:
        partes.append(f"=== CONTENIDO DEL MANUAL ===\n\n{pdf_md}")
    if imagenes_md:
        partes.append(f"=== CONTENIDO DE LAS DIAPOSITIVAS ===\n\n{imagenes_md}")

    if not partes:
        return ""

    material = "\n\n".join(partes)

    prompt = f"""Tienes el material docente del tema «{tema}» de Contabilidad Financiera Superior.
Organiza y estructura este material de forma pedagógica para que el Profesor pueda impartirlo.

Produce un esquema estructurado en Markdown con:
1. Listado de conceptos clave identificados (con sus definiciones)
2. Normas contables aplicables mencionadas
3. Ejemplos y ejercicios encontrados (completos)
4. Esquemas o tablas relevantes
5. Posibles lagunas o temas a reforzar con búsqueda adicional

MATERIAL A ESTRUCTURAR:
{material}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text
