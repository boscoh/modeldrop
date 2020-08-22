import sys

from .app import show_models
from .basemodel import BaseModel


class LoktaVolterraEcologyModel(BaseModel):
    def setup(self):
        self.url = (
            "https://github.com/boscoh/modeldrop/blob/master/modeldrop/ecology.py"
        )
        self.param.time = 200
        self.param.dt = 0.2
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
        self.plots = [
            {
                "title": "ecology",
                "markdown": """
                    The first complex population model (1925), uses these sets of coupled equation to
                    reproduce the periodic rise and fall of populations in the wild. These
                    equations are also used in studying auto-catalytic chemical reactions.
                    
                    The Lokta-Volterra equations follow two populations, a prey population with an endogenous
                    growth function where the prey presumably takes in nutrients from an abundant
                    environment, but will also die from the predator attack it, as represented
                    by the predation rate.
                     
                    ```math
                    \\frac{d}{dt}(prey) = preyGrowthRate \\times prey  - predationRate \\times prey \\times predator
                    ``` 
                    
                    In contrast, the predator relies totally on the prey as its food source, which
                     is represented by the digestion rate, which determines how many prey a predator
                     has to eat before it can produce a new predator. Finally, we need to include
                     an explicit death rate for the predator:
                    
                    ```math
                    \\frac{d}{dt}(predator) = digestionRate \\times prey \\times predator - predatorDeathRate \\times predator
                    ```
                    """,
                "vars": ["predator", "prey"],
            },
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


if __name__ == "__main__":
    show_models([LoktaVolterraEcologyModel()], sys.argv)
