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
        self.fns.carryingCapacityFn = make_approach_fn(
            1, self.param.maxCarryCapacity, self.param.stateRevenueAtHalfCapacity
        )
        self.var.populationDensity = 0.2
        self.var.stateRevenue = 0

    def calc_aux_vars(self):
        self.aux_var.carryingCapacity = self.fns.carryingCapacityFn(
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
                "title": "People",
                "vars": ["populationDensity", "carryingCapacity"],
                "ymin": 0,
                "markdown": """
                    Demographic models examine the endogenous evolution of a state, based on different key factors.
                    This particular model is Peter Turchin's Demographic Fiscal State Model and provides a simple model of how a state can
                    improve the carrying capacity of its environment, which augments the population, but also precipitates a sudden decline.
                     
                    First, a state can organize a population to produce more food, which improves the growth rate of the population. This is
                    represented by the surplus:
                    
                    ```math
                    \\frac{d}{dt}(population) = populationGrowthRate \\times population \\times surplus 
                    ```
                    
                    The model makes simple assumptions about how the surplus relates to 
                    the carrying capacity and state revenue. In general the model shows how a state follows a simple growth and sudden decline simply due to internal dynamics
                """,
            },
            {
                "fn": "carryingCapacityFn",
                "xlims": [0, 100],
                "ymin": 0,
                "var": "stateRevenue",
                "markdown": """
                First we postulate a simple function of how revenue
                improves the carrying capacity. It is a simple monotoically
                increasing function that saturates to a given carrying
                capacity, modeling the fact that there is an upper limit 
                to how much the carrying capacity can be improved

                ```math
                carryingCapacityFunction = 1 + capacityDiff \\times \\left( \\frac{revenue}{ revenueAtHalfCapacity + revenue}  \\right)
                ```
                """,
            },
            {
                "title": "Surplus",
                "vars": ["surplus"],
                "markdown": """
                    We define an expression for the surplus such that a 
                    surplus will be produced if the population is
                    below the carrying capacity, but if the 
                    population rises above the carrying capacity, crops will 
                    fail and the surplus will go negative. 
                    
                    The surplus evolves over time as:
                    
                    ```math
                    surplus = maxSurplus \\times \\left(  1 - \\frac{ population } { carryingCapacityFunction } \\right) 
                    ```

                    """,
            },
            {
                "title": "State Revenue",
                "vars": ["stateRevenue"],
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
