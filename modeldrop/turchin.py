from .basemodel import BaseModel


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
        self.param.stateAtHalfCapacity = 10
        self.param.carryCapacityDiff = 3

        def carryingCapacityFn(state):
            if state < 0:
                return 1
            return 1 + self.param.carryCapacityDiff * (
                state / (self.param.stateAtHalfCapacity + state)
            )

        self.fns.carryingCapacityFn = carryingCapacityFn

        self.init_var.populationDensity = 0.2
        self.init_var.stateRevenue = 0

        self.setup_ui()

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
        self.var_plots = [
            {
                "key": "People",
                "vars": ["populationDensity", "carryingCapacity"],
                "ymin": 0,
            },
            {"key": "Surplus", "vars": ["surplus"]},
            {"key": "State Revenue", "vars": ["stateRevenue"]},
        ]

        self.fn_plots = [
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
        ]
