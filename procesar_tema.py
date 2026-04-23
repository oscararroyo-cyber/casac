"""
Convierte un manual PDF + diapositivas de presentación en apuntes Markdown completos.

Uso:
  python procesar_tema.py --tema "Inmovilizado Material" --pdf manual.pdf --imagenes slides/
  python procesar_tema.py --tema "Existencias" --pdf manual.pdf
  python procesar_tema.py --tema "Leasing" --imagenes slides/ --ejercicios ejercicios.pdf
  python procesar_tema.py --tema "Provisiones" --pdf manual.pdf --output mis_apuntes.md

Arquitectura multi-agente:
  Convertidor  →  Catedrático  →  Investigador  →  Profesor  →  apuntes.md
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


def _cabecera(tema: str) -> str:
    fecha = datetime.now().strftime("%d/%m/%Y")
    return (
        f"# Apuntes: {tema}\n\n"
        f"> **Contabilidad Financiera Superior — ADE**  \n"
        f"> Generado el {fecha} mediante sistema multi-agente (Catedrático → Investigador → Profesor)\n\n"
        "---\n\n"
    )


def procesar(
    tema: str,
    ruta_pdf: str | None = None,
    directorio_imagenes: str | None = None,
    ruta_ejercicios: str | None = None,
    ruta_salida: str | None = None,
) -> str:
    """Pipeline completo: materiales → apuntes Markdown."""
    from agents.convertidor import convertir_pdf, convertir_directorio_imagenes
    from agents.catedratico import Catedratico

    pdf_md = ""
    imagenes_md = ""
    ejercicios_md = ""

    # 1. Convertir el PDF del manual
    if ruta_pdf:
        ruta = Path(ruta_pdf)
        if not ruta.exists():
            print(f"[ERROR] No se encuentra el PDF: {ruta}", file=sys.stderr)
            sys.exit(1)
        print(f"\n[1/4] Extrayendo contenido del manual: {ruta.name}")
        pdf_md = convertir_pdf(ruta, titulo=tema)
        print(f"      Listo ({len(pdf_md):,} caracteres extraídos).")

    # 2. Convertir las imágenes de la presentación
    if directorio_imagenes:
        dir_path = Path(directorio_imagenes)
        if not dir_path.is_dir():
            print(f"[ERROR] No es un directorio válido: {dir_path}", file=sys.stderr)
            sys.exit(1)
        print(f"\n[2/4] Procesando diapositivas en: {dir_path}/")
        imagenes_md = convertir_directorio_imagenes(dir_path, contexto=tema)
        if imagenes_md:
            print(f"      Listo ({len(imagenes_md):,} caracteres extraídos).")
        else:
            print("      No se encontraron imágenes compatibles (jpg, jpeg, png, gif, webp).")

    # 3. Convertir ejercicios (si se proporcionan en PDF separado)
    if ruta_ejercicios:
        ruta_ej = Path(ruta_ejercicios)
        if ruta_ej.exists():
            print(f"\n[3/4] Extrayendo ejercicios de: {ruta_ej.name}")
            ejercicios_md = convertir_pdf(ruta_ej, titulo=f"Ejercicios — {tema}")
            print(f"      Listo ({len(ejercicios_md):,} caracteres extraídos).")
        else:
            print(f"[AVISO] No se encuentra el PDF de ejercicios: {ruta_ej}", file=sys.stderr)
    else:
        print("\n[3/4] Sin PDF de ejercicios (se generarán desde el material disponible).")

    if not pdf_md and not imagenes_md:
        print(
            "[ERROR] Debes proporcionar al menos un PDF (--pdf) o imágenes (--imagenes).",
            file=sys.stderr,
        )
        sys.exit(1)

    # 4. Orquestar Catedrático → Investigador → Profesor
    print(f"\n[4/4] Generando apuntes con el sistema multi-agente para «{tema}»…")
    catedratico = Catedratico()

    material_completo_pdf = pdf_md
    if ejercicios_md:
        material_completo_pdf += f"\n\n---\n\n## Ejercicios del Tema\n\n{ejercicios_md}"

    catedratico.cargar_material(
        pdf_md=material_completo_pdf,
        imagenes_md=imagenes_md,
        tema=tema,
    )

    solicitud = (
        f"Redacta unos apuntes completos y muy claros del tema «{tema}» de "
        "Contabilidad Financiera Superior para un alumno que nunca ha estudiado contabilidad. "
        "Usa el material docente disponible (manual + diapositivas) como base principal. "
        "El documento final debe ser auto-contenido: definiciones, normas, ejemplos con "
        "asientos contables completos, ejercicios resueltos y puntos clave."
    )

    apuntes = catedratico.orquestar(solicitud)

    # 5. Guardar el resultado
    salida = Path(ruta_salida) if ruta_salida else Path(f"apuntes_{tema.replace(' ', '_').lower()}.md")
    contenido_final = _cabecera(tema) + apuntes
    salida.write_text(contenido_final, encoding="utf-8")

    print(f"\n✓ Apuntes guardados en: {salida.resolve()}")
    print(f"  Total: {len(contenido_final):,} caracteres")

    return contenido_final


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera apuntes de Contabilidad Financiera desde PDF + imágenes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--tema", required=True, help="Nombre del tema contable")
    parser.add_argument("--pdf", metavar="ARCHIVO.pdf", help="PDF del manual del tema")
    parser.add_argument("--imagenes", metavar="DIRECTORIO/", help="Directorio con diapositivas")
    parser.add_argument("--ejercicios", metavar="EJERCICIOS.pdf", help="PDF con ejercicios (opcional)")
    parser.add_argument("--output", metavar="APUNTES.md", help="Archivo de salida (por defecto: apuntes_<tema>.md)")

    args = parser.parse_args()

    if not args.pdf and not args.imagenes:
        parser.error("Debes indicar al menos --pdf o --imagenes (o ambos).")

    procesar(
        tema=args.tema,
        ruta_pdf=args.pdf,
        directorio_imagenes=args.imagenes,
        ruta_ejercicios=args.ejercicios,
        ruta_salida=args.output,
    )


if __name__ == "__main__":
    main()
