"""Comparación entre inflación observada, expectativas y meta."""


def calcular_error_pronostico(tabla):
    """Agrega a la tabla lo que se esperaba hace 12 meses y el error de pronóstico."""
    resultado = tabla.copy()
    resultado["esperado_hace_12m"] = resultado["expectativa_12m"].shift(12)
    resultado["error_pronostico"] = (
        resultado["inflacion_12m"] - resultado["esperado_hace_12m"]
    )
    return resultado


def resumen_ultimo_dato(tabla, meta):
    """Resume el último mes disponible en un diccionario sencillo."""
    ultimo = tabla.dropna(subset=["inflacion_12m"]).iloc[-1]
    minimo, maximo = meta
    return {
        "fecha": ultimo.name.strftime("%Y-%m"),
        "inflacion_12m": round(float(ultimo["inflacion_12m"]), 2),
        "inflacion_mensual": round(float(ultimo["inflacion_mensual"]), 2),
        "expectativa_12m": round(float(ultimo["expectativa_12m"]), 2),
        "esperado_hace_12m": round(float(ultimo["esperado_hace_12m"]), 2),
        "error_pronostico": round(float(ultimo["error_pronostico"]), 2),
        "meta": f"{minimo}% - {maximo}%",
        "dentro_de_meta": bool(minimo <= ultimo["inflacion_12m"] <= maximo),
    }