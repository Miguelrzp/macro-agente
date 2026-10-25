"""Banco de gráficas reutilizables."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def grafica_inflacion(tabla, nombre_pais, meta, archivo, desde="2020-01"):
    """Inflación a 12 meses vs. expectativas, con la franja del rango meta."""
    datos = tabla.loc[desde:]
    minimo, maximo = meta

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axhspan(minimo, maximo, color="green", alpha=0.1,
               label=f"Rango meta ({minimo}% - {maximo}%)")
    ax.plot(datos.index, datos["inflacion_12m"], linewidth=2,
            label="Inflación 12 meses")
    ax.plot(datos.index, datos["expectativa_12m"], linewidth=2, linestyle="--",
            label="Expectativa a 12 meses")

    ax.set_title(f"{nombre_pais}: inflación y expectativas")
    ax.set_ylabel("%")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()

    ruta = Path(archivo)
    ruta.parent.mkdir(exist_ok=True)
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return ruta