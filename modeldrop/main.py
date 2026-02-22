from modeldrop.app import DashModelAdaptor
from modeldrop.demo import TurchinEliteDemographicModel
from modeldrop.ecology import LoktaVolterraEcologyModel
from modeldrop.epi import StandardThreePartEpidemiologyModel
from modeldrop.fathers import TurchinFathersAndSonsModel
from modeldrop.goodwin import GoodwinBusinessCycleModel
from modeldrop.growth import FundamentalPopulationModel
from modeldrop.keen import KeenDynamicEconomyModel
from modeldrop.property import PropertyVsFundInvestmentModel
from modeldrop.spring import ElasticSpringModel
from modeldrop.turchin import TurchinDemographicStateModel

MODEL_REGISTRY: dict[str, type] = {
    "growth": FundamentalPopulationModel,
    "spring": ElasticSpringModel,
    "ecology": LoktaVolterraEcologyModel,
    "epi": StandardThreePartEpidemiologyModel,
    "goodwin": GoodwinBusinessCycleModel,
    "keen": KeenDynamicEconomyModel,
    "turchin": TurchinDemographicStateModel,
    "demo": TurchinEliteDemographicModel,
    "fathers": TurchinFathersAndSonsModel,
    "property": PropertyVsFundInvestmentModel,
}

dash_app = DashModelAdaptor(list(cls() for cls in MODEL_REGISTRY.values()))
server = dash_app.server  # for gunicorn
