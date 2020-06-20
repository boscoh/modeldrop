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
from typing import Any, Dict, List, Optional

import arrow
import matplotlib
import numpy
import pandas
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.dates import date2num
from matplotlib.figure import Figure
from pandas.plotting import register_matplotlib_converters
from PIL import Image
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)

count_color = (0, 1, 0, 0.2)


def number(n: Any) -> Optional[float]:
    """
    Converts numbers to JSON-friendly format
    """
    return None if pandas.isnull(n) else float(n)


def is_date(d: Any) -> bool:
    """Checks if d is a date-like object"""
    if isinstance(d, datetime.datetime):
        return True
    if isinstance(d, arrow.Arrow):
        return True
    if isinstance(d, pandas.Timestamp):
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
    return json.dumps(o, default=convert_to_datestring, indent=2)


def ensure_dir(d):
    """
    Makes a directory if it does not already exist
    """
    if d is "":
        return
    if not os.path.isdir(d):
        os.makedirs(d)


def convert_to_datestring(o):
    """
    Converts to ISO datestring depending on type of o
    """
    if (
        isinstance(o, datetime.datetime)
        or isinstance(o, arrow.Arrow)
        or isinstance(o, pandas.Timestamp)
    ):
        return o.isoformat()
    if isinstance(o, pandas.DatetimeIndex):
        return [t.isoformat() for t in o]


def init():
    register_matplotlib_converters()
    matplotlib.style.use("ggplot")
    # plt.rcParams["font.family"] = '"Helvetica Neue" "Helvetica" Serif'


init()


def create_graph() -> Dict:
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


def make_linear_fitted_lines(series, t0, t1, color, is_linear_fit=True):
    """Generates a dataset that draws a line of best fit for
    a time-series between the times [t0, t1]. The dataset
    will also a summary dictionary that stores the parameters
    of the fit.
    """
    xvals = [t0, t1]

    mean = series.mean()
    std = series.std()

    y0 = float(mean)
    y1 = float(mean)

    slope = None
    intercept = None

    if is_linear_fit:
        try:
            model = LinearRegression()
            times = series.index

            if is_date(times[0]):
                date_nums = date2num(times).reshape(-1, 1)
            else:
                date_nums = numpy.array(times).reshape(-1, 1)

            model.fit(date_nums, numpy.array(series.values).reshape(-1, 1))

            slope = float(model.coef_[0][0])
            intercept = float(model.intercept_[0])

            if is_date(xvals[0]):
                predict_xvals = date2num(xvals)
            else:
                predict_xvals = numpy.array(xvals)

            predicted_yvals = model.predict(predict_xvals.reshape(-1, 1))

            [y0, y1] = [y[0] for y in predicted_yvals]
        except:
            logger.warning(
                "make_linear_fitted_lines warning: failed to find linear fit"
            )
            pass

    result = [
        {
            "yvals": [y0, y1],
            "xvals": xvals,
            "summary": {
                "mean": number(mean),
                "std": number(std),
                "slope": number(slope),
                "intercept": number(intercept),
                "color": matplotlib.colors.to_rgb(color),
            },
            "color": lighten_color(color, 1.3),
            "ls": "--",
            "linewidth": 2,
            "graph_type": "line",
        },
        {
            "ystacks": [[y0 - std, y1 - std], [y0 + std, y1 + std]],
            "xvals": xvals,
            "color": lighten_color(color, 0.8, 0.2),
            "ls": ":",
            "graph_type": "fillbetween",
        },
    ]
    return result


def is_more_than_a_day_apart(time0, time1):
    timedelta = time1 - time0
    if is_date(time0):
        return abs(timedelta.days) > 1
    else:
        return timedelta > 1


def split_dataset(
    dataset: Dict, is_discontinous_fn=is_more_than_a_day_apart
) -> List[Dict]:
    """Returns a list of dataset, each of which is a subset of
    the original dataset, where the split occurs whenever there
    is a discontinuity between x-values."""
    result = []

    def add_result(i, j):
        sub_dataset = {}
        for key in dataset.keys():
            sub_dataset[key] = dataset[key][i:j]
        result.append(sub_dataset)

    i_start = 0
    xvals = dataset["xvals"]
    n = len(xvals)
    for i in range(1, n):
        if i == n - 1:
            add_result(i_start, n)
        elif is_discontinous_fn(xvals[i - 1], xvals[i]):
            add_result(i_start, i)
            i_start = i
    return result


def get_filled_daily_times(times):
    """
    Backfills a list of times so that missing days are included
    in the list
    """
    if len(times) == 0:
        return []
    full_times = [times[0]]
    is_date = is_date(times[0])
    for i in range(1, len(times)):
        if is_date:
            days = abs((times[i - 1] - times[i]).days)
        else:
            days = times[i - 1] - times[i]
        if days > 1:
            for i_day in range(days - 1):
                if is_date:
                    new_time = times[i - 1] + datetime.timedelta(days=i_day)
                else:
                    new_time = times[i - 1] + i_day
                full_times.append(new_time)
        full_times.append(times[i])
    return full_times


def make_daily_aggregated_dataset(times, values, method="avg", min_time=None):
    """Consolidate a time-series with multiple values at each
    time step into a base dataset where x-vals are unique
    times and y-vals are aggregations of all values at
    a particular time
    """
    values_by_time = {}
    for time, y in zip(times, values):
        if pandas.isnull(time):
            continue
        if min_time is not None:
            if time < min_time:
                continue
        if time not in values_by_time:
            values_by_time[time] = []
        values_by_time[time].append(y)

    dataset = {}
    dataset["xvals"] = []
    dataset["yvals"] = []
    dataset["counts"] = []
    dataset["neg_stds"] = []
    dataset["pos_stds"] = []
    dataset["uppers"] = []
    dataset["lowers"] = []
    dataset["stds"] = []

    times = list(sorted(values_by_time.keys()))

    for time in get_filled_daily_times(times):
        if time in values_by_time:
            values = numpy.array(values_by_time[time])
            count = len(values)
            if method == "avg":
                mean = values.mean()
                std = values.std()
            else:  # method == "sum":
                mean = values.sum()
                std = 0
            diffs = values - mean
            pos_diffs = diffs[diffs >= 0]
            var = sum([d * d for d in pos_diffs])
            pos_std = numpy.sqrt(var / len(pos_diffs)) if len(pos_diffs) else 0
            neg_diffs = diffs[diffs <= 0]
            var = sum([d * d for d in neg_diffs])
            neg_std = numpy.sqrt(var / len(neg_diffs)) if len(neg_diffs) else 0
        else:
            count = 0
            mean = numpy.nan
            std = 0
            pos_std = 0
            neg_std = 0

        dataset["xvals"].append(time)
        dataset["yvals"].append(mean)
        dataset["pos_stds"].append(pos_std)
        dataset["neg_stds"].append(neg_std)
        dataset["uppers"].append(mean + pos_std)
        dataset["lowers"].append(mean - neg_std)
        dataset["stds"].append(std)
        dataset["counts"].append(count)

    dataset["errors"] = [dataset["neg_stds"], dataset["pos_stds"]]

    return dataset


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


def fill_missing_days_in_dataset(dataset):
    """
    Backfills a list of times so that missing days are included
    in the list, and vals at those points are set to nan
    """
    if "xvals" not in dataset:
        return

    xvals = dataset["xvals"]

    if len(xvals) == 0:
        return

    is_xdate = is_date(xvals[0])

    is_ystacks = "ystacks" in dataset
    if is_ystacks:
        ystacks = dataset["ystacks"]
        n_ystack = len(ystacks)
    else:
        yvals = dataset["yvals"]

    full_xvals = [xvals[0]]
    if is_ystacks:
        full_ystacks = [[ystacks[i][0]] for i in range(n_ystack)]
    else:
        full_yvals = [yvals[0]]

    for i in range(1, len(xvals)):
        if is_xdate:
            days = abs((xvals[i - 1] - xvals[i]).days)
        else:
            days = xvals[i - 1] - xvals[i]
        if days > 1:
            for i_day in range(days - 1):
                if is_xdate:
                    new_time = xvals[i - 1] + datetime.timedelta(days=i_day)
                else:
                    new_time = xvals[i - 1] + i_day
                full_xvals.append(new_time)
                if is_ystacks:
                    for i_stack in range(n_ystack):
                        full_ystacks[i_stack].append(numpy.nan)
                else:
                    full_yvals.append(numpy.nan)
        full_xvals.append(xvals[i])
        if is_ystacks:
            for i_stack in range(n_ystack):
                full_ystacks[i_stack].append(ystacks[i_stack][i])
        else:
            full_yvals.append(yvals[i])

    dataset["xvals"] = full_xvals
    if is_ystacks:
        dataset["ystacks"] = full_ystacks
    else:
        dataset["yvals"] = full_yvals


def make_ts_scatter_dataset(ts, color):
    return {
        "xvals": ts.index.to_list(),
        "yvals": ts.to_list(),
        "graph_type": "scatter",
        "color": lighten_color(color, 0.7, opacity=0.2),
    }


def make_ts_line_dataset(ts, color, ls="--"):
    return {
        "xvals": ts.index.to_list(),
        "yvals": ts.to_list(),
        "linewidth": 2,
        "graph_type": "line",
        "ls": ls,
        "color": lighten_color(color, 0.9),
    }


def make_vline(x, color):
    return {
        "x": x,
        "color": lighten_color(color, opacity=0.5),
        "ls": "--",
        "linewidth": 2,
    }
