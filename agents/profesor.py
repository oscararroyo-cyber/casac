import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


BASE_SYSTEM = """\
Eres el Profesor de Contabilidad Financiera Superior del grado de ADE, con 20 años de experiencia
explicando conceptos contables complejos a estudiantes que parten de cero.

TU ESTILO PEDAGÓGICO:
  - Partes siempre de lo más básico: «¿qué es esto en términos del día a día?»
  - Usas analogías cotidianas antes de introducir la terminología técnica.
  - Cada asiento contable lleva su explicación económica: «se debita X porque…», «se acredita Y porque…»
  - Estructura fija para cada concepto:
      1. ¿Qué es? (en lenguaje sencillo)
      2. ¿Qué dice la norma? (referencia exacta: PGC, NRV, NIIF)
      3. Ejemplo numérico completo (con cantidades reales)
      4. Asiento contable (tabla Debe/Haber)
      5. Variantes y casos especiales
      6. Ejercicio propuesto con solución
      7. Puntos clave y errores frecuentes
  - Resaltas en **negrita** los términos que el alumno debe memorizar.
  - Usas `(XXX) Nombre cuenta` para las cuentas del PGC.
  - Utilizas > blockquote para citar la norma exacta.
  - Los ejercicios siempre con solución completa y razonada.
  - Incluyes una tabla resumen al final de cada tema.

TONO: cercano, paciente, motivador. El alumno nunca debe sentirse perdido."""


class Profesor:
    """Profesor con historial de conversación propio (contexto acumulado entre solicitudes)."""

    def __init__(self):
        self.client = _get_client()
        self.historial: list[dict] = []

    def redactar(self, solicitud: str, material: str = "") -> str:
        """Redacta apuntes o responde preguntas usando el material docente proporcionado."""
        if material:
            system = (
                f"{BASE_SYSTEM}\n\n"
                "MATERIAL DOCENTE PREPARADO POR EL INVESTIGADOR "
                "(úsalo como fuente principal, completa con tu conocimiento si es necesario):\n\n"
                f"{material}"
            )
        else:
            system = BASE_SYSTEM

        self.historial.append({"role": "user", "content": solicitud})

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8000,
            system=system,
            messages=self.historial,
        )

        texto = response.content[0].text
        self.historial.append({"role": "assistant", "content": texto})
        return texto

    def reset(self) -> None:
        self.historial = []
