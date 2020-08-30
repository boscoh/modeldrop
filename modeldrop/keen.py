from .basemodel import BaseModel, make_lin_fn


class KeenDynamicEconomyModel(BaseModel):
    def setup(self):
        self.url = "https://github.com/boscoh/modeldrop/blob/master/modeldrop/keen.py"

        self.param.time = 200
        self.param.dt = 0.1

        self.param.birthRate = 0.01
        self.param.capitalAccelerator = 3
        self.param.depreciationRate = 0.06
        self.param.productivityRate = 0.02

        self.param.interestRate = 0.04
        self.param.investSlope = 10
        self.param.investXOrigin = 0.03
        self.param.wageSlope = 4
        self.param.wageXOrigin = 0.6

        self.param.initialWage = 0.850
        self.param.initialLaborFraction = 0.61

        self.setup_ui()

    def init_vars(self):
        self.fns.wageFn = make_lin_fn(self.param.wageSlope, self.param.wageXOrigin)

        self.fns.investFn = make_lin_fn(
            self.param.investSlope, self.param.investXOrigin
        )

        self.var.wage = self.param.initialWage
        self.var.productivity = 1
        self.var.population = 100
        self.var.laborFraction = self.param.initialLaborFraction
        self.var.output = (
            self.param.initialLaborFraction
            * self.var.population
            * self.var.productivity
        )
        self.var.wageShare = self.var.wage / self.var.productivity
        self.var.debtRatio = 0.0

    def calc_aux_vars(self):
        self.aux_var.labor = self.var.laborFraction * self.var.population
        self.aux_var.wageDelta = self.fns.wageFn(self.var.laborFraction)
        self.aux_var.laborWages = self.var.wage * self.aux_var.labor
        self.aux_var.wages = self.var.wage * self.aux_var.labor

        self.aux_var.capital = self.var.output * self.param.capitalAccelerator

        self.aux_var.bankShare = self.param.interestRate * self.var.debtRatio
        self.aux_var.profitShare = 1 - self.var.wageShare - self.aux_var.bankShare

        self.aux_var.profitRate = (
            self.aux_var.profitShare / self.param.capitalAccelerator
        )

        self.aux_var.investDelta = self.fns.investFn(self.aux_var.profitRate)
        self.aux_var.investment = self.aux_var.investDelta * self.var.output
        self.aux_var.realGrowthRate = (
            self.aux_var.investDelta / self.param.capitalAccelerator
            - self.param.depreciationRate
        )

        self.aux_var.debt = self.var.debtRatio * self.var.output
        self.aux_var.bank = self.aux_var.bankShare * self.var.output
        self.aux_var.profit = self.aux_var.profitShare * self.var.output

        self.aux_var.borrow = self.aux_var.investment - self.aux_var.profit

    def calc_dvars(self, t):
        self.dvar.wage = self.aux_var.wageDelta * self.var.wage

        self.dvar.productivity = self.param.productivityRate * self.var.productivity

        self.dvar.population = self.param.birthRate * self.var.population

        self.dvar.laborFraction = self.var.laborFraction * (
            self.aux_var.realGrowthRate
            - self.param.productivityRate
            - self.param.birthRate
        )

        self.dvar.output = self.var.output * self.aux_var.realGrowthRate

        self.dvar.wageShare = self.var.wageShare * (
            self.aux_var.wageDelta - self.param.productivityRate
        )

        self.dvar.debtRatio = (
            self.aux_var.investDelta
            - self.aux_var.profitShare
            - self.var.debtRatio * self.aux_var.realGrowthRate
        )

    def setup_ui(self):
        self.editable_params = [
            {"key": "time", "max": 500,},
            {"key": "birthRate", "max": 0.1,},
            {"key": "capitalAccelerator", "max": 5,},
            {"key": "depreciationRate", "max": 0.1,},
            {"key": "productivityRate", "max": 0.1,},
            {"key": "initialLaborFraction", "max": 1.0,},
            {"key": "interestRate", "max": 0.2,},
            {"key": "wageSlope", "max": 30, "min": -30},
            {"key": "wageXOrigin", "max": 1, "min": -1},
            {"key": "investSlope", "max": 30, "min": -30},
            {"key": "investXOrigin", "max": 0.5, "min": -0.5},
        ]
        self.plots = [
            {
                "markdown": """
                
                    The Keen-Minksy model, developed by [Steve Keen]( 
                    https://keenomics.s3.amazonaws.com/debtdeflation_media 
                    /papers/PaperPrePublicationProof.pdf), provides a model 
                    of the economy that has the 
                    attractive feature of generating both stable business 
                    cycles and catastrophic crashes.
                                        
                    The economy has three sectors:
                    
                    1. labor takes wages from capital to generate output
                    2. capital borrows money for investment and pays for labor to generate output
                    3. bank lends money to capital and takes interest for income
                    
                    The starting point of the model are these equations 
                    between labor and capital, which are dynamical 
                    restatements of standard macroeconomic relationships 
                    
                    ```math
                    output = labor \\times productivity
                    ```
                    ```math
                    capital = output \\times capitalAccelerator
                    ```
                    ```math
                    \\frac{d}{dt}(capital) = investment - depreciationRate \\times capital
                    ```
                    
                    Productivity is assumed to increase steadily due to innovations in
                    technology:

                    ```math
                    \\frac{d}{dt}(productivity) = productivity \\times productivityGrowthRate
                    ```

                    The model generates the evolution of the relative incomes 
                    of labor (wage share), capital (profit share) and bank 
                    (bank share), based purely on self-interacting 
                    dynamics: 

                    """,
                "title": "Share",
                "vars": ["wageShare", "profitShare", "bankShare"],
                "ymin_cutoff": -0.5,
                "ymax_cutoff": 1.5,
            },
            {
                "markdown": """

                    ### The Workers

                    In our model, we have a typical population:

                    ```math
                    \\frac{d}{dt}(population) = population \\times populationGrowthRate
                    ```

                    The population grows exponentially, but labor fluctuates with the typical 
                    business cycle. 
                    
                    """,
                "title": "People",
                "vars": ["population", "labor"],
            },
            {
                "markdown": """
                    The number of employed workers - labor - depends on the other two actors
                    in the economy. Labor
                    depends on how much capital is in the system, and changes in capital 
                    depends on profitability, which in turn depends on wages:

                    ```math
                    wages = labor \\times wage
                    ```

                    We must explicitly introduce a model of how wage changes:

                    ```math
                    \\frac{d}{dt}(wage) = wage \\times wageFn \\left[ \\frac{labor}{population} \\right]
                    ```

                    We use the Keen Wage Function that models the upward pressure on
                    the wage as the employment fraction approaches 1.
                    """,
                "fn": "wageFn",
                "xlims": [0, 1.1],
                "var": "laborFraction",
            },
            {
                "markdown": """
                    ### The Profit Drive of Capital

                    The behaviour of capitalists is modeled as a reaction to profitability.
                    The profitability is defined by the profit rate:

                    ```math
                    profit = output - wages - interest
                    ```

                    ```math
                    profitRate = \\frac{profit}{capital}
                    ```
                    
                    And the amount that the capitalists would like to borrow is 
                    determined by the invest function, which models the psychological
                    behavior of capitalists.

                    ```math
                    borrow = investFn(profitRate) \\times output - profit
                    ```
                    
                    Minsky argued that in general a capitalist will want to 
                    invest more when the profit rate is positive, and attempt
                    to divest if the situation is unprofitable (profit rate < 0).
                    This can be expressed through the Keen Investment Function:
                                         
                    """,
                "fn": "investFn",
                "xlims": [-0.5, 0.5],
                "var": "profitRate",
            },
            {
                "markdown": """
                    ### The Bank, their debt and the Economy                      
                                        
                    The bank's role is to create debt to lend to capitalists. 
                    This assumes (unlike neoclassical models) that banks 
                    create new money and new debt, upon making a loan. 
                    This is the official position 
                    taken by central banks such as the [Bank of England](https://www.bankofengland.co.uk/-/media/boe/files/quarterly-bulletin/2014/money-creation-in-the-modern-economy.pdf?la=en&hash=9A8788FD44A62D8BB927123544205CE476E01654).
                    
                    The income of the bank is thus the interest generated from the debt,
                    paid by the capitalist:
                    
                    ```math
                    interest = interestRate \\times debt
                    ```

                    Combining the money borrowed, and the interest payments, we
                    obtain the equation for the debt generated by the banking sector:
                    
                    ```math
                    \\frac{d}{dt}(debt) = interestRate \\times debt + borrow
                    ```
                    When combined with all the equations above, this results 
                    in this equation of the total output of the economy:
                    
                    ```math
                    \\frac{d}{dt}(output) = output \\times \\left( \\frac{investmentFn\\left[profitRate\\right]}{capitalAccelerator} - depreciationRate \\right)
                    ```
                    
                    We can now plot all the major components to the output, 
                    and compare it to the bank debt. We can now see that the 
                    business cycle oscillates, but accumulates debt, 
                    until the debt runs away and overwhelms the system with 
                    interest payments. The breakdown point is when the profit 
                    of the capitalists is driven below zero due to the 
                    banking sector. 
                    
                    """,
                "title": "Output",
                "vars": [ "wages", "profit", "bank", "debt", "output",],
            },
        ]
