import yaml

from datos.bcrp import descargar_series

with open("config.yaml", encoding="utf-8") as archivo:
    config = yaml.safe_load(archivo)

peru = descargar_series(config["peru"]["series"])
print(peru.tail(12))