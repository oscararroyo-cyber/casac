import json
import anthropic
from agents.investigador import buscar_contenido
from agents.profesor import Profesor

TOOLS: list[dict] = [
    {
        "name": "buscar_contenido_frances",
        "description": (
            "Encarga al Investigador que prepare material educativo de francés sobre un tema "
            "concreto. Úsalo cuando necesites contenido nuevo antes de que el Profesor imparta "
            "una lección."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tema": {
                    "type": "string",
                    "description": (
                        "Tema específico (ej.: 'presente de indicativo verbos irregulares', "
                        "'vocabulario de la alimentación', 'rédaction d'une lettre formelle')."
                    ),
                },
                "tipo": {
                    "type": "string",
                    "enum": ["vocabulario", "gramática", "expresión escrita", "expresión oral"],
                    "description": "Categoría del contenido.",
                },
                "nivel": {
                    "type": "string",
                    "enum": ["A1", "A2", "B1", "B2", "C1"],
                    "description": "Nivel MCER del estudiante.",
                },
            },
            "required": ["tema", "tipo", "nivel"],
        },
    },
    {
        "name": "ensenar_al_estudiante",
        "description": (
            "Delega al Profesor para que responda al estudiante e imparta la lección. "
            "SIEMPRE debe ser la última herramienta llamada en cada turno, ya que su salida "
            "es la respuesta que verá el estudiante."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "mensaje_estudiante": {
                    "type": "string",
                    "description": "Mensaje o pregunta exacta del estudiante.",
                },
                "directriz": {
                    "type": "string",
                    "description": (
                        "Instrucción del Catedrático al Profesor: qué aspecto enfatizar, "
                        "qué ejercicio proponer, cómo abordar la dificultad detectada, etc."
                    ),
                },
            },
            "required": ["mensaje_estudiante"],
        },
    },
]

SYSTEM_CATEDRATICO = """\
Eres el Catedrático Director de un programa intensivo de preparación al examen de francés.
Diriges un equipo de dos agentes: el Investigador (genera material) y el Profesor (imparte la clase).

ÁREAS DEL EXAMEN:
  1. Vocabulario
  2. Gramática
  3. Expresión escrita
  4. Expresión oral

TU FLUJO DE TRABAJO POR TURNO:
  a) Analiza el mensaje del estudiante y su historial de progreso.
  b) Decide si necesitas nuevo contenido → llama a `buscar_contenido_frances`.
  c) Siempre finaliza llamando a `ensenar_al_estudiante` con la directriz pedagógica adecuada.

REGLAS:
  - Nunca respondas tú directamente al estudiante; la respuesta siempre la da el Profesor.
  - Distribuye las lecciones equilibrando las cuatro áreas.
  - Si el estudiante tiene dificultades en un tema, pide al Investigador contenido adicional
    y al Profesor que refuerce con más ejercicios.
  - Ajusta el nivel y ritmo según el rendimiento percibido.
"""


class Catedratico:
    def __init__(self, nivel: str = "A2"):
        self.client = anthropic.Anthropic()
        self.nivel = nivel
        self.temas_estudiados: list[str] = []
        self.contenido_actual: str | None = None
        self.profesor = Profesor()

    def _ejecutar_herramienta(self, nombre: str, inputs: dict) -> str:
        if nombre == "buscar_contenido_frances":
            nivel = inputs.get("nivel", self.nivel)
            tema = inputs["tema"]
            tipo = inputs["tipo"]
            print(f"\n  [Investigador] Preparando {tipo} → {tema} (nivel {nivel})…")
            contenido = buscar_contenido(tema=tema, tipo=tipo, nivel=nivel)
            self.contenido_actual = contenido
            clave = f"{tipo}:{tema}"
            if clave not in self.temas_estudiados:
                self.temas_estudiados.append(clave)
            return f"Contenido listo: {tipo} sobre «{tema}» (nivel {nivel})."

        if nombre == "ensenar_al_estudiante":
            directriz = inputs.get("directriz", "")
            mensaje = inputs["mensaje_estudiante"]
            if directriz:
                mensaje_interno = f"[Directriz del Catedrático: {directriz}]\n\n{mensaje}"
            else:
                mensaje_interno = mensaje
            print("  [Profesor] Preparando respuesta…")
            return self.profesor.responder(
                mensaje_estudiante=mensaje_interno,
                contenido=self.contenido_actual,
            )

        return f"Herramienta desconocida: {nombre}"

    def orquestar(self, mensaje_usuario: str) -> str:
        """Ejecuta el agentic loop del Catedrático y devuelve la respuesta del Profesor."""
        progreso = (
            ", ".join(self.temas_estudiados) if self.temas_estudiados else "ninguno aún"
        )
        contexto = (
            f"Nivel del estudiante: {self.nivel}\n"
            f"Temas ya tratados: {progreso}\n\n"
            f"Mensaje del estudiante:\n{mensaje_usuario}"
        )

        messages: list[dict] = [{"role": "user", "content": contexto}]
        respuesta_final = ""

        while True:
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=4096,
                thinking={"type": "adaptive"},
                system=SYSTEM_CATEDRATICO,
                tools=TOOLS,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if block.type == "text":
                        respuesta_final = block.text
                break

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                resultados = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"\n[Catedrático → {block.name}]")
                        resultado = self._ejecutar_herramienta(block.name, block.input)
                        if block.name == "ensenar_al_estudiante":
                            respuesta_final = resultado
                        resultados.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": resultado,
                        })
                messages.append({"role": "user", "content": resultados})
            else:
                break

        return respuesta_final or "El sistema no pudo generar una respuesta. Inténtalo de nuevo."
