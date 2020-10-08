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

import copy
import logging
import math
import re
import textwrap
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
from flask import Flask, send_from_directory

from .basemodel import BaseModel

logger = logging.getLogger(__name__)


import dash_dangerously_set_inner_html
import markdown as md
import markdown_katex


def md_to_html(md_text):
    md_text = textwrap.dedent(md_text)
    return md.markdown(md_text, extensions=["markdown_katex"])


def make_md_div(md):
    return html.Div(
        dash_dangerously_set_inner_html.DangerouslySetInnerHTML(md_to_html(md))
    )


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

    return step, mark_dict


def make_slug(s):
    return s.lower().replace(" ", "-")


def make_title(key):
    """https://stackoverflow.com/a/1176023"""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1 \2", key)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1 \2", s1)
    s3 = s2.replace("_", " ")
    return s3.lower().title()


class DashModelAdaptor(dict):
    def __init__(self, models):
        super().__init__()

        self.models = models

        self.is_running = False
        for model in self.models:
            model.name = make_title(model.__class__.__name__)

            model.prefix = make_slug(model.name)

            model.init_param = copy.deepcopy(model.param)

            for p in model.editable_params:
                p["id"] = model.prefix + "-" + p["key"]

            for p in model.plots:
                if "vars" in p:
                    p["id"] = model.prefix + "-" + make_slug(p["title"])
                elif "fn" in p:
                    p["id"] = model.prefix + "-" + make_slug(make_title(p["fn"]))

            model.slider_callback = self.make_model_slider_callback(model)

        self.choose_model(0)

        self.server = Flask(__name__)

        self.app = Dash(
            __name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=self.server
        )

        self.app.title = "modeldrop"

        self.app.layout = self.make_layout()

        self.register_callbacks(self.app)

    def choose_model(self, i):
        self.model = self.models[i]

        model = self.model
        self.title = f"Modeldrop :: {model.name}"

        self.is_running = False

    def get_input_param(self, key):
        for p in self.model.editable_params:
            if p["key"] == key:
                return p
        return None

    def make_models_dropdown_menu(self):
        """Create a dropdown menu component with the assets.
        """
        menu_items = [dbc.NavLink(f"Home", external_link=True, href=f"./")] + [
            dbc.NavLink(f"{model.name}", external_link=True, href=f"./{model.prefix}")
            for model in self.models
        ]
        return dbc.DropdownMenu(
            children=menu_items,
            className="pt-3 pb-2",
            in_navbar=False,
            nav=False,
            label="modeldrop::models",
            color="info",
            style={"listStyleType": "none"},
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

            if my_param.get("is_log10"):
                min_val = math.log10(min_val)
                max_val = math.log10(max_val)
                step, mark_dict = get_log_mark_dict(min_val, max_val)
            else:
                step, mark_dict = get_mark_dict(min_val, max_val)

            logger.info(f"make_parameter_div key={input_key} {mark_dict}")

            children.append(
                dbc.Label(f"{make_title(input_key)} = {value}", id=f'{p["id"]}-value')
            )

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
            className="text-left",
            style={
                "fontSize": "0.8em",
                "letterSpacing": "0.05em",
                "paddingTop": "30px",
            },
        )

    def make_graphs_children(self):
        result = [
            dbc.Navbar(
                [self.make_models_dropdown_menu()],
                dark=False,
                className="pl-0",
                sticky="top",
                color="white",
            ),
        ]

        title = [html.H2(self.model.name, className="mt-5")]
        if hasattr(self.model, "url"):
            title.append(html.Div(html.A("[python source]", href=self.model.url)))

        children = [
            *title,
            html.Br(),
        ]

        logger.info(f"make_graphs_div {self.model.name}")

        for plot in self.model.plots:
            graph = dcc.Graph(
                id=plot["id"],
                config={
                    "responsive": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": [
                        "lasso2d",
                        "hoverClosestCartesian",
                        "hoverCompareCartesian",
                        "toggleSpikelines",
                        "resetScale2d",
                    ],
                },
                style={"height": "405px"},
                animate=True,
                animation_options={
                    "frame": {"redraw": False, "duration": 1000},
                    "easing": "cubic-in-out",
                    "transition": {"duration": 500},
                },
            )
            if "markdown" in plot:
                children.append(make_md_div(plot["markdown"]))

            children.append(graph)

        result.append(
            html.Div(
                children,
                style={
                    "height": "calc(100vh - 80px)",
                    "padding-right": "30px",
                    "overflow": "scroll",
                },
            )
        )
        return result

    def make_figures(self, model):
        result = []

        for plot in model.plots:
            if "vars" in plot:

                all_x_vals = []
                all_y_vals = []
                data = []
                for key in plot["vars"]:
                    x_vals = []
                    y_vals = []
                    if key in model.solution:
                        for x, y in zip(model.times, model.solution[key]):
                            if x is None or numpy.isnan(x):
                                logger.info(f"make_stages_graphs_div error x={x}")
                                continue
                            if y is None or numpy.isnan(y):
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
                            "name": make_title(key),
                        }
                    )

                min_x = min(all_x_vals)
                max_x = max(all_x_vals)
                min_y = min(all_y_vals)
                max_y = max(all_y_vals)

                if plot.get("ymin_cutoff") is not None:
                    if min_y < plot["ymin_cutoff"]:
                        min_y = plot["ymin_cutoff"]

                if plot.get("ymax_cutoff") is not None:
                    if max_y > plot["ymax_cutoff"]:
                        max_y = plot["ymax_cutoff"]

                if plot.get("ymin") is not None:
                    min_y = plot["ymin"]

                if plot.get("ymax") is not None:
                    max_y = plot["ymax"]

                figure = {
                    "data": data,
                    "layout": {
                        "title": {"text": plot["title"], "font": {"size": 14}},
                        "margin": {"t": 40},
                        "xaxis": {"range": [min_x, max_x], "title": "Time"},
                        "yaxis": {"range": [min_y, max_y]},
                    },
                }
                result.append(figure)

            elif "fn" in plot:

                xlims = plot["xlims"]
                xdiff = xlims[1] - xlims[0]
                exp = math.floor(math.log10(xdiff))
                step = math.pow(10, exp - 2)
                this_x = xlims[0]
                x_vals = []
                while this_x <= xlims[1]:
                    x_vals.append(this_x)
                    this_x += step

                key = plot["fn"]
                fn = model.fn[key]
                y_vals = list(map(fn, x_vals))

                min_y = min(y_vals)
                max_y = max(y_vals)
                if plot.get("ymin") is not None:
                    min_y = plot["ymin"]

                data = [{"x": x_vals, "y": y_vals, "type": "scatter", "name": key,}]
                figure = {
                    "data": data,
                    "layout": {
                        "title": {"text": make_title(plot["fn"]), "font": {"size": 14}},
                        "margin": {"t": 40},
                        "yaxis": {"range": [min_y, max_y]},
                    },
                }

                if "var" in plot:
                    figure["layout"]["xaxis"] = {"title": f"{make_title(plot['var'])}"}

                result.append(figure)

        return result

    def make_content_children(self):
        return dbc.Row(
            [
                dbc.Col(
                    self.make_parameter_div(),
                    xs=4,
                    lg=3,
                    md=4,
                    sm=4,
                    style={
                        "borderRight": "1px solid #DDD",
                        # "backgroundColor": "#EEE",
                        "marginTop": "130px",
                        "overflow": "scroll",
                        "paddingLeft": "20px",
                        "boxSizing": "border-box",
                        "height": "calc(100vh - 130px)",
                    },
                ),
                dbc.Col(
                    html.Div(
                        self.make_graphs_children(),
                        id="graphs",
                        style={
                            "overflow": "scroll",
                            "boxSizing": "border-box",
                            "padding-left": "30px",
                            "padding-right": "0px",
                            "height": "calc(100vh)",
                            "max-width": "750px",
                        },
                    ),
                    xs=8,
                    lg=9,
                    md=8,
                    sm=8,
                ),
            ]
        )

    def make_home_content(self):
        links = []
        for model in self.models:
            links.append(html.Li(html.A(f"{model.name}", href=f"./{model.prefix}")))
        return dbc.Row(
            [
                dbc.Col(
                    xs=4,
                    lg=3,
                    md=4,
                    sm=4,
                    style={
                        "borderRight": "1px solid #DDD",
                        "marginTop": "130px",
                        "height": "calc(100vh - 130px)",
                    },
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Navbar(
                                [self.make_models_dropdown_menu(), html.Div(),],
                                dark=False,
                                className="pl-0 mb-3",
                                sticky="top",
                                color="white",
                            ),
                            make_md_div(
                                """

                            <br>

                            ### modeldrop
                            
                            <br>
                            
                            Python library to explore dynamical models 
                            with scipy and dash, with a focus on
                            dynamic population models.
                            
                            <https://github.com/boscoh/modeldrop>
                            
                            Current Models
                            """
                            ),
                            html.Ul(links),
                            html.Br(),
                        ],
                        id="graphs",
                        style={
                            "overflow": "scroll",
                            "boxSizing": "border-box",
                            "padding-left": "30px",
                            "padding-right": "30px",
                            "height": "calc(100vh)",
                            "max-width": "750px",
                        },
                    ),
                    xs=8,
                    lg=9,
                    md=8,
                    sm=8,
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
                dbc.Container(id="content", fluid=True),
            ],
            id="page_layout",
            style={"overflow": "hidden"},
        )

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
                figures = self.make_figures(model)
            except Exception as e:
                traceback.print_exc()
                logger.info(f"slider_callback exception: {e}...")
                figures = [
                    {"data": {"x": [], "y": [], "type": "scatter"}}
                    for i in range(len(model.plots))
                ]

            self.is_running = False
            titles = [make_title(p["key"]) for p in model.editable_params]
            values = [model.param[p["key"]] for p in model.editable_params]
            outputs = [f"{t} = {v}" for t, v in zip(titles, values)]
            return figures + outputs

        return slider_callback

    def register_callbacks(self, app):

        app.config["suppress_callback_exceptions"] = True

        @app.callback(
            Output("content", "children"), [Input("url", "pathname")],
        )
        def display_page(pathname):
            logger.info(f"display_page {pathname}")

            if pathname is None or pathname == "/":
                return self.make_home_content()

            if isinstance(pathname, str):
                tokens = pathname.split("/")
                if len(tokens) > 0:
                    token = tokens[1]
                    for model in self.models:
                        if token == model.prefix:
                            self.model = model
            return self.make_content_children()

        for model in self.models:
            plot_outputs = [Output(p["id"], "figure") for p in model.plots]
            value_outputs = [
                Output(f'{p["id"]}-value', "children") for p in model.editable_params
            ]
            outputs = plot_outputs + value_outputs
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


def show_models(models, argv):
    logging.basicConfig(level=logging.DEBUG)
    port = "8050"
    if "-o" in argv:
        open_url_in_background(f"http://127.0.0.1:{port}/")
    is_debug = "-d" in argv
    DashModelAdaptor(models).run_server(port=port, is_debug=is_debug)
