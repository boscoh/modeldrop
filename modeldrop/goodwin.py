from .basemodel import BaseModel, make_cutoff_fn, make_sq_fn


class GoodwinBusinessCycleModel(BaseModel):
    def setup(self):
        self.url = (
            "https://github.com/boscoh/modeldrop/blob/master/modeldrop/goodwin.py"
        )

        self.param.accelerator = 3
        self.param.depreciation = 0.01
        self.param.productivityRate = 0.02
        self.param.birthRate = 0.01
        self.param.time = 100
        self.param.dt = 0.1

        wageSqFn = make_sq_fn(0.000_064_1, 1, 1, 0.040_064_1)
        self.fns.wageChange = make_cutoff_fn(wageSqFn, 0.9999)

        self.setup_ui()

    def init_vars(self):
        self.var.wage = 0.95
        self.var.productivity = 1
        self.var.population = 50
        laborFraction = 0.9
        self.var.labor = laborFraction * self.var.population

    def calc_aux_vars(self):
        self.aux_var.laborFraction = self.var.labor / self.var.population
        self.aux_var.output = self.var.labor * self.var.productivity
        self.aux_var.capital = self.aux_var.output * self.param.accelerator
        self.aux_var.wages = self.var.labor * self.var.wage

        self.aux_var.wageShare = self.aux_var.wages / self.aux_var.output
        self.aux_var.profitShare = 1 - self.aux_var.wageShare

    def calc_dvars(self, t):
        self.dvar.labor = self.var.labor * (
            (1 - self.var.wage / self.var.productivity) / self.param.accelerator
            - self.param.depreciation
            - self.param.productivityRate
        )
        self.dvar.wage = self.fns.wageChange(self.aux_var.laborFraction) * self.var.wage
        self.dvar.productivity = self.param.productivityRate * self.var.productivity
        self.dvar.population = self.param.birthRate * self.var.population

    def setup_ui(self):
        self.editable_params = [
            {"key": "time", "max": 500,},
            {"key": "birthRate", "max": 0.1,},
            {"key": "accelerator", "max": 5,},
            {"key": "depreciation", "max": 0.1,},
            {"key": "productivityRate", "max": 0.1,},
        ]

        self.var_plots = [
            {"key": "Share", "vars": ["wageShare", "profitShare"]},
            {"key": "Output", "vars": ["output", "wages"]},
            {"key": "People", "vars": ["population", "labor"]},
        ]
        self.fn_plots = [
            {"fn": "wageChange", "xlims": [0.8, 0.9999]},
        ]
