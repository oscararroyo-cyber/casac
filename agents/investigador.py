import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


SYSTEM = """Eres un investigador académico especializado en lingüística francesa y didáctica
del francés como lengua extranjera (FLE). Tu misión es generar material educativo estructurado,
preciso y pedagógicamente apropiado.

Normas de formato:
- Vocabulario: palabra + fonética IPA + clase gramatical + traducción + ejemplo bilingüe.
- Gramática: regla clara → ejemplos positivos → excepciones → errores frecuentes.
- Expresión escrita: estructura del texto → conectores → modelo → consignas de práctica.
- Expresión oral: frases clave → pronunciación → patrones de conversación → ejercicios de repetición.

Devuelve siempre: explicación teórica, 5+ ejemplos, 3-5 ejercicios resueltos y puntos clave."""


def buscar_contenido(tema: str, tipo: str, nivel: str = "A2") -> str:
    """Investigador: genera contenido educativo de francés listo para que el Profesor lo imparta."""
    client = _get_client()

    prompt = f"""Genera contenido educativo completo sobre:
Tipo: {tipo}
Tema: {tema}
Nivel MCER: {nivel}

Incluye:
1. Explicación teórica clara y concisa
2. Al menos 5 ejemplos prácticos con traducción
3. 3-5 ejercicios de práctica (incluye las soluciones)
4. Puntos clave para recordar
5. Errores comunes que cometen los hispanohablantes en este tema"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text
