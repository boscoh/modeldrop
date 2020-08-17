import sys

from modeldrop.basemodel import BaseModel
from modeldrop.app import DashModelAdaptor, open_url_in_background


class Ecology(BaseModel):
    def setup(self):
        self.param.time = 200
        self.param.initialPrey = 10
        self.param.initialPredator = 5
        self.param.preyGrowthRate = 0.2
        self.param.predationRate = 0.1
        self.param.digestionRate = 0.1
        self.param.predatorDeathRate = 0.2
        self.setup_plots()

    def init_vars(self):
        self.var.predator = self.param.initialPredator
        self.var.prey = self.param.initialPrey

    def calc_dvars(self, t):
        self.dvar.prey = (
            self.var.prey * self.param.preyGrowthRate
            - self.param.predationRate * self.var.prey * self.var.predator
        )
        self.dvar.predator = (
            self.param.digestionRate * self.var.prey * self.var.predator
            - self.var.predator * self.param.predatorDeathRate
        )

    def setup_plots(self):
        self.model_plots = [
            {"key": "ecology", "vars": ["predator", "prey"], "ymin": -100, "ymax": 100},
        ]
        self.editable_params = [
            {"key": "time", "max": 300},
            {"key": "initialPrey", "max": 20,},
            {"key": "initialPredator", "max": 20,},
            {"key": "preyGrowthRate", "max": 2,},
            {"key": "predationRate", "max": 2,},
            {"key": "predatorDeathRate", "max": 2,},
            {"key": "digestionRate", "max": 2,},
        ]
        self.extract_editable_params()


def show_models(models, argv):
    port = "8050"
    if "-o" in argv:
        open_url_in_background(f"http://127.0.0.1:{port}/")
    is_debug = "-d" in argv
    DashModelAdaptor(models).run_server(port=port, is_debug=is_debug)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)

    model = Ecology()

    # for graph in model.make_graphs():
    #     graphing.write_graph(graph)
    # os.system("open plot-*.png")

    show_models([model], sys.argv)