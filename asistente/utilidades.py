import datetime

DIAS_SEMANA = [
    "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"
]


def obtener_dia_semana() -> str:
    dia = datetime.date.today().weekday()
    return DIAS_SEMANA[dia]


def obtener_hora_actual() -> str:
    ahora = datetime.datetime.now()
    hora = ahora.hour
    minuto = ahora.minute

    if hora == 0:
        return f"las {12} y {minuto} minutos de la madrugada"
    elif hora < 12:
        return f"las {hora} y {minuto} minutos de la mañana"
    elif hora == 12:
        return f"las {hora} y {minuto} minutos del mediodía"
    else:
        return f"las {hora - 12} y {minuto} minutos de la tarde"


def obtener_saludo() -> str:
    hora = datetime.datetime.now().hour
    if hora < 12:
        return "Buenos días"
    elif hora < 18:
        return "Buenas tardes"
    else:
        return "Buenas noches"
