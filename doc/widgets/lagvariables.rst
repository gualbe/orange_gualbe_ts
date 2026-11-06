.. _variables lag/lead:

Variables Lag/Lead
=====================

Genera nuevas variables desplazadas en el tiempo (*lag*: valores del
pasado; *lead*: valores del futuro) a partir de una serie temporal, y
las **agrega** a la tabla, conservando las variables originales.

Descripción
-----------

El widget funciona por acumulación de **operaciones**: cada operación
especifica un conjunto de variables, un tamaño de ventana **T** (número
de filas) y una dirección (pasado o futuro). Las operaciones se van
añadiendo a una lista y **no se ejecutan hasta que se pulsa "Aplicar"**.

Una operación con ventana **T** no genera una única variable, sino
**T variables**, una por cada desplazamiento de 1 a T filas. Por
ejemplo, una operación "Pasado" con T=3 sobre una variable ``Pepe``
genera ``Pepe_t-1``, ``Pepe_t-2`` y ``Pepe_t-3``.

Este comportamiento es análogo a las funciones de ventana ``LAG()`` y
``LEAD()`` de SQL: ``LAG(N)`` toma el valor de N filas atrás y
``LEAD(N)`` el de N filas adelante, dejando un valor ausente donde no
hay dato disponible (por ejemplo, las primeras filas de un ``LAG``).

Entradas
--------

- **Time series**: una tabla de tipo ``Timeseries`` con una variable
  temporal definida — es decir, que ya ha pasado por el widget
  **Form Timeseries** (u otro widget de Orange3-Timeseries que también
  produzca una serie temporal, como *Difference* o *Moving Transform*).
  El widget no acepta una tabla de datos genérica sin marca temporal.

Salidas
-------

- **Time series**: la misma serie temporal de entrada, con las
  variables lag/lead generadas **añadidas** — todas las variables
  originales (incluida la temporal y los metadatos) se conservan sin
  cambios.

1. Elige las variables a considerar
------------------------------------

La lista muestra todas las variables de la tabla de entrada, excepto la
variable temporal (no tiene sentido desplazarla: es la referencia de
orden de las filas). Se pueden seleccionar varias a la vez, o usar los
botones **"Seleccionar todas"** / **"Deseleccionar todas"**.

2. Configura la ventana y la dirección
-----------------------------------------

- **Tamaño de la ventana (T)**: número de variables desplazadas a
  generar por cada variable elegida.
- **Dirección**:

  .. list-table::
     :header-rows: 1
     :widths: 20 80

     * - Dirección
       - Qué genera
     * - **Pasado (LAG)**
       - T variables ``<var>_t-1`` ... ``<var>_t-T``. La fila *i* de
         ``<var>_t-k`` toma el valor de la fila *i − k* de la variable
         original (equivalente a ``shift(k)`` en pandas). Las primeras
         k filas de cada una quedan sin dato.
     * - **Futuro (LEAD)**
       - T variables ``<var>_t+1`` ... ``<var>_t+T``. La fila *i* de
         ``<var>_t+k`` toma el valor de la fila *i + k* (equivalente a
         ``shift(-k)``). Las últimas k filas quedan sin dato.

3. Añade la operación a la lista
-----------------------------------

El botón **"Añadir operación a la lista"** guarda la combinación de
variables, ventana y dirección actual como una nueva operación
pendiente, y permite configurar inmediatamente otra distinta — por
ejemplo, una operación "Pasado" y otra "Futuro" sobre la misma
variable. La lista se puede editar con **"Eliminar seleccionada"** y
**"Vaciar lista"**.

Si dos operaciones afectan a la misma variable en la misma dirección
(por ejemplo, T=2 y T=5 en "Pasado" sobre la misma variable), no se
duplican columnas: se genera una única serie de variables hasta el T
mayor de las dos (en este ejemplo, ``t-1`` a ``t-5``).

4. Aplica
---------

El botón **"Aplicar"** ejecuta todas las operaciones de la lista y
genera la tabla de salida. Ningún cambio en los datos de entrada ni en
la lista de operaciones se refleja en la salida hasta que se vuelve a
pulsar "Aplicar" — el widget avisa cuando la salida ha quedado
desactualizada. Si la lista de operaciones está vacía, la salida es la
tabla de entrada sin cambios.

Nombres y orden de las variables generadas
---------------------------------------------

Cada variable generada se llama ``<nombre original>_t-<k>`` (pasado) o
``<nombre original>_t+<k>`` (futuro). Si el nombre ya existe, Orange
añade automáticamente un sufijo numérico entre paréntesis para evitar
duplicados.

El orden de las variables en la tabla de salida es siempre:

1. Primero, las variables que **no** se han elegido en ninguna
   operación, sin modificar, en su orden original.
2. Después, para cada variable original que sí se ha desplazado (en su
   orden original), un bloque ordenado temporalmente: del pasado más
   lejano al futuro más lejano, con la variable original en el centro.
   Por ejemplo, con T=3 en ambas direcciones sobre ``Pepe``::

       Pepe_t-3, Pepe_t-2, Pepe_t-1, Pepe, Pepe_t+1, Pepe_t+2, Pepe_t+3

Notas importantes
------------------

- Los datos de entrada deben ser una serie temporal con variable
  temporal definida (salida de **Form Timeseries** u otro widget
  equivalente).
- Las filas sin dato disponible tras el desplazamiento quedan con un
  valor ausente, compatible con el resto de widgets de Orange.
- Las variables a desplazar deben ser atributos o la variable objetivo
  de la tabla (no metadatos).
