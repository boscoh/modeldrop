import sys

from modeldrop.basemodel import BaseModel
from modeldrop.app import DashModelAdaptor, open_url_in_background


class EpiModel(BaseModel):
    def setup(self):
        self.param.initialPopulation = 50000
        self.param.initialPrevalence = 3000
        self.param.recoverRate = 0.1
        self.param.reproductionNumber = 1.5
        self.param.infectiousPeriod = 10
        self.setup_plots()

    def init_vars(self):
        self.param.recoverRate = 1 / self.param.infectiousPeriod
        self.param.contactRate = (
            self.param.reproductionNumber * self.param.recoverRate)

        self.var.infectious = self.param.initialPrevalence
        self.var.susceptible = (
            self.param.initialPopulation - self.param.initialPrevalence)
        self.var.recovered = 0
        
    def calc_aux_vars(self):
        self.aux_var.population = sum(self.var.values())
        self.aux_var.rateForce = (
            (self.param.contactRate / self.aux_var.population) *
            self.var.infectious)
        self.aux_var.rn = (
            (self.var.susceptible / self.aux_var.population) *
            self.param.reproductionNumber)

    def calc_dvars(self, t):
        self.dvar.susceptible = (
            - self.var.susceptible * self.aux_var.rateForce
        )
        self.dvar.infectious = (
            - self.var.infectious * self.param.recoverRate
            + self.var.susceptible * self.aux_var.rateForce
        )
        self.dvar.recovered = (
            + self.var.infectious * self.param.recoverRate
        )

    def setup_plots(self):
        self.model_plots = [
            {"key": "compartments", "vars": ["susceptible", "infectious", "recovered"]}
        ]
        self.editable_params = [
            {
                "key": 'infectiousPeriod',
                "max": 100,
                "label": 'Infectious Period (days)',
            },
            {
                "key": 'initialPrevalence',
                "max": 100000,
                "label": 'Prevalence',
            },
            {
                "key": 'initialPopulation',
                "max": 100000,
                "label": 'Initial Population',
            },
        ]


def show_models(models, argv):
    port = "8050"
    if "-o" in argv:
        open_url_in_background(f"http://127.0.0.1:{port}/")
    is_debug = "-d" in argv
    DashModelAdaptor(models).run_server(port=port, is_debug=is_debug)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)

    model = EpiModel()

    # for graph in model.make_graphs():
    #     graphing.write_graph(graph)
    # os.system("open plot-*.png")

    show_models([model], sys.argv)

