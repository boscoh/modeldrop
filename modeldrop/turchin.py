from .basemodel import BaseModel, make_approach_fn


class TurchinDemographicStateModel(BaseModel):
    def setup(self):
        self.url = (
            "https://github.com/boscoh/modeldrop/blob/master/modeldrop/turchin.py"
        )

        self.param.time = 500
        self.param.maxSurplus = 1
        self.param.taxOnSurplus = 1
        self.param.growth = 0.02
        self.param.expenditurePerCapita = 0.25
        self.param.stateRevenueAtHalfCapacity = 10
        self.param.maxCarryCapacity = 3

        self.setup_ui()

    def init_vars(self):
        self.fns.carryingCapacityFn = make_approach_fn(
            1, self.param.maxCarryCapacity,
            self.param.stateRevenueAtHalfCapacity
        )
        self.var.populationDensity = 0.2
        self.var.stateRevenue = 0

    def calc_aux_vars(self):
        self.aux_var.carryingCapacity = self.fns.carryingCapacityFn(
            self.var.stateRevenue
        )
        self.aux_var.surplus = self.param.maxSurplus * (
            1 - self.var.populationDensity / self.aux_var.carryingCapacity
        )

    def calc_dvars(self, t):
        self.dvar.populationDensity = (
            self.param.growth * self.var.populationDensity * self.aux_var.surplus
        )
        self.dvar.stateRevenue = (
            self.param.taxOnSurplus * self.var.populationDensity * self.aux_var.surplus
            - self.param.expenditurePerCapita * self.var.populationDensity
        )

    def setup_ui(self):
        self.plots = [
            {
                "title": "People",
                "vars": ["populationDensity", "carryingCapacity"],
                "ymin": 0,
            },
            {"title": "Surplus", "vars": ["surplus"]},
            {"title": "State Revenue", "vars": ["stateRevenue"]},
            {
                "fn": "carryingCapacityFn",
                "xlims": [0, 100],
                "ymin": 0,
                "var": "stateRevenue",
            },
        ]

        self.editable_params = [
            {"key": "time", "max": 1000},
            {"key": "maxSurplus", "max": 2,},
            {"key": "taxOnSurplus", "max": 2,},
            {"key": "growth", "max": 0.1,},
            {"key": "stateRevenueAtHalfCapacity", "max": 50,},
            {"key": "maxCarryCapacity", "max": 10,},
        ]
