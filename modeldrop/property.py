import logging
import math

from .basemodel import BaseModel


def get_min_payment(principal, rate, n_payment):
    return (rate * principal) / (1.0 - math.pow(1.0 + rate, -n_payment))


logger = logging.getLogger(__name__)


class PropertyModel(BaseModel):
    def setup(self):
        self.param.initialProperty = 600000
        self.param.deposit = 150000
        self.param.interestRate = 0.05
        self.param.propertyRate = 0.045
        self.param.mortgageLength = 30
        self.param.fundRate = 0.08
        self.param.rentMonth = 2000
        self.param.inflation = 0.02
        self.param.time = 50

        self.editable_params = [
            {"key": "time", "max": 100,},
            {"key": "mortgageLength", "max": 100,},
            {"key": "interestRate", "max": 0.5,},
            {"key": "initialProperty", "max": 1000000},
            {"key": "deposit", "max": 1000000},
            {"key": "propertyRate", "max": 0.5,},
            {"key": "fundRate", "max": 0.5,},
        ]

        self.model_plots = [
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

    def init_vars(self):
        self.init_var.property = self.param.initialProperty
        self.init_var.principal = self.param.initialProperty - self.param.deposit
        self.aux_var.paymentRate = get_min_payment(
            self.init_var.principal, self.param.interestRate, self.param.mortgageLength,
        )
        self.init_var.totalInterest = 0
        self.init_var.fund = self.param.deposit
        self.init_var.rent = self.param.rentMonth * 12
        self.init_var.totalRent = 0
        self.init_var.paid = self.param.deposit

        super().init_vars()

    def calc_aux_vars(self):
        self.aux_var.interestPaid = self.param.interestRate * self.var.principal

        self.aux_var.fundChange = self.aux_var.paymentRate - self.var.rent

        self.aux_var.interestMonth = self.aux_var.interestPaid / 12
        self.aux_var.paymentMonth = self.aux_var.paymentRate / 12
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
                self.aux_var.paymentRate - self.aux_var.interestPaid
            )
        else:
            self.dvar.principal = 0
        self.dvar.fund = self.param.fundRate * self.var.fund + self.aux_var.fundChange
        self.dvar.paid = self.aux_var.paymentRate
        self.dvar.rent = self.param.inflation * self.var.rent
        self.dvar.totalRent = self.var.rent
