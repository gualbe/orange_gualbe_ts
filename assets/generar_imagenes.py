# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Gualberto Asencio Cortés
# Part of orange_gualbe_ts. See the LICENSE and NOTICE files for details.

"""Genera las imágenes del README (assets/*.svg y, con --capturas, assets/*.png).

Uso (desde la raíz del repo, con Orange3, PyQt5 y Orange3-Timeseries
instalados):

    python assets/generar_imagenes.py              # esquemas SVG
    python assets/generar_imagenes.py --capturas   # + capturas de los widgets

Los SVG son autocontenidos: los iconos de Orange se incrustan como data
URI, porque GitHub y PyPI muestran las imágenes como <img> y no cargan
recursos externos.
"""
import base64
import os
import sys

ASSETS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ASSETS)
OUR_ICONS = os.path.join(ROOT, "orangecontrib", "orange_gualbe_ts", "widgets", "icons")

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
TEXT = "#24292F"
MUTED = "#57606A"
FAINT = "#A0A7AF"
BORDER = "#D8DEE4"
TEAL = "#3EA6A6"
TEAL_DARK = "#1F6F6F"
PAST_BG, PAST_FG = "#DDF2EE", "#0F6E56"
FUT_BG, FUT_FG = "#FCEBD5", "#8A4B08"
EXO_BG, EXO_FG = "#FAE6E0", "#993C1D"
PRED_BG, PRED_FG = "#ECEAFD", "#3C3489"
NEUTRAL_BG = "#F2F4F6"


def orange_icon(module, name):
    mod = __import__(module, fromlist=["__file__"])
    return os.path.join(os.path.dirname(mod.__file__), "icons", name)


def data_uri(path):
    with open(path, "rb") as f:
        return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()


def icon(path, cx, cy, size):
    uri = data_uri(path)
    x, y = cx - size / 2, cy - size / 2
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" '
            f'href="{uri}" xlink:href="{uri}"/>')


def text(x, y, s, size=14, fill=TEXT, weight=400, anchor="middle", style=""):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'dominant-baseline="central"{style}>{s}</text>')


def rect(x, y, w, h, fill, stroke="none", rx=6, sw=1, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<title>{title}</title>'
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M1 1L9 5L1 9z" fill="context-stroke"/></marker></defs>'
            + rect(0.5, 0.5, w - 1, h - 1, "#FFFFFF", BORDER, rx=16)
            + body + "</svg>\n")


def save(name, content):
    with open(os.path.join(ASSETS, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("escrito", name, f"({len(content) // 1024} KB)")


def arrow(x1, y1, x2, y2, color=MUTED, width=2, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{width}"{d} marker-end="url(#ah)"/>')


# ---------------------------------------------------------------- banner
def banner():
    w, h = 860, 240
    b = []
    b.append(f'<circle cx="140" cy="120" r="78" fill="#A9DCDC" stroke="{TEAL}" stroke-width="3"/>')
    b.append(icon(os.path.join(OUR_ICONS, "category.svg"), 140, 120, 104))
    b.append(text(260, 92, "orange_gualbe_ts", 46, TEXT, 700, "start"))
    b.append(text(262, 140, "Utilidades de series temporales para Orange Data Mining",
                  21, MUTED, 400, "start"))
    chips = [("owlagvariables.svg", "Variables Lag/Lead", 220),
             ("owregressionmodel.svg", "Predicción vía Regresión", 262)]
    x = 260
    for fname, label, cw in chips:
        b.append(rect(x, 172, cw, 42, "#EAF6F6", TEAL, rx=21, sw=1.5))
        b.append(f'<circle cx="{x + 21}" cy="193" r="16" fill="#A9DCDC"/>')
        b.append(icon(os.path.join(OUR_ICONS, fname), x + 21, 193, 24))
        b.append(text(x + 44, 193, label, 16, TEAL_DARK, 600, "start"))
        x += cw + 16
    save("banner.svg", svg(w, h, "".join(b),
                           "orange_gualbe_ts: utilidades de series temporales para Orange"))


# ---------------------------------------------------------------- flujo
def flujo():
    w, h = 960, 470
    R = 30
    data_c = ("#FFD39F", "#D99A4E")
    ts_c = ("#A6D8FF", "#33AAFF")
    model_c = ("#FAC1D9", "#D9799F")
    ours_c = ("#A9DCDC", TEAL)
    nodes = {
        "file": (90, 200, "File", data_c, orange_icon("Orange.widgets.data", "File.svg")),
        "form": (250, 200, "Form Timeseries", ts_c,
                 orange_icon("orangecontrib.timeseries.widgets", "TableToTimeseries.svg")),
        "lag": (480, 80, "Variables Lag/Lead", ours_c, os.path.join(OUR_ICONS, "owlagvariables.svg")),
        "table": (700, 80, "Data Table", data_c, orange_icon("Orange.widgets.data", "Table.svg")),
        "arima": (480, 225, "ARIMA Model", ts_c,
                  orange_icon("orangecontrib.timeseries.widgets", "ARIMA.svg")),
        "pred": (480, 355, "Predicción vía Regresión", ours_c,
                 os.path.join(OUR_ICONS, "owregressionmodel.svg")),
        "knn": (250, 385, "kNN (u otro modelo)", model_c, orange_icon("Orange.widgets.model", "KNN.svg")),
        "eval": (750, 290, "Model Evaluation", ts_c,
                 orange_icon("orangecontrib.timeseries.widgets", "ModelEvaluation.svg")),
    }

    def link(a, b, label=None, via=None):
        x1, y1 = nodes[a][0] + R + 3, nodes[a][1]
        x2, y2 = nodes[b][0] - R - 3, nodes[b][1]
        if via:
            c1, c2 = via
        else:
            dx = (x2 - x1) / 2
            c1, c2 = (x1 + dx, y1), (x2 - dx, y2)
        out = (f'<path d="M{x1} {y1} C{c1[0]} {c1[1]} {c2[0]} {c2[1]} {x2} {y2}" '
               f'fill="none" stroke="#9AA3AD" stroke-width="2.5"/>'
               f'<circle cx="{x1}" cy="{y1}" r="3.5" fill="#9AA3AD"/>'
               f'<circle cx="{x2}" cy="{y2}" r="3.5" fill="#9AA3AD"/>')
        if label:
            lx, ly, ltxt = label
            out += text(lx, ly, ltxt, 12, MUTED, 400, "middle")
        return out

    b = []
    b.append(link("file", "form"))
    b.append(link("form", "lag"))
    b.append(link("lag", "table"))
    b.append(link("form", "arima"))
    b.append(link("form", "pred"))
    b.append(link("knn", "pred", label=(372, 392, "Learner")))
    b.append(link("arima", "eval"))
    b.append(link("pred", "eval"))
    b.append(link("form", "eval", via=((400, 150), (590, 150))))

    for key, (x, y, label, (fill, stroke), path) in nodes.items():
        if path.startswith(OUR_ICONS):
            b.append(f'<circle cx="{x}" cy="{y}" r="{R + 9}" fill="none" stroke="{TEAL}" '
                     f'stroke-width="2" stroke-dasharray="5 4"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        b.append(icon(path, x, y, 40))
        weight = 600 if path.startswith(OUR_ICONS) else 400
        b.append(text(x, y + R + 22, label, 14, TEXT, weight))

    b.append(f'<circle cx="672" cy="440" r="11" fill="none" stroke="{TEAL}" '
             'stroke-width="2" stroke-dasharray="4 3"/>')
    b.append(text(690, 440, "widgets de orange_gualbe_ts", 13, MUTED, 400, "start"))
    save("flujo.svg", svg(w, h, "".join(b), "Flujo de trabajo típico en Orange"))


# ---------------------------------------------------------------- lag/lead
def lag_lead():
    w, h = 960, 540
    ventas = [10, 12, 15, 14, 18]
    precio = ["3,0", "3,1", "3,1", "3,2", "3,3"]
    fechas = ["01/03", "02/03", "03/03", "04/03", "05/03"]
    ROW, HDR = 27, 30
    hl = 15

    def cell(x, y, cw, v, bg, fg, bold=False):
        missing = v is None
        s = "?" if missing else str(v)
        is_hl = (not missing) and v == hl
        out = rect(x + 2, y + 2, cw - 4, ROW - 4, bg if not missing else "#FFFFFF",
                   (fg if is_hl else "none"), rx=4, sw=1.5)
        out += text(x + cw / 2, y + ROW / 2, s, 14,
                    FAINT if missing else fg, 700 if (bold or is_hl) else 400)
        return out

    b = []
    # --- entrada
    x0, y0 = 60, 58
    b.append(text(x0, 34, "Entrada", 14, MUTED, 700, "start"))
    cols_in = [("Fecha", 82, fechas, NEUTRAL_BG, TEXT),
               ("Ventas", 76, ventas, NEUTRAL_BG, TEXT),
               ("Precio", 76, precio, NEUTRAL_BG, TEXT)]
    x = x0
    for name, cw, vals, bg, fg in cols_in:
        b.append(text(x + cw / 2, y0 + HDR / 2, name, 14, TEXT, 700))
        for i, v in enumerate(vals):
            b.append(cell(x, y0 + HDR + i * ROW, cw, v, bg, fg))
        x += cw
    b.append(f'<line x1="{x0}" y1="{y0 + HDR}" x2="{x}" y2="{y0 + HDR}" stroke="{BORDER}"/>')

    # --- operaciones
    ox, oy, ow = 420, 58, 470
    b.append(text(ox, 34, "Lista de operaciones (widget)", 14, MUTED, 700, "start"))
    b.append(rect(ox, oy, ow, 120, "#FAFBFC", BORDER, rx=10))
    ops = [("1.", "LAG", "T = 3", "Ventas", PAST_BG, PAST_FG, "pasado"),
           ("2.", "LEAD", "T = 3", "Ventas", FUT_BG, FUT_FG, "futuro")]
    for k, (n, kind, t, var, bg, fg, word) in enumerate(ops):
        yy = oy + 30 + k * 38
        b.append(text(ox + 22, yy, n, 15, MUTED, 400, "start"))
        b.append(rect(ox + 44, yy - 13, 70, 26, bg, "none", rx=13))
        b.append(text(ox + 79, yy, kind, 13, fg, 700))
        b.append(text(ox + 128, yy, f"{t}  ·  {var}  ·  {word}", 15, TEXT, 400, "start"))
    b.append(rect(ox + ow - 112, oy + 96 - 13, 92, 28, TEAL, "none", rx=14))
    b.append(text(ox + ow - 66, oy + 97, "Aplicar", 14, "#FFFFFF", 700))

    b.append(arrow(480, 222, 480, 262, TEAL, 3))

    # --- salida
    groups = [("sin elegir", 2, NEUTRAL_BG, MUTED),
              ("pasado (LAG)", 3, PAST_BG, PAST_FG),
              ("original", 1, "#E4E9EE", TEXT),
              ("futuro (LEAD)", 3, FUT_BG, FUT_FG)]
    shift = lambda k: [ventas[i - k] if 0 <= i - k < len(ventas) else None
                       for i in range(len(ventas))]
    cols_out = [("Fecha", 76, fechas, NEUTRAL_BG, TEXT),
                ("Precio", 66, precio, NEUTRAL_BG, TEXT),
                ("Ventas_t-3", 96, shift(3), PAST_BG, PAST_FG),
                ("Ventas_t-2", 96, shift(2), PAST_BG, PAST_FG),
                ("Ventas_t-1", 96, shift(1), PAST_BG, PAST_FG),
                ("Ventas", 78, ventas, "#E4E9EE", TEXT),
                ("Ventas_t+1", 96, shift(-1), FUT_BG, FUT_FG),
                ("Ventas_t+2", 96, shift(-2), FUT_BG, FUT_FG),
                ("Ventas_t+3", 96, shift(-3), FUT_BG, FUT_FG)]
    total = sum(c[1] for c in cols_out)
    sx, gy = (w - total) / 2, 296
    b.append(text(sx, 278, "Salida: originales + bloque temporal de la variable elegida",
                  14, MUTED, 700, "start"))
    x, ci = sx, 0
    for label, n, bg, fg in groups:
        gw = sum(c[1] for c in cols_out[ci:ci + n])
        b.append(rect(x + 2, gy, gw - 4, 22, bg, "none", rx=11))
        b.append(text(x + gw / 2, gy + 11, label, 12, fg, 700))
        x += gw
        ci += n
    hy = gy + 28
    x = sx
    for name, cw, vals, bg, fg in cols_out:
        b.append(text(x + cw / 2, hy + HDR / 2, name, 13, TEXT, 700))
        for i, v in enumerate(vals):
            b.append(cell(x, hy + HDR + i * ROW, cw, v, bg, fg))
        x += cw
    b.append(f'<line x1="{sx}" y1="{hy + HDR}" x2="{sx + total}" y2="{hy + HDR}" stroke="{BORDER}"/>')
    b.append(text(w / 2, h - 22,
                  "El mismo valor (15) se desplaza en diagonal; «?» = valor ausente donde no hay dato.",
                  13, MUTED, 400))
    save("lag_lead.svg", svg(w, h, "".join(b), "Qué hace el widget Variables Lag/Lead"))


# ---------------------------------------------------------------- predicción
def prediccion():
    w, h = 960, 540
    serie = [10, 12, 15, 14, 18, 20, 19, 23]
    b = []
    # paneles
    b.append(rect(20, 20, 448, 500, "#FAFBFC", BORDER, rx=12))
    b.append(rect(492, 20, 448, 500, "#FAFBFC", BORDER, rx=12))
    b.append(text(44, 48, "1 · Entrenamiento", 17, TEXT, 700, "start"))
    b.append(text(516, 48, "2 · Pronóstico recursivo", 17, TEXT, 700, "start"))

    # --- 1: ventana deslizante sobre la serie
    cw, x0, y0 = 46, 60, 112
    b.append(text(44, 72, "Serie (variable objetivo), con T = 3 lags", 13, MUTED, 400, "start"))
    for i, v in enumerate(serie):
        x = x0 + i * cw
        if 2 <= i <= 4:
            bg, fg = PAST_BG, PAST_FG
        elif i == 5:
            bg, fg = PRED_BG, PRED_FG
        else:
            bg, fg = "#FFFFFF", TEXT
        b.append(rect(x + 2, y0, cw - 4, 34, bg, BORDER, rx=5))
        b.append(text(x + cw / 2, y0 + 17, str(v), 15, fg, 600))
        b.append(text(x + cw / 2, y0 + 48, f"t{i + 1}", 11, FAINT))
    bx1, bx2 = x0 + 2 * cw + 4, x0 + 5 * cw - 4
    b.append(f'<path d="M{bx1} {y0 - 8} V{y0 - 14} H{bx2} V{y0 - 8}" fill="none" stroke="{PAST_FG}" stroke-width="2"/>')
    b.append(text((bx1 + bx2) / 2, y0 - 24, "lags", 12, PAST_FG, 700))
    b.append(text(x0 + 5 * cw + cw / 2, y0 - 24, "objetivo", 12, PRED_FG, 700))

    # tabla interna
    ty, tx = 198, 60
    b.append(text(44, ty - 14, "Tabla interna (una fila por posición de la ventana)",
                  13, MUTED, 400, "start"))
    hdr = [("lag1", PAST_BG, PAST_FG), ("lag2", PAST_BG, PAST_FG),
           ("lag3", PAST_BG, PAST_FG), ("objetivo", PRED_BG, PRED_FG)]
    colw = 92
    for j, (name, bg, fg) in enumerate(hdr):
        b.append(rect(tx + j * colw + 2, ty, colw - 4, 26, bg, "none", rx=5))
        b.append(text(tx + j * colw + colw / 2, ty + 13, name, 13, fg, 700))
    for r, i in enumerate(range(3, 8)):
        yy = ty + 32 + r * 25
        vals = [serie[i - 1], serie[i - 2], serie[i - 3], serie[i]]
        active = i == 5
        for j, v in enumerate(vals):
            fg = (PAST_FG if j < 3 else PRED_FG) if active else MUTED
            if active:
                b.append(rect(tx + j * colw + 2, yy, colw - 4, 23,
                              PAST_BG if j < 3 else PRED_BG, "none", rx=4))
            b.append(text(tx + j * colw + colw / 2, yy + 11.5, str(v), 14, fg, 700 if active else 400))
    b.append(text(tx + 4 * colw + 8, ty + 32 + 2 * 25 + 11, "← fila de arriba", 12, PRED_FG, 400, "start"))
    b.append(text(44, 368, "+ con Tx > 0, también lags de las demás variables (exógenas)",
                  12, EXO_FG, 400, "start"))

    b.append(arrow(244, 380, 244, 402, TEAL, 3))
    # learner
    b.append(rect(60, 408, 368, 100, "#FFFFFF", TEAL, rx=12, sw=2))
    b.append(text(244, 432, "Learner de regresión que conectes", 15, TEAL_DARK, 700))
    learners = [("KNN.svg", "kNN"), ("Tree.svg", "Árbol"),
                ("LinearRegression.svg", "Lineal"), ("RandomForest.svg", "Bosque")]
    for k, (fname, lab) in enumerate(learners):
        cx = 114 + k * 87
        b.append(f'<circle cx="{cx}" cy="466" r="17" fill="#FAC1D9" stroke="#D9799F" stroke-width="1.5"/>')
        b.append(icon(orange_icon("Orange.widgets.model", fname), cx, 466, 24))
        b.append(text(cx, 496, lab, 12, MUTED))

    # --- 2: gráfico de pronóstico
    X0, dx = 536, 36
    Y = lambda v: 400 - (v - 8) * 13
    fc = [24.4, 25.3, 26.1]
    ci = [1.4, 2.0, 2.5]
    hx = [X0 + i * dx for i in range(8)]
    fx = [X0 + (8 + k) * dx for k in range(3)]
    # ejes
    b.append(f'<line x1="{X0 - 14}" y1="410" x2="{fx[-1] + 24}" y2="410" stroke="{BORDER}" stroke-width="1.5"/>')
    # banda de confianza
    up = " ".join(f"{x},{Y(v + c)}" for x, v, c in zip(fx, fc, ci))
    lo = " ".join(f"{x},{Y(v - c)}" for x, v, c in reversed(list(zip(fx, fc, ci))))
    b.append(f'<polygon points="{hx[-1]},{Y(serie[-1])} {up} {lo}" fill="{PRED_BG}" stroke="none"/>')
    # "ahora"
    nx = (hx[-1] + fx[0]) / 2
    b.append(f'<line x1="{nx}" y1="96" x2="{nx}" y2="410" stroke="{FAINT}" stroke-width="1.5" stroke-dasharray="4 4"/>')
    b.append(text(nx - 6, 92, "datos reales", 12, MUTED, 400, "end"))
    b.append(text(nx + 6, 92, "pronóstico", 12, PRED_FG, 400, "start"))
    # serie
    pts = " ".join(f"{x},{Y(v)}" for x, v in zip(hx, serie))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{TEXT}" stroke-width="2.5"/>')
    fpts = f"{hx[-1]},{Y(serie[-1])} " + " ".join(f"{x},{Y(v)}" for x, v in zip(fx, fc))
    b.append(f'<polyline points="{fpts}" fill="none" stroke="{PRED_FG}" stroke-width="2.5" stroke-dasharray="6 5"/>')
    for i, (x, v) in enumerate(zip(hx, serie)):
        col = PAST_FG if i >= 5 else TEXT
        b.append(f'<circle cx="{x}" cy="{Y(v)}" r="{5 if i >= 5 else 4}" fill="{col}"/>')
    for k, (x, v) in enumerate(zip(fx, fc)):
        b.append(f'<circle cx="{x}" cy="{Y(v)}" r="6" fill="#FFFFFF" stroke="{PRED_FG}" stroke-width="2.5"/>')
        b.append(text(x, 428, f"h={k + 1}", 12, PRED_FG, 700))
    # ventana de lags para h=1
    b.append(f'<path d="M{hx[5] - 8} 282 V290 H{hx[7] + 8} V282" fill="none" stroke="{PAST_FG}" stroke-width="2"/>')
    b.append(text((hx[5] + hx[7]) / 2, 304, "lags para h=1", 12, PAST_FG, 700))
    # realimentación
    b.append(f'<path d="M{fx[0] + 4} {Y(fc[0]) - 12} C{fx[0] + 10} {Y(fc[0]) - 70} '
             f'{fx[1] - 10} {Y(fc[1]) - 70} {fx[1] - 2} {Y(fc[1]) - 16}" fill="none" '
             f'stroke="{PRED_FG}" stroke-width="1.8" marker-end="url(#ah)"/>')
    b.append(text(fx[1] + 12, Y(fc[1]) + 62, "ŷ(h=1) pasa a ser", 12, PRED_FG, 700, "middle"))
    b.append(text(fx[1] + 12, Y(fc[1]) + 78, "el lag1 de h=2", 12, PRED_FG, 700, "middle"))

    # leyenda
    ly = 462
    b.append(rect(516, ly - 7, 22, 14, PRED_BG, "none", rx=3))
    b.append(text(546, ly, "intervalo de confianza (aproximado, crece con √h)", 12, MUTED, 400, "start"))
    b.append(f'<circle cx="527" cy="{ly + 26}" r="6" fill="#FFFFFF" stroke="{PRED_FG}" stroke-width="2.5"/>')
    b.append(text(546, ly + 26, "predicción en cada horizonte (Forecast steps ahead)", 12, MUTED, 400, "start"))
    save("prediccion.svg", svg(w, h, "".join(b), "Cómo funciona Predicción vía Regresión"))


# ---------------------------------------------------------------- capturas
def capturas():
    import numpy as np
    from AnyQt.QtWidgets import QApplication
    from AnyQt.QtCore import QItemSelectionModel
    app = QApplication.instance() or QApplication([])
    from Orange.data import Domain, ContinuousVariable, TimeVariable
    from Orange.modelling import KNNLearner
    from orangecontrib.timeseries import Timeseries
    from orangecontrib.orange_gualbe_ts.widgets.owlagvariables import OWLagVariables, PAST, FUTURE
    from orangecontrib.orange_gualbe_ts.widgets.owregressionmodel import OWRegressionModel

    n = 40
    tv = TimeVariable("Fecha", have_date=1)
    domain = Domain([tv, ContinuousVariable("Temperatura"), ContinuousVariable("Humedad")],
                    ContinuousVariable("Ventas"))
    i = np.arange(n)
    X = np.column_stack([i * 86400.0, np.sin(i / 4) * 5 + 20, np.cos(i / 5) * 10 + 60])
    Y = 50 + i * 0.5 + np.sin(i / 3) * 4
    data = Timeseries.from_numpy(domain, X, Y, time_attr=tv)

    w = OWLagVariables()
    w.set_data(data)
    w.operations = [{"variables": ["Ventas"], "window": 3, "direction": PAST},
                    {"variables": ["Ventas"], "window": 2, "direction": FUTURE},
                    {"variables": ["Temperatura", "Humedad"], "window": 1, "direction": PAST}]
    w._refresh_operations_widget()
    w.var_view.selectionModel().select(w.var_model.index(2), QItemSelectionModel.Select)
    w.window_size = 3
    w._apply()
    # listas más bajas para que la captura no tenga huecos vacíos
    w.var_view.setMaximumHeight(96)
    w.ops_widget.setMaximumHeight(80)
    w.show()
    app.processEvents()
    w.resize(470, 0)
    app.processEvents()
    w.grab().save(os.path.join(ASSETS, "captura_lag_lead.png"))

    w2 = OWRegressionModel()
    w2.ar_order, w2.exog_ar_order = 4, 1
    w2.set_data(data)
    w2.set_learner(KNNLearner())
    w2.apply.now()
    w2.show()
    app.processEvents()
    w2.adjustSize()
    app.processEvents()
    w2.grab().save(os.path.join(ASSETS, "captura_prediccion.png"))
    print("escritas las capturas")


if __name__ == "__main__":
    banner()
    flujo()
    lag_lead()
    prediccion()
    if "--capturas" in sys.argv:
        capturas()
