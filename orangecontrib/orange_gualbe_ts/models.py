# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Gualberto Asencio Cortés
# Part of orange_gualbe_ts. See the LICENSE and NOTICE files for details.

import numpy as np
from scipy.stats import norm

from Orange.data import ContinuousVariable, Domain, Table
from Orange.data.util import get_unique_names
from orangecontrib.timeseries.models import _BaseModel


class _Results:
    """Contenedor mínimo compatible con lo que `_BaseModel.residuals()`
    espera encontrar en `self.results` (solo el atributo `resid`). AIC/BIC
    no tienen una definición general para un learner de regresión
    arbitrario, así que deliberadamente no se rellenan: quien los use
    (p. ej. el widget "Model Evaluation") verá un valor de error en vez de
    un número inventado."""

    def __init__(self, resid):
        self.resid = resid


class RegressionForecaster(_BaseModel):
    """Autorregresión (AR) genérica sobre un ``Orange.base.Learner`` de
    regresión arbitrario (kNN, Árbol, Regresión Lineal, Bosque Aleatorio,
    ...), en vez de un método de ajuste fijo como usan ARIMA (mínimos
    cuadrados/máxima verosimilitud) o VAR.

    Cada valor de la serie se predice a partir de sus propios `ar_order`
    valores anteriores (lags) y, opcionalmente (si `exog_ar_order > 0`),
    también de los `exog_ar_order` valores anteriores de las demás
    variables de la tabla de entrada (todas menos la temporal y la
    variable objetivo): se construye una tabla de entrenamiento con esos
    lags como atributos y se entrena el learner recibido igual que haría
    el widget "Predictions" de Orange.

    El pronóstico a varios pasos es recursivo: se predice un paso, se añade
    el valor predicho al historial como si fuera dato real, y se repite
    hasta completar los pasos pedidos — igual que hacen ARIMA/VAR. Para
    las variables exógenas (de las que no hay forma de conocer valores
    futuros reales) se asume que cada una mantiene su último valor
    observado a partir del final de los datos de entrada ("carry
    forward"): sus lags siguen siendo los valores reales mientras estén
    disponibles, y pasan a repetir el último valor real en cuanto el
    horizonte de predicción los sobrepasa.

    El intervalo de confianza es una aproximación genérica: al contrario
    que ARIMA/VAR, un learner de regresión arbitrario no tiene una fórmula
    cerrada para la incertidumbre de la predicción, así que se usa la
    desviación típica de los residuos dentro de muestra, ensanchada con la
    raíz cuadrada del horizonte (mismo crecimiento que un paseo aleatorio).
    """

    def __init__(self, regression_learner, ar_order=3, exog_ar_order=0):
        super().__init__()
        self.regression_learner = regression_learner
        self.ar_order = ar_order
        self.exog_ar_order = exog_ar_order
        # Conservador: aun sin saber si los datos traeran variables
        # exogenas, `max_order` (usado por Model Evaluation para calcular
        # cuantas filas hacen falta) debe reflejar el peor caso.
        self.order = (max(ar_order, exog_ar_order),)
        self._domain = None
        self._fitted_insample = None
        self._resid_std = 0.0
        self._last_window = None
        self._exog_vars = []
        self._last_exog_windows = []

    def __str__(self):
        name = getattr(self.regression_learner, 'name', None) \
            or str(self.regression_learner)
        extra = ', AR exog={}'.format(self.exog_ar_order) \
            if self.exog_ar_order else ''
        return 'Regresión ({}, AR={}{})'.format(name, self.ar_order, extra)

    def fit(self, endog, exog=None):
        time_var = None
        if isinstance(endog, Table):
            assert exog is None
            y, X_full = self._orange_arrays(endog)
            attrs = list(endog.domain.attributes)
            time_var = getattr(endog, 'time_variable', None)
            exog_idx = [i for i, v in enumerate(attrs) if v is not time_var]
            self._exog_vars = [attrs[i] for i in exog_idx]
            X_exog = X_full[:, exog_idx] if exog_idx else \
                np.zeros((len(y), 0))
        else:
            y = np.asarray(endog, dtype=float)
            X_exog = np.zeros((len(y), 0))
            self._exog_vars = []

        y = np.asarray(y, dtype=float)
        p = self.ar_order
        q = self.exog_ar_order
        m = len(self._exog_vars)
        use_exog = m > 0 and q > 0
        n = len(y)
        start = max(p, q) if use_exog else p
        if n <= start:
            raise ValueError(
                'La serie tiene {} valor(es); hacen falta más de {} '
                '(el mayor de los órdenes autorregresivos elegidos) para '
                'entrenar.'.format(n, start))

        self._endog = y

        used_names = ['lag{}'.format(k) for k in range(1, p + 1)]
        lag_vars = [ContinuousVariable(name) for name in used_names]
        target_lag_cols = [y[start - k:n - k] for k in range(1, p + 1)]

        exog_lag_vars = []
        exog_lag_cols = []
        if use_exog:
            for j, var in enumerate(self._exog_vars):
                col = X_exog[:, j]
                for k in range(1, q + 1):
                    name = get_unique_names(
                        used_names, '{}_t-{}'.format(var.name, k))
                    used_names.append(name)
                    exog_lag_vars.append(ContinuousVariable(name))
                    exog_lag_cols.append(col[start - k:n - k])

        target_var = ContinuousVariable('target')
        domain = Domain(lag_vars + exog_lag_vars, target_var)
        X = np.column_stack(target_lag_cols + exog_lag_cols)
        target = y[start:]
        train_table = Table.from_numpy(domain, X, target)

        fitted_model = self.regression_learner(train_table)

        self.model = fitted_model
        self._domain = domain
        self._fitted_insample = np.asarray(
            fitted_model(train_table), dtype=float)
        resid = target - self._fitted_insample
        self.results = _Results(resid=resid)
        self._resid_std = (
            float(np.std(resid, ddof=1)) if len(resid) > 1 else 0.0)
        self._last_window = y[-p:].tolist()
        self._last_exog_windows = (
            [X_exog[-q:, j].tolist() for j in range(m)] if use_exog else [])
        return self

    def _fittedvalues(self):
        return self._fitted_insample

    def _predict(self, steps, exog, alpha):
        p = self.ar_order
        q = self.exog_ar_order
        use_exog = bool(self._last_exog_windows) and q > 0
        window = list(self._last_window)
        exog_windows = [list(w) for w in self._last_exog_windows]

        forecasts = []
        for _ in range(steps):
            # Lags mas recientes primero: [y_{t-1}, y_{t-2}, ..., y_{t-p}],
            # mismo orden de columnas que en el entrenamiento.
            feats = window[-1:-p - 1:-1]
            if use_exog:
                for ew in exog_windows:
                    feats = feats + ew[-1:-q - 1:-1]
            feats = np.array(feats, dtype=float).reshape(1, -1)
            row_table = Table.from_numpy(
                self._domain, feats, np.full(1, np.nan))
            pred = float(np.asarray(self.model(row_table)).ravel()[0])
            forecasts.append(pred)
            window.append(pred)
            if use_exog:
                # No se conoce el valor futuro real de las variables
                # exogenas: se mantiene ("carry forward") el ultimo valor
                # conocido/asumido de cada una.
                for ew in exog_windows:
                    ew.append(ew[-1])

        forecast = np.asarray(forecasts)
        z = norm.ppf(1 - alpha / 2)
        horizon = np.arange(1, steps + 1)
        err = z * self._resid_std * np.sqrt(horizon)
        return np.asarray([forecast, forecast - err, forecast + err])
