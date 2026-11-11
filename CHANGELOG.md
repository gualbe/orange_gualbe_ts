# Cambios

Cada versión se publica a la vez en GitHub (release `vX.Y.Z`) y en
[PyPI](https://pypi.org/project/orange-gualbe-ts/).

## 0.2.5 (2026-11-11)

- Metadatos para Zenodo (`.zenodo.json`): cada release se archiva con DOI.
- Sin cambios funcionales en los widgets.

## 0.2.4 (2026-11-11)

- Autoría y licencia reforzadas, sin cambiar de licencia (sigue siendo
  GPL-3.0-or-later):
  - Cabecera SPDX con el copyright de Gualberto Asencio Cortés en todos los
    ficheros `.py`.
  - Nuevo fichero `NOTICE` con la autoría, la licencia y los términos adicionales
    del artículo 7 de la GPL-3 (atribución, marcado de las versiones modificadas
    y nombres «orange_gualbe», «Orange Gualbe» y «Gualbe» reservados), y los
    componentes de terceros (Orange3, Orange3-Timeseries, NumPy y SciPy; el
    método `update_learner()` adaptado de Orange3-Timeseries y los iconos de los
    esquemas del README).
  - Nuevo fichero `CITATION.cff` para citar el add-on.
  - El paquete declara la licencia con la sintaxis SPDX (PEP 639) e incluye
    `LICENSE` y `NOTICE` en el wheel y en el sdist; el autor figura con su
    nombre completo.
  - README: la sección «Licencia» pasa a «Licencia y autoría», con la política
    de nombres para forks y cómo citar.
  - Ayuda (F1): página «Licencia y autoría» y copyright del autor en el pie.
- Sin cambios funcionales en los widgets.

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
