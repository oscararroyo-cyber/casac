from agents.catedratico import Catedratico


class SesionEstudio:
    """Fachada que expone una interfaz simple: enviar_mensaje → respuesta del Profesor."""

    def __init__(self, nivel: str = "A2"):
        self.catedratico = Catedratico(nivel=nivel)

    @property
    def nivel(self) -> str:
        return self.catedratico.nivel

    @property
    def temas_estudiados(self) -> list[str]:
        return self.catedratico.temas_estudiados

    def enviar_mensaje(self, mensaje: str) -> str:
        return self.catedratico.orquestar(mensaje)
