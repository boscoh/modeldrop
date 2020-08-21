from modeldrop.basemodel import BaseModel


class PopModel(BaseModel):
    def setup(self):
        self.param.population_exponent = 0.035
        self.param.time = 200
        self.init_var.population = 10
        self.var_plots = [
            {"key": "people", "vars": ["population"]},
        ]
        self.editable_params = [
            {"key": "population_exponent", "max": 0.1,},
        ]

    def calc_dvars(self, t):
        self.dvar.population = self.param.population_exponent * self.var.population


if __name__ == "__main__":
    import os

    from modeldrop import graphing

    for graph in PopModel().make_graphs():
        graphing.write_graph(graph)

    os.system("open plot-*.png")
