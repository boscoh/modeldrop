from modeldrop.basemodel import BaseModel


class SpringModel(BaseModel):
    def setup(self):
        self.url = "https://github.com/boscoh/modeldrop/blob/master/spring.py"
        self.param.a = 1
        self.param.time = 5
        self.param.dt = 0.1
        self.param.initX = 1
        self.param.initV = 0
        self.setup_ui()

    def init_vars(self):
        self.var.x = self.param.initX
        self.var.v = self.param.initV

    def calc_dvars(self, t):
        self.dvar.x = self.var.v
        self.dvar.v = -self.param.a * self.var.x

    def setup_ui(self):
        self.plots = [
            {
                "markdown": """
             
                    ### Spring
                    The Second order equation spring equation
                    
                    ```math
                    \\frac{d^{2}}{dt^{2}}(x) = -a \\times x
                    ```
                    
                    Can be reexpressed as: 

                    ```math
                    \\frac{d}{dt}(v) = -a \\times x
                    ``` 

                    ```math
                    \\frac{d}{dt}(x) = v
                    ``` 
                    """,
                "title": "Spring",
                "vars": ["x", "v"],
            },
        ]
        self.extract_editable_params()


if __name__ == "__main__":
    import sys
    from modeldrop.app import show_models
    show_models([SpringModel()], sys.argv)
