import logging

from modeldrop.app import DashModelAdaptor, open_url_in_background
from modeldrop.basemodel import BaseModel
from modeldrop.goodwin import GoodwinModel
from modeldrop.keen import KeenModel
from modeldrop.property import PropertyModel


class DemographicFiscalModel(BaseModel):
    def __init__(self):
        super().__init__({})

        self.param.time = 500
        # self.param.carryingCapacityLimit = 1
        self.param.maxSurplus = 1
        self.param.taxOnSurplus = 1
        self.param.growth = 0.02
        self.param.expenditurePerCapita = 0.25
        self.param.stateAtHalfCapacity = 10
        self.param.carryCapacityDiff = 3
        self.fns.carryCapacityFromStateRevenue = lambda state: (
            1
            + self.param.carryCapacityDiff
            * (state / (self.param.stateAtHalfCapacity + state))
        )

        self.model_plots = [
            {
                "key": "People",
                "vars": ["populationDensity", "carryingCapacity"],
                "ymin": 0,
            },
            {"key": "Surplus", "vars": ["surplus"]},
            {"key": "State Revenue", "vars": ["state"]},
        ]

        self.fn_plots = [
            {"fn": "carryCapacityFromStateRevenue", "xlims": [0, 100], "ymin": 0},
        ]

        self.editable_params = [
            {"key": "time", "max": 1000},
            {"key": "maxSurplus", "max": 2,},
            {"key": "taxOnSurplus", "max": 2,},
            {"key": "growth", "max": 0.1,},
            # {"key": "carryingCapacityLimit", "max": 2,},
        ]

        self.init_var.populationDensity = 0.2
        self.init_var.state = 0

    def calc_aux_vars(self):
        s = self.var.state if self.var.state > 0 else 0
        self.aux_var.carryingCapacity = self.fns.carryCapacityFromStateRevenue(s)
        self.aux_var.surplus = self.param.maxSurplus * (
            1 - self.var.populationDensity / self.aux_var.carryingCapacity
        )

    def calc_dvars(self, t):
        self.calc_aux_vars()
        self.dvar.populationDensity = (
            self.param.growth * self.var.populationDensity * self.aux_var.surplus
        )
        self.dvar.state = (
            self.param.taxOnSurplus * self.var.populationDensity * self.aux_var.surplus
            - self.param.expenditurePerCapita * self.var.populationDensity
        )
        if self.var.state < 0 and self.dvar.state <= 0:
            self.dvar.state = 0
            self.var.state = 0

# logging.basicConfig(level=logging.DEBUG)
models = [DemographicFiscalModel(), PropertyModel(), KeenModel(), GoodwinModel()]
port = "8050"
open_url_in_background(f"http://127.0.0.1:{port}/")
DashModelAdaptor(models).run_server(port=port)
