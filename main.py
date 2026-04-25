"""
Sistema de estudio de francés – punto de entrada.

Arquitectura multi-agente:
  Catedrático (claude-opus-4-7)  → orquesta con tool use
      ↓ buscar_contenido_frances
  Investigador (claude-sonnet-4-6) → genera material educativo
      ↓ ensenar_al_estudiante
  Profesor (claude-sonnet-4-6)   → imparte la clase al estudiante
"""

import sys
import io

# Windows: forzar UTF-8 para que los caracteres especiales se muestren correctamente
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

from study_session import SesionEstudio

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║           SISTEMA DE PREPARACIÓN AL EXAMEN DE FRANCÉS        ║
║                                                              ║
║   Catedrático  →  Investigador  →  Profesor  →  Tú          ║
╚══════════════════════════════════════════════════════════════╝

Áreas cubiertas:
  • Vocabulario
  • Gramática
  • Expresión escrita
  • Expresión oral

Comandos especiales:
  /temas     → ver temas estudiados en esta sesión
  /nivel     → cambiar nivel (A1‥C1)
  /salir     → terminar la sesión
"""


def pedir_nivel() -> str:
    niveles = {"A1", "A2", "B1", "B2", "C1"}
    while True:
        nivel = input("¿Cuál es tu nivel actual de francés? (A1/A2/B1/B2/C1) [A2]: ").strip().upper() or "A2"
        if nivel in niveles:
            return nivel
        print(f"  Nivel no válido. Elige entre: {', '.join(sorted(niveles))}")


def main() -> None:
    print(BANNER)
    nivel = pedir_nivel()
    sesion = SesionEstudio(nivel=nivel)

    print(f"\nSesión iniciada – nivel {nivel}.")
    print("Escribe tu primera pregunta o 'Empieza la clase' para que el Catedrático planifique.\n")
    print("─" * 64)

    while True:
        try:
            entrada = input("\nTú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nAu revoir ! Bonne chance pour ton examen ! 🇫🇷")
            sys.exit(0)

        if not entrada:
            continue

        if entrada.lower() in ("/salir", "salir", "exit", "quit"):
            print("\nAu revoir ! Bonne chance pour ton examen ! 🇫🇷")
            break

        if entrada.lower() == "/temas":
            if sesion.temas_estudiados:
                print("\nTemas estudiados en esta sesión:")
                for t in sesion.temas_estudiados:
                    print(f"  • {t}")
            else:
                print("\nTodavía no has estudiado ningún tema.")
            continue

        if entrada.lower() == "/nivel":
            nuevo = pedir_nivel()
            sesion.catedratico.nivel = nuevo
            print(f"Nivel actualizado a {nuevo}.")
            continue

        print("\n[El Catedrático está coordinando la lección…]\n")
        respuesta = sesion.enviar_mensaje(entrada)
        print(f"\nProfesor Marc:\n{respuesta}")
        print("\n" + "─" * 64)


if __name__ == "__main__":
    main()
