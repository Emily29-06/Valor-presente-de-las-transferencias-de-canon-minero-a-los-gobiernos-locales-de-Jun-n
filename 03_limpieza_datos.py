# Nombres y apellidos: QUINTO DE LA CRUZ, EMILY LADY
# Código de matrícula: 2024200518K
# Tema: N.º 32 - Valor presente de las transferencias de canon minero a los gobiernos locales de Junín
# Fecha de extracción: 2026-09-28

"""
03_limpieza_datos.py
====================
Toma el CSV crudo generado por 01_extraccion_api.py y produce el archivo procesado:
  datos_procesados/datos_procesados_<matricula>.csv

Pasos: normaliza el periodo ("Abr.2021" -> "2021-04"), ordena por fecha, valida que no haya
duplicados ni nulos y que existan los 60 meses esperados, y calcula el hash SHA-256 del resultado.

Uso: ejecutar desde la carpeta raíz del proyecto, después de 01_extraccion_api.py.
"""

import os
import hashlib
import pandas as pd
from datetime import datetime, timezone

# Rutas relativas al proyecto
try:
    BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
except NameError:
    BASE = os.getcwd()

RUTA_CRUDOS = os.path.join(BASE, "datos_crudos")
RUTA_PROCESADOS = os.path.join(BASE, "datos_procesados")
RUTA_LOG = os.path.join(BASE, "log_ejecucion.txt")
os.makedirs(RUTA_PROCESADOS, exist_ok=True)

CODIGO_MATRICULA = "2024200518K"

# Ventana esperada (debe coincidir con FECHA_INICIO y FECHA_CORTE de 01_extraccion_api.py)
PERIODO_INICIO = "2021-01"
PERIODO_FIN = "2025-12"

# Columnas finales del archivo procesado, en este orden
COLUMNAS = [
    "periodo",
    "precio_cobre_lme_cUSlb",
    "precio_zinc_lme_cUSlb",
    "tasa_referencia_bcrp_pct",
    "rendimiento_bono_10a_soles_pct",
    "tipo_cambio_interbancario_prom",
]

# El BCRP abrevia los meses en español; escribe setiembre como "Set" (se acepta también "Sep")
MESES = {"Ene": "01", "Feb": "02", "Mar": "03", "Abr": "04", "May": "05", "Jun": "06",
         "Jul": "07", "Ago": "08", "Set": "09", "Sep": "09", "Oct": "10", "Nov": "11", "Dic": "12"}


def log(mensaje):
    """Imprime el mensaje y lo agrega a log_ejecucion.txt con fecha y hora (UTC)."""
    linea = f"{datetime.now(timezone.utc).isoformat()} | {mensaje}"
    print(linea)
    with open(RUTA_LOG, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def normalizar_periodo(texto):
    """Convierte 'Abr.2021' en '2021-04'."""
    mes, anio = texto.split(".")
    return f"{anio}-{MESES[mes]}"


if __name__ == "__main__":
    log("=== INICIO limpieza de datos ===")

    ruta_crudo = os.path.join(RUTA_CRUDOS, f"datos_crudos_{CODIGO_MATRICULA}_bcrp.csv")
    df = pd.read_csv(ruta_crudo)
    log(f"Crudo cargado: {len(df)} filas, {df.shape[1]} columnas")

    # 1. Periodo normalizado y orden cronológico (el ordenamiento alfabético del crudo no sirve)
    df["periodo"] = df["periodo_bcrp"].apply(normalizar_periodo)
    df = df.drop(columns=["periodo_bcrp"]).sort_values("periodo").reset_index(drop=True)

    # 2. Validaciones: si alguna falla, el script se detiene con un mensaje claro
    assert df["periodo"].is_unique, "Hay periodos duplicados"
    assert df.isna().sum().sum() == 0, "Hay valores nulos"
    esperado = pd.period_range(PERIODO_INICIO, PERIODO_FIN, freq="M").astype(str).tolist()
    assert df["periodo"].tolist() == esperado, "Los periodos no coinciden con la ventana esperada"
    log(f"Validaciones OK: {len(df)} periodos únicos y consecutivos, sin nulos")

    # 3. Selección y orden de columnas, y guardado
    df = df[COLUMNAS]
    ruta_salida = os.path.join(RUTA_PROCESADOS, f"datos_procesados_{CODIGO_MATRICULA}.csv")
    df.to_csv(ruta_salida, index=False, encoding="utf-8")

    # 4. Hash SHA-256 del archivo procesado (se declara en el README)
    with open(ruta_salida, "rb") as f:
        hash_procesado = hashlib.sha256(f.read()).hexdigest()
    log(f"Guardado: {ruta_salida} ({len(df)} filas, {df.shape[1]} columnas)")
    log(f"SHA-256 datos_procesados: {hash_procesado}")
    log("=== FIN limpieza de datos ===")
