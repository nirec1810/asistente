import logging

from asistente.audio import hablar, escuchar, esperar_wake_word
from asistente.utilidades import obtener_saludo
from asistente.comandos import procesar_comando
from asistente.config import NOMBRE_ASISTENTE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def iniciar():
    while True:
        hablar(f"Di {NOMBRE_ASISTENTE} cuando me necesites")

        comando_inicial = esperar_wake_word()

        saludo = obtener_saludo()
        hablar(f"{saludo}, soy {NOMBRE_ASISTENTE}, tu asistente virtual. ¿En qué puedo ayudarte?")

        if comando_inicial:
            if not procesar_comando(comando_inicial):
                continue

        activo = True
        while activo:
            comando = escuchar()
            if comando:
                activo = procesar_comando(comando)


if __name__ == "__main__":
    iniciar()
