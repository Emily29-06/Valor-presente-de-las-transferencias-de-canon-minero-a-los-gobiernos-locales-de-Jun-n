# Carpeta N.º 3 — Base de datos y código (avance: Vía 1 / API)
**QUINTO DE LA CRUZ, EMILY LADY**

- Código de matrícula: 2024200518K
- Tema (N.º 32 del temario): Valor presente de las transferencias de canon minero a los gobiernos locales de Junín
- Curso: Finanzas I (055D) · Ciclo V · UNCP · 2026-II · Unidad I

## Estado de avance
- [x] Vía 1 (API): BCRPData, 5 series mensuales (cobre, zinc, tasa de referencia, bono a 10 años, tipo de cambio), 60 observaciones (ene-2021 a dic-2025).
- [x] Limpieza, validación y análisis preliminar (descriptivos, correlaciones, factores de descuento).
- [ ] Población distrital (Datos Abiertos del Perú): el endpoint CKAN documentado devuelve 404 (el portal migró a Drupal). Ver incidencias_fuente.md.
- [ ] Transferencias de canon por municipalidad (MEF): el portal responde con una protección anti-bots en lugar del archivo. Se aplicó el numeral 2.4.3: incidencia documentada y solicitud de sustitución de fuente al docente (pendiente de respuesta).
- [ ] Panel distrital (123 distritos × 60 meses) y valor presente del flujo de canon: dependen de la fuente autorizada.

## Fuentes y endpoints
BCRPData REST: `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codigo}/json/{inicio}/{fin}/esp`
Series: PN01652XM, PN01657XM, PD04722MM, PD31895MM, PN01207PM (detalle en diccionario_variables.md). No requiere clave.

## Parámetros congelados
FECHA_INICIO = 2021-1 · FECHA_CORTE = 2025-12

## Fecha de extracción
2026-09-28 02:56 UTC

## Hash SHA-256
- datos_crudos_2024200518K_bcrp.csv: `14446e2350d2933a0e09f48fb23ec43e9a1382b7a1c16c93840252254d20b2c4`
- datos_procesados_2024200518K.csv: `986c887510b15b3da66c5ecf3a6b822bedba414f0df729a50fdd0605bf44ba10`

## Ejecución
Google Colab (sin Google Drive). Python 3.13.15. Versiones de librerías en requirements.txt. Cada llamada HTTP queda en log_ejecucion.txt.

## Repositorio GitHub
<<COMPLETAR: enlace del repositorio, con al menos 3 commits en fechas distintas>>
