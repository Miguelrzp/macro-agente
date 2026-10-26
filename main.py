from pathlib import Path

import pandas as pd
import yaml

from agente.redactor import redactar_borrador, revisar_borrador
from alertas.controles import revisar_datos
from analisis.comparacion import calcular_error_pronostico, resumen_ultimo_dato
from datos.bcrp import descargar_series
from graficas.inflacion import grafica_inflacion

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)

with open("config.yaml", encoding="utf-8") as archivo:
    config = yaml.safe_load(archivo)

peru_config = config["peru"]

# 1. Datos
peru = descargar_series(peru_config["series"])

# 2. Controles de calidad
alertas = revisar_datos(peru, peru_config["meta_inflacion"], **peru_config["alertas"])
print("=== ALERTAS ===")
for nivel, mensaje in alertas:
    print(f"[{nivel}] {mensaje}")
if not alertas:
    print("Sin alertas.")
print()

# 3. Análisis
peru = calcular_error_pronostico(peru)
ficha = resumen_ultimo_dato(peru, peru_config["meta_inflacion"])
ficha["pais"] = peru_config["nombre"]
ficha["fuente_expectativas"] = peru_config["fuente_expectativas"]
print("=== FICHA ===")
print(ficha)
print()

# 4. Gráfica
ruta = grafica_inflacion(
    peru, peru_config["nombre"], peru_config["meta_inflacion"], "salidas/inflacion_peru.png"
)
print(f"Gráfica guardada en: {ruta}")
print()

# 5. Agente redactor (solo si los datos son confiables)
problemas = [a for a in alertas if a[0] in ("ERROR", "ADVERTENCIA")]
if problemas:
    print("El agente NO redacta: hay alertas de calidad que un analista debe revisar primero.")
else:
    borrador = redactar_borrador(ficha, alertas, config["agente"])
    print("=== BORRADOR ===")
    print(borrador)
    print()

    revision = revisar_borrador(borrador, ficha, alertas, config["agente"])
    print("=== REVISIÓN ===")
    print(revision)

    Path("salidas/reporte_peru.md").write_text(revision, encoding="utf-8")
    print()
    print("Reporte guardado en: salidas/reporte_peru.md")