# Cambios

Cada versión se publica a la vez en GitHub (release `vX.Y.Z`) y en
[PyPI](https://pypi.org/project/orange-gualbe-ts/).

## 0.2.3 (2026-11-06)

- README renovado, también en PyPI: encabezado con insignias, tabla resumen,
  esquema del flujo típico en el lienzo de Orange, esquemas de cómo funciona cada
  widget y capturas reales de su interfaz.
- Se añade `assets/generar_imagenes.py` para regenerar esas imágenes.
- Sin cambios funcionales en los widgets.

## 0.2.2 (2026-11-06)

- La publicación en PyPI pasa a ser automática con Trusted Publishing: cada
  release de GitHub construye el paquete, lo sube a PyPI y adjunta los ficheros a
  la release.
- Sin cambios funcionales en los widgets.

## 0.2.1 (2026-11-06)

- Añadido el fichero `LICENSE` (GPL-3.0-or-later), incluido también en el
  paquete de PyPI.
- Sin cambios funcionales respecto a la 0.2.0.

## 0.2.0 (2026-11-06)

- Nuevo widget **Predicción vía Regresión**: pronostica una serie temporal con
  cualquier learner de regresión del panel Model de Orange sobre los lags de la
  serie y, opcionalmente, de las variables exógenas. Compatible con *Model
  Evaluation* de Orange3-Timeseries para compararlo con ARIMA y VAR.

## 0.1.0

Primera versión (solo en PyPI, anterior al repositorio), con el widget
**Variables Lag/Lead**: genera variables desplazadas hacia el pasado o el futuro a
partir de una serie temporal de Orange3-Timeseries.
