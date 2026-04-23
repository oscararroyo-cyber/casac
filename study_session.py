from agents.catedratico import Catedratico


class SesionContabilidad:
    """Fachada que expone una interfaz simple para la sesión de contabilidad."""

    def __init__(self):
        self.catedratico = Catedratico()

    @property
    def temas_tratados(self) -> list[str]:
        return self.catedratico.temas_tratados

    def cargar_material(self, pdf_md: str = "", imagenes_md: str = "", tema: str = "") -> None:
        self.catedratico.cargar_material(pdf_md=pdf_md, imagenes_md=imagenes_md, tema=tema)

    def enviar_mensaje(self, mensaje: str) -> str:
        return self.catedratico.orquestar(mensaje)
