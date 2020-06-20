import logging
from modeldrop.app import DashModelAdaptor
from modeldrop import keen
from modeldrop import goodwin
from modeldrop import property

logging.basicConfig(level=logging.INFO)
models = [property.PropertyModel(), keen.KeenModel(), goodwin.GoodwinModel()]
dash_model = DashModelAdaptor(models)
dash_model.run_server()
