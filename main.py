"""
Sistema de apuntes de Contabilidad Financiera Superior — modo interactivo.

Para procesar un PDF o imágenes directamente usa:
  python procesar_tema.py --tema "Nombre" --pdf manual.pdf --imagenes slides/

Arquitectura multi-agente:
  Catedrático (claude-opus-4-7)    → orquesta con tool use
      ↓ buscar_contenido_contabilidad
  Investigador (claude-sonnet-4-6) → genera material educativo
      ↓ redactar_apuntes_tema
  Profesor (claude-sonnet-4-6)     → redacta apuntes para el alumno
"""

import sys
from study_session import SesionContabilidad

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║     SISTEMA DE APUNTES — CONTABILIDAD FINANCIERA SUPERIOR        ║
║                                                                  ║
║   Catedrático  →  Investigador  →  Profesor  →  Tú              ║
╚══════════════════════════════════════════════════════════════════╝

Puedes preguntar sobre cualquier tema de Contabilidad Financiera:
  • Inmovilizado material e intangible         • Leasing y arrendamientos
  • Existencias y deterioro de valor           • Instrumentos financieros
  • Provisiones y pasivos contingentes         • Impuesto sobre beneficios
  • Subvenciones                               • Consolidación de CCFF

Comandos especiales:
  /temas     → ver temas tratados en esta sesión
  /nuevo     → limpiar historial y empezar un tema nuevo
  /salir     → terminar la sesión
"""


def main() -> None:
    print(BANNER)
    sesion = SesionContabilidad()

    print("Escribe tu pregunta o el tema que quieres estudiar y el Profesor te explicará.\n")
    print("─" * 66)

    while True:
        try:
            entrada = input("\nTú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n¡Hasta la próxima! Mucho éxito en el estudio.")
            sys.exit(0)

        if not entrada:
            continue

        if entrada.lower() in ("/salir", "salir", "exit", "quit"):
            print("\n¡Hasta la próxima! Mucho éxito en el estudio.")
            break

        if entrada.lower() == "/temas":
            if sesion.temas_tratados:
                print("\nTemas tratados en esta sesión:")
                for t in sesion.temas_tratados:
                    print(f"  • {t}")
            else:
                print("\nTodavía no se ha tratado ningún tema.")
            continue

        if entrada.lower() == "/nuevo":
            sesion = SesionContabilidad()
            print("Sesión reiniciada.")
            continue

        print("\n[El Catedrático está coordinando la respuesta…]\n")
        respuesta = sesion.enviar_mensaje(entrada)
        print(f"\nProfesor:\n{respuesta}")
        print("\n" + "─" * 66)


if __name__ == "__main__":
    main()
