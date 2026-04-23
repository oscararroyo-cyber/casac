import anthropic
from agents.investigador import buscar_contenido, estructurar_material
from agents.profesor import Profesor

TOOLS: list[dict] = [
    {
        "name": "buscar_contenido_contabilidad",
        "description": (
            "Encarga al Investigador que genere material educativo de Contabilidad Financiera "
            "sobre un tema concreto. Úsalo cuando necesites ampliar o completar el material "
            "docente antes de que el Profesor redacte los apuntes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tema": {
                    "type": "string",
                    "description": (
                        "Tema contable específico (ej.: 'inmovilizado material', "
                        "'deterioro de valor de créditos', 'operaciones de leasing', "
                        "'consolidación de estados financieros')."
                    ),
                },
                "tipo": {
                    "type": "string",
                    "enum": ["concepto", "norma", "asientos", "valoración", "ejercicios", "comparativa"],
                    "description": "Tipo de contenido a generar.",
                },
            },
            "required": ["tema", "tipo"],
        },
    },
    {
        "name": "redactar_apuntes_tema",
        "description": (
            "Delega al Profesor para que redacte apuntes claros y comprensibles del tema. "
            "SIEMPRE debe ser la última herramienta llamada en cada turno. "
            "Su salida es el documento final de apuntes que verá el alumno."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "solicitud": {
                    "type": "string",
                    "description": "Descripción de qué apuntes debe redactar el Profesor.",
                },
                "directriz": {
                    "type": "string",
                    "description": (
                        "Instrucción pedagógica del Catedrático: qué enfatizar, cómo estructurar, "
                        "qué nivel de detalle usar, qué ejercicios incluir, etc."
                    ),
                },
            },
            "required": ["solicitud"],
        },
    },
]

SYSTEM_CATEDRATICO = """\
Eres el Catedrático de Contabilidad Financiera Superior del grado de ADE.
Diriges un equipo pedagógico: el Investigador (genera y estructura material) y el Profesor (redacta apuntes).

TU MISIÓN:
  Supervisar la elaboración de apuntes claros y completos para alumnos SIN conocimientos previos
  de contabilidad, usando como base el material docente proporcionado (manual + diapositivas).

FLUJO DE TRABAJO POR TURNO:
  a) Analiza el material docente disponible y el historial del alumno.
  b) Si detectas lagunas o necesitas ampliar algún punto → llama a `buscar_contenido_contabilidad`.
  c) Siempre finaliza llamando a `redactar_apuntes_tema` con la directriz pedagógica precisa.

DIRECTRICES PEDAGÓGICAS QUE DEBES TRANSMITIR AL PROFESOR:
  - Explicar cada concepto partiendo de cero, sin asumir conocimientos previos.
  - Usar analogías del día a día para conceptos abstractos.
  - Cada asiento contable debe incluir el razonamiento económico ("¿por qué se debita X?").
  - Estructurar: concepto → norma → ejemplo numérico → asiento → variantes → ejercicio.
  - Los ejercicios siempre con solución completa paso a paso.
  - Terminar con un resumen de puntos clave y errores frecuentes.

REGLAS:
  - Nunca respondas tú directamente; la respuesta siempre la da el Profesor.
  - El documento final debe poder leerse de forma autónoma (auto-contenido).
  - Si el material docente cubre el tema, priorízalo sobre el conocimiento propio.
"""


class Catedratico:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.temas_tratados: list[str] = []
        self.material_actual: str = ""
        self.profesor = Profesor()

    def cargar_material(self, pdf_md: str = "", imagenes_md: str = "", tema: str = "") -> None:
        """Carga el material docente (PDF + imágenes) y lo estructura con el Investigador."""
        if not pdf_md and not imagenes_md:
            return
        print("  [Investigador] Estructurando material docente…")
        self.material_actual = estructurar_material(pdf_md, imagenes_md, tema)

    def _ejecutar_herramienta(self, nombre: str, inputs: dict) -> str:
        if nombre == "buscar_contenido_contabilidad":
            tema = inputs["tema"]
            tipo = inputs.get("tipo", "concepto")
            print(f"\n  [Investigador] Buscando {tipo} → {tema}…")
            contenido = buscar_contenido(tema=tema, tipo=tipo)
            if self.material_actual:
                self.material_actual += f"\n\n---\n\n## Contenido adicional: {tema}\n\n{contenido}"
            else:
                self.material_actual = contenido
            clave = f"{tipo}:{tema}"
            if clave not in self.temas_tratados:
                self.temas_tratados.append(clave)
            return f"Contenido generado: {tipo} sobre «{tema}»."

        if nombre == "redactar_apuntes_tema":
            solicitud = inputs["solicitud"]
            directriz = inputs.get("directriz", "")
            if directriz:
                mensaje_interno = f"[Directriz del Catedrático: {directriz}]\n\n{solicitud}"
            else:
                mensaje_interno = solicitud
            print("  [Profesor] Redactando apuntes…")
            return self.profesor.redactar(
                solicitud=mensaje_interno,
                material=self.material_actual,
            )

        return f"Herramienta desconocida: {nombre}"

    def orquestar(self, solicitud: str) -> str:
        """Ejecuta el agentic loop del Catedrático y devuelve los apuntes del Profesor."""
        temas_str = ", ".join(self.temas_tratados) if self.temas_tratados else "ninguno aún"
        material_str = (
            f"\n\nMATERIAL DOCENTE DISPONIBLE:\n{self.material_actual}"
            if self.material_actual
            else "\n\nNo hay material docente cargado aún."
        )

        contexto = (
            f"Temas ya tratados: {temas_str}{material_str}\n\n"
            f"Solicitud actual:\n{solicitud}"
        )

        messages: list[dict] = [{"role": "user", "content": contexto}]
        respuesta_final = ""

        while True:
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=4096,
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
                        if block.name == "redactar_apuntes_tema":
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
