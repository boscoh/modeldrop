from modeldrop.basemodel import BaseModel
import math

class SpringModel(BaseModel):
    def setup(self):
        self.url = "https://github.com/boscoh/modeldrop/blob/master/spring.py"
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
        self.dvar.v = -4 * math.pi * math.pi / self.param.period / self.param.period * self.var.x

    def setup_ui(self):
        self.plots = [
            {
                "markdown": """
             
                    ### Spring
                    The Second order equation spring equation
                    
                    ```math
                    \\frac{d^{2}}{dt^{2}}(x) = - \\frac {4 \\pi^2}{period^2}   \\times x
                    ```
                    
                    Can be expressed as: 

                    ```math
                    \\frac{d}{dt}(v) = - \\frac {4 \\pi^2}{period^2} \\times x
                    ``` 

                    ```math
                    \\frac{d}{dt}(x) = v
                    ``` 
                    """,
                "title": "Spring",
                "vars": ["x", "v"],
            },
        ]
        self.editable_params = [
            {"key": "initX", "min": -5, "max": 5},
            {"key": "initV", "min": -5, "max": 5}
        ]
        self.extract_editable_params()



if __name__ == "__main__":
    import sys

    from modeldrop.app import show_models

    show_models([SpringModel()], sys.argv)
