from .basemodel import BaseModel, make_approach_fn


class TurchinDemographicStateModel(BaseModel):
    def setup(self):
        self.url = (
            "https://github.com/boscoh/modeldrop/blob/master/modeldrop/turchin.py"
        )

        self.param.time = 500
        self.param.maxSurplus = 1
        self.param.taxOnSurplus = 1
        self.param.growth = 0.02
        self.param.expenditurePerCapita = 0.25
        self.param.stateRevenueAtHalfCapacity = 10
        self.param.maxCarryCapacity = 3

        self.setup_ui()

    def init_vars(self):
        self.fn.carryingCapacityFn = make_approach_fn(
            1, self.param.maxCarryCapacity, self.param.stateRevenueAtHalfCapacity
        )
        self.var.populationDensity = 0.2
        self.var.stateRevenue = 0

    def calc_aux_vars(self):
        self.aux_var.carryingCapacity = self.fn.carryingCapacityFn(
            self.var.stateRevenue
        )
        self.aux_var.surplus = self.param.maxSurplus * (
            1 - self.var.populationDensity / self.aux_var.carryingCapacity
        )

    def calc_dvars(self, t):
        self.dvar.populationDensity = (
            self.param.growth * self.var.populationDensity * self.aux_var.surplus
        )
        self.dvar.stateRevenue = (
            self.param.taxOnSurplus * self.var.populationDensity * self.aux_var.surplus
            - self.param.expenditurePerCapita * self.var.populationDensity
        )
        if self.dvar.stateRevenue + self.var.stateRevenue < 0:
            self.dvar.stateRevenue = -self.var.stateRevenue

    def setup_ui(self):
        self.plots = [
            {
                "markdown": """
                    The Demographic Fiscal State model from Peter Turchin 
                    examines the effects of a state that taxes a population 
                    (fiscal) on the growth of a population (demographic). 
                     
                    First, we have a population that grows depending
                    on the amount of surplus, or food that is produced:                    from paying taxes to the state:
                    
                    ```math
                    \\frac{d}{dt}(population) = 
                        populationGrowthRate 
                        \\times population 
                        \\times surplus 
                    ```
                    
                    The population will rise and fall depending on the
                    surplus produced, which will depend on  
                    improvements to the carrying capacity:
                    """,
                "title": "People",
                "vars": ["populationDensity", "carryingCapacity"],
                "ymin": 0,
            },
            {
                "markdown": """
                    First we postulate a simple function of how state revenue
                    improves the carrying capacity. It is a simple monotonically
                    increasing function that saturates to a given carrying
                    capacity, beyond which the carrying capacity cannot be improved
    
                    ```math
                    carryingCapacityFunction = 1 + capacityDiff \\times \\left( \\frac{revenue}{ revenueAtHalfCapacity + revenue}  \\right)
                    ```
                """,
                "fn": "carryingCapacityFn",
                "xlims": [0, 100],
                "ymin": 0,
                "var": "stateRevenue",
            },
            {
                "markdown": """
                    We define an expression for the surplus that will be
                    positive if the population is
                    below the carrying capacity. But if the 
                    population rises above the carrying capacity, crops will 
                    fail and the surplus will go negative:                    
                    
                    ```math
                    surplus = maxSurplus 
                        \\times \\left(  
                            1 - 
                            \\frac{ population } { carryingCapacity } 
                        \\right) 
                    ```

                    This results in the changes of the surplus over time
                    due to the intervention of the state in improving
                    the carrying capacity:
                    """,
                "title": "Surplus",
                "vars": ["surplus"],
            },
            {
                "markdown": """
                    For the state to improve the carrying capacity, it must have
                    sufficient revenue collected from the population. This revenue
                    is defined as a fraction of the surplus produced by the population. As
                    well, the state is assume to spend some of the revenue on 
                    the population, and this is the expenditure.
                    
                    ```math
                    \\frac{d}{dt}(revenue) = tax \\times population \\times surplus - expenditurePerCapita * population
                    ```
                    """,
                "title": "State Revenue",
                "vars": ["stateRevenue"],
            },
        ]

        self.editable_params = [
            {"key": "time", "max": 1000},
            {"key": "maxSurplus", "max": 2,},
            {"key": "taxOnSurplus", "max": 2,},
            {"key": "growth", "max": 0.1,},
            {"key": "stateRevenueAtHalfCapacity", "max": 50,},
            {"key": "maxCarryCapacity", "max": 10,},
        ]
