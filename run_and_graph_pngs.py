from modeldrop.growth import FundamentalPopulationModel
from modeldrop.modelgraph import make_graphs_from_model

model = FundamentalPopulationModel()

make_graphs_from_model(model, "growth_pngs", transparent=True)
