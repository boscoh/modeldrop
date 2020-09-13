__doc__ = """

Graphing Interface
==================

Basic graphing module that provides a data interface to draw graphs, currently uses
`matplotlib` as the rendering engine, but the common graph data is json-compatible and
can be sent to any graphing renderer.

.. literalinclude:: ../../examples/graph.py

- X-Axis intelligently switches between dates and integers
- Legends moved over to the right
- Axes lightened for better contrast
- Labels automatically added to enable nice legend labels

Basic Graph dictionary
----------------------

.. code-block:: python

    graph = {
        "datasets": [
            # Here is where all the components of 
            # the graphs will be appended as
            # discussed in "Types of Datasets" below
        ],
        "hlines": [],
        "vlines": [],
        "summary": {
            "fn": graph_params["fn"],
        },
        "basename": "",
    }

There are a bunch of modifiers available for all graphs. Add
these fields to the main ``graph`` dictionary:

    - ``"figsize": (10, 3)`` - which gives the dimensions
      of the graph in terms of inches, which is used by
      ``matplotlib``
    - ``xmin``, ``xmax``, ``ymin``, ``ymax`` - are values
      used to determine the data-extend of the graph, dates
      can be used when it is appropriate
    - ``is_legend: True`` - will set aside space on the 
      right and show a legend
    - ``is_compact`` - will use a flatter dimension to
      draw the graph, move the title into the body,
      and hide some labels
    - ``is_title_hidden`` - will hide the title, useful
      for generating graphs to be shown in schematic
      table view
    - ``title``, ``ylabel``, ``xlabel`` - modifiable text labels
    - ``is_ylog`` - force y-axis to use log scale
    - ``grid_color`` - sets the color of the grid box-area


Matplotlib Colors and Styles
----------------------------

Colors are processed through matplotlib and are typically stored as
3-tuples of (0, 1), e.g. (0.5, 0, 1). But matplotlib is used to interpret
hex-strings etc.

In particular, opacity can be profitably used in many cases to
show density of data.

Line styles use the matplotlib linestyle modifiers:

    - ``linestyle: ":"`` - examples such as ":", "-", "--"
    - ``linewidth: 1`` - widths of lines

Types of Datasets
-----------------

A graph can take multiple dataset - single basic chart type,
which looks like:

.. code-block:: python

    dataset = { 
        'graph_type': 'line',

        # x-values either datetime or integers (for days)
        'xvals': [],

        # either 'yvals' or 'ystacks' depending on 'graph_type'
        'yvals': [],
        'ystacks': [
            [],
        ],

        # optional 
        'label': 'name of graph',
        'counts': [],
    }
        
`graph_type` available:

- ``line`` - plots a single line with modifiers, lines can 
  be modified with ``linewidth``, ``linestyle`` and ``color``
- ``scatter`` - plots markers with modifiers ``markersize`` and ``color``
- ``fillbetween`` - plots the area between two sets of yvals
  stored in `ystacks`
- ``bar`` - basic bar plot, where widths cover the entire extent
- ``stack`` - `ystacks` indicate the different sets of values
  to be stacked on top of each other. Order is maintained for both
  the display stacks and the legend, this overrides the 
  standard legend function
- ``label`` - the label to be inserted into the legend for this
  dataset   
- ``counts`` - special auxiliary count frequency plot over time
  that will be drawn in the bottom 1/10th of the graph. 
  Used to compare with the main dataset
  

Overlaying Lines
----------------

Vertical and horizontal guide-lines can be easily added.

Vertical lines are added to the ``vlines`` list:

.. code-block:: python

    vline = { 
        "x": float,
        "ls": ":",
        "color": "g",
        "linewidth": 3
    }

Horiziontal lines are added to the ``hlines`` list:

.. code-block:: python

    hline = { 
        "y": float,
        "ls": ":",
        "color": "g",
        "linewidth": 3
    }
    
Transparency Images
-------------------

The ``write_graph`` allows a transparency option that turns the
white background transparent in the resultant .png file. This
allows more involved graphic-design in resultant powerpoint
presentations with themed backgrounds.

"""

import colorsys
import datetime
import json
import logging
import os
import numpy

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.dates import date2num
from matplotlib.figure import Figure

from PIL import Image

from modeldrop.basemodel import float_range

logger = logging.getLogger(__name__)

count_color = (0, 1, 0, 0.2)


def is_date(d) -> bool:
    """Checks if d is a date-like object"""
    if isinstance(d, datetime.datetime):
        return True
    return False


def get_kwargs(o: dict, keys: list) -> dict:
    """
    Returns object with key-value pairs specified by keys
    """
    kwargs = {}
    for key in keys:
        if key in o:
            kwargs[key] = o[key]
    return kwargs


def write_json(o, fname):
    write_file(json_dumps(o), fname)


def write_file(txt, fname):
    """
    Convenience wrapper that checks for directory and uses block scope
    """
    ensure_dir(os.path.dirname(fname))
    with open(fname, "w") as f:
        f.write(txt)


def json_dumps(o):
    """
    Convenience dumper to JSON-string that converts datetimes to datetime strings
    """
    return json.dumps(o, default=json_converter, indent=2)


def ensure_dir(d):
    """
    Makes a directory if it does not already exist
    """
    if d is "":
        return
    if not os.path.isdir(d):
        os.makedirs(d)


def json_converter(o):
    """
    Converts to ISO datestring depending on type of o
    """
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    if isinstance(o, numpy.ndarray):
        return list(o)


def init():
    matplotlib.style.use("ggplot")


init()


def create_graph() -> dict:
    """
    Generates a default template for a graph, including all the essential
    fields to use in ``graphing.make_matplotlib_fig()``.
    """
    graph = {
        "datasets": [],
        "hlines": [],
        "vlines": [],
        "basename": "",
        "title": "",
        "ylabel": "",
        "xlabel": "",
        "xmin": None,
        "xmax": None,
        "is_legend": False,
        "summary": {},
    }
    return graph


def lighten_color(color, amount=None, opacity=None):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:

    .. code-block:: python

        lighten_color('g', 0.3)
        lighten_color('#F034A3', 0.6)
        lighten_color((.3,.55,.1), 0.5)

    """
    try:
        c = matplotlib.colors.cnames[color]
    except:
        c = color
    if amount is not None:
        c = colorsys.rgb_to_hls(*matplotlib.colors.to_rgb(c))
        c = colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])
    if opacity is not None:
        rgb = matplotlib.colors.to_rgb(c)
        c = (*rgb, opacity)
    return c


def get_default_color(i):
    """Returns the ith color in the default matplotlib palette"""
    cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    return cycle[i % len(cycle)]


def get_rgb(color):
    """Returns a 3-tuple from a color or color string"""
    return matplotlib.colors.to_rgb(color)


def make_matplotlib_figure(graph: dict, png: str) -> Figure:
    """
    Generates a matplotlib figure from a graph dictionary, which
    is described in the module docstring.

    Avoids using the pyplot figure manager and thus can
    be gc managed by standard Python
    https://stackoverflow.com/questions/16334588/create-a-figure-that-is-reference-counted/16337909#16337909
    """
    figsize = graph.get("figsize", [15, 4])
    if graph.get("is_compact"):
        figsize = (figsize[0], 2)

    figure = Figure(figsize=figsize)

    ax1 = figure.add_subplot(111)
    axes = [ax1]
    for dataset in graph.get("datasets", []):
        if dataset.get("secondary"):
            ax2 = ax1.twinx()
            ax2.grid(False)
            axes.append(ax2)

    # decide if we have dates or scalar x-axis
    is_xaxis_date = False
    is_x_empty = True
    for dataset in graph.get("datasets", []):
        xvals = dataset.get("xvals", [])
        if len(xvals) > 0:
            is_x_empty = False
            if is_date(xvals[0]):
                is_xaxis_date = True
                break

    # Following needs to be done for both primary
    # and secondary axes to keep them in sync
    for ax in axes:
        # figure out the central plotting area
        # relative to the png, allowing sufficent
        # space for axis decorations such as ticks
        # and legends
        bounds = list(ax.get_position().bounds)
        y_spacer = 1 / figsize[1] * 0.5
        bounds[0] = 0.07
        bounds[2] = 0.87
        bounds[1] = y_spacer
        bounds[3] = 1.0 - 1.5 * y_spacer
        ax.set_position(bounds, which="both")

        if graph.get("is_compact"):
            bounds = list(ax.get_position().bounds)
            bounds[1] = 0.15
            bounds[3] = 0.85
            ax.set_position(bounds, which="both")

        if not graph.get("is_flush_right"):
            bounds = list(ax.get_position().bounds)
            bounds[0] = 0.07
            bounds[2] = 0.77
            ax.set_position(bounds, which="both")

        if graph.get("is_summary_table"):
            bounds = list(ax.get_position().bounds)
            bounds[0] = 0.35
            bounds[2] = 0.4
            ax.set_position(bounds, which="both")

        ax2_color = get_default_color(0)
        ax2_ylabel = ""

        # loop through all the graph views
        for dataset in graph.get("datasets", []):

            if ax == ax1 and dataset.get("secondary"):
                continue

            if ax != ax1 and not dataset.get("secondary"):
                continue

            if ax != ax1:
                if dataset.get("color"):
                    ax2_color = dataset["color"]
                if dataset.get("secondary_ylabel"):
                    ax2_ylabel = dataset["secondary_ylabel"]

            if dataset["graph_type"] == "line":
                kwargs = get_kwargs(
                    dataset,
                    [
                        "label",
                        "color",
                        "ls",
                        "linestyle",
                        "linewidth",
                        "marker",
                        "markersize",
                    ],
                )
                ax.plot(dataset["xvals"], dataset["yvals"], **kwargs)
            elif dataset["graph_type"] == "scatter":
                kwargs = get_kwargs(
                    dataset, ["label", "color", "ls", "marker", "s", "facecolor"]
                )
                ax.scatter(dataset["xvals"], dataset["yvals"], **kwargs)
            elif dataset["graph_type"] == "errorbar":
                kwargs = get_kwargs(
                    dataset,
                    [
                        "label",
                        "color",
                        "marker",
                        "fmt",
                        "markersize",
                        "elinewidth",
                        "ecolor",
                        "facecolor",
                    ],
                )
                ax.errorbar(
                    dataset["xvals"], dataset["yvals"], yerr=dataset["errors"], **kwargs
                )
            elif dataset["graph_type"] == "bar":
                kwargs = get_kwargs(dataset, ["label", "color", "facecolor", "width"])
                ax.bar(dataset["xvals"], dataset["yvals"], edgecolor="none", **kwargs)
            elif dataset["graph_type"] == "fillbetween":
                kwargs = get_kwargs(dataset, ["label", "color"])
                ax.fill_between(
                    dataset["xvals"],
                    dataset["ystacks"][0],
                    dataset["ystacks"][1],
                    **kwargs,
                )
            elif dataset["graph_type"] == "stack":
                kwargs = get_kwargs(dataset, ["colors"])
                ax.stackplot(dataset["xvals"], dataset["ystacks"], **kwargs)
                for label, color in zip(
                    reversed(dataset["labels"]), reversed(dataset["colors"])
                ):
                    ax.plot([], [], label=label, color=color)
            elif dataset["graph_type"] == "label":
                kwargs = get_kwargs(dataset, ["linestyle", "ls", "linewidth"])
                ax.plot(
                    [], [], label=dataset["label"], color=dataset["color"], **kwargs
                )
            elif dataset["graph_type"] == "counts":
                pass  # handle after limits
            else:
                raise Exception(f"Did not recognize graph_type={dataset['graph_type']}")

        if ax != ax1:
            if ax2_ylabel:
                ax.set_ylabel(ax2_ylabel, color=ax2_color)
            ax.tick_params(axis="y", labelcolor=ax2_color)

        if ax == ax1 and not is_x_empty:
            if is_xaxis_date:
                left, right = ax.get_xlim()
                if graph.get("xmin") is not None:
                    left = date2num(graph["xmin"])
                if graph.get("xmax") is not None:
                    right = date2num(graph["xmax"])
                n = right - left + 1
                if n > 700:
                    ax.xaxis.set_major_locator(matplotlib.dates.YearLocator())
                    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
                elif n > 30:
                    ax.xaxis.set_major_locator(
                        matplotlib.dates.DayLocator(bymonthday=1)
                    )
                    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b%y"))
                else:
                    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=7))
                    ax.xaxis.set_major_formatter(
                        matplotlib.dates.DateFormatter("%-d%b%y")
                    )
                ax.set_xlim(left=left, right=right)
            else:
                left, right = ax.get_xlim()
                if graph.get("xmin") is not None:
                    left = graph["xmin"]
                if graph.get("xmax") is not None:
                    right = graph["xmax"]
                n = right - left + 1
                if n < 30 and n > 5:
                    labels = range(int(left), int(right) + 1)
                    ax.set_xticks(labels)
                    ax.set_xticklabels(labels)
                    ax.set_xlim(left=left, right=right)

        # allow overriding of graph limits,
        # makes sure done after setting xticks
        if graph.get("xmin") is not None:
            ax.set_xlim(left=graph["xmin"])

        if graph.get("xmax") is not None:
            ax.set_xlim(right=graph["xmax"])

    if graph.get("vlines"):
        for vline in graph["vlines"]:
            x = vline["x"]
            kwargs = get_kwargs(vline, ["ls", "color", "linewidth"])
            ax1.axvline(x, **kwargs)

    if graph.get("hlines"):
        for hline in graph["hlines"]:
            y = hline["y"]
            kwargs = get_kwargs(hline, ["ls", "linestyle", "color", "linewidth"])
            ax1.axhline(y, **kwargs)

    if graph.get("ymin") is not None:
        ax1.set_ylim(bottom=graph["ymin"])

    if graph.get("ymax") is not None:
        ax1.set_ylim(top=graph["ymax"])

    if graph.get("ylabel"):
        ax1.set_ylabel(graph["ylabel"])

    if graph.get("xlabel"):
        ax1.set_xlabel(graph["xlabel"])

    face_color = graph.get("gridbox_color", (0.9, 0.9, 0.9))
    ax1.set_facecolor(face_color)

    if graph.get("is_ylog"):
        if not is_x_empty:
            ax1.set_yscale("log")

    if graph.get("yticks"):
        yticks = graph["yticks"]
        ax1.set_yticks(yticks["vals"], yticks["labels"])

    # recolor the axes and axes decorators
    ax_color = graph.get("axis_color", (0.4, 0.4, 0.4))

    ax1.tick_params(axis="x", colors=ax_color)
    ax1.tick_params(axis="y", colors=ax_color)
    ax1.yaxis.label.set_color(ax_color)
    ax1.xaxis.label.set_color(ax_color)

    grid_box_border_color = "none"
    ax1.spines["bottom"].set_color(grid_box_border_color)
    ax1.spines["top"].set_color(grid_box_border_color)
    ax1.spines["right"].set_color(grid_box_border_color)
    ax1.spines["left"].set_color(grid_box_border_color)

    # format and move the legend to the right-hand side
    # out of the central graphing area
    if graph.get("is_legend"):
        font = matplotlib.font_manager.FontProperties()
        legend = ax1.legend(bbox_to_anchor=(1, 1), loc="upper left", prop=font)
        frame = legend.get_frame()
        frame.set_facecolor("none")
        frame.set_edgecolor("none")
        for text in legend.get_texts():
            text.set_color(ax_color)

    if graph.get("title"):
        if graph.get("is_compact"):
            ax1.title.set_color("black")
            ax1.set_title(
                graph["title"],
                x=0.01,
                y=0.87,
                horizontalalignment="left",
                verticalalignment="top",
            )
        else:
            ax1.set_title(graph["title"])

    # add the counts frequency at the bottom
    # of the graph, must do after limits have
    # been set in order to determine the size
    # of the graph which is 0.1 of the graph height
    is_count = False
    max_count = None
    for dataset in graph.get("datasets", []):
        if dataset["graph_type"] == "counts":
            kwargs = get_kwargs(dataset, ["label", "color"])
            ymin, ymax = ax1.get_ylim()
            ax1.set_ylim(bottom=ymin)
            yvals = dataset["yvals"]
            val_max = max(yvals)
            if max_count is None:
                max_count = val_max
            elif val_max > max_count:
                max_count = val_max
            yvals = [v / val_max * 0.1 * (ymax - ymin) + ymin for v in yvals]
            lowers = [ymin] * len(yvals)
            ax1.fill_between(dataset["xvals"], yvals, lowers, **kwargs)
            is_count = True

    if is_count:
        text = f"{max_count} wells"
        ymin, ymax = ax1.get_ylim()
        ax1.axhline(0.1 * (ymax - ymin) + ymin, color=count_color, ls=":")
        ax1.text(
            1.006,
            0.1,
            text,
            color=count_color,
            transform=ax1.transAxes,
            verticalalignment="center",
        )

    if png is not None:
        FigureCanvas(figure).print_figure(png)

    return figure


def make_png_transparent(png, target=(255, 255, 255)):
    img = Image.open(png)
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] == target[0] and item[1] == target[1] and item[2] == target[2]:
            new_data.append((*target, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    img.save(png, "PNG")


def write_graph(graph, directory=".", transparent=False):
    """Generates a .png from a graph dict, with a flag
    to turn the white background transparent."""
    json_fname = os.path.join(directory, graph["basename"] + ".json")
    write_json(graph, json_fname)
    png = os.path.join(directory, graph["basename"] + ".png")
    graph["png"] = os.path.basename(png)
    logger.info(f"write_graph {png}")
    make_matplotlib_figure(graph, png)
    if transparent:
        make_png_transparent(png)
    return png


def make_vline(x, color):
    return {
        "x": x,
        "color": lighten_color(color, opacity=0.5),
        "ls": "--",
        "linewidth": 2,
    }


def make_graphs_from_model(model, directory=".", transparent=False):
    model.run()
    model.calc_aux_var_solutions()

    graphs = []
    for plot in model.plots:

        if "title" in plot:

            basename, keys = "plot-" + plot["title"], plot["vars"]
            graph = {"basename": basename, "is_legend": True, "datasets": []}
            for key in keys:
                dataset = {
                    "graph_type": "line",
                    "xvals": model.times,
                    "yvals": model.solution[key],
                    "label": key,
                }
                graph["datasets"].append(dataset)
            graphs.append(graph)

        elif "fn" in plot:

            fn = plot["fn"]
            basename, xlims = "plot-" + fn, plot["xlims"]
            d = (xlims[1] - xlims[0]) / 100.0
            x_vals = list(float_range(xlims[0], xlims[1], d))
            graph = {"basename": basename, "is_legend": True, "datasets": []}
            dataset = {
                "graph_type": "line",
                "xvals": x_vals,
                "yvals": [model.fn[fn](x) for x in x_vals],
                "label": fn,
            }
            graph["datasets"].append(dataset)
            graphs.append(graph)

    for graph in graphs:
        write_graph(graph, directory, transparent)

    return graphs
