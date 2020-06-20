from .basemodel import BaseModel, float_range, make_cutoff_fn, make_exp_fn, make_sq_fn


class KeenModel(BaseModel):
    def __init__(self):
        super().__init__({})
        self.param.time = 100
        self.param.dt = 0.1

        self.param.birthRate = 0.01

        self.param.accelerator = 3
        self.param.depreciation = 0.01
        self.param.productivityRate = 0.02
        self.param.interestMultiplier = 0.04
        self.param.interest = 0.04

        # asymptote at x = 1 / 1 = 1
        wageSqFn = make_sq_fn(0.000_064_1, 1, 1, 0.040_064_1)
        self.fns.wageChange = make_cutoff_fn(wageSqFn, 0.9999)
        wageExpFn = make_exp_fn(0.95, 0.0, 0.5, -0.01)
        self.fns.wageChange = wageExpFn

        # asymptote x = 0.53 / 6 = 0.083
        investSqFn = make_sq_fn(0.0175, 0.53, 6, 0.065)
        self.fns.investChange = investSqFn
        self.fns.investChange = make_cutoff_fn(investSqFn, 0.0829999999)
        investExpFn = make_exp_fn(0.05, 0.05, 1.75, 0)
        self.fns.investChange = investExpFn

        self.editable_params = [
            {"key": "time", "max": 500,},
            {"key": "birthRate", "max": 0.1,},
            {"key": "accelerator", "max": 5,},
            {"key": "depreciation", "max": 0.1,},
            {"key": "productivityRate", "max": 0.1,},
            {"key": "interestMultiplier", "max": 0.5,},
            {"key": "interest", "max": 0.2,},
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
            {"fn": "wageChange", "xlims": [0.8, 1.1]},
            {"fn": "investChange", "xlims": [-0.5, 0.3]},
        ]

        self.init_var.wage = 0.95
        self.init_var.productivity = 1
        self.init_var.population = 50
        self.init_var.output = 0.9 * self.init_var.population * self.init_var.productivity
        self.init_var.debt = 0

    def calc_aux_vars(self):
        self.aux_var.labor = self.var.output / self.var.productivity
        self.aux_var.laborFraction = self.aux_var.labor / self.var.population

        self.aux_var.wages = self.var.wage * self.aux_var.labor
        self.aux_var.debtRatio = self.var.debt / self.var.output
        self.aux_var.interest = (
            self.param.interest + self.param.interestMultiplier * self.aux_var.debtRatio
        )
        self.aux_var.bank = self.aux_var.interest * self.var.debt
        self.aux_var.profit = self.var.output - self.aux_var.wages - self.aux_var.bank

        self.aux_var.wageShare = self.aux_var.wages / self.var.output
        self.aux_var.bankShare = self.aux_var.bank / self.var.output
        self.aux_var.profitShare = 1 - self.aux_var.wageShare - self.aux_var.bankShare

        self.aux_var.capital = self.var.output * self.param.accelerator
        self.aux_var.profitRate = self.aux_var.profit / self.aux_var.capital
        self.aux_var.investmentChange = self.fns.investChange(self.aux_var.profitRate)

    def calc_dvars(self, t):
        self.calc_aux_vars()
        self.dvar.output = self.var.output * (
            (self.aux_var.investmentChange / self.param.accelerator)
            - self.param.depreciation
        )
        self.dvar.wage = self.fns.wageChange(self.aux_var.laborFraction) * self.var.wage
        self.dvar.productivity = self.param.productivityRate * self.var.productivity
        self.dvar.population = self.param.birthRate * self.var.population
        self.dvar.debt = (
                self.aux_var.investmentChange * self.var.output - self.aux_var.profit
        )


if __name__ == "__main__":
    KeenModel().make_graph_pngs(is_open=True)
