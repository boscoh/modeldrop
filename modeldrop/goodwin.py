from .basemodel import BaseModel, make_cutoff_fn, make_sq_fn


class GoodwinBusinessCycleModel(BaseModel):
    def setup(self):
        self.url = (
            "https://github.com/boscoh/modeldrop/blob/master/modeldrop/goodwin.py"
        )

        self.param.accelerator = 3
        self.param.depreciation = 0.01
        self.param.productivityRate = 0.02
        self.param.birthRate = 0.01
        self.param.time = 100
        self.param.dt = 0.1

        wageSqFn = make_sq_fn(0.000_064_1, 1, 1, 0.040_064_1)
        self.fn.wageChangeFn = make_cutoff_fn(wageSqFn, 0.9999)

        self.setup_ui()

    def init_vars(self):
        self.var.wage = 0.95
        self.var.productivity = 1
        self.var.population = 50
        laborFraction = 0.9
        self.var.labor = laborFraction * self.var.population

    def calc_aux_vars(self):
        self.aux_var.laborFraction = self.var.labor / self.var.population
        self.aux_var.output = self.var.labor * self.var.productivity
        self.aux_var.capital = self.aux_var.output * self.param.accelerator
        self.aux_var.wages = self.var.labor * self.var.wage

        self.aux_var.wageShare = self.aux_var.wages / self.aux_var.output
        self.aux_var.profitShare = 1 - self.aux_var.wageShare

    def calc_dvars(self, t):
        self.dvar.labor = self.var.labor * (
            (1 - self.var.wage / self.var.productivity) / self.param.accelerator
            - self.param.depreciation
            - self.param.productivityRate
        )
        self.dvar.wage = (
            self.fn.wageChangeFn(self.aux_var.laborFraction) * self.var.wage
        )
        self.dvar.productivity = self.param.productivityRate * self.var.productivity
        self.dvar.population = self.param.birthRate * self.var.population

    def setup_ui(self):
        self.editable_params = [
            {"key": "time", "max": 500,},
            {"key": "birthRate", "max": 0.1,},
            {"key": "accelerator", "max": 5,},
            {"key": "depreciation", "max": 0.1,},
            {"key": "productivityRate", "max": 0.1,},
        ]

        self.plots = [
            {
                "markdown": """
                    The Goodwin Business Cycle is one of the earliest descriptions
                    of a fully dynamical model of the economy, which was first
                    [implemented numerically][1] by Steve Keen.
                      
                    [1]:(https://keenomics.s3.amazonaws.com/debtdeflation_media/papers/PaperPrePublicationProof.pdf)
                    
                    The model assumes two actors in the economy:
                    
                    1. workers get paid for labor
                    2. capitalists employ workers with capital
                    
                    Skipping ahead, the model generates the evolution of the relative incomes
                    of labor (wages), capital (profit), based purely
                    on self-interacting dynamics.
                    """,
                "title": "Share",
                "vars": ["wageShare", "profitShare"],
            },
            {
                "markdown": """
                    The relationship between labor and capital are determined
                    by these equations, which restate standard macro relationships 
                    
                    ```math
                    output = labor \\times productivity
                    ```
                    ```math
                    capital = output \\times outputAccelerator
                    ```
                    ```math
                    \\frac{d}{dt}(capital) = investment - depreciationRate \\times capital
                    ```
                    
                    ```math
                    wages = labor \\times wage
                    ```
                    
                    Productivity is assumed to increase steadily due to innovations in
                    technology:
                    
                    ```math
                    \\frac{d}{dt}(productivity) = productivity \\times productivityGrowthRate
                    ```
                    
                    Capitalists are assume to reinvest all their profits
                    back into the businesses.
                    
                    Labor depends on how much capital is in the system. 
                    Changes in capital depends on profitability, which in turn 
                    depends on wages, leading to the cycle.
                    """,
                "title": "Output",
                "vars": ["output", "wages", "capital"],
            },
            {
                "markdown": """
                    The workers are modeled as a typical population, which grows exponentially:
                    
                    ```math
                    \\frac{d}{dt}(population) = population \\times populationGrowthRate
                    ```
                    """,
                "title": "People",
                "vars": ["population", "labor"],
            },
            {
                "markdown": """
                    Finally, workers can demand wage increases as it gets to
                    full employment which
                    will reduce the profit of the capitalist. This
                    is modeled by the Keen wage change function that responds to
                    the labor fraction:
                    
                    ```math
                    \\frac{d}{dt}(wage) = wage \\times wageChangeFn \\left[ laborFraction \\right]
                    ```
                    """,
                "fn": "wageChangeFn",
                "xlims": [0.8, 0.995],
                "var": "laborFraction",
            },
        ]
