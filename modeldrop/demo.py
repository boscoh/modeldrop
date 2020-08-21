import sys

from modeldrop.app import show_models
from modeldrop.basemodel import BaseModel


class TurchinEliteDemographicModel(BaseModel):
    def setup(self):
        self.url = (
            "https://github.com/boscoh/modeldrop/blob/master/modeldrop/demo.py"
        )

        self.param.r0 = 2
        self.param.b1 = 0.02
        self.param.b2 = 0.5
        self.param.d1 = 0.02
        self.param.d2 = 0.025
        self.param.g = 1
        self.param.gam = 10
        self.param.a = 1
        self.param.h = 1
        self.param.c = 1
        self.param.al = 0.2
        self.param.stateAtHalfCapacity = 5
        self.param.carryCapacityDiff = 1.5

        self.param.init_p = 1
        self.param.init_e = 0.01
        self.param.init_s = 0.0

        self.setup_plots()

    def init_vars(self):
        self.var.p = self.param.init_p
        self.var.e = self.param.init_e
        self.var.s = self.param.init_s

        def fn(state):
            if state < 0:
                return 1
            return 1 + self.param.carryCapacityDiff * (
                state / (self.param.stateAtHalfCapacity + state)
            )
        self.fns["carryCapacityFromStateRevenue"] = fn

    def calc_aux_vars(self):
        self.aux_var.g = self.fns.carryCapacityFromStateRevenue(self.var.s)
        self.aux_var.x = (
            self.var.p * (1 - (1 / self.aux_var.g) * self.var.p) / (1 + self.var.e)
        )

    def calc_dvars(self, t):
        self.dvar.p = self.param.b1 * self.aux_var.x - self.param.d1 * self.var.p
        self.dvar.e = (
            self.param.b2 * self.var.e * self.aux_var.x
            - self.param.d2 * self.var.e / (1 + self.var.s)
        )
        self.dvar.s = self.param.gam * self.dvar.e - self.param.al * self.var.e

    def setup_plots(self):
        self.plots = [
            {"title": "people", "vars": ["p", "e", "s"], "ymin": -100, "ymax": 100},
        ]
        self.fn_plots = [
            {"fn": "carryCapacityFromStateRevenue", "xlims": [0, 100], "ymin": 0},
        ]
        self.editable_params = [
            {"key": "time", "max": 1000,},
        ]
        self.extract_editable_params()


if __name__ == "__main__":
    model = TurchinEliteDemographicModel()
    show_models([model], sys.argv)
