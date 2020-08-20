import sys
import logging

logging.basicConfig(level=logging.DEBUG)

from modeldrop.app import DashModelAdaptor, open_url_in_background
from modeldrop.goodwin import GoodwinBusinessCycleModel
from modeldrop.keen import KeenDynamicEconomyModel
from modeldrop.property import PropertyVsFundInvestmentModel
from modeldrop.turchin import TurchinDemographicStateModel
from modeldrop.epi import EpidemiologySirModel
from modeldrop.ecology import LoktaVolterraEcologyModel

port = "8050"
if "-o" in sys.argv:
    open_url_in_background(f"http://127.0.0.1:{port}/")
is_debug = "-d" in sys.argv

adaptor = DashModelAdaptor(
    [KeenDynamicEconomyModel(), LoktaVolterraEcologyModel(), EpidemiologySirModel(), TurchinDemographicStateModel(), PropertyVsFundInvestmentModel(), GoodwinBusinessCycleModel(), ]
)
server = adaptor.server

if __name__ == "__main__":
    adaptor.run_server(port=port, is_debug=is_debug)
