import sys
import logging
logging.basicConfig(level=logging.DEBUG)

from modeldrop.app import DashModelAdaptor, open_url_in_background
from modeldrop.goodwin import GoodwinModel
from modeldrop.keen import KeenModel
from modeldrop.property import PropertyModel
from modeldrop.turchin import DemographicFiscalModel

port = "8050"
if "-o" in sys.argv:
    open_url_in_background(f"http://127.0.0.1:{port}/")
is_debug = "-d" in sys.argv

models = [KeenModel(), DemographicFiscalModel(), PropertyModel(), GoodwinModel()]
DashModelAdaptor(models).run_server(port=port, is_debug=is_debug)
