import pandas as pd
import yaml

from analisis.comparacion import calcular_error_pronostico, resumen_ultimo_dato
from datos.bcrp import descargar_series

pd.set_option("display.width", 200)

with open("config.yaml", encoding="utf-8") as archivo:
    config = yaml.safe_load(archivo)

peru_config = config["peru"]
peru = descargar_series(peru_config["series"])
peru = calcular_error_pronostico(peru)

print(peru.tail(6).round(2))
print()
print(resumen_ultimo_dato(peru, peru_config["meta_inflacion"]))