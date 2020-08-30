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
        self.param.preyBirthRate = 0.2
        self.param.predationRate = 0.1
        self.param.digestionRate = 0.1
        self.param.predatorDeathRate = 0.2
        self.setup_plots()

    def init_vars(self):
        self.var.predator = self.param.initialPredator
        self.var.prey = self.param.initialPrey

    def calc_dvars(self, t):
        self.dvar.prey = (
            self.var.prey * self.param.preyBirthRate
            - self.param.predationRate * self.var.prey * self.var.predator
        )
        self.dvar.predator = (
            self.param.digestionRate * self.var.prey * self.var.predator
            - self.var.predator * self.param.predatorDeathRate
        )

    def setup_plots(self):
        self.plots = [
            {
                "markdown": """
                    The first successful population model (1925) was able to reproduce 
                    the oscillating populatons of a predator-prey ecology over time.
                    
                    The change in the prey population depends on the intrinsic prey birth rate and
                    the predation rate at which the prey is caught and eaten by the predator:
                     
                    ```math
                    \\frac{d}{dt}(prey) = preyBirthRate \\times prey  - predationRate \\times prey \\times predator
                    ``` 
                    
                    The predator's growth rate depends on the digestion rate - how well the predator
                    can digest the prey and grow a new predator. As well the predator will
                    die by natural attrition through the predator death rate:
                    
                    ```math
                    \\frac{d}{dt}(predator) = digestionRate \\times prey \\times predator - predatorDeathRate \\times predator
                    ```
                    """,
                "title": "ecology",
                "vars": ["predator", "prey"],
            },
        ]
        self.editable_params = [
            {"key": "time", "max": 300},
            {"key": "initialPrey", "max": 20,},
            {"key": "initialPredator", "max": 20,},
            {"key": "preyBirthRate", "max": 2,},
            {"key": "predationRate", "max": 2,},
            {"key": "predatorDeathRate", "max": 2,},
            {"key": "digestionRate", "max": 2,},
        ]
        self.extract_editable_params()


if __name__ == "__main__":
    show_models([LoktaVolterraEcologyModel()], sys.argv)
