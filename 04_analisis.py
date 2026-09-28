# Nombres y apellidos: QUINTO DE LA CRUZ, EMILY LADY
# Código de matrícula: 2024200518K
# Tema: N.º 32 - Valor presente de las transferencias de canon minero a los gobiernos locales de Junín
# Fecha de extracción: 2026-09-28

"""
04_analisis.py
==============
Análisis preliminar (Vía 1) a partir de datos_procesados/datos_procesados_<matricula>.csv.
Todas las tablas y figuras se guardan en /salidas y se regeneran ejecutando este script.

Contenido:
  1. Estadísticos descriptivos.
  2. Correlaciones en niveles y en variaciones (log-diferencias). Las de variaciones son las
     recomendables para interpretar: correlacionar niveles puede dar relaciones espurias.
  3. Figuras: precios del cobre y zinc; tasas de interés.
  4. Factores de descuento mensuales a partir del rendimiento del bono soberano a 10 años.
     Cuando se disponga de las transferencias de canon por municipalidad:
         VP = suma(transferencia_t * factor_descuento_t)

Uso: ejecutar desde la carpeta raíz del proyecto, después de 03_limpieza_datos.py.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend sin ventana: guarda las figuras en archivo
import matplotlib.pyplot as plt
from datetime import datetime, timezone

# Rutas relativas al proyecto
try:
    BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
except NameError:
    BASE = os.getcwd()

RUTA_PROCESADOS = os.path.join(BASE, "datos_procesados")
RUTA_SALIDAS = os.path.join(BASE, "salidas")
RUTA_LOG = os.path.join(BASE, "log_ejecucion.txt")
os.makedirs(RUTA_SALIDAS, exist_ok=True)

CODIGO_MATRICULA = "2024200518K"

VARIABLES = [
    "precio_cobre_lme_cUSlb",
    "precio_zinc_lme_cUSlb",
    "tasa_referencia_bcrp_pct",
    "rendimiento_bono_10a_soles_pct",
    "tipo_cambio_interbancario_prom",
]


def log(mensaje):
    """Imprime el mensaje y lo agrega a log_ejecucion.txt con fecha y hora (UTC)."""
    linea = f"{datetime.now(timezone.utc).isoformat()} | {mensaje}"
    print(linea)
    with open(RUTA_LOG, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


if __name__ == "__main__":
    log("=== INICIO análisis ===")

    df = pd.read_csv(os.path.join(RUTA_PROCESADOS, f"datos_procesados_{CODIGO_MATRICULA}.csv"))
    df["fecha"] = pd.to_datetime(df["periodo"], format="%Y-%m")
    log(f"Datos procesados cargados: {len(df)} filas")

    # 1. Descriptivos
    descriptivos = df[VARIABLES].describe().round(2)
    descriptivos.to_csv(os.path.join(RUTA_SALIDAS, "tabla_descriptivos.csv"), encoding="utf-8")

    # 2. Correlaciones en niveles
    corr_niveles = df[VARIABLES].corr().round(3)
    corr_niveles.to_csv(os.path.join(RUTA_SALIDAS, "tabla_correlacion_niveles.csv"), encoding="utf-8")

    # 2b. Correlaciones en variaciones: log-diferencias de precios y tipo de cambio,
    #     diferencia simple para el rendimiento del bono (ya está en porcentaje)
    variaciones = pd.DataFrame({
        "dln_cobre": np.log(df["precio_cobre_lme_cUSlb"]).diff(),
        "dln_zinc": np.log(df["precio_zinc_lme_cUSlb"]).diff(),
        "d_bono_10a": df["rendimiento_bono_10a_soles_pct"].diff(),
        "dln_tipo_cambio": np.log(df["tipo_cambio_interbancario_prom"]).diff(),
    }).dropna()
    corr_variaciones = variaciones.corr().round(3)
    corr_variaciones.to_csv(os.path.join(RUTA_SALIDAS, "tabla_correlacion_variaciones.csv"), encoding="utf-8")
    log(f"Correlación en niveles:\n{corr_niveles.to_string()}")
    log(f"Correlación en variaciones (n={len(variaciones)}):\n{corr_variaciones.to_string()}")

    # 3a. Figura: cobre y zinc (dos ejes)
    fig, eje1 = plt.subplots(figsize=(9, 4.5))
    eje1.plot(df["fecha"], df["precio_cobre_lme_cUSlb"], color="tab:orange")
    eje1.set_ylabel("Cobre LME (cUS$/lb)", color="tab:orange")
    eje2 = eje1.twinx()
    eje2.plot(df["fecha"], df["precio_zinc_lme_cUSlb"], color="tab:blue")
    eje2.set_ylabel("Zinc LME (cUS$/lb)", color="tab:blue")
    plt.title("Precios internacionales del cobre y del zinc, 2021-2025")
    fig.tight_layout()
    fig.savefig(os.path.join(RUTA_SALIDAS, "figura_precios_cobre_zinc.png"), dpi=150)
    plt.close(fig)

    # 3b. Figura: tasas de interés
    fig, eje = plt.subplots(figsize=(9, 4.5))
    eje.plot(df["fecha"], df["rendimiento_bono_10a_soles_pct"], label="Bono soberano 10 años (S/)")
    eje.plot(df["fecha"], df["tasa_referencia_bcrp_pct"], label="Tasa de referencia BCRP")
    eje.set_ylabel("%")
    eje.legend()
    plt.title("Tasas de interés: bono a 10 años y tasa de referencia, 2021-2025")
    fig.tight_layout()
    fig.savefig(os.path.join(RUTA_SALIDAS, "figura_tasas.png"), dpi=150)
    plt.close(fig)

    # 4. Factores de descuento mensuales
    #    Tasa mensual equivalente al rendimiento anual de cada mes; el factor acumulado
    #    descuenta cada mes con las tasas vigentes hasta ese momento (simplificación que
    #    debe declararse en la sección de métodos del artículo).
    rendimiento_anual = df["rendimiento_bono_10a_soles_pct"] / 100
    tasa_mensual = (1 + rendimiento_anual) ** (1 / 12) - 1
    factor_descuento = 1 / np.cumprod(1 + tasa_mensual)
    tabla_factores = pd.DataFrame({
        "periodo": df["periodo"],
        "tasa_mensual": tasa_mensual.round(6),
        "factor_descuento": factor_descuento.round(6),
    })
    tabla_factores.to_csv(os.path.join(RUTA_SALIDAS, "tabla_factores_descuento.csv"), index=False, encoding="utf-8")
    factor_anualidad = factor_descuento.sum()
    log(f"Factor de anualidad (VP de S/1 mensual durante {len(df)} meses): {factor_anualidad:.4f}")
    log("=== FIN análisis ===")
