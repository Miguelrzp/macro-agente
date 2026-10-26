"""Agente redactor: convierte la ficha de datos en un párrafo de coyuntura."""
import json

import anthropic
from dotenv import load_dotenv

load_dotenv()
cliente = anthropic.Anthropic()

INSTRUCCIONES_REDACTOR = """Eres un analista de research macroeconómico de un banco de inversión.
Redactas párrafos de coyuntura de inflación para reportes mensuales.

Reglas:
- Usa ÚNICAMENTE las cifras de la ficha de datos. No inventes cifras.
- No atribuyas causas a los movimientos de la inflación si la ficha no las menciona.
- Puedes usar las interpretaciones que aparezcan en las alertas del sistema.
- Escribe en español, en tono profesional y sobrio, en un solo párrafo de 100 a 150 palabras.
- Usa coma decimal (por ejemplo, 4,55%) y menciona el país y el mes de referencia.
- Comenta: la inflación a 12 meses frente al rango meta, el error de pronóstico
  frente a lo esperado hace 12 meses, y las expectativas actuales."""

INSTRUCCIONES_REVISOR = """Eres un editor que verifica la precisión de textos de research.
Recibes una ficha de datos, las alertas del sistema y un borrador. Tu tarea:
1. Verifica que cada cifra del borrador coincida con la ficha.
2. Verifica que el borrador no invente causas ni datos que no estén en la ficha
   o en las alertas. Las interpretaciones presentes en las alertas son válidas.
3. Responde con este formato exacto:
VEREDICTO: APROBADO (si todo es correcto) o VEREDICTO: CORREGIDO (si hubo errores)
TEXTO FINAL: el párrafo final, corregido si hacía falta
CAMBIOS: lista breve de lo que corregiste, o "Ninguno" """


def _llamar_claude(instrucciones, mensaje, config_agente):
    """Envía un mensaje a Claude y devuelve solo el texto de la respuesta."""
    respuesta = cliente.messages.create(
        model=config_agente["modelo"],
        max_tokens=config_agente["max_tokens"],
        system=instrucciones,
        messages=[{"role": "user", "content": mensaje}],
    )
    # La respuesta puede traer bloques de razonamiento; nos quedamos solo con el texto.
    return "".join(bloque.text for bloque in respuesta.content if bloque.type == "text")


def _contexto(ficha, alertas):
    """Arma el mismo contexto para el redactor y el revisor."""
    texto_alertas = "\n".join(f"[{nivel}] {mensaje}" for nivel, mensaje in alertas)
    return (
        f"Ficha de datos:\n{json.dumps(ficha, ensure_ascii=False, indent=2)}\n\n"
        f"Alertas del sistema:\n{texto_alertas or 'Ninguna'}"
    )


def redactar_borrador(ficha, alertas, config_agente):
    """Primer paso: el redactor escribe el borrador."""
    mensaje = f"{_contexto(ficha, alertas)}\n\nRedacta el párrafo de coyuntura de inflación."
    return _llamar_claude(INSTRUCCIONES_REDACTOR, mensaje, config_agente)


def revisar_borrador(borrador, ficha, alertas, config_agente):
    """Segundo paso: el revisor verifica con la misma información que tuvo el redactor."""
    mensaje = f"{_contexto(ficha, alertas)}\n\nBorrador:\n{borrador}"
    return _llamar_claude(INSTRUCCIONES_REVISOR, mensaje, config_agente)