import sys

from .app import show_models
from .basemodel import BaseModel


class EpidemiologySirModel(BaseModel):
    def setup(self):
        self.url = "https://github.com/boscoh/modeldrop/blob/master/modeldrop/epi.py"

        self.param.initialPopulation = 50000
        self.param.initialPrevalence = 3000
        self.param.recoverRate = 0.1
        self.param.reproductionNumber = 1.5
        self.param.infectiousPeriod = 10

        self.setup_flows()

        self.setup_ui()

    def init_vars(self):
        self.param.recoverRate = 1 / self.param.infectiousPeriod
        self.param.contactRate = self.param.reproductionNumber * self.param.recoverRate

        self.var.infectious = self.param.initialPrevalence
        self.var.susceptible = (
            self.param.initialPopulation - self.param.initialPrevalence
        )
        self.var.recovered = 0

    def calc_aux_vars(self):
        self.aux_var.population = sum(self.var.values())
        self.aux_var.rateForce = (
            self.param.contactRate / self.aux_var.population
        ) * self.var.infectious
        self.aux_var.rn = (
            self.var.susceptible / self.aux_var.population
        ) * self.param.reproductionNumber

    def setup_flows(self):
        self.aux_var_flows = [["susceptible", "infectious", "rateForce"]]
        self.param_flows = [["infectious", "recovered", "recoverRate"]]

    def calc_dvars(self, t):
        for key in self.var.keys():
            self.dvar[key] = 0
        self.add_to_dvars_from_flows()

    def setup_ui(self):
        self.var_plots = [
            {"key": "Populations", "vars": ["susceptible", "infectious", "recovered"]},
            {"key": "Effective Reproduction Number", "vars": ["rn"]},
        ]
        self.editable_params = [
            {"key": "time", "max": 1000,},
            {"key": "infectiousPeriod", "max": 100,},
            {"key": "reproductionNumber", "max": 25},
            {"key": "initialPrevalence", "max": 100000},
            {"key": "initialPopulation", "max": 100000},
        ]


if __name__ == "__main__":
    show_models([EpidemiologySirModel()], sys.argv)
