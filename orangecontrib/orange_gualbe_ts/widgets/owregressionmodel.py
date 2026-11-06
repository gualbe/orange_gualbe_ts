from AnyQt.QtCore import Qt

from orangewidget.utils.widgetpreview import WidgetPreview

from Orange.base import Learner
from Orange.widgets import gui, settings
from Orange.widgets.widget import Input, Msg

from orangecontrib.timeseries import Timeseries
from orangecontrib.timeseries.widgets._owmodel import OWBaseModel

from orangecontrib.orange_gualbe_ts.models import RegressionForecaster


class OWRegressionModel(OWBaseModel):
    name = "Predicción vía Regresión"
    description = ("Pronostica una serie temporal aplicando un algoritmo de "
                    "regresión de Orange (kNN, Árbol, Regresión Lineal, "
                    "Bosque Aleatorio...) sobre sus propios valores "
                    "anteriores (lags).")
    icon = "icons/owregressionmodel.svg"
    priority = 20
    keywords = ("regresión, prediccion, forecast, autorregresion, learner, "
               "series temporales")

    ar_order = settings.Setting(3)
    exog_ar_order = settings.Setting(0)

    class Inputs(OWBaseModel.Inputs):
        learner = Input("Learner", Learner)

    class Error(OWBaseModel.Error):
        no_learner = Msg(
            "Conecta un widget de aprendizaje (Learner) de regresión a la "
            "entrada 'Learner' (por ejemplo, kNN, Árbol, Regresión Lineal "
            "o Bosque Aleatorio).")

    class Warning(OWBaseModel.Warning):
        no_exog_variables = Msg(
            "El orden autorregresivo en variables exógenas no tiene "
            "efecto: la tabla de entrada no tiene ninguna variable aparte "
            "de la temporal y la variable objetivo.")

    def __init__(self):
        self.regression_learner = None
        self.learner_label = None
        super().__init__()

    @Inputs.learner
    def set_learner(self, learner):
        self.regression_learner = learner
        self._update_learner_label()
        self.apply.deferred()

    def _update_learner_label(self):
        if self.regression_learner is None:
            self.learner_label.setText(
                "Ningún learner conectado a la entrada 'Learner'.")
        else:
            self.learner_label.setText(
                "Learner conectado: {}".format(self.regression_learner.name))

    def add_main_layout(self):
        box = gui.vBox(self.controlArea, "Parámetros")
        gui.spin(
            box, self, "ar_order", 1, 100,
            label="Orden autorregresivo (número de lags):",
            alignment=Qt.AlignRight, controlWidth=50,
            callback=self.apply.deferred)
        gui.spin(
            box, self, "exog_ar_order", 0, 100,
            label="Orden autorregresivo en variables exógenas "
                 "(número de lags):",
            alignment=Qt.AlignRight, controlWidth=50,
            callback=self.apply.deferred)
        self.learner_label = gui.widgetLabel(box, "")
        self._update_learner_label()

    def is_data_valid(self):
        self.Error.no_learner.clear()
        self.Warning.no_exog_variables.clear()
        if not super().is_data_valid():
            return False
        if self.regression_learner is None:
            self.Error.no_learner()
            return False
        if self.exog_ar_order > 0:
            n_exog = sum(1 for var in self.data.domain.attributes
                        if var is not self.data.time_variable)
            self.Warning.no_exog_variables(shown=n_exog == 0)
        return True

    def create_learner(self):
        if self.regression_learner is None:
            return None
        return RegressionForecaster(
            self.regression_learner, self.ar_order, self.exog_ar_order)

    def update_learner(self):
        # A diferencia de ARIMA/VAR, aqui `create_learner()` puede devolver
        # None (todavia no hay Learner conectado); OWBaseModel.update_learner
        # no contempla ese caso y revienta al hacer `learner.name = ...`.
        learner = self.learner = self.create_learner()
        if learner is not None:
            self.name_lineedit.setPlaceholderText(str(learner))
            learner.name = self.learner_name or str(learner)
        else:
            self.name_lineedit.setPlaceholderText("")
        self.Outputs.learner.send(learner)

    def send_report(self):
        super().send_report()
        self.report_items((
            ("Orden autorregresivo (lags)", self.ar_order),
            ("Orden autorregresivo en variables exógenas",
             self.exog_ar_order or "0 (desactivado)"),
        ))


if __name__ == "__main__":  # pragma: no cover
    import numpy as np
    from Orange.data import Domain, ContinuousVariable, TimeVariable
    from Orange.modelling import RandomForestLearner

    def _demo_data():
        n = 60
        t = np.arange(n, dtype=float)
        y = np.sin(t / 5) * 10 + t * 0.2
        time_var = TimeVariable("t")
        target = ContinuousVariable("y")
        domain = Domain([time_var], target)
        ts = Timeseries.from_numpy(
            domain, t.reshape(-1, 1), y, time_attr=time_var)
        return ts

    WidgetPreview(OWRegressionModel).run(
        set_data=_demo_data(), set_learner=RandomForestLearner())
