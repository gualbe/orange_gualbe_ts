# orange_gualbe_ts

Add-on de **utilidades para series temporales** para
[Orange Data Mining](https://orangedatamining.com/).

Añade una nueva categoría "Utilidades de Series Temporales" al lienzo de
Orange, con widgets que trabajan sobre series temporales (tablas de tipo
`Timeseries`) generadas por el add-on
[Orange3-Timeseries](https://orange3-timeseries.readthedocs.io/), del
que este add-on depende.

## Widgets incluidos

### Variables Lag/Lead

Genera nuevas variables desplazadas en el tiempo (*lag*: valores del
pasado; *lead*: valores del futuro) y las **agrega** a la tabla de
entrada, conservando todas las variables originales.

- **Entrada**: una tabla `Timeseries` con variable temporal definida —
  es decir, que ya ha pasado por el widget **Form Timeseries** (u otro
  widget de Orange3-Timeseries que también produzca una serie temporal).
- El widget acumula **operaciones** (variables a considerar + tamaño de
  ventana T + dirección pasado/futuro) en una lista, sin ejecutarlas.
  Al pulsar **Aplicar**, se ejecutan todas.
- Una operación con ventana **T** genera **T variables**, no solo una:
  por ejemplo, T=3 en "Pasado" sobre `Pepe` genera `Pepe_t-1`,
  `Pepe_t-2` y `Pepe_t-3`.
- Las filas sin dato disponible tras el desplazamiento (por ejemplo, las
  primeras filas de un `LAG`) quedan con un valor ausente compatible con
  Orange.
- La salida conserva **todas** las variables originales (incluida la
  temporal y los metadatos) y añade las variables lag/lead generadas,
  con un orden de columnas fijo: primero las variables no elegidas para
  ninguna operación (en su orden original), y luego, para cada variable
  sí elegida (en su orden original), un bloque temporal del pasado más
  lejano al futuro más lejano con la variable original en el centro —
  p. ej. `Pepe_t-3, Pepe_t-2, Pepe_t-1, Pepe, Pepe_t+1, Pepe_t+2, Pepe_t+3`.

### Predicción vía Regresión

Pronostica una serie temporal aplicando un algoritmo de **regresión**
cualquiera del panel "Model" de Orange (kNN, Árbol, Regresión Lineal,
Bosque Aleatorio, SVM, Red Neuronal...) sobre los propios valores
anteriores de la serie (lags), en vez de un método de ajuste fijo como
usan **ARIMA Model** o **VAR Model** — de hecho, en cuanto a entradas y
salidas funciona igual que esos dos widgets, así que se puede conectar
a **Model Evaluation** para comparar sus errores con los de ARIMA/VAR.

- **Entradas**: "Time series" (la serie a pronosticar, con target
  continuo) y **"Learner"** (el algoritmo de regresión a usar — la
  salida "Learner" de cualquier widget del panel "Model").
- **Salidas**: "Time series model" (para Model Evaluation), "Forecast"
  (pronóstico + intervalo de confianza), "Fitted values" y "Residuals".
- Parámetros propios: **orden autorregresivo (T)** — cuántos valores
  anteriores de la serie se usan como atributos para predecir el
  siguiente — y **orden autorregresivo en variables exógenas (Tx)** —
  opcional (0 por defecto): si es mayor que 0, añade también los Tx
  valores anteriores de cada una de las demás variables de la tabla
  (no la temporal, no la objetivo) como atributos adicionales. "Forecast
  steps ahead" y "Confidence intervals" son los mismos controles que
  usan ARIMA y VAR.
- El pronóstico a varios pasos es recursivo (igual que ARIMA/VAR): se
  predice un paso, se añade al historial, y se repite. Para las
  variables exógenas (Tx > 0), como no se conoce su valor real futuro,
  a partir del segundo paso se asume que cada una mantiene su último
  valor observado ("carry forward").
- El intervalo de confianza es una **aproximación** (desviación típica
  de los residuos, ensanchada con la raíz del horizonte) — un learner
  de regresión genérico no tiene una fórmula cerrada como ARIMA/VAR.
  Por la misma razón, AIC/BIC no se calculan (aparecen como error si se
  usa junto a **Model Evaluation**); el resto de métricas sí.

Ambos widgets integran su ayuda con el **sistema de ayuda nativo de
Orange**: selecciona el widget en el lienzo y pulsa **F1**, o haz clic
en el icono **"?"** de la barra de estado del widget.

## Instalación para desarrollo

```bash
python -m venv .venv
source .venv/bin/activate
pip install Orange3 PyQt5 Orange3-Timeseries
pip install -e .
```

Abrir Orange Canvas con el add-on instalado:

```bash
python -m Orange.canvas
```

Los widgets aparecerán en el lienzo bajo la categoría "Utilidades de
Series Temporales". Para conectar **Variables Lag/Lead** o la entrada
"Time series" de **Predicción vía Regresión**, primero se necesita un
widget que produzca una serie temporal (por ejemplo, **Form Timeseries**
del add-on Orange3-Timeseries) — ambas entradas rechazan a nivel de
conexión cualquier tabla que no sea de tipo `Timeseries`. La entrada
"Learner" de **Predicción vía Regresión** acepta cualquier widget del
panel "Model" de Orange (kNN, Árbol, Regresión Lineal, Bosque
Aleatorio...).

## Ayuda de los widgets (documentación)

La ayuda que se abre con F1/"?" se genera con [Sphinx](https://www.sphinx-doc.org/)
a partir de los archivos en `doc/`. Cada widget tiene una página en
`doc/widgets/<nombre>.rst`, con una etiqueta al inicio que debe coincidir
**exactamente** con el nombre del widget en minúsculas (por ejemplo,
`.. _variables lag/lead:` para el widget `name = "Variables Lag/Lead"`) —
así es como Orange encuentra la página correcta.

El HTML generado se guarda **dentro del propio paquete**
(`orangecontrib/orange_gualbe_ts/_help/html/`), no en `doc/build/`, para
que la ayuda funcione también en instalaciones normales desde PyPI (no
solo en modo editable) — se declara como `package-data` en
`pyproject.toml` y viaja dentro del wheel.

Para (re)generar la documentación tras editar o añadir un widget:

```bash
pip install sphinx
python -m sphinx -b html doc orangecontrib/orange_gualbe_ts/_help/html
```

`orangecontrib/orange_gualbe_ts/_help/` no se versiona en el control de
código fuente: es un artefacto generado, igual que `dist/`. **Debe
reconstruirse antes de cada `python -m build`** (si no, el paquete se
publica con la documentación desactualizada o sin ella).

## Publicar en PyPI

```bash
python -m sphinx -b html doc orangecontrib/orange_gualbe_ts/_help/html
python -m pip install --upgrade build twine
python -m build
twine check dist/*
twine upload dist/*
```

`twine upload` pedirá tu usuario (`__token__`) y tu API token de PyPI.
Para la primera publicación de un proyecto nuevo, el token debe tener
ámbito "Entire account" (uno limitado a un proyecto concreto no puede
crearlo).

## Requisitos de los datos de entrada

- La tabla de entrada debe ser una serie temporal (`Timeseries`) con
  variable temporal definida — pásala antes por **Form Timeseries**.
- **Variables Lag/Lead**: las variables a desplazar deben ser atributos
  o la variable objetivo de la tabla (no metadatos), de cualquier tipo
  (continuas, discretas o temporales).
- **Predicción vía Regresión**: la tabla debe tener una variable
  objetivo (target) continua, y necesita un learner de regresión
  conectado a su entrada "Learner".
