import asyncio
import logging
import os
import tempfile

import speech_recognition as sr

from asistente.config import (
    IDIOMA,
    TIEMPO_PAUSA,
    TIMEOUT_ESCUCHA,
    TIEMPO_MAX_FRASE,
    PALABRA_CLAVE,
    NOMBRE_ASISTENTE,
)

logger = logging.getLogger(__name__)

VOZ_EDGE = "es-ES-ElviraNeural"

_HAY_EDGE = False
_HAY_GTTs = False
_HAY_PYGAME = False
_HABILITAR_GTTs = False
_HAY_PYTTSX3 = False

try:
    import edge_tts
    _HAY_EDGE = True
    logger.info("edge-tts disponible")
except ImportError:
    logger.info("edge-tts no instalado")

try:
    from gtts import gTTS
    _HAY_GTTs = True
except ImportError:
    logger.info("gTTS no instalado")

try:
    import pygame
    _HAY_PYGAME = True
except ImportError:
    logger.info("pygame no instalado")

if _HAY_PYGAME:
    try:
        pygame.mixer.init()
        _HABILITAR_GTTs = True
        logger.info("pygame.mixer listo")
    except Exception as e:
        logger.warning("Error al iniciar pygame.mixer: %s", e)

try:
    import pyttsx3
    _HAY_PYTTSX3 = True
    logger.info("pyttsx3 disponible como respaldo")
except ImportError:
    logger.info("pyttsx3 no instalado")

logger.info(
    "Estado TTS - edge-tts: %s, gTTS: %s, pygame: %s, pyttsx3: %s",
    _HAY_EDGE, _HAY_GTTs, pygame.mixer.get_init() if _HAY_PYGAME else False, _HAY_PYTTSX3,
)


def _reproducir_mp3(archivo: str) -> None:
    pygame.mixer.music.load(archivo)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)


def _hablar_con_edge_tts(mensaje: str) -> None:
    archivo = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            archivo = tmp.name

        async def _generar():
            communicate = edge_tts.Communicate(mensaje, VOZ_EDGE)
            await communicate.save(archivo)

        asyncio.run(_generar())
        _reproducir_mp3(archivo)
    finally:
        if archivo and os.path.exists(archivo):
            try:
                os.unlink(archivo)
            except Exception as e:
                logger.warning("No se pudo eliminar archivo temporal: %s", e)


def _hablar_con_gtts(mensaje: str) -> None:
    archivo = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            archivo = tmp.name
        tts = gTTS(text=mensaje, lang="es", slow=False)
        tts.save(archivo)
        _reproducir_mp3(archivo)
    finally:
        if archivo and os.path.exists(archivo):
            try:
                os.unlink(archivo)
            except Exception as e:
                logger.warning("No se pudo eliminar archivo temporal: %s", e)


def _hablar_con_pyttsx3(mensaje: str) -> None:
    engine = pyttsx3.init()
    voces = engine.getProperty("voices")
    for voz in voces:
        nombre = (voz.name or "").lower()
        id_voz = (voz.id or "").lower()
        if any(m in nombre or m in id_voz for m in ("spanish", "espanol", "es_", "es-", "mb-es")):
            try:
                engine.setProperty("voice", voz.id)
            except Exception:
                pass
            break
    engine.say(mensaje)
    engine.runAndWait()


def hablar(mensaje: str) -> None:
    print(f"[{NOMBRE_ASISTENTE}]: {mensaje}")

    if _HAY_EDGE and _HAY_PYGAME:
        try:
            _hablar_con_edge_tts(mensaje)
            return
        except Exception as e:
            logger.error("edge-tts falló: %s", e)
            logger.info("Intentando con gTTS...")

    if _HABILITAR_GTTs:
        try:
            _hablar_con_gtts(mensaje)
            return
        except Exception as e:
            logger.error("gTTS falló: %s", e)
            logger.info("Intentando con pyttsx3...")

    if _HAY_PYTTSX3:
        try:
            _hablar_con_pyttsx3(mensaje)
            return
        except Exception as e:
            logger.error("pyttsx3 falló: %s", e)

    if not _HAY_EDGE and not _HABILITAR_GTTs and not _HAY_PYTTSX3:
        logger.warning("No hay motor de voz disponible. Instala edge-tts, gTTS + pygame o pyttsx3")


def escuchar() -> str | None:
    reconocedor = sr.Recognizer()
    reconocedor.pause_threshold = TIEMPO_PAUSA

    try:
        with sr.Microphone() as origen:
            print("[🎤 Escuchando...]")
            try:
                audio = reconocedor.listen(
                    origen,
                    timeout=TIMEOUT_ESCUCHA,
                    phrase_time_limit=TIEMPO_MAX_FRASE,
                )
            except sr.WaitTimeoutError:
                return None
    except (AttributeError, OSError) as e:
        logger.error("Error con el micrófono: %s", e)
        hablar("No tengo acceso al micrófono")
        return None

    try:
        texto = reconocedor.recognize_google(audio, language=IDIOMA)
        print(f"[Tú]: {texto}")
        return texto
    except sr.UnknownValueError:
        print("[No te entendí]")
        return None
    except sr.RequestError as e:
        logger.error("Error de conexión con Google Speech: %s", e)
        hablar("No tengo conexión a internet")
        return None
    except Exception as e:
        logger.error("Error al reconocer voz: %s", e)
        return None


def esperar_wake_word(palabra_clave: str | None = None) -> str | None:
    if palabra_clave is None:
        palabra_clave = PALABRA_CLAVE

    while True:
        texto = escuchar()
        if texto is None:
            continue

        texto_lower = texto.lower()

        if palabra_clave.lower() in texto_lower:
            indice = texto_lower.find(palabra_clave.lower())
            comando = texto[indice + len(palabra_clave):].strip()
            logger.info("Palabra clave detectada, comando: %s", comando or "(ninguno)")
            return comando
