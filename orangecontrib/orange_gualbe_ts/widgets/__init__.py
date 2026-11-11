# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Gualberto Asencio Cortés
# Part of orange_gualbe_ts. See the LICENSE and NOTICE files for details.

import os

NAME = "Utilidades de Series Temporales"
DESCRIPTION = "Widgets de utilidades para preparar y transformar series temporales."
ICON = "icons/category.svg"
BACKGROUND = "#3EA6A6"

# Ruta absoluta a la documentacion HTML generada con Sphinx a partir de las
# fuentes en doc/ (ver README: "Ayuda de los widgets"). Se empaqueta DENTRO
# del propio paquete (orangecontrib/orange_gualbe_ts/_help/html) para que
# funcione igual en instalacion editable que instalado desde PyPI - una ruta
# fuera del paquete solo existiria en este checkout de desarrollo, no en el
# wheel publicado. Se calcula con __file__ en lugar del marcador
# {DEVELOP_ROOT} de WIDGET_HELP_PATH, cuya resolucion no es fiable con
# `pip install -e .` (ver memoria de trampas tecnicas de add-ons Orange).
_HELP_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "_help", "html")
)

WIDGET_HELP_PATH = (
    (_HELP_DIR + os.sep, None),
)
