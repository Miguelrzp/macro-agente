"""Conector a la API del BCRP (Banco Central de Reserva del Perú)."""
import json
import re

import pandas as pd
import requests

URL_BASE = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"

MESES = {
    "ene": 1, "jan": 1, "feb": 2, "mar": 3, "abr": 4, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "ago": 8, "aug": 8, "sep": 9,
    "set": 9, "oct": 10, "nov": 11, "dic": 12, "dec": 12,
}


def _a_fecha(texto):
    """Convierte textos como 'Ene.2025' en una fecha (primer día del mes)."""
    coincidencia = re.match(r"([A-Za-z]+)\W*(\d{4})", texto)
    mes, anio = coincidencia.groups()
    return pd.Timestamp(year=int(anio), month=MESES[mes[:3].lower()], day=1)


def _descargar_una(codigo, desde, hasta):
    """Descarga una sola serie del BCRP y la devuelve como pd.Series."""
    url = f"{URL_BASE}/{codigo}/json/{desde}/{hasta}"
    respuesta = requests.get(url, timeout=30)
    respuesta.raise_for_status()
    datos = json.loads(respuesta.text.lstrip("\ufeff"))

    fechas = [_a_fecha(p["name"]) for p in datos["periods"]]
    valores = [pd.to_numeric(p["values"][0], errors="coerce") for p in datos["periods"]]
    return pd.Series(valores, index=fechas)


def descargar_series(series, desde="2015-1"):
    """Descarga varias series del BCRP, una por una.

    series: diccionario {codigo: nombre_de_columna}
    Devuelve un DataFrame con una columna por serie e índice de fechas.
    """
    hoy = pd.Timestamp.today()
    hasta = f"{hoy.year}-{hoy.month}"

    columnas = {}
    for codigo, nombre in series.items():
        columnas[nombre] = _descargar_una(codigo, desde, hasta)

    tabla = pd.DataFrame(columnas)
    tabla.index.name = "fecha"
    return tabla