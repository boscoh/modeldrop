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
            self.param.initialProperty, self.param.interestRate, self.param.mortgageLength,
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
            self.dvar.principal = -(
                self.param.paymentRate - self.aux_var.interestPaid
            )
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

        self.var_plots = [
            {
                "key": "Month",
                "vars": [
                    "paymentMonth",
                    "interestMonth",
                    "rentMonth",
                    "fundChangeMonth",
                ],
            },
            {
                "key": "Property",
                "vars": [
                    "paid",
                    "property",
                    "totalInterest",
                    "propertyProfit",
                    "principal",
                ],
            },
            {"key": "Fund", "vars": ["paid", "fund", "totalRent", "fundProfit"],},
        ]
