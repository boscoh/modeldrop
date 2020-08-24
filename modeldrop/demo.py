import sys

from modeldrop.app import show_models
from modeldrop.basemodel import BaseModel, make_approach_fn


class TurchinEliteDemographicModel(BaseModel):
    def setup(self):
        self.url = "https://github.com/boscoh/modeldrop/blob/master/modeldrop/demo.py"

        self.param.time = 400

        self.param.maxProductionRate = 2
        self.param.producerBirth = 0.02
        self.param.producerDeath = 0.02
        self.param.initProductionDecline = 0.5
        self.param.eliteBirth = 0.05
        self.param.eliteAtHalfExtraction = 0.3
        self.param.maxEliteDeath = 0.12
        self.param.stateAtHalfPeace = 0.3
        self.param.stateAtHalfCarry = 0.07
        self.param.finalStateProductionDecline = 0.2
        self.param.stateTaxRate = 1
        self.param.stateEmploymentRate = 0.01

        self.param.initProducer = 0.5
        self.param.initElite = 0.02
        self.param.initState = 0.0

        self.setup_plots()

    def init_vars(self):
        self.var.producer = self.param.initProducer
        self.var.elite = self.param.initElite
        self.var.state = self.param.initState

        self.fns.productionDeclineFn = make_approach_fn(
            self.param.initProductionDecline,
            self.param.finalStateProductionDecline,
            self.param.stateAtHalfCarry,
        )

    def calc_aux_vars(self):
        self.aux_var.productionDecline = self.fns.productionDeclineFn(self.var.state)

        self.aux_var.totalProduct = (
            self.var.producer
            * self.param.maxProductionRate
            * (1 - self.aux_var.productionDecline * self.var.producer)
        )

        self.aux_var.eliteFraction = self.var.elite / (
            self.param.eliteAtHalfExtraction + self.var.elite
        )
        self.aux_var.eliteShare = self.aux_var.totalProduct * self.aux_var.eliteFraction
        self.aux_var.producerShare = self.aux_var.totalProduct - self.aux_var.eliteShare

        self.aux_var.carry = (
            (
                self.param.maxProductionRate * self.param.producerBirth
                - self.param.producerDeath
            )
            / self.aux_var.productionDecline
            / self.param.maxProductionRate
            / self.param.producerBirth
        )

        self.aux_var.deathModifier = 1 - self.var.state / (
            self.param.stateAtHalfPeace + self.var.state
        )
        self.aux_var.eliteDeathRate = (
            self.param.maxEliteDeath * self.aux_var.deathModifier
        )
        self.aux_var.eliteDeath = self.var.elite * self.aux_var.eliteDeathRate

        self.aux_var.elitePerCapita = self.aux_var.eliteShare / self.var.elite
        self.aux_var.producerPerCapita = self.aux_var.producerShare / self.var.producer

    def calc_dvars(self, t):
        self.dvar.producer = (
            self.param.producerBirth * self.aux_var.producerShare
            - self.param.producerDeath * self.var.producer
        )

        self.dvar.elite = (
            self.param.eliteBirth * self.aux_var.eliteShare - self.aux_var.eliteDeath
        )

        self.dvar.state = 0
        if self.dvar.elite > 0:
            self.dvar.state += self.param.stateTaxRate * self.dvar.elite
        self.dvar.state -= self.param.stateEmploymentRate * self.var.elite
        if self.dvar.state + self.var.state < 0:
            self.dvar.state = -self.var.state

    def setup_plots(self):
        self.plots = [
            {
                "title": "people",
                "vars": ["producer", "elite", "state"],
                "ymax_cutoff": 100,
            },
            {
                "title": "Production Rate",
                "vars": ["producerShare", "eliteShare", "totalProduct"],
                "ymin": 0,
            },
            {
                "title": "Earnings Per Capita",
                "vars": ["producerPerCapita", "elitePerCapita"],
                "ymin": 0,
            },
            {
                "title": "State Action on Producer Capacity",
                "vars": ["producer", "carry"],
                "ymin": 0,
            },
            {
                "title": "State Action on Elites",
                "vars": ["eliteDeathRate", "eliteDeath"],
                "ymin": 0,
            },
            {"fn": "productionDeclineFn", "xlims": [0, 1], "ymin": 0, "var": "state"},
        ]
        self.editable_params = [
            {"key": "time", "max": 2000,},
        ]
        self.extract_editable_params()


if __name__ == "__main__":
    model = TurchinEliteDemographicModel()
    show_models([model], sys.argv)
