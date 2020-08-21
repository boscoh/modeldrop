# -*- coding: utf-8 -*-
"""
Dash app to display channels data and stages.

    > python app.py

Then open the webbrowser at the indicated url address.

Installation:

    pip install dash==0.21.1
    pip install dash-renderer==0.13.0
    pip install dash-html-components==0.11.0
    pip install dash-core-components==0.23.0
    pip install plotly --upgrade
    pip install dash-bootstrap-components

"""

import logging
import math
import re
import threading
import time
import traceback
import webbrowser
from pathlib import Path
from urllib.request import urlopen

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy
from dash import Dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask import send_from_directory, Flask

from .basemodel import BaseModel

logger = logging.getLogger(__name__)

millnames = ["", "k", "m", "b", "t"]


def millify(n):
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


def get_mark_dict(min_val, max_val):
    exp = math.floor(math.log10(max_val))
    step = math.pow(10, exp - 2)
    if step >= 1:
        step = int(step)

    mark = (max_val - min_val) / 5.0

    n_sig = -math.floor(math.log10(mark))
    if n_sig < 0 or mark >= 1:
        n_sig = 0
    format = f"%.{n_sig}f"

    # if abs(1 - mark) < 0.5:
    #     format = "%.1f"

    mark_dict = {0: "0"}
    this_mark = 0
    while this_mark < max_val:
        if mark >= 1:
            mark_key = int(this_mark)
        else:
            mark_key = float(this_mark)
        if this_mark > 100:
            s = millify(mark_key)
        else:
            s = format % mark_key
        mark_dict[mark_key] = s
        this_mark += mark

    this_mark = 0
    while this_mark > min_val:
        if abs(mark) >= 1:
            mark_key = int(this_mark)
        else:
            mark_key = float(this_mark)
        if abs(this_mark) > 100:
            s = millify(this_mark)
        else:
            s = format % this_mark
        mark_dict[mark_key] = s
        this_mark -= mark

    logger.info(f"format={format} step={step} mark={mark}")
    logger.info(f"{mark_dict}")

    return step, mark_dict


def get_log_mark_dict(min_val, max_val):
    step = 0.01

    mark_dict = {}
    for n in range(int(math.floor(min_val)), int(math.floor(max_val)) + 1):
        if n < 0:
            format = f"%.{-n}f"
        else:
            format = "%.0f"
        mark_dict[n] = format % math.pow(10, n)

    logger.info(f"min_val={min_val} max_val={max_val}")
    logger.info(f"step={step} mark={1}")
    logger.info(f"{mark_dict}")

    return step, mark_dict


class DashModelAdaptor(dict):
    def __init__(self, models):
        super().__init__()

        self.models = models

        self.is_running = False
        for model in self.models:
            model.name = self.format_param_name(model.__class__.__name__)
            model.prefix = model.name.lower().replace(" ", "_")

            for p in model.editable_params:
                p["id"] = model.prefix + "-" + p["key"]

            for p in model.model_plots:
                p["id"] = model.prefix + "-" + p["key"]

            for p in model.fn_plots:
                p["id"] = model.prefix + "-" + p["fn"]

            model.slider_callback = self.make_model_slider_callback(model)

        self.choose_model(0)

        self.server = Flask(__name__)

        self.app = Dash(
            __name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=self.server
        )

        self.app.layout = self.make_layout()

        self.register_callbacks(self.app)

    def make_model_slider_callback(self, model: BaseModel):
        def slider_callback(*values):
            if self.is_running:
                logger.debug(f"change_inputs skipping as running already")
                raise PreventUpdate

            self.is_running = True

            try:
                for p, val in zip(model.editable_params, values):
                    if p.get("is_log10"):
                        model.param[p["key"]] = float(math.pow(10, val))
                    else:
                        model.param[p["key"]] = float(val)
                logger.info(f"slider_callback run {model.param}")
                model.run()
                model.calc_aux_var_solutions()
                figures = self.get_figures(model)
            except Exception as e:
                traceback.print_exc()
                logger.info(f"slider_callback exception: {e}...")
                figures = [
                    {"data": {"x": [], "y": [], "type": "scatter"}}
                    for i in range(len(model.model_plots) + len(model.fn_plots))
                ]

            self.is_running = False

            return figures

        return slider_callback

    def choose_model(self, i):
        self.model = self.models[i]

        model = self.model
        self.title = f"Modeldrop :: {model.name}"

        self.is_running = False

    @staticmethod
    def format_param_name(key):
        """https://stackoverflow.com/a/1176023"""
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1 \2", key)
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1 \2", s1)
        return s2.lower().title()

    def get_input_param(self, key):
        for p in self.model.editable_params:
            if p["key"] == key:
                return p
        return None

    def make_models_dropdown_menu(self):
        """Create a dropdown menu component with the assets.
        """
        menu_items = [
            dbc.NavLink(f"{model.name}", external_link=True, href=f"./{model.prefix}")
            for model in self.models
        ]
        return dbc.DropdownMenu(
            children=menu_items,
            className="pt-3 pb-2",
            in_navbar=False,
            nav=False,
            label="Models",
            color="info",
            style={"listStyleType": "none"},
        )

    def make_nav_bar(self):
        return dbc.Navbar(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.NavbarBrand(
                                    self.title, id="model-title", className="ml-2"
                                )
                            ),
                        ],
                        align="center",
                        no_gutters=True,
                    ),
                    href="#",
                ),
            ],
            dark=False,
            color="white",
            style={"border-bottom": "1px solid #AAA"},
        )

    def make_parameter_div(self):
        children = [
            html.H6("Parameters", style={"marginBottom": "1em"}),
        ]
        model = self.model
        for p in self.model.editable_params:
            input_key = p["key"]

            value = model.param[input_key]

            my_param = self.get_input_param(input_key)

            max_val = my_param.get("max", value * 5)
            min_val = my_param.get("min", 0)

            logger.info(f"key={input_key}")

            if my_param.get("is_log10"):
                min_val = math.log10(min_val)
                max_val = math.log10(max_val)
                step, mark_dict = get_log_mark_dict(min_val, max_val)
            else:
                step, mark_dict = get_mark_dict(min_val, max_val)

            children.append(dbc.Label(f"{self.format_param_name(input_key)}"),)
            children.append(
                html.Div(
                    dcc.Slider(
                        id=p["id"],
                        min=min_val,
                        max=max_val,
                        step=step,
                        marks=mark_dict,
                        value=value,
                    ),
                    style={
                        "marginLeft": "15px",
                        "marginRight": "15px",
                        "paddingBottom": "2.5em",
                    },
                )
            )

        return html.Div(
            children=children,
            style={
                "fontSize": "0.8em",
                "letterSpacing": "0.05em",
                "paddingTop": "30px",
            },
        )

    def make_graphs_children(self):
        children = [
            self.make_models_dropdown_menu(),
            html.Div(html.H3("Model"), id="page-title"),
            html.Br()
        ]
        model = self.model
        logger.info(f"make_graphs_div {model.name}")

        for model_plot in model.model_plots:
            graph = dcc.Graph(
                id=model_plot["id"],
                config={"responsive": True},
                style={"height": "405px"},
                animate=True,
                animation_options={
                    "frame": {"redraw": False, "duration": 1000},
                    "easing": "cubic-in-out",
                    "transition": {"duration": 500},
                },
            )
            children.append(html.H4(model_plot["key"]))
            children.append(graph)

        for fn_plot in self.model.fn_plots:
            graph = dcc.Graph(
                id=fn_plot["id"],
                config={"responsive": True},
                style={"height": "405px"},
                animate=True,
                animation_options={
                    "frame": {"redraw": False, "duration": 1000},
                    "easing": "cubic-in-out",
                    "transition": {"duration": 500},
                },
            )
            children.append(html.H4(self.format_param_name(fn_plot["fn"])))
            children.append(graph)
        return children

    def get_figures(self, model):
        result = []

        for model_plot in model.model_plots:
            all_x_vals = []
            all_y_vals = []
            data = []
            for key in model_plot["vars"]:
                x_vals = []
                y_vals = []
                if key in model.solution:
                    for x, y in zip(model.times, model.solution[key]):
                        if numpy.isnan(x):
                            logger.info(f"make_stages_graphs_div error x={x}")
                            continue
                        if numpy.isnan(y):
                            logger.info(f"make_stages_graphs_div error y={y}")
                            continue
                        x_vals.append(float(x))
                        y_vals.append(float(y))
                all_x_vals.extend(x_vals)
                all_y_vals.extend(y_vals)
                data.append(
                    {
                        "x": x_vals,
                        "y": y_vals,
                        "type": "scatter",
                        "name": self.format_param_name(key),
                    }
                )

            min_x = min(all_x_vals)
            max_x = max(all_x_vals)
            min_y = min(all_y_vals)
            max_y = max(all_y_vals)

            if model_plot.get("ymin") is not None:
                if min_y < model_plot["ymin"]:
                    min_y = model_plot["ymin"]

            if model_plot.get("ymax") is not None:
                if max_y > model_plot["ymax"]:
                    max_y = model_plot["ymax"]

            figure = {
                "data": data,
                "layout": {
                    "margin": {"t": 40},
                    "xaxis": {"range": [min_x, max_x], "title": "Time"},
                    "yaxis": {"range": [min_y, max_y]},
                },
            }
            result.append(figure)

        for fn_plot in self.model.fn_plots:
            xlims = fn_plot["xlims"]
            xdiff = xlims[1] - xlims[0]
            exp = math.floor(math.log10(xdiff))
            step = math.pow(10, exp - 2)
            this_x = xlims[0]
            x_vals = []
            while this_x <= xlims[1]:
                x_vals.append(this_x)
                this_x += step

            key = fn_plot["fn"]
            fn = model.fns[key]
            y_vals = list(map(fn, x_vals))

            min_y = min(y_vals)
            max_y = max(y_vals)
            if fn_plot.get("ymin") is not None:
                min_y = fn_plot["ymin"]

            data = [{"x": x_vals, "y": y_vals, "type": "scatter", "name": key,}]
            figure = {
                "data": data,
                "layout": {
                    "margin": {"t": 40},
                    "yaxis": {"range": [min_y, max_y]},
                },
            }

            if "var" in fn_plot:
                figure["layout"]["xaxis"] = {
                    "title": f"{self.format_param_name(fn_plot['var'])}"
                }

            result.append(figure)

        return result

    def make_content_children(self):
        return dbc.Row(
            [
                dbc.Col(
                    self.make_parameter_div(),
                    xs=12,
                    lg=3,
                    md=4,
                    sm=5,
                    style={
                        "borderRight": "1px solid #CCC",
                        # "backgroundColor": "#EEE",
                        "overflow": "scroll",
                        "paddingLeft": "20px",
                        "boxSizing": "border-box",
                        "height": "calc(100vh - 56px)",
                    },
                ),
                dbc.Col(
                    html.Div(
                        self.make_graphs_children(),
                        id="graphs",
                        style={
                            "overflow": "scroll",
                            "boxSizing": "border-box",
                            "height": "calc(100vh - 56px)",
                        },
                    ),
                ),
            ]
        )

    def make_layout(self):
        return html.Div(
            [
                # handle url address bar
                dcc.Location(id="url", refresh=False),
                # object to start polling server to trigger events
                dcc.Interval(id="interval-component", interval=1000, n_intervals=0),
                self.make_nav_bar(),
                dbc.Container(id="content", fluid=1,),
            ],
            id="page_layout",
        )

    def register_callbacks(self, app):

        app.config["suppress_callback_exceptions"] = True

        # Sets up the local `static` directory as the source for http://*.*.*/static/* files
        @app.server.route("/static/<path>")
        def static_file(path):
            static_folder = Path().cwd() / "static"
            return send_from_directory(static_folder, path)

        @app.callback(
            [
                Output("content", "children"),
                Output("model-title", "children"),
                Output("page-title", "children"),
            ],
            [Input("url", "pathname")],
        )
        def display_page(pathname):
            if isinstance(pathname, str):
                tokens = pathname.split("/")
                if len(tokens) > 0:
                    token = tokens[1]
                    for model in self.models:
                        if token == model.prefix:
                            self.model = model
            return (
                self.make_content_children(),
                [f"Modeldrop :: {self.model.name}"],
                [html.H3(self.model.name), html.Div(html.A("Source", href=self.model.url))],
            )

        # add callback for toggling the collapse on small screens
        @app.callback(
            Output("navbar-collapse", "is_open"),
            [Input("navbar-toggler", "n_clicks")],
            [State("navbar-collapse", "is_open")],
        )
        def toggle_navbar_collapse(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open

        @app.callback(
            Output("counter", "children"), [Input("interval-component", "n_intervals")],
        )
        def poll_server(n_intervals):
            # logger.info(f"poll_server n_interval={n_intervals}")
            if n_intervals % 2 != 0:
                raise PreventUpdate
            else:
                return n_intervals

        for model in self.models:
            outputs = [Output(p["id"], "figure") for p in model.model_plots] + [
                Output(p["id"], "figure") for p in model.fn_plots
            ]
            inputs = [Input(p["id"], "value") for p in model.editable_params]
            app.callback(outputs, inputs)(model.slider_callback)

    def run_server(self, port=8050, is_debug=True):
        self.app.run_server(debug=is_debug, port=port)


def open_url_in_background(url, sleep_in_s=1):
    def inner():
        elapsed = 0
        is_server_not_running = True
        while is_server_not_running:
            try:
                response_code = urlopen(url).getcode()
                if response_code < 400:
                    webbrowser.open(url)
                    is_server_not_running = False
            except:
                time.sleep(sleep_in_s)
                elapsed += sleep_in_s
                logger.info(f"open_url_in_background: waited {elapsed}s for {url}...")

    # creates a thread to poll server before opening client
    threading.Thread(target=inner).start()
