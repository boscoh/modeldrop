from .basemodel import BaseModel


class StandardThreePartEpidemiologyModel(BaseModel):
    def setup(self):
        self.url = "https://github.com/boscoh/modeldrop/blob/master/modeldrop/epi.py"

        self.param.time = 300
        self.param.initialPopulation = 50000
        self.param.initialPrevalence = 3000
        self.param.recoverRate = 0.1
        self.param.reproductionNumber = 1.5
        self.param.infectiousPeriod = 10

        self.setup_flows()

        self.setup_ui()

    def init_vars(self):
        self.param.recoverRate = 1 / self.param.infectiousPeriod
        self.param.contactRate = self.param.reproductionNumber * self.param.recoverRate

        self.var.infectious = self.param.initialPrevalence
        self.var.susceptible = (
            self.param.initialPopulation - self.param.initialPrevalence
        )
        self.var.recovered = 0

    def calc_aux_vars(self):
        self.aux_var.population = sum(self.var.values())
        self.aux_var.rateForce = (
            self.param.contactRate / self.aux_var.population
        ) * self.var.infectious
        self.aux_var.rn = (
            self.var.susceptible / self.aux_var.population
        ) * self.param.reproductionNumber

    def setup_flows(self):
        self.aux_var_flows = [["susceptible", "infectious", "rateForce"]]
        self.param_flows = [["infectious", "recovered", "recoverRate"]]

    def calc_dvars(self, t):
        for key in self.var.keys():
            self.dvar[key] = 0
        self.add_to_dvars_from_flows()

    def setup_ui(self):
        self.plots = [
            {
                "title": "Populations",
                "vars": ["susceptible", "infectious", "recovered"],
                "markdown": """
                    The SIR model is the most basic epidemiological model of 
                    a transmissible disease. It consists of 3 populations (called
                    compartments): 
                    
                    - Susceptible people don't have the disease,
                    - Infectious people have caught the disease and can transmit it,  
                    - Recovered people have become immune to the disease      
                    
                    The transmissability of disease is through the force of infection:
                    
                    ```math
                    forceOfInfection = \\frac{infectious}{population} \\times \\frac{reproductionNumber}{infectiousPeriod}
                    ```
                    where the reproduction number is the total number of people an infectious person would 
                    infect during the infectious period.

                    Infectious people will recover at the rate:
                    
                    ```math
                    recoverRate = \\frac{1}{infectiousPerod}
                    ```
                    
                    This type of model is often called a compartmental model
                    as the change equations are balanced growth/decline equations where
                    the decline in one compartment (population) results in growth in another compartment:
                    
                    ```math
                    \\frac{d}{dt}susceptible = - susceptible \\times forceOfInfection
                    ```
                    ```math
                    \\frac{d}{dt}infectious = - infectious \\times recoverRate + susceptible \\times forceOfInfection 
                    ```
                    ```math
                    \\frac{d}{dt}recovered = infectious \\times recoverRate
                    ```
                    """,
            },
            {"title": "Effective Reproduction Number", "vars": ["rn"]},
        ]
        self.editable_params = [
            {"key": "time", "max": 1000,},
            {"key": "infectiousPeriod", "max": 100,},
            {"key": "reproductionNumber", "max": 15},
            {"key": "initialPrevalence", "max": 100000},
            {"key": "initialPopulation", "max": 100000},
        ]


