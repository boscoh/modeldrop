from pprint import pprint

from .basemodel import AttrDict, BaseModel


class TurchinFathersAndSonsModel(BaseModel):
    def setup(self):
        self.url = (
            "https://github.com/boscoh/modeldrop/blob/master/modeldrop/fathers.py"
        )

        self.integrate_method = "euler_integrate"
        self.param.time = 100
        self.param.dt = 0.5

        self.param.radicalisation = 0.3
        self.param.disenchantment = 0.5
        self.param.aversion = 1
        self.param.dischenchantmentDelay = 10
        self.param.nAgeGroup = 25

        self.groups = ["naive", "moderate", "radical"]

        self.init_vars()

        self.setup_ui()

    def init_vars(self):
        self.param.nAgeGroup = int(self.param.nAgeGroup)

        self.pops = AttrDict()
        for group in self.groups:
            self.pops[group] = [f"{group}_{age}" for age in range(self.param.nAgeGroup)]

        for age in range(self.param.nAgeGroup):
            for group in self.groups:
                key = f"{group}_{age}"
                if group == "naive":
                    self.var[key] = 0.5 / self.param.nAgeGroup
                elif group == "radical":
                    self.var[key] = 0.1 / self.param.nAgeGroup
                else:
                    self.var[key] = 0.4 / self.param.nAgeGroup

    def calc_aux_vars(self):
        for group in self.groups:
            key = f"{group}_total"
            self.aux_var[key] = 0
            for n in self.pops[group]:
                v = self.var[n]
                if v is not None:
                    self.aux_var[key] += v

        i = int(self.param.dischenchantmentDelay / self.param.dt)
        self.aux_var.radical_total_delayed = 0
        for key in self.pops.radical:
            if key not in self.solution:
                continue
            if len(self.solution[key]) > i:
                self.aux_var.radical_total_delayed += self.solution[key][-i]

        self.aux_var.rho = self.param.disenchantment * self.aux_var.radical_total_delayed

        self.aux_var.sigma = self.aux_var.radical_total * (
            self.param.radicalisation - self.param.aversion * self.aux_var.moderate_total
        )

    def calc_dvars(self, t):
        self.dvar = {}

        for k in self.keys:
            self.dvar[k] = -self.var[k]

        self.dvar[f"naive_0"] += 1.0 / self.param.nAgeGroup

        for j in range(1, self.param.nAgeGroup):
            i = j - 1
            self.dvar[f"naive_{j}"] += self.var[f"naive_{i}"] * (1 - self.aux_var.sigma)
            self.dvar[f"radical_{j}"] += self.var[f"radical_{i}"] * (
                1 - self.aux_var.rho
            )
            self.dvar[f"radical_{j}"] += self.var[f"naive_{i}"] * self.aux_var.sigma
            self.dvar[f"moderate_{j}"] += self.var[f"moderate_{i}"]
            self.dvar[f"moderate_{j}"] += self.var[f"radical_{i}"] * self.aux_var.rho

    def setup_ui(self):
        self.plots = [
            {
                "title": "All",
                "vars": ["naive_total", "radical_total", "moderate_total"],
            },
            {"title": "Naive", "vars": self.pops.naive,},
            {"title": "Radical", "vars": self.pops.radical,},
            {"title": "Moderate", "vars": self.pops.moderate,},
        ]
        self.editable_params = [
            {"key": "time", "max": 500,},
            {"key": "nAgeGroup", "max": 50,},
        ]
        self.extract_editable_params()
