.. _predicción vía regresión:

Predicción vía Regresión
============================

Pronostica una serie temporal aplicando un algoritmo de **regresión**
cualquiera del panel "Model" de Orange (kNN, Árbol, Regresión Lineal,
Bosque Aleatorio, ...) sobre los propios valores anteriores de la serie
(*lags*), en vez de un método de ajuste fijo como usan los widgets
**ARIMA Model** o **VAR Model**.

Descripción
-----------

El widget funciona en cuanto a entradas y salidas de forma análoga a
**ARIMA Model** y **VAR Model**: recibe una serie temporal, ajusta un
modelo, y produce un pronóstico a futuro más los valores ajustados y los
residuos dentro de muestra. Su salida "Time series model" se puede
conectar a **Model Evaluation** para comparar sus errores con los de
ARIMA y VAR sobre los mismos datos.

A diferencia de ARIMA/VAR, el algoritmo de ajuste no es fijo: se recibe
como una conexión de entrada adicional, **"Learner"**, a la que se puede
conectar cualquier widget de regresión del panel "Model" de Orange
(kNN, Árbol, Regresión Lineal, Bosque Aleatorio, SVM, Red Neuronal...),
con la configuración que traiga ese widget.

Cómo se entrena
------------------

Para un orden autorregresivo **T** configurado en el widget, cada valor
de la serie se predice a partir de sus **T** valores anteriores: se
construye una tabla con esos T lags como atributos, y se entrena el
learner conectado sobre ella — el mismo procedimiento que haría el
widget **Predictions** de Orange con un learner cualquiera, pero con
lags de la propia serie como atributos en vez de columnas ya existentes.

Si además se configura un **orden autorregresivo en variables exógenas**
mayor que 0 (llamémoslo **Tx**), se añaden también, para cada una de las
demás variables de la tabla de entrada (todas menos la temporal y la
variable objetivo), sus Tx valores anteriores como atributos
adicionales — por ejemplo, con Tx=2 y una variable "Temperatura" en la
tabla, se añaden ``Temperatura_t-1`` y ``Temperatura_t-2``. Con Tx=0 (el
valor por defecto), el widget funciona exactamente igual que sin esta
opción: solo usa los lags de la propia serie objetivo.

El pronóstico a varios pasos es **recursivo**: se predice un paso, el
valor predicho se añade al historial como si fuera dato real, y se
repite hasta completar los pasos pedidos. Es el mismo principio que usan
ARIMA y VAR para pronosticar más de un paso adelante.

**Variables exógenas más allá del primer paso de pronóstico:** el valor
real de una variable exógena en el futuro no se conoce (a diferencia de
la propia serie objetivo, que sí se puede "predecir recursivamente"). El
primer paso de pronóstico sí usa valores reales de las variables
exógenas (son datos ya observados), pero a partir del segundo paso el
widget asume que cada variable exógena **mantiene su último valor
observado** ("carry forward"). Es una simplificación razonable a corto
plazo, pero su precisión se degrada cuanto más rápido cambie realmente
la variable exógena y más lejano sea el horizonte de predicción.

Entradas
--------

- **Time series**: una serie temporal con una variable objetivo (target)
  continua definida — la serie a pronosticar.
- **Learner**: un learner de regresión de Orange (salida "Learner" de
  cualquier widget del panel "Model": kNN, Árbol, Regresión Lineal,
  Bosque Aleatorio, etc.), con la configuración que traiga ese widget.
  Sin esta conexión, el widget no puede ajustar ningún modelo.

Salidas
-------

- **Time series model**: el modelo (sin ajustar) — se puede conectar a
  **Model Evaluation** para comparar contra ARIMA, VAR u otras
  instancias de este mismo widget con distinto learner u orden
  autorregresivo.
- **Forecast**: el pronóstico a futuro, con los "Pasos de pronóstico"
  configurados, la media y el intervalo de confianza.
- **Fitted values**: los valores ajustados dentro de muestra (empiezan
  en la fila T, ya que las primeras T filas no tienen suficientes lags
  anteriores para predecir).
- **Residuals**: los residuos (valor real − valor ajustado) dentro de
  muestra.

Parámetros
----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Parámetro
     - Qué hace
   * - **Orden autorregresivo (número de lags)**
     - Cuántos valores anteriores de la serie se usan como atributos
       para predecir el siguiente. Equivalente al **p** de ARIMA o al
       **"Maximum auto-regression order"** de VAR, pero aplicado a un
       learner de regresión arbitrario en vez de mínimos cuadrados.
   * - **Orden autorregresivo en variables exógenas (número de lags)**
     - Cuántos valores anteriores de las **demás** variables de la
       tabla (no la objetivo, no la temporal) se añaden también como
       atributos. Con 0 (por defecto) no se añade ninguno y el widget
       se comporta igual que si esta opción no existiera.
   * - **Forecast steps ahead**
     - Número de pasos futuros a pronosticar (heredado del mismo control
       que usan ARIMA y VAR).
   * - **Confidence intervals**
     - Nivel de confianza del intervalo de pronóstico (heredado del
       mismo control que usan ARIMA y VAR).

Sobre el intervalo de confianza
-----------------------------------

A diferencia de ARIMA y VAR, un learner de regresión arbitrario (por
ejemplo, un Bosque Aleatorio) no tiene una fórmula estadística cerrada
para la incertidumbre de sus predicciones. El intervalo de confianza que
ofrece este widget es una **aproximación**: se basa en la desviación
típica de los residuos dentro de muestra, ensanchada con la raíz
cuadrada del horizonte de predicción (el mismo crecimiento que la
incertidumbre de un paseo aleatorio). Es una aproximación razonable,
pero no tiene el mismo respaldo estadístico que los intervalos de
ARIMA/VAR — trátalo como una referencia aproximada, no como un
resultado exacto.

Por la misma razón, si conectas la salida de este widget a un widget
que muestre AIC/BIC (como la tabla de **Model Evaluation**), esas dos
columnas aparecerán como error para este modelo: son criterios de
información basados en una verosimilitud estadística que un learner de
regresión genérico (kNN, árboles, bosques...) no define. El resto de
métricas (RMSE, MAE, MAPE, POCID, R²) sí se calculan con normalidad.

Notas importantes
------------------

- El learner conectado debe admitir un problema de regresión (variable
  objetivo continua) — todos los algoritmos del panel "Model" de Orange
  (kNN, Árbol, Regresión Lineal, Bosque Aleatorio, SVM, Red Neuronal...)
  se adaptan automáticamente al tipo de variable objetivo, así que
  cualquiera de ellos funciona sin configuración adicional.
- La serie de entrada debe tener más filas que el mayor de los dos
  órdenes autorregresivos elegidos; si no, el widget avisa con un error
  explícito.
- Si se activa el orden autorregresivo en variables exógenas pero la
  tabla de entrada no tiene ninguna variable aparte de la temporal y la
  objetivo, el widget avisa de que esa opción no tiene efecto.
- A diferencia de ARIMA, este widget no tiene una segunda entrada para
  proporcionar valores futuros reales de variables exógenas: más allá
  del primer paso de pronóstico, se asume que cada variable exógena
  mantiene su último valor observado (ver más arriba).
