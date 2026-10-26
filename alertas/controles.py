"""Controles de calidad y alertas sobre los datos."""
import pandas as pd


def _meses_entre(fecha_inicio, fecha_fin):
    return (fecha_fin.year - fecha_inicio.year) * 12 + (fecha_fin.month - fecha_inicio.month)


def revisar_datos(tabla, meta, max_meses_rezago=2, umbral_atipico=3):
    """Revisa la tabla y devuelve una lista de alertas (nivel, mensaje)."""
    alertas = []
    hoy = pd.Timestamp.today()

    # 1 y 2. Series vacías o desactualizadas
    for columna in tabla.columns:
        serie = tabla[columna].dropna()
        if serie.empty:
            alertas.append(("ERROR", f"{columna}: la serie está vacía. Revisar código o fuente."))
            continue
        ultimo = serie.index[-1]
        rezago = _meses_entre(ultimo, hoy)
        if rezago > max_meses_rezago:
            alertas.append((
                "ADVERTENCIA",
                f"{columna}: el último dato es de {ultimo:%Y-%m} "
                f"({rezago} meses de rezago). Puede estar desactualizada.",
            ))

    # 3. Valor atípico en la inflación mensual (vs. los 5 años anteriores)
    mensual = tabla["inflacion_mensual"].dropna()
    historia = mensual.iloc[-61:-1]
    z = (mensual.iloc[-1] - historia.mean()) / historia.std()
    if abs(z) > umbral_atipico:
        alertas.append((
            "ADVERTENCIA",
            f"inflacion_mensual: el último dato ({mensual.iloc[-1]:.2f}%) es atípico "
            f"({z:.1f} desviaciones estándar). Verificar antes de publicar.",
        ))

    # 4. Inflación y expectativas frente a la meta
    minimo, maximo = meta
    inflacion = tabla["inflacion_12m"].dropna().iloc[-1]
    expectativa = tabla["expectativa_12m"].dropna().iloc[-1]
    if not minimo <= inflacion <= maximo:
        alertas.append(("INFO", f"La inflación a 12 meses ({inflacion:.2f}%) está fuera del rango meta."))
    if not minimo <= expectativa <= maximo:
        alertas.append(("INFO", f"Las expectativas ({expectativa:.2f}%) están fuera del rango meta: posible desanclaje."))

    return alertas