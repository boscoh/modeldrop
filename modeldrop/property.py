import math

from .basemodel import BaseModel


def get_min_payment(principal, rate, n_payment):
    return (rate * principal) / (1.0 - math.pow(1.0 + rate, -n_payment))


class PropertyVsFundInvestmentModel(BaseModel):
    def setup(self):
        self.url = (
            "https://github.com/boscoh/modeldrop/blob/master/modeldrop/property.py"
        )

        self.param.initialProperty = 600000
        self.param.deposit = 150000
        self.param.interestRate = 0.05
        self.param.propertyRate = 0.045
        self.param.mortgageLength = 30
        self.param.fundRate = 0.08
        self.param.rentMonth = 2000
        self.param.inflation = 0.02
        self.param.time = 50

        self.setup_ui()

    def init_vars(self):
        self.param.paymentRate = get_min_payment(
            self.param.initialProperty,
            self.param.interestRate,
            self.param.mortgageLength,
        )

        self.var.property = self.param.initialProperty
        self.var.principal = self.param.initialProperty - self.param.deposit
        self.var.totalInterest = 0
        self.var.fund = self.param.deposit
        self.var.rent = self.param.rentMonth * 12
        self.var.totalRent = 0
        self.var.paid = self.param.deposit

    def calc_aux_vars(self):
        self.aux_var.interestPaid = self.param.interestRate * self.var.principal

        self.aux_var.fundChange = self.param.paymentRate - self.var.rent

        self.aux_var.interestMonth = self.aux_var.interestPaid / 12
        self.aux_var.paymentMonth = self.param.paymentRate / 12
        self.aux_var.rentMonth = self.var.rent / 12
        self.aux_var.fundChangeMonth = self.aux_var.fundChange / 12

        self.aux_var.propertyProfit = (
            self.var.property
            - self.param.deposit
            - self.var.principal
            - self.var.totalInterest
        )

        self.aux_var.fundProfit = (
            self.var.fund - self.param.deposit - self.var.totalRent
        )

    def calc_dvars(self, t):
        self.dvar.totalInterest = self.aux_var.interestPaid
        self.dvar.property = self.param.propertyRate * self.var.property
        if self.var.principal >= 0:
            self.dvar.principal = -(self.param.paymentRate - self.aux_var.interestPaid)
        else:
            self.dvar.principal = 0
        self.dvar.fund = self.param.fundRate * self.var.fund + self.aux_var.fundChange
        self.dvar.paid = self.param.paymentRate
        self.dvar.rent = self.param.inflation * self.var.rent
        self.dvar.totalRent = self.var.rent

    def setup_ui(self):
        self.editable_params = [
            {"key": "time", "max": 100,},
            {"key": "mortgageLength", "max": 100,},
            {"key": "interestRate", "max": 0.5,},
            {"key": "initialProperty", "max": 1000000},
            {"key": "deposit", "max": 1000000},
            {"key": "propertyRate", "max": 0.5,},
            {"key": "fundRate", "max": 0.5,},
        ]

        self.plots = [
            {
                "markdown": """
                    There's that proverb which says rent money is dead money. But interest
                    repayment is also dead money. Maybe that could
                    have been better put in an investment fund. So which is better in the 
                    long run? 
                    
                    One big problem with thinking about the profitability of property is 
                    that it's hard to visualize interest repayments. 
                    So here, we've provided a whole raft of interactive visualization 
                    to help you compare property to investment funds.
                    
                    ### Property
                    
                    The first thing to do is express the growth in a property price
                    as a standard growth equation:
                    
                    ```math
                    \\frac{d}{dt}(property) = property \\times propertyGrowthRate
                    ```
                    
                    We assume that you made a bank loan with a deposit, leaving you with 
                    a principal. Then the total interest paid is a growth equation based on 
                    the principal:
                    
                    ```math
                    \\frac{d}{dt}(totalInterest) = principal \\times interestRate
                    ```
                    
                    The principal will decline with a death rate
                    equal to the portion of the mortgage payment not eaten by 
                    interest repayments:
                    
                    ```math
                    principalRepayment = payment - principal \\times interestRate
                    ```
                    
                    ```math
                    \\frac{d}{dt}(principal) = -principalRepayment
                    ```
                    
                    The mortgage payment (per year) can be computed from this standard equation:
                    
                    ```math
                    payment =  principal \\times \\frac{ interestRate}{1 - interestRate \\times (1 + interestRate)^{-years})}
                    ```
                    """,
                "title": "Property",
                "vars": [
                    "paid",
                    "property",
                    "totalInterest",
                    "propertyProfit",
                    "principal",
                ],
            },
            {
                "markdown": """
                    ### Monthly Expenses comparison
                    
                    Finally, as a practical cash-flow concern, we can look
                    at how the differences play out on a monthly basis. We
                    cannot make a perfect comparison with the incomes as 
                    the rent inflation in later years may force us to pay more
                    per month than the minimum payment per month would allow.
                    
                    If we're looking at dead money paid, it would be comparing
                    the payment of rent versus interest, on a monthly basis, 
                    for different scenarios.
                    """,
                "title": "Month",
                "vars": [
                    "paymentMonth",
                    "interestMonth",
                    "rentMonth",
                    "fundChangeMonth",
                ],
            },
            {
                "markdown": """

                    ### Investment Fund and Renting
                    
                    Instead of buying a property with interest, one could invest the
                    same money in an investment fund. To make the comparison, we first
                    put the deposit in an investment fund. 
                    
                    Then we take the standard mortgage payment as the equivalent of our income.
                    We put a chunk of that income into rent, where rents typically grows with inflation:
                    
                    ```math
                    \\frac{d}{dt}(rent) = inflationRate \\times rent
                    ```
                    
                    ```math
                    \\frac{d}{dt}(totalRent) = rent
                    ```
                    
                    And thus the fund payment is what is left over, giving the
                    fund growth equation:
                    
                    ```math
                    \\frac{d}{dt}(fund) = payment - rent
                    ```

                    """,
                "title": "Fund",
                "vars": ["paid", "fund", "totalRent", "fundProfit"],
            },
        ]
