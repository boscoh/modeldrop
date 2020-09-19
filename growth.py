from modeldrop.basemodel import BaseModel, make_lin_fn


class FundamentalPopulationModel(BaseModel):
    def setup(self):
        self.url = "https://github.com/boscoh/modeldrop/blob/master/growth.py"

        self.param.growth_rate = 0.035
        self.param.carrying_capacity = 1e3
        self.param.time = 400
        self.setup_ui()

    def init_vars(self):
        self.var.population = 10
        self.var.population2 = 10
        self.fn.testFn = make_lin_fn(1, 2)

    def calc_dvars(self, t):
        self.dvar.population = self.param.growth_rate * self.var.population
        self.dvar.population2 = (
            self.param.growth_rate
            * self.var.population2
            * (1 - self.var.population2 / self.param.carrying_capacity)
        )

    def setup_ui(self):
        self.plots = [
            {
                "markdown": """
             
                    ### Exponential Growth       
                    All dynamic population models have an exponential
                    growth equation at the heart of the system. This 
                    population will grow exponentially without limits.
                    
                    ```math
                    \\frac{d}{dt}(population) = growthRate \\times population
                    ``` 

                    """,
                "title": "Exponential Growth",
                "vars": ["population"],
            },
            {
                "markdown": """
                     
                     ### Resource constrained
                     
                     Each individual model will then add some kind of constraint.
                     The simplest constraint is a carrying capacity
                     constraint, where the growth rate is reduced 
                     by crowding effects as the population approaches
                     a carrying capacity. This equation is known as the logistic
                     equation:
                     
                     ```math
                     \\frac{d}{dt}(population) = 
                        growthRate 
                            \\times 
                                \\left[
                                    1 - \\frac{population}{carryingCapacity} 
                                \\right] 
                            \\times population
                     ``` 

                     """,
                "title": "Resource Constrained",
                "vars": ["population2"],
            },
            {"fn": "testFn", "xlims": [-5, 5]},
        ]
        self.extract_editable_params()


if __name__ == "__main__":
    model = FundamentalPopulationModel()

    from modeldrop.modelgraph import make_graphs_from_model

    make_graphs_from_model(model, "growth_pngs", transparent=True)

    # from modeldrop.app import show_models
    # show_models([FundamentalPopulationModel()], sys.argv)
