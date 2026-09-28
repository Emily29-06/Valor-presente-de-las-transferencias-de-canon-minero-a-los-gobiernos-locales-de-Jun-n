# Nombres y apellidos: QUINTO DE LA CRUZ, EMILY LADY
# Código de matrícula: 2024200518K
# Tema: N.º 32 - Valor presente de las transferencias de canon minero a los gobiernos locales de Junín
# Fecha de extracción: 2026-09-28

"""
01_extraccion_api.py
====================
Vía 1 (API): consumo de BCRPData (API REST del Banco Central de Reserva del Perú).

Descarga 5 series mensuales y las guarda SIN editar (evidencia primaria):
  - un JSON crudo por cada serie: datos_crudos/datos_crudos_<matricula>_bcrp_<codigo>.json
  - un CSV consolidado:           datos_crudos/datos_crudos_<matricula>_bcrp.csv

Uso: ejecutar desde la carpeta raíz del proyecto (la que contiene /codigo).
No requiere clave de API.
"""

import os
import time
import requests
import pandas as pd
from functools import reduce
from datetime import datetime, timezone

# --------------------------------------------------------------------------------------
# Rutas relativas al proyecto (nunca rutas absolutas del computador del estudiante)
# --------------------------------------------------------------------------------------
try:
    BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
except NameError:  # si el código se pega en una celda de Colab, se usa la carpeta actual
    BASE = os.getcwd()

RUTA_CRUDOS = os.path.join(BASE, "datos_crudos")
RUTA_LOG = os.path.join(BASE, "log_ejecucion.txt")
os.makedirs(RUTA_CRUDOS, exist_ok=True)

CODIGO_MATRICULA = "2024200518K"

# --------------------------------------------------------------------------------------
# Parámetros congelados (constantes, no fechas dinámicas): ventana de extracción.
# El formato AAAA-M (mes sin cero adelante) es el que exige la API del BCRP.
# --------------------------------------------------------------------------------------
FECHA_INICIO = "2021-1"
FECHA_CORTE = "2025-12"

# Series de BCRPData (código verificado en el catálogo de series mensuales del BCRP)
SERIES = {
    "precio_cobre_lme_cUSlb": "PN01652XM",            # Cobre - LME (cUS$ por libra)
    "precio_zinc_lme_cUSlb": "PN01657XM",             # Zinc - LME (cUS$ por libra)
    "tasa_referencia_bcrp_pct": "PD04722MM",          # Tasa de Referencia de la Política Monetaria (%)
    "rendimiento_bono_10a_soles_pct": "PD31895MM",    # Rendimiento del bono soberano a 10 años en S/ (%)
    "tipo_cambio_interbancario_prom": "PN01207PM",    # TC interbancario, promedio del periodo (S/ por US$)
}

URL_API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codigo}/json/{inicio}/{fin}/esp"
HEADERS = {"User-Agent": "UNCP-FinanzasI-Tema32-2024200518K/1.0 (uso academico)"}
PAUSA_SEGUNDOS = 1  # pausa entre solicitudes, para no sobrecargar el servidor


def log(mensaje):
    """Imprime el mensaje y lo agrega a log_ejecucion.txt con fecha y hora (UTC)."""
    linea = f"{datetime.now(timezone.utc).isoformat()} | {mensaje}"
    print(linea)
    with open(RUTA_LOG, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def descargar_serie(nombre, codigo):
    """Pide una serie a la API, guarda el JSON crudo y devuelve un DataFrame (periodo, valor)."""
    url = URL_API.format(codigo=codigo, inicio=FECHA_INICIO, fin=FECHA_CORTE)
    log(f"[{codigo}] Consultando {url}")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    log(f"[{codigo}] HTTP {resp.status_code}")

    try:
        datos = resp.json()
    except ValueError:
        # Si la respuesta no es JSON (por ejemplo, una página de error), se registra y se sigue
        log(f"[{codigo}] ERROR: la respuesta no es JSON. Primeros 300 caracteres: {resp.text[:300]}")
        return None

    # Se guarda la respuesta tal como salió de la fuente
    ruta_json = os.path.join(RUTA_CRUDOS, f"datos_crudos_{CODIGO_MATRICULA}_bcrp_{codigo}.json")
    with open(ruta_json, "w", encoding="utf-8") as f:
        f.write(resp.text)

    filas = []
    for periodo in datos.get("periods", []):
        try:
            valor = float(periodo["values"][0])
        except (TypeError, ValueError):  # "n.d." u otro texto = dato no disponible
            valor = None
        filas.append({"periodo_bcrp": periodo["name"], nombre: valor})

    df_serie = pd.DataFrame(filas)
    log(f"[{codigo}] {len(df_serie)} filas, {df_serie[nombre].isna().sum()} valores nulos")
    return df_serie


if __name__ == "__main__":
    log(f"=== INICIO extracción BCRPData (FECHA_INICIO={FECHA_INICIO}, FECHA_CORTE={FECHA_CORTE}) ===")
    tablas = []
    for nombre_variable, codigo_serie in SERIES.items():
        df_serie = descargar_serie(nombre_variable, codigo_serie)
        if df_serie is not None:
            tablas.append(df_serie)
        time.sleep(PAUSA_SEGUNDOS)

    if tablas:
        # Se unen todas las series por el periodo
        df_bcrp = reduce(lambda a, b: a.merge(b, on="periodo_bcrp", how="outer"), tablas)
        ruta_csv = os.path.join(RUTA_CRUDOS, f"datos_crudos_{CODIGO_MATRICULA}_bcrp.csv")
        df_bcrp.to_csv(ruta_csv, index=False, encoding="utf-8")
        log(f"Guardado: {ruta_csv} ({len(df_bcrp)} filas, {df_bcrp.shape[1]} columnas)")
    else:
        log("ERROR: no se pudo descargar ninguna serie.")
    log("=== FIN extracción ===")
