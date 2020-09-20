import logging
import sys

from modeldrop.app import DashModelAdaptor, open_url_in_background
from modeldrop.demo import TurchinEliteDemographicModel
from modeldrop.ecology import LoktaVolterraEcologyModel
from modeldrop.epi import StandardThreePartEpidemiologyModel
from modeldrop.goodwin import GoodwinBusinessCycleModel
from modeldrop.growth import FundamentalPopulationModel
from modeldrop.keen import KeenDynamicEconomyModel
from modeldrop.property import PropertyVsFundInvestmentModel
from modeldrop.spring import ElasticSpringModel
from modeldrop.turchin import TurchinDemographicStateModel

dash = DashModelAdaptor(
    [
        FundamentalPopulationModel(),
        ElasticSpringModel(),
        LoktaVolterraEcologyModel(),
        StandardThreePartEpidemiologyModel(),
        GoodwinBusinessCycleModel(),
        KeenDynamicEconomyModel(),
        TurchinDemographicStateModel(),
        TurchinEliteDemographicModel(),
        PropertyVsFundInvestmentModel(),
    ],
)
server = dash.server

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    port = "8050"
    if "-o" in sys.argv:
        open_url_in_background(f"http://127.0.0.1:{port}/")
    is_debug = "-d" in sys.argv
    dash.run_server(port=port, is_debug=is_debug)
