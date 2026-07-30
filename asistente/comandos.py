import logging
import os
import webbrowser

import yfinance as yf
import wikipedia
import pyjokes

from asistente.audio import hablar
from asistente.utilidades import obtener_dia_semana, obtener_hora_actual

logger = logging.getLogger(__name__)


def _extraer(texto: str, *patrones: str) -> str:
    texto_lower = texto.lower()
    for patron in patrones:
        if patron in texto_lower:
            idx = texto_lower.find(patron)
            return (texto[:idx] + texto[idx + len(patron):]).strip()
    return texto.strip()


def ayuda(texto):
    mensaje = (
        "Puedes pedirme: abrir YouTube, abrir el navegador, "
        "preguntar la hora, el día o la fecha, buscar en Wikipedia, "
        "buscar en internet, reproducir música en YouTube, "
        "contar un chiste, consultar el precio de acciones, "
        "o decir adiós para salir"
    )
    hablar(mensaje)


def abrir_youtube(texto):
    hablar("Abriendo YouTube")
    webbrowser.open("https://www.youtube.com")


def abrir_navegador(texto):
    hablar("Abriendo el navegador")
    webbrowser.open("https://www.google.com")


def pedir_dia(texto):
    dia = obtener_dia_semana()
    hablar(f"Hoy es {dia}")


def pedir_hora(texto):
    hora = obtener_hora_actual()
    hablar(f"Son {hora}")


def buscar_wikipedia(texto):
    consulta = _extraer(texto, "busca en wikipedia", "busca wikipedia", "buscar wikipedia", "buscar en wikipedia")
    if not consulta:
        hablar("¿Qué quieres que busque en Wikipedia?")
        return
    try:
        wikipedia.set_lang("es")
        resultado = wikipedia.summary(consulta, sentences=2)
        hablar(resultado)
    except wikipedia.exceptions.DisambiguationError as e:
        opciones = ", ".join(e.options[:5])
        hablar(f"Hay varias páginas con ese nombre. Las opciones son: {opciones}")
    except wikipedia.exceptions.PageError:
        hablar("No encontré nada en Wikipedia sobre eso")
    except Exception as e:
        logger.error("Error en Wikipedia: %s", e)
        hablar("Ocurrió un error al buscar en Wikipedia")


def buscar_internet(texto):
    consulta = _extraer(texto, "busca en internet", "busca internet", "buscar internet", "buscar en internet", "busca en google", "buscar en google")
    if not consulta:
        hablar("¿Qué quieres que busque en internet?")
        return
    hablar("Buscando en internet")
    try:
        import pywhatkit
        pywhatkit.search(consulta)
    except Exception as e:
        logger.error("Error con pywhatkit: %s", e)
        webbrowser.open(f"https://www.google.com/search?q={consulta}")
    hablar("Esto es lo que encontré")


def reproducir(texto):
    consulta = _extraer(texto, "reproduce", "reproducir", "pon", "ponme", "tocar", "toca", "poner")
    if not consulta:
        hablar("¿Qué quieres que reproduzca?")
        return
    hablar("Buena idea, vamos a escucharlo")
    try:
        import pywhatkit
        pywhatkit.playonyt(consulta)
    except Exception as e:
        logger.error("Error con pywhatkit: %s", e)
        webbrowser.open(f"https://www.youtube.com/results?search_query={consulta}")
    hablar("Reproduciendo la canción")


def contar_chiste(texto):
    try:
        broma = pyjokes.get_joke("es")
        hablar(broma)
    except Exception as e:
        logger.error("Error al obtener chiste: %s", e)
        hablar("No tengo chistes en este momento")


def precio_accion(texto):
    ticker = _extraer(texto, "precio de las acciones", "precio acción", "precio de acción", "acciones", "cotización", "cotizacion", "valor de acción")
    if not ticker:
        hablar("¿De qué acción quieres el precio?")
        return
    try:
        stock = yf.Ticker(ticker)
        historial = stock.history(period="1d")
        if not historial.empty:
            precio = historial["Close"].iloc[0]
            hablar(f"El precio de las acciones de {ticker} es {precio}")
        else:
            hablar(f"No encontré información para {ticker}")
    except Exception as e:
        logger.error("Error obteniendo precio de acción: %s", e)
        hablar("Ocurrió un error al obtener el precio de la acción")


def despedirse(texto):
    hablar("Hasta luego, si necesitas algo más puedes llamarme")
    return False


COMANDOS = [
    ("ayuda", ayuda),
    ("qué puedes hacer", ayuda),
    ("comandos", ayuda),
    ("abrir youtube", abrir_youtube),
    ("abre youtube", abrir_youtube),
    ("abrir navegador", abrir_navegador),
    ("abre navegador", abrir_navegador),
    ("abrir google", abrir_navegador),
    ("abre google", abrir_navegador),
    ("qué día es", pedir_dia),
    ("que día es", pedir_dia),
    ("qué hora es", pedir_hora),
    ("que hora es", pedir_hora),
    ("busca en wikipedia", buscar_wikipedia),
    ("busca wikipedia", buscar_wikipedia),
    ("buscar wikipedia", buscar_wikipedia),
    ("buscar en wikipedia", buscar_wikipedia),
    ("busca en internet", buscar_internet),
    ("busca internet", buscar_internet),
    ("buscar internet", buscar_internet),
    ("buscar en internet", buscar_internet),
    ("busca en google", buscar_internet),
    ("reproduce", reproducir),
    ("reproducir", reproducir),
    ("pon", reproducir),
    ("ponme", reproducir),
    ("toca", reproducir),
    ("tocar", reproducir),
    ("broma", contar_chiste),
    ("chiste", contar_chiste),
    ("un chiste", contar_chiste),
    ("precio de las acciones", precio_accion),
    ("precio acción", precio_accion),
    ("precio de acción", precio_accion),
    ("acciones", precio_accion),
    ("cotización", precio_accion),
    ("cotizacion", precio_accion),
    ("adiós", despedirse),
    ("chao", despedirse),
    ("hasta luego", despedirse),
    ("salir", despedirse),
    ("me voy", despedirse),
    ("nos vemos", despedirse),
]


def procesar_comando(texto: str | None) -> bool:
    if not texto:
        return True

    texto_lower = texto.lower()

    for patron, funcion in COMANDOS:
        if patron in texto_lower:
            resultado = funcion(texto)
            if resultado is False:
                return False
            return True

    hablar("No entendí ese comando. Di 'ayuda' para conocer los comandos disponibles")
    return True


def _ayuda_api(texto):
    return (
        "Puedes pedirme: abrir YouTube, abrir el navegador, "
        "preguntar la hora, el día o la fecha, buscar en Wikipedia, "
        "buscar en internet, reproducir música en YouTube, "
        "contar un chiste, consultar el precio de acciones, "
        "o decir adiós para salir"
    ), "complete", None


def _abrir_youtube_api(texto):
    webbrowser.open("https://www.youtube.com")
    return "Abriendo YouTube", "complete", None


def _abrir_navegador_api(texto):
    webbrowser.open("https://www.google.com")
    return "Abriendo el navegador", "complete", None


def _pedir_dia_api(texto):
    dia = obtener_dia_semana()
    return f"Hoy es {dia}", "complete", None


def _pedir_hora_api(texto):
    hora = obtener_hora_actual()
    return f"Son {hora}", "complete", None


def _buscar_wikipedia_api(texto):
    consulta = _extraer(texto, "busca en wikipedia", "busca wikipedia", "buscar wikipedia", "buscar en wikipedia")
    if not consulta:
        return "¿Qué quieres que busque en Wikipedia?", "waiting_input", "wikipedia_search"
    try:
        wikipedia.set_lang("es")
        resultado = wikipedia.summary(consulta, sentences=2)
        return resultado, "complete", None
    except wikipedia.exceptions.DisambiguationError as e:
        opciones = ", ".join(e.options[:5])
        return f"Hay varias páginas con ese nombre. Las opciones son: {opciones}", "complete", None
    except wikipedia.exceptions.PageError:
        return "No encontré nada en Wikipedia sobre eso", "complete", None
    except Exception as e:
        logger.error("Error en Wikipedia: %s", e)
        return "Ocurrió un error al buscar en Wikipedia", "complete", None


def _buscar_internet_api(texto):
    consulta = _extraer(texto, "busca en internet", "busca internet", "buscar internet", "buscar en internet", "busca en google", "buscar en google")
    if not consulta:
        return "¿Qué quieres que busque en internet?", "waiting_input", "internet_search"
    try:
        import pywhatkit
        pywhatkit.search(consulta)
    except Exception as e:
        logger.error("Error con pywhatkit: %s", e)
        webbrowser.open(f"https://www.google.com/search?q={consulta}")
    return "Esto es lo que encontré", "complete", None


def _reproducir_api(texto):
    consulta = _extraer(texto, "reproduce", "reproducir", "pon", "ponme", "tocar", "toca", "poner")
    if not consulta:
        return "¿Qué quieres que reproduzca?", "waiting_input", "music_search"
    try:
        import pywhatkit
        pywhatkit.playonyt(consulta)
    except Exception as e:
        logger.error("Error con pywhatkit: %s", e)
        webbrowser.open(f"https://www.youtube.com/results?search_query={consulta}")
    return "Buena idea, reproduciendo la canción", "complete", None


def _contar_chiste_api(texto):
    try:
        broma = pyjokes.get_joke("es")
        return broma, "complete", None
    except Exception as e:
        logger.error("Error al obtener chiste: %s", e)
        return "No tengo chistes en este momento", "complete", None


def _precio_accion_api(texto):
    ticker = _extraer(texto, "precio de las acciones", "precio acción", "precio de acción", "acciones", "cotización", "cotizacion", "valor de acción")
    if not ticker:
        return "¿De qué acción quieres el precio?", "waiting_input", "stock_price"
    try:
        stock = yf.Ticker(ticker)
        historial = stock.history(period="1d")
        if not historial.empty:
            precio = historial["Close"].iloc[0]
            return f"El precio de las acciones de {ticker} es {precio:.2f}", "complete", None
        else:
            return f"No encontré información para {ticker}", "complete", None
    except Exception as e:
        logger.error("Error obteniendo precio de acción: %s", e)
        return "Ocurrió un error al obtener el precio de la acción", "complete", None


def _despedirse_api(texto):
    return "Hasta luego, si necesitas algo más puedes llamarme", "complete", None


COMANDOS_API = [
    ("ayuda", _ayuda_api),
    ("qué puedes hacer", _ayuda_api),
    ("comandos", _ayuda_api),
    ("abrir youtube", _abrir_youtube_api),
    ("abre youtube", _abrir_youtube_api),
    ("abrir navegador", _abrir_navegador_api),
    ("abre navegador", _abrir_navegador_api),
    ("abrir google", _abrir_navegador_api),
    ("abre google", _abrir_navegador_api),
    ("qué día es", _pedir_dia_api),
    ("que día es", _pedir_dia_api),
    ("qué hora es", _pedir_hora_api),
    ("que hora es", _pedir_hora_api),
    ("busca en wikipedia", _buscar_wikipedia_api),
    ("busca wikipedia", _buscar_wikipedia_api),
    ("buscar wikipedia", _buscar_wikipedia_api),
    ("buscar en wikipedia", _buscar_wikipedia_api),
    ("busca en internet", _buscar_internet_api),
    ("busca internet", _buscar_internet_api),
    ("buscar internet", _buscar_internet_api),
    ("buscar en internet", _buscar_internet_api),
    ("busca en google", _buscar_internet_api),
    ("reproduce", _reproducir_api),
    ("reproducir", _reproducir_api),
    ("pon", _reproducir_api),
    ("ponme", _reproducir_api),
    ("toca", _reproducir_api),
    ("tocar", _reproducir_api),
    ("broma", _contar_chiste_api),
    ("chiste", _contar_chiste_api),
    ("un chiste", _contar_chiste_api),
    ("precio de las acciones", _precio_accion_api),
    ("precio acción", _precio_accion_api),
    ("precio de acción", _precio_accion_api),
    ("acciones", _precio_accion_api),
    ("cotización", _precio_accion_api),
    ("cotizacion", _precio_accion_api),
    ("adiós", _despedirse_api),
    ("chao", _despedirse_api),
    ("hasta luego", _despedirse_api),
    ("salir", _despedirse_api),
    ("me voy", _despedirse_api),
    ("nos vemos", _despedirse_api),
]


def _procesar_seguimiento_api(texto, context):
    if context == "wikipedia_search":
        try:
            wikipedia.set_lang("es")
            resultado = wikipedia.summary(texto, sentences=2)
            return resultado, "complete", None
        except wikipedia.exceptions.DisambiguationError as e:
            opciones = ", ".join(e.options[:5])
            return f"Hay varias páginas con ese nombre. Las opciones son: {opciones}", "complete", None
        except wikipedia.exceptions.PageError:
            return "No encontré nada en Wikipedia sobre eso", "complete", None
        except Exception as e:
            logger.error("Error en Wikipedia: %s", e)
            return "Ocurrió un error al buscar en Wikipedia", "complete", None

    elif context == "internet_search":
        try:
            import pywhatkit
            pywhatkit.search(texto)
        except Exception as e:
            logger.error("Error con pywhatkit: %s", e)
            webbrowser.open(f"https://www.google.com/search?q={texto}")
        return "Esto es lo que encontré", "complete", None

    elif context == "music_search":
        try:
            import pywhatkit
            pywhatkit.playonyt(texto)
        except Exception as e:
            logger.error("Error con pywhatkit: %s", e)
            webbrowser.open(f"https://www.youtube.com/results?search_query={texto}")
        return "Buena idea, reproduciendo la canción", "complete", None

    elif context == "stock_price":
        try:
            stock = yf.Ticker(texto)
            historial = stock.history(period="1d")
            if not historial.empty:
                precio = historial["Close"].iloc[0]
                return f"El precio de las acciones de {texto} es {precio:.2f}", "complete", None
            else:
                return f"No encontré información para {texto}", "complete", None
        except Exception as e:
            logger.error("Error obteniendo precio de acción: %s", e)
            return "Ocurrió un error al obtener el precio de la acción", "complete", None

    return "No entendí tu respuesta", "complete", None


def procesar_comando_api(texto, context=None):
    if context:
        return _procesar_seguimiento_api(texto, context)

    texto_lower = texto.lower()

    for patron, funcion in COMANDOS_API:
        if patron in texto_lower:
            return funcion(texto)

    return "No entendí ese comando. Di 'ayuda' para conocer los comandos disponibles", "complete", None
