import math

from modeldrop.basemodel import BaseModel


class ElasticSpringModel(BaseModel):
    def setup(self):
        self.url = "https://github.com/boscoh/modeldrop/blob/master/modeldrop/spring.py"
        self.param.period = 1
        self.param.time = 5
        self.param.dt = 0.01
        self.param.initX = 1
        self.param.initV = 0
        self.setup_ui()

    def init_vars(self):
        self.var.x = self.param.initX
        self.var.v = self.param.initV

    def calc_dvars(self, t):
        self.dvar.x = self.var.v
        self.dvar.v = (
            -4 * math.pi * math.pi / self.param.period / self.param.period * self.var.x
        )

    def setup_ui(self):
        self.plots = [
            {
                "markdown": """
             
                    The spring is the cleanest dynamical model
                    of a oscillating periodic cycle.
                    It is represented by this very simple
                    second order differential equation:
                    
                    ```math
                    \\frac{d^{2}}{dt^{2}}(x) = - \\frac {4 \\pi^2}{period^2}   \\times x
                    ```
                    
                    A simple transformation, gives the equivalent 
                    motion in terms of two first order
                    equations of x and v, which gives us the essential
                    predator-prey relationship without the intrinsic 
                    growth factors:  

                    ```math
                    \\frac{d}{dt}(v) = - \\frac {4 \\pi^2}{period^2} \\times x
                    ``` 

                    ```math
                    \\frac{d}{dt}(x) = v
                    ``` 
                    """,
                "title": "Spring",
                "vars": ["x", "v"],
            }
        ]
        self.editable_params = [
            {"key": "initX", "min": -5, "max": 5},
            {"key": "initV", "min": -5, "max": 5},
        ]
        self.extract_editable_params()


if __name__ == "__main__":
    import sys

    from modeldrop.app import show_models

    show_models([ElasticSpringModel()], sys.argv)
