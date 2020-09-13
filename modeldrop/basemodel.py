import logging
import math

__doc__ = """
"""

from scipy.integrate import odeint


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

        self.var = AttrDict()
        self.dvar = AttrDict()
        self.aux_var = AttrDict()

        self.aux_var_flows = []
        self.param_flows = []

        self.fn = AttrDict()

        self.param.time = 100
        self.param.dt = 1
        self.times = None

        self.solution = AttrDict()

        self.editable_params = []
        self.plots = []
        self.fn_plots = []

        self.setup()

    def setup(self):
        pass

    def init_vars(self):
        pass

    def calc_vars(self):
        pass

    def calc_dvars(self, t):
        pass

    def calc_aux_vars(self):
        pass

    def reset_solutions(self):
        self.solution.clear()

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
        def calc_dvar_array(var_array, t):
            for v, key in zip(var_array, self.keys):
                self.var[key] = v
            self.calc_aux_vars()
            self.calc_dvars(t)
            return [self.dvar[k] for k in self.keys]

        y_init = [self.var[key] for key in self.keys]

        self.output, info_dict = odeint(
            calc_dvar_array, y_init, self.times, full_output=True
        )

        for i, key in enumerate(self.keys):
            self.solution[key] = self.output[:, i]

    def add_to_dvars_from_flows(self):
        flows = []

        if len(self.aux_var_flows):
            for (from_key, to_key, aux_var_key) in self.aux_var_flows:
                val = self.aux_var[aux_var_key]
                flows.append([from_key, to_key, val])

        if len(self.param_flows):
            for (from_key, to_key, param_key) in self.param_flows:
                val = self.param[param_key]
                flows.append([from_key, to_key, val])

        if len(flows):
            for (from_key, to_key, val) in flows:
                self.dvar[from_key] -= val
                self.dvar[to_key] += val

    def chunky_run(self):
        self.check_consistency()
        self.reset_solutions()
        self.init_vars()
        self.times = list(float_range(0, self.param.time, self.param.dt))
        self.keys = self.var.keys()
        self.crude_integrate()

    def run(self):
        self.check_consistency()
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
                "yvals": [self.fn[fn](x) for x in x_vals],
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
        for plot in self.plots:
            if "title" in plot:
                graph = self.make_output_graph(
                    "plot-" + plot["title"], plot["key"], plot["vars"]
                )
                result.append(graph)
            elif "fn" in plot:
                graph = self.make_fn_graph(
                    "plot-" + plot["fn"], plot["fn"], plot["xlims"]
                )
            result.append(graph)
        return result

    def check_consistency(self):
        self.init_vars()
        self.calc_aux_vars()
        self.calc_dvars(0)

        for v in self.var:
            if v not in self.dvar:
                raise Exception(f"var {v} has no matching dvar in self.calc_dvar")

        for v in self.dvar:
            if v not in self.var:
                raise Exception(f"dvar {v} has no matching var for self.init_var")

        for p in self.plots:
            if "vars" in p:
                for v in p["vars"]:
                    if v not in self.var and v not in self.aux_var:
                        raise Exception(
                            f'plot {p["title"]} has var {v} not in self.vars nor in self.aux_vars'
                        )
            if "fn" in p:
                if p["fn"] not in self.fn:
                    raise Exception(f'plot {p["fn"]} has fn {p["fn"]} not in self.fn')

        for p in self.editable_params:
            if p["key"] not in self.param:
                raise Exception(f'editable param {p["key"]} not in self.param')

        for (f, t, v) in self.aux_var_flows:
            if f not in self.var:
                raise Exception(f"flow from_key {f} not in self.var")
            if t not in self.var:
                raise Exception(f"flow to_key {t} not in self.var")
            if v not in self.aux_var:
                raise Exception(f"flow aux_var {v} not in self.aux_var")

        for (f, t, p) in self.param_flows:
            if f not in self.var:
                raise Exception(f"flow from_key {f} not in self.var")
            if t not in self.var:
                raise Exception(f"flow to_key {t} not in self.var")
            if p not in self.param:
                raise Exception(f"flow param {p} not in self.param")

    def extract_editable_params(self):
        for k in self.param:
            if k == "dt":
                continue
            if not is_key_in_list(self.editable_params, key=k):
                val = self.param[k]
                if val > 0:
                    val = 5 * val
                elif val == 0:
                    val = 1
                else:
                    raise Exception("Can't handle negative param")
                self.editable_params.append({"key": k, "max": val})


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


def is_key_in_list(p_list, **kwargs):
    for p in p_list:
        for k, v in kwargs.items():
            if p[k] == v:
                return True
    return False


def make_approach_fn(y_init, y_final, x_at_midpoint):
    def fn(x):
        if x < 0:
            return y_init
        diff_g = y_final - y_init
        return y_init + diff_g * (x / (x_at_midpoint + x))

    return fn
