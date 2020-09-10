import sys
from growth import FundamentalPopulationModel
from modeldrop.ecology import LoktaVolterraEcologyModel
from modeldrop.epi import StandardThreePartEpidemiologyModel
from modeldrop.goodwin import GoodwinBusinessCycleModel
from modeldrop.keen import KeenDynamicEconomyModel
from modeldrop.property import PropertyVsFundInvestmentModel
from modeldrop.turchin import TurchinDemographicStateModel
from modeldrop.demo import TurchinEliteDemographicModel
from modeldrop.app import show_models

show_models(
    [
        FundamentalPopulationModel(),
        LoktaVolterraEcologyModel(),
        StandardThreePartEpidemiologyModel(),
        GoodwinBusinessCycleModel(),
        KeenDynamicEconomyModel(),
        TurchinDemographicStateModel(),
        TurchinEliteDemographicModel(),
        PropertyVsFundInvestmentModel(),
    ],
    sys.argv
)
