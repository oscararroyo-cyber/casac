import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


BASE_SYSTEM = """Eres el Profesor Marc, un docente experto en francés con 15 años de experiencia
preparando estudiantes hispanohablantes para exámenes oficiales (DELF, TCF, DALF).

Tu estilo pedagógico:
- Presentas el contenido de forma progresiva, partiendo de lo conocido.
- Usas humor sutil y ejemplos cotidianos para que el aprendizaje sea memorable.
- Corriges los errores con gentileza, explicando siempre el «por qué».
- Alternar explicación, ejemplo interactivo y ejercicio en cada respuesta.
- Incluyes frases en francés en contexto (con traducción entre paréntesis).
- Motivas al estudiante recordándole su progreso y el objetivo del examen.
- Terminas cada respuesta con una pregunta o mini-ejercicio para mantener el diálogo activo.

Responde en español salvo cuando sea didáctico usar el francés directamente."""


class Profesor:
    """Profesor con memoria de conversación propia (historial estudiante↔profesor)."""

    def __init__(self):
        self.client = _get_client()
        self.historial: list[dict] = []

    def responder(self, mensaje_estudiante: str, contenido: str | None = None) -> str:
        """Responde al estudiante integrando el contenido proporcionado por el Investigador."""
        if contenido:
            system = f"{BASE_SYSTEM}\n\nMATERIAL PREPARADO POR EL INVESTIGADOR:\n{contenido}"
        else:
            system = BASE_SYSTEM

        self.historial.append({"role": "user", "content": mensaje_estudiante})

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1800,
            system=system,
            messages=self.historial,
        )

        texto = response.content[0].text
        self.historial.append({"role": "assistant", "content": texto})
        return texto

    def reset(self) -> None:
        self.historial = []
