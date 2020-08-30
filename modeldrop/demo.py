import sys

from modeldrop.app import show_models
from modeldrop.basemodel import BaseModel, make_approach_fn


class TurchinEliteDemographicModel(BaseModel):
    def setup(self):
        self.url = "https://github.com/boscoh/modeldrop/blob/master/modeldrop/demo.py"

        self.param.time = 400

        self.param.maxProductionRate = 2
        self.param.producerBirth = 0.02
        self.param.producerDeath = 0.02
        self.param.initProdDecline = 0.5
        self.param.eliteBirth = 0.05
        self.param.eliteAtHalfExtraction = 0.3
        self.param.maxEliteDeath = 0.12
        self.param.stateAtHalfPeace = 0.3
        self.param.stateAtHalfCarry = 0.07
        self.param.finalStateprodDecline = 0.2
        self.param.stateTaxRate = 1
        self.param.stateEmploymentRate = 0.01

        self.param.initProducer = 0.5
        self.param.initElite = 0.02
        self.param.initState = 0.0

        self.setup_plots()

    def init_vars(self):
        self.var.producer = self.param.initProducer
        self.var.elite = self.param.initElite
        self.var.state = self.param.initState

        self.fns.prodDeclineFn = make_approach_fn(
            self.param.initProdDecline,
            self.param.finalStateprodDecline,
            self.param.stateAtHalfCarry,
        )

    def calc_aux_vars(self):
        self.aux_var.prodDecline = self.fns.prodDeclineFn(self.var.state)

        self.aux_var.totalProduct = (
            self.var.producer
            * self.param.maxProductionRate
            * (1 - self.aux_var.prodDecline * self.var.producer)
        )

        self.aux_var.eliteFraction = self.var.elite / (
            self.param.eliteAtHalfExtraction + self.var.elite
        )
        self.aux_var.eliteShare = self.aux_var.totalProduct * self.aux_var.eliteFraction
        self.aux_var.producerShare = self.aux_var.totalProduct - self.aux_var.eliteShare

        self.aux_var.carry = (
            (
                self.param.maxProductionRate * self.param.producerBirth
                - self.param.producerDeath
            )
            / self.aux_var.prodDecline
            / self.param.maxProductionRate
            / self.param.producerBirth
        )

        self.aux_var.stateModifiedFraction = 1 - self.var.state / (
            self.param.stateAtHalfPeace + self.var.state
        )
        self.aux_var.eliteDeathRate = (
            self.param.maxEliteDeath * self.aux_var.stateModifiedFraction
        )
        self.aux_var.eliteDeath = self.var.elite * self.aux_var.eliteDeathRate

        self.aux_var.productPerElite = self.aux_var.eliteShare / self.var.elite
        self.aux_var.productPerProducer = self.aux_var.producerShare / self.var.producer

    def calc_dvars(self, t):
        self.dvar.producer = (
            self.param.producerBirth * self.aux_var.producerShare
            - self.param.producerDeath * self.var.producer
        )

        self.dvar.elite = (
            self.param.eliteBirth * self.aux_var.eliteShare - self.aux_var.eliteDeath
        )

        self.dvar.state = 0
        if self.dvar.elite > 0:
            self.dvar.state += self.param.stateTaxRate * self.dvar.elite
        self.dvar.state -= self.param.stateEmploymentRate * self.var.elite
        if self.dvar.state + self.var.state < 0:
            self.dvar.state = -self.var.state

    def setup_plots(self):
        self.plots = [
            {
                "markdown": """

                    The Elite Demographic State model from Peter Turchin provides
                    a concrete model for the rise and fall of states. The state
                    has three major components:
                    
                    1. Producers make the food, and increase if there is enough food
                    2. Elites extract food from the producers but are prone to infighting
                    3. The State improves the productivity of producers and pacifies elite infighting 
                     
                    The producer population will rise and fall depending on the
                    surplus produced, which depends on how many elites are 
                    extracting wealth, and on the productivity improvements due to the state:
                    
                    """,
                "title": "people",
                "vars": ["producer", "elite", "state"],
                "ymax_cutoff": 100,
            },
            {
                "markdown": """

                    ### Share of Production
                    
                    The amount of resources produced is:
                    
                    ```math
                    totalProduct = producer \\times productionRate
                    ```

                    where the production rate can be improved by the
                    state through the production decline function (discussed below)
                    ```math
                    productionRate = 
                         maxProductionRate
                         \\times 
                            \\left[
                              1 - prodDeclineFn(state)
                               \\times producer
                            \\right]
                    ```
                    
                    Here, we use a greedy elite model where all the product will
                    be extracted if the elite numbers grows large enough, leading to
                    the elite fraction for the total product:
                    
                    ```math
                    eliteFraction = 
                      \\frac
                        { elite }
                        {1 - eliteAtHalfExtraction \\times elite}
                    ```
                                        
                    ```math
                    eliteShare = totalProduct \\times eliteFraction
                    ```
                    
                    This leaves the producers:
                    
                    ```math
                    producerShare = totalProduct - eliteShare
                    ```
                    
                    """,
                "title": "Production Rate",
                "vars": ["producerShare", "eliteShare", "totalProduct"],
                "ymin": 0,
            },
            {
                "markdown": """

                    When expressed per capita, we can see the relative
                    wealth of producers versus elites over time.
        
                    """,
                "title": "Earnings Per Capita",
                "vars": ["productPerProducer", "productPerElite"],
                "ymin": 0,
            },
            {
                "markdown": """

                    ### State improves production
        
                    As the State gets stronger, it will be able to improve 
                    production. This is expressed through the Production 
                    Decline Function which defines how the state softens the 
                    production decline. The production decline measures
                    the decline in the production rate due to over-crowding
                    as the producer population nears the carrying capacity. 
                    
                    """,
                "fn": "prodDeclineFn", "xlims": [0, 1], "ymin": 0, "var": "state"},
            {
                "markdown": """

                    Thus we can see how as state revenue increases, the 
                    effective carrying capacity increases.

                    """,
                "title": "State Action on Producer Capacity",
                "vars": ["producer", "carry", "state"],
                "ymin": 0,
            },
            {
                "markdown": """

                    ### Pacification of Elite infighting

                    In the model, the intrinsic maxEliteDeath is quite high as 
                    elites will fight amongst themselves for 
                    resources. However, as the state increases strength, 
                    the state can impose peace on the elites, and this is reflected 
                    in: 
                    
                    ```math
                    stateModifiedFraction = 1 
                        - 
                        \\frac
                            {state}
                            {stateAtHalfPeace + state}
                    ```
                    
                    resulting in a lower elite death rate:
                    
                    ```math
                    eliteDeathRate = maxEliteDeath
                        \\times stateModifiedFraction
                    ```
                    
                    The deaths of elites obviously depends also
                    on the number of elites that have managed
                    to grow due to extraction of resources from
                    the producers:
                    
                    ```math
                    eliteDeath = elite 
                        \\times eliteDeathRate
                    ```
                    
                    """,
                "title": "State Action on Elites",
                "vars": ["eliteDeathRate", "eliteDeath", "state"],
                "ymin": 0,
            },
        ]
        self.editable_params = [
            {"key": "time", "max": 2000,},
        ]
        self.extract_editable_params()


if __name__ == "__main__":
    model = TurchinEliteDemographicModel()
    show_models([model], sys.argv)
