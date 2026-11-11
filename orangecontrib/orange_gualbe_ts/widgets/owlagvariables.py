# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Gualberto Asencio Cortés
# Part of orange_gualbe_ts. See the LICENSE and NOTICE files for details.

from itertools import chain

import numpy as np

from AnyQt.QtWidgets import QListView, QListWidget, QSizePolicy

from Orange.data import Domain
from Orange.data.util import get_unique_names
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.utils.itemmodels import VariableListModel
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.widget import OWWidget, Input, Output, Msg

from orangecontrib.timeseries import Timeseries

PAST, FUTURE = range(2)
DIRECTION_LABELS = [
    "Pasado (LAG): genera T variables con los valores de 1 a T filas "
    "anteriores",
    "Futuro (LEAD): genera T variables con los valores de 1 a T filas "
    "posteriores",
]
DIRECTION_SHORT = ["LAG", "LEAD"]


def shift_column(column, offset, direction):
    """Desplaza `column` `offset` filas hacia el pasado (LAG) o el futuro
    (LEAD), rellenando con NaN las posiciones sin dato disponible."""
    n = len(column)
    out = np.full(n, np.nan, dtype=float)
    if offset <= 0 or offset >= n:
        return out if offset > 0 else column.copy()
    if direction == PAST:
        out[offset:] = column[:n - offset]
    else:
        out[:n - offset] = column[offset:]
    return out


class OWLagVariables(OWWidget):
    name = "Variables Lag/Lead"
    description = ("Genera variables desplazadas en el tiempo (lag/lead) a "
                    "partir de una serie temporal y las agrega a la tabla, "
                    "conservando las variables originales.")
    icon = "icons/owlagvariables.svg"
    priority = 10
    keywords = "lag, lead, desplazamiento, series temporales, shift, rezago"
    want_main_area = False
    resizing_enabled = True

    class Inputs:
        time_series = Input("Time series", Timeseries)

    class Outputs:
        time_series = Output("Time series", Timeseries)

    class Error(OWWidget.Error):
        no_time_variable = Msg(
            "Los datos de entrada no tienen una variable temporal "
            "definida. Pase antes los datos por el widget "
            "'Form Timeseries'.")

    class Warning(OWWidget.Warning):
        no_candidate_variables = Msg(
            "Los datos de entrada no tienen ninguna variable (aparte de "
            "la temporal) para generar variables lag/lead.")
        stale_output = Msg(
            "Los datos de entrada o la lista de operaciones han cambiado. "
            "Pulse 'Aplicar' para actualizar la salida.")

    window_size = Setting(1)
    direction = Setting(PAST)
    operations = Setting([], schema_only=True)

    def __init__(self):
        super().__init__()
        self.data = None
        self.candidates = []

        # --- Variables a considerar --------------------------------------
        vars_box = gui.vBox(self.controlArea, "Variables a considerar")
        self.var_model = VariableListModel(parent=self)
        self.var_view = QListView(
            selectionMode=QListView.ExtendedSelection)
        self.var_view.setModel(self.var_model)
        self.var_view.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.var_view.selectionModel().selectionChanged.connect(
            self._on_var_selection_changed)
        vars_box.layout().addWidget(self.var_view)

        buttons_box = gui.hBox(vars_box)
        gui.button(
            buttons_box, self, "Seleccionar todas",
            callback=self.var_view.selectAll)
        gui.button(
            buttons_box, self, "Deseleccionar todas",
            callback=self.var_view.clearSelection)

        # --- Parametros de la operacion -----------------------------------
        op_box = gui.vBox(self.controlArea, "Parámetros de la operación")
        gui.spin(
            op_box, self, "window_size", minv=1, maxv=10000, step=1,
            label="Tamaño de la ventana (T):", controlWidth=80)
        gui.radioButtons(
            op_box, self, "direction", btnLabels=DIRECTION_LABELS)

        self.add_op_button = gui.button(
            op_box, self, "Añadir operación a la lista",
            callback=self._add_operation)
        self.add_op_button.setEnabled(False)

        # --- Lista de operaciones pendientes ------------------------------
        list_box = gui.vBox(self.controlArea, "Lista de operaciones")
        self.ops_widget = QListWidget()
        self.ops_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.ops_widget.itemSelectionChanged.connect(
            self._on_op_selection_changed)
        list_box.layout().addWidget(self.ops_widget)

        list_buttons_box = gui.hBox(list_box)
        self.remove_op_button = gui.button(
            list_buttons_box, self, "Eliminar seleccionada",
            callback=self._remove_selected_operation)
        self.remove_op_button.setEnabled(False)
        self.clear_ops_button = gui.button(
            list_buttons_box, self, "Vaciar lista",
            callback=self._clear_operations)

        # --- Aplicar --------------------------------------------------------
        apply_box = gui.vBox(self.controlArea)
        self.status_label = gui.widgetLabel(apply_box, "Sin datos de entrada.")
        gui.button(
            apply_box, self, "Aplicar", callback=self._apply,
            autoDefault=True)

        self._refresh_operations_widget()
        self.clear_ops_button.setEnabled(bool(self.operations))

    # ------------------------------------------------------------------
    # Entrada de datos
    # ------------------------------------------------------------------
    @Inputs.time_series
    def set_data(self, data):
        self.Error.no_time_variable.clear()
        self.data = None
        if data is not None:
            if data.time_variable is None:
                self.Error.no_time_variable()
            else:
                self.data = data

        self._update_candidates()
        self.Outputs.time_series.send(None)
        self._update_status()

    def _update_candidates(self):
        if self.data is None:
            self.candidates = []
        else:
            time_var = self.data.time_variable
            self.candidates = [
                var for var in chain(self.data.domain.attributes,
                                     self.data.domain.class_vars)
                if var is not time_var]
        self.var_model[:] = self.candidates
        self.Warning.no_candidate_variables(
            shown=self.data is not None and not self.candidates)

    # ------------------------------------------------------------------
    # Construccion de la lista de operaciones
    # ------------------------------------------------------------------
    def _on_var_selection_changed(self):
        has_selection = bool(self.var_view.selectionModel().selectedRows())
        self.add_op_button.setEnabled(has_selection)

    def _on_op_selection_changed(self):
        self.remove_op_button.setEnabled(bool(self.ops_widget.selectedItems()))

    def _add_operation(self):
        names = [self.var_model.data(index)
                 for index in self.var_view.selectionModel().selectedRows()]
        if not names:
            return
        self.operations = self.operations + [{
            "variables": names,
            "window": int(self.window_size),
            "direction": int(self.direction),
        }]
        self._refresh_operations_widget()
        self._update_status()

    def _remove_selected_operation(self):
        row = self.ops_widget.currentRow()
        if row < 0:
            return
        self.operations = self.operations[:row] + self.operations[row + 1:]
        self._refresh_operations_widget()
        self._update_status()

    def _clear_operations(self):
        if not self.operations:
            return
        self.operations = []
        self._refresh_operations_widget()
        self._update_status()

    def _refresh_operations_widget(self):
        self.ops_widget.clear()
        for i, op in enumerate(self.operations, start=1):
            label = "{}. {}(T={}): {}".format(
                i, DIRECTION_SHORT[op["direction"]], op["window"],
                ", ".join(op["variables"]))
            self.ops_widget.addItem(label)
        self.remove_op_button.setEnabled(False)
        self.clear_ops_button.setEnabled(bool(self.operations))

    # ------------------------------------------------------------------
    # Aplicar
    # ------------------------------------------------------------------
    def _update_status(self, applied_count=None):
        self.Warning.stale_output.clear()
        if self.data is None:
            self.status_label.setText("Sin datos de entrada.")
            return
        if applied_count is None:
            self.Warning.stale_output()
            self.status_label.setText(
                "Pendiente de aplicar ({} operación(es) en la lista)."
                .format(len(self.operations)))
        elif applied_count:
            self.status_label.setText(
                "Aplicado: {} variable(s) lag/lead generada(s), añadidas "
                "a las variables originales.".format(applied_count))
        else:
            self.status_label.setText(
                "Aplicado: sin operaciones, tabla original sin cambios.")

    def _apply(self):
        self.Warning.stale_output.clear()

        if self.data is None:
            self.Outputs.time_series.send(None)
            self._update_status()
            return

        result, n_new = self._compute(self.data, self.operations)
        self.Outputs.time_series.send(result)
        self._update_status(applied_count=n_new)

    @staticmethod
    def _compute(data, operations):
        domain = data.domain
        time_var = data.time_variable
        original_vars = list(chain(domain.attributes, domain.class_vars))

        # Ventana maxima solicitada por variable y direccion: el tamano T de
        # una operacion implica generar T variables (desplazamientos 1..T),
        # asi que varias operaciones sobre la misma variable/direccion solo
        # amplian el rango (basta con quedarse con el T mayor).
        past_window = {}
        future_window = {}
        for op in operations:
            window = op["window"]
            target = past_window if op["direction"] == PAST else future_window
            for var_name in op["variables"]:
                if var_name not in domain:
                    continue
                target[var_name] = max(target.get(var_name, 0), window)

        lagged_names = set(past_window) | set(future_window)
        used_names = [var.name for var in chain(domain.variables, domain.metas)]

        out_vars = []
        out_columns = []

        # 1) Variables no escogidas para ninguna operacion, sin modificar,
        #    en su orden original.
        for var in original_vars:
            if var.name not in lagged_names:
                out_vars.append(var)
                out_columns.append(
                    np.asarray(data.get_column(var), dtype=float))

        # 2) Para cada variable laggeada (en su orden original), un bloque
        #    ordenado temporalmente: t-T, ..., t-1, original, t+1, ..., t+T.
        n_new = 0
        for var in original_vars:
            if var.name not in lagged_names:
                continue
            column = np.asarray(data.get_column(var), dtype=float)
            n_past = past_window.get(var.name, 0)
            n_future = future_window.get(var.name, 0)

            for k in range(n_past, 0, -1):
                name = get_unique_names(used_names, f"{var.name}_t-{k}")
                used_names.append(name)
                out_vars.append(var.copy(name=name, compute_value=None))
                out_columns.append(shift_column(column, k, PAST))
                n_new += 1

            out_vars.append(var)
            out_columns.append(column)

            for k in range(1, n_future + 1):
                name = get_unique_names(used_names, f"{var.name}_t+{k}")
                used_names.append(name)
                out_vars.append(var.copy(name=name, compute_value=None))
                out_columns.append(shift_column(column, k, FUTURE))
                n_new += 1

        if out_columns:
            X = np.column_stack(out_columns)
        else:
            X = np.zeros((len(data), 0), dtype=float)

        out_domain = Domain(tuple(out_vars), class_vars=(), metas=domain.metas)
        result = Timeseries.from_numpy(
            out_domain, X, Y=None, metas=data.metas, time_attr=time_var)
        return result, n_new

    def send_report(self):
        if not self.operations:
            self.report_items("Operaciones", [("Lista", "vacía")])
            return
        items = [
            ("Operación {}".format(i),
             "{}(T={}) sobre {}".format(
                 DIRECTION_SHORT[op["direction"]], op["window"],
                 ", ".join(op["variables"])))
            for i, op in enumerate(self.operations, start=1)]
        self.report_items("Operaciones", items)


if __name__ == "__main__":  # pragma: no cover
    def _demo_data():
        n = 20
        t = np.arange(n, dtype=float) * 86400.0
        x1 = np.arange(n, dtype=float)
        x2 = np.sin(np.arange(n, dtype=float))
        from Orange.data import ContinuousVariable, TimeVariable
        time_var = TimeVariable("Fecha", have_date=1, have_time=0)
        v1 = ContinuousVariable("Temperatura")
        v2 = ContinuousVariable("Presión")
        domain = Domain([time_var, v1, v2])
        ts = Timeseries.from_numpy(
            domain, np.column_stack([t, x1, x2]), time_attr=time_var)
        return ts

    WidgetPreview(OWLagVariables).run(_demo_data())
