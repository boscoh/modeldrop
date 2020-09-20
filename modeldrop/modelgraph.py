from .basemodel import float_range
from .graphing import write_graph


def make_graphs_from_model(model, directory=".", transparent=False):
    model.run()

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
