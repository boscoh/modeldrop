import logging
import math

from scipy.integrate import odeint

logger = logging.getLogger(__name__)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def float_range(start, stop, step):
    while start < stop:
        yield float(start)
        start += step


class BaseModel:
    def __init__(self, param=None):
        self.param = AttrDict()
        if param is not None:
            for k, v in param.items():
                self.param[k] = v

        self.init_var = AttrDict()

        self.var = AttrDict()
        self.dvar = AttrDict()
        self.aux_var = AttrDict()

        self.fns = AttrDict()

        self.param.dt = 1
        self.times = None
        self.solution = AttrDict()

        self.editable_params = []
        self.model_plots = []
        self.fn_plots = []

        self.setup()

    def setup(self):
        pass

    def reset_solutions(self):
        self.solution.clear()

    def init_vars(self):
        for key, val in self.init_var.items():
            self.var[key] = val

    def calc_vars(self):
        pass

    def calc_dvars(self, t):
        pass

    def calc_aux_vars(self):
        pass

    def update(self, t):
        self.calc_dvars(t)
        for key in self.dvar.keys():
            self.var[key] += self.dvar[key] * self.param.dt
        self.calc_vars()

    def crude_integrate(self):
        for time in self.times:
            self.update(time)
            for key in self.keys:
                if not key in self.solution:
                    self.solution[key] = []
                if math.isfinite(self.var[key]):
                    self.solution[key].append(self.var[key])
                else:
                    self.solution[key].append(None)

    def scipy_integrate(self):
        def func(y, t):
            for v, key in zip(y, self.keys):
                self.var[key] = v
            self.calc_dvars(t)
            dVar = [self.dvar[k] for k in self.keys]
            return dVar

        y_init = [self.var[key] for key in self.keys]

        self.output, info_dict = odeint(func, y_init, self.times, full_output=True)

        for i, key in enumerate(self.keys):
            self.solution[key] = self.output[:, i]

    def chunky_run(self):
        self.reset_solutions()
        self.init_vars()
        self.times = list(float_range(0, self.param.time, self.param.dt))
        self.keys = self.var.keys()
        self.crude_integrate()

    def run(self):
        self.reset_solutions()
        self.init_vars()
        self.times = list(float_range(0, self.param.time, self.param.dt))
        self.keys = list(self.var.keys())
        self.scipy_integrate()

    def calc_aux_var_solutions(self):
        for i_time, time in enumerate(self.times):
            for key in self.keys:
                if key in self.solution:
                    self.var[key] = self.solution[key][i_time]
            self.calc_aux_vars()
            for key, value in self.aux_var.items():
                if key not in self.solution:
                    self.solution[key] = []
                self.solution[key].append(value)

    def make_output_graph(self, basename, title, keys):
        graph = {"basename": basename, "is_legend": True, "datasets": []}
        for key in keys:
            dataset = {
                "graph_type": "line",
                "xvals": self.times,
                "yvals": self.solution[key],
                "label": key,
            }
            graph["datasets"].append(dataset)
        return graph

    def make_fn_graph(self, basename, fn, xlims):
        graph = {"basename": basename, "is_legend": True, "datasets": []}

        def add_dataset(fn, x_vals):
            dataset = {
                "graph_type": "line",
                "xvals": x_vals,
                "yvals": [self.fns[fn](x) for x in x_vals],
                "label": fn,
            }
            graph["datasets"].append(dataset)

        d = (xlims[1] - xlims[0]) / 100.0
        add_dataset(fn, list(float_range(xlims[0], xlims[1], d)))
        return graph

    def make_graphs(self):
        self.run()
        self.calc_aux_var_solutions()
        result = []
        for plot in self.model_plots:
            graph = self.make_output_graph(
                "plot-" + plot["key"], plot["key"], plot["vars"]
            )
            result.append(graph)
        for plot in self.fn_plots:
            graph = self.make_fn_graph("plot-" + plot["fn"], plot["fn"], plot["xlims"])
            result.append(graph)
        return result


def make_exp_fn(x_val, y_val, scale, y_min):
    y_diff = y_val - y_min
    return lambda x: y_diff * math.exp((scale * (x - x_val)) / y_diff) + y_min


def make_sq_fn(A, B, C, D):
    # x_min = B / C
    def fn(x):
        num = B - C * x
        return A / num / num - D

    return fn


def make_lin_fn(slope, x_zero):
    def fn(x):
        return slope * (x - x_zero)
    return fn


def make_cutoff_fn(fn, x_max):
    y_max = fn(x_max)

    def new_fn(x):
        if x > x_max:
            return y_max
        y = fn(x)
        if y > y_max:
            return y_max
        return y

    return new_fn


