# orange_gualbe_ts — Utilidades de Series Temporales

Add-on de Orange Data Mining con utilidades para series temporales, construido
sobre Orange3-Timeseries. Responde siempre en español de España. Esta carpeta es
la de la sesión de trabajo `ts-mant`; la coordinadora del grupo vive en
`../orange-hub` y te manda las peticiones.

Antes de tocar widgets, ayuda o empaquetado lee
`../orange-hub/conocimiento/trampas-orange.md`.

## Identidad

- Distribución y namespace: `orange_gualbe_ts` / `orangecontrib.orange_gualbe_ts`
  (en PyPI normalizado como `orange-gualbe-ts`).
- Categoría: «Utilidades de Series Temporales», color `#3EA6A6`.
- Dependencias: `Orange3>=3.32.0`, **`Orange3-Timeseries>=0.5.0`** (dependencia
  dura: usa su clase `Timeseries` y su `OWBaseModel`).
- Repo público https://github.com/gualbe/orange_gualbe_ts (rama `main`, fuente de
  verdad) · PyPI https://pypi.org/project/orange-gualbe-ts/
- Ayuda en castellano (`doc/conf.py`: `language = "es"`).

## Widgets

### Variables Lag/Lead (`owlagvariables.py`, `OWLagVariables`)

- Entrada `Input("Time series", Timeseries)`, no `Table`: así el lienzo solo deja
  conectar widgets que producen `Timeseries` (Form Timeseries, Difference…).
- Lista de operaciones (estilo «Select Rows»): variables + tamaño de ventana T +
  dirección (pasado/futuro) → «Añadir operación». Nada se calcula hasta
  «Aplicar»; `Warning.stale_output` avisa de cambios sin aplicar.
- Salida: se CONSERVAN todas las variables originales y se AÑADEN T variables por
  operación (`<v>_t-1..t-T` / `<v>_t+1..t+T`), con `get_unique_names` ante
  colisiones. Operaciones repetidas sobre la misma variable y dirección se
  fusionan con el T máximo. Orden fijo: primero las variables no elegidas, luego
  por cada elegida el bloque `<v>_t-T … <v> … <v>_t+T`. `class_vars=()`. Lista
  vacía = paso a través. Relleno con `np.nan`.
- Candidatos: `attributes` + `class_vars` sin la variable temporal; las metas no.
- El `Setting` se llama `window_size` (con `window` revienta: ver trampas).

### Predicción vía Regresión (`owregressionmodel.py`, `OWRegressionModel`; modelo en `models.py`, `RegressionForecaster`)

- Hereda de `orangecontrib.timeseries.widgets._owmodel.OWBaseModel` (como ARIMA y
  VAR): entradas/salidas y controles heredados, y su salida «Time series model» es
  compatible con **Model Evaluation**. Todo widget nuevo que sea un modelo de
  series debe heredar igual.
- `RegressionForecaster` subclasea `_BaseModel` y sobrescribe `fit()`: tabla con
  `ar_order` lags (`lag1..lagT`) y ajuste del `Learner` conectado (cualquiera del
  panel Model). Pronóstico recursivo a varios pasos. Solo sobrescribe
  `_fittedvalues()` y `_predict()`.
- Intervalo de confianza aproximado: σ de residuos × `norm.ppf(1-α/2)` ×
  √horizonte (documentado como aproximación). AIC/BIC no se rellenan a propósito.
- Exógenas: `exog_ar_order` (0 = desactivado) añade `<var>_t-k`; desde el segundo
  paso de pronóstico cada exógena se congela en su último valor («carry
  forward»). Limitación inherente y documentada en
  `doc/widgets/regressionmodel.rst`. `self.order = max(ar_order, exog_ar_order)`.
  `Warning.no_exog_variables` si no hay exógenas.
- `update_learner()` está sobrescrito con guarda `if learner is not None` (el
  heredado revienta sin learner conectado).
- El `RuntimeWarning: subclassing of widget classes is deprecated` viene de
  `OWBaseModel`; no es nuestro.

## Estructura

- `orangecontrib/orange_gualbe_ts/`: `models.py`, `widgets/` (widgets e `icons/`).
- `doc/`: fuentes Sphinx; HTML en `orangecontrib/orange_gualbe_ts/_help/html`
  (ignorado en git).
- `assets/`: imágenes del README, regenerables con
  `python assets/generar_imagenes.py --capturas`.
- `tests/`: todavía no hay tests propios; `../orange-hub/scripts/probar.sh` hace al
  menos la prueba de humo.

## Pruebas

```bash
../orange-hub/scripts/probar.sh .            # humo + tests/test_*.py + ayuda + paquete
../orange-hub/scripts/probar.sh . --rapido   # solo humo y tests, en Orange.app
```

Cada `tests/test_*.py` es un script ejecutable con el Python de Orange que sale con
código distinto de 0 si algo falla. Para el flujo completo, alimentar con la salida
real de «Form Timeseries» y probar `orangecontrib.timeseries.functions.model_evaluation()`
con una mezcla de ARIMA, VAR y `RegressionForecaster`.

## Ficheros comunes con los otros add-ons

Iguales en todos salvo el nombre del paquete: `.github/workflows/publish.yml`,
`.gitignore`, `LICENSE`, `doc/conf.py` (salvo idioma y estáticos), la estructura de
`pyproject.toml` y la cabecera de `widgets/__init__.py` (`WIDGET_HELP_PATH`). Si un
cambio toca uno de ellos, dilo en el informe a la coordinadora.
`../orange-hub/scripts/comparar.sh <ruta>` muestra cuánto difiere.

## Cierre obligatorio de cada mantenimiento

Skill `orange-release`. En resumen: pruebas en verde → `version` en
`pyproject.toml` (parche para correcciones, menor para funciones nuevas) →
sección `## X.Y.Z (AAAA-MM-DD)` en `CHANGELOG.md` → si cambia un widget, su ayuda y
el README (y las imágenes) → commit en `main` («Descripción (X.Y.Z)») →
`../orange-hub/scripts/publicar.sh .` (push, release `vX.Y.Z`, CI a PyPI e
instalación en Orange.app y Orange-Gualbe.app). Los cambios que solo afectan al
repo (README de GitHub, CLAUDE.md, CHANGELOG) no necesitan versión nueva. Las notas
de instalación mencionan `pip install Orange3-Timeseries orange_gualbe_ts`.

## Pendientes conocidos

- Falta la comprobación visual del usuario en el lienzo (Form Timeseries + los dos
  widgets + Model Evaluation, incluido el orden exógeno).
- Mejora natural si se pide: entrada «Exogenous data» (como ARIMA) para dar valores
  futuros reales de las exógenas en vez del «carry forward».
- Ideas de widgets: ventanas móviles adicionales, relleno/interpolación de huecos,
  variables de calendario (día de la semana, festivos…).
