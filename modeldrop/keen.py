from .basemodel import BaseModel, make_lin_fn


class KeenDynamicEconomyModel(BaseModel):
    def setup(self):
        self.url = "https://github.com/boscoh/modeldrop/blob/master/modeldrop/keen.py"

        self.param.time = 150
        self.param.dt = 0.1

        self.param.birthRate = 0.01
        self.param.capitalAccelerator = 3
        self.param.depreciationRate = 0.06
        self.param.productivityRate = 0.02

        self.param.interestRate = 0.04
        self.param.investSlope = 10
        self.param.investXOrigin = 0.03
        self.param.wageSlope = 4
        self.param.wageXOrigin = 0.6

        self.param.initialWage = 0.850
        self.param.initialLaborFraction = 0.61

        self.setup_ui()

    def init_vars(self):
        self.fns.wageFn = make_lin_fn(self.param.wageSlope, self.param.wageXOrigin)

        self.fns.investFn = make_lin_fn(
            self.param.investSlope, self.param.investXOrigin
        )

        self.var.wage = self.param.initialWage
        self.var.productivity = 1
        self.var.population = 100
        self.var.laborFraction = self.param.initialLaborFraction
        self.var.output = (
            self.param.initialLaborFraction
            * self.var.population
            * self.var.productivity
        )
        self.var.wageShare = self.var.wage / self.var.productivity
        self.var.debtRatio = 0.0

    def calc_aux_vars(self):
        self.aux_var.labor = self.var.laborFraction * self.var.population
        self.aux_var.wageDelta = self.fns.wageFn(self.var.laborFraction)
        self.aux_var.laborWages = self.var.wage * self.aux_var.labor
        self.aux_var.wages = self.var.wage * self.aux_var.labor

        self.aux_var.capital = self.var.output * self.param.capitalAccelerator

        self.aux_var.bankShare = self.param.interestRate * self.var.debtRatio
        self.aux_var.profitShare = 1 - self.var.wageShare - self.aux_var.bankShare

        self.aux_var.profitRate = (
            self.aux_var.profitShare / self.param.capitalAccelerator
        )

        self.aux_var.investDelta = self.fns.investFn(self.aux_var.profitRate)
        self.aux_var.realGrowthRate = (
            self.aux_var.investDelta / self.param.capitalAccelerator
            - self.param.depreciationRate
        )

        self.aux_var.debt = self.var.debtRatio * self.var.output
        self.aux_var.bank = self.aux_var.bankShare * self.var.output
        self.aux_var.profit = self.aux_var.profitShare * self.var.output

        self.aux_var.investment = self.aux_var.investDelta * self.var.output
        self.aux_var.borrow = self.aux_var.investment - self.aux_var.profit

    def calc_dvars(self, t):
        self.dvar.wage = self.aux_var.wageDelta * self.var.wage

        self.dvar.productivity = self.param.productivityRate * self.var.productivity

        self.dvar.population = self.param.birthRate * self.var.population

        self.dvar.laborFraction = self.var.laborFraction * (
            self.aux_var.realGrowthRate
            - self.param.productivityRate
            - self.param.birthRate
        )

        self.dvar.output = self.var.output * self.aux_var.realGrowthRate

        self.dvar.wageShare = self.var.wageShare * (
            self.aux_var.wageDelta - self.param.productivityRate
        )

        self.dvar.debtRatio = (
            self.aux_var.investDelta
            - self.aux_var.profitShare
            - self.var.debtRatio * self.aux_var.realGrowthRate
        )

    def setup_ui(self):
        self.editable_params = [
            {"key": "time", "max": 500,},
            {"key": "birthRate", "max": 0.1,},
            {"key": "capitalAccelerator", "max": 5,},
            {"key": "depreciationRate", "max": 0.1,},
            {"key": "productivityRate", "max": 0.1,},
            {"key": "initialLaborFraction", "max": 1.0,},
            {"key": "interestRate", "max": 0.2,},
            {"key": "wageSlope", "max": 30, "min": -30},
            {"key": "wageXOrigin", "max": 1, "min": -1},
            {"key": "investSlope", "max": 30, "min": -30},
            {"key": "investXOrigin", "max": 0.5, "min": -0.5},
        ]
        self.plots = [
            {
                "title": "Share",
                "vars": ["bankShare", "wageShare", "profitShare"],
                "ymin_cutoff": -0.5,
                "ymax_cutoff": 1.5,
            },
            {"title": "People", "vars": ["population", "labor"]},
            {"title": "Output", "vars": ["output", "wages", "debt", "profit", "bank"]},
            {"fn": "wageFn", "xlims": [0, 1], "var": "laborFraction"},
            {"fn": "investFn", "xlims": [-0.5, 0.5], "var": "profitRate"},
        ]
