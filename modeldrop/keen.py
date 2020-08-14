import math
from .basemodel import BaseModel, float_range, make_cutoff_fn, make_lin_fn, make_exp_fn, make_sq_fn


class KeenModel(BaseModel):
    def __init__(self):
        super().__init__({})
        self.param.time = 150
        self.param.dt = 0.1
        self.param.timeStep = -1

        self.param.birthRate = 0.01
        self.param.capitalAccelerator = 3
        self.param.depreciationRate = 0.06
        self.param.productivityRate = 0.02
        self.param.initialWage = 0.850
        self.param.initialLaborFraction = 0.61
        self.param.interestRate = 0.04

        wageSqFn = make_sq_fn(0.000_064_1, 1, 1, 0.040_064_1)
        self.fns.wageFn = make_cutoff_fn(wageSqFn, 0.9999)
        investSqFn = make_sq_fn(0.0175, 0.53, 6, 0.065)
        self.fns.investFn = make_cutoff_fn(investSqFn, 0.0829999999)

        self.fns.wageFn = make_exp_fn(0.95, 0.0, 0.5, -0.01)
        self.fns.investFn = make_exp_fn(0.05, 0.05, 1.75, 0)

        self.fns.wageFn = make_lin_fn(4, 0.6)
        self.fns.investFn = make_lin_fn(10, 0.03)

        self.editable_params = [
            {"key": "time", "max": 300,},
            {"key": "timeStep", "max": 10, "min": 0.001, "is_log10": True},
            {"key": "birthRate", "max": 0.1,},
            {"key": "capitalAccelerator", "max": 5,},
            {"key": "depreciationRate", "max": 0.1,},
            {"key": "productivityRate", "max": 0.1,},
            {"key": "initialLaborFraction", "max": 1.0,},
            {"key": "interestRate", "max": 0.2,},
        ]
        self.model_plots = [
            {
                "key": "Share of Output",
                "vars": ["bankShare", "wageShare", "profitShare"],
            },
            {"key": "People", "vars": ["population", "labor"]},
            {"key": "Output", "vars": ["output", "wages", "debt", "profit", "bank"]},
        ]
        self.fn_plots = [
            {"fn": "wageFn", "xlims": [0.8, 1.1]},
            {"fn": "investFn", "xlims": [-0.5, 0.3]},
        ]

    def init_vars(self):
        self.var.wage = self.param.initialWage
        self.var.productivity = 1
        self.param.dt = self.param.timeStep
        self.var.population = 100
        self.var.laborFraction = self.param.initialLaborFraction
        self.var.output = self.param.initialLaborFraction * self.var.population * self.var.productivity
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
        self.calc_aux_vars()

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


if __name__ == "__main__":
    KeenModel().make_graph_pngs(is_open=True)
