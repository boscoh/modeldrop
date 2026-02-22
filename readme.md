# modeldrop

Explore dynamical population models with interactive parameter sliders.

Modeldrop abstracts the UI and numerical integration so you can focus on
the equations. Models run in [scipy](https://scipy.org) via Runge-Kutta,
and are explored through a [Dash](https://dash.plotly.com) web interface
styled with [Bootstrap 5](https://getbootstrap.com).

Demo at [modeldrop.io](http://modeldrop.io).

Talk from PyConAU 2020: "[Tweaking the rise and fall of empires and economies](https://www.youtube.com/watch?v=2-it3crJYu0&ab_channel=PyConAU)".

---

## Installation

Requires Python 3.11+. Install with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install modeldrop
```

Or into a project:

```bash
uv add modeldrop
```

---

## Usage

### Run the interactive server

```bash
modeldrop serve             # start on port 8050
modeldrop serve -o          # open browser automatically
modeldrop serve -r          # hot-reload mode
modeldrop serve --port 8080 # custom port
```

### Generate PNG graphs

```bash
modeldrop graph growth             # write PNGs to current directory
modeldrop graph epi ./output       # write to a specific directory
modeldrop graph keen . --transparent
```

Available model names: `growth`, `spring`, `ecology`, `epi`, `goodwin`,
`keen`, `turchin`, `demo`, `fathers`, `property`.

### Production (Gunicorn)

```bash
gunicorn modeldrop.main:server -w 4 -b 0.0.0.0:8050
```

---

## Writing a model

### Core concepts

`BaseModel` exposes four `AttrDict` namespaces (dict with attribute access):

| Namespace | Purpose |
|---|---|
| `self.param` | Parameters — editable via UI sliders |
| `self.var` | State variables — integrated over time |
| `self.dvar` | Derivatives of `self.var` |
| `self.aux_var` | Derived quantities used in calculations or diagnostics |

### Override these methods

```python
from modeldrop.basemodel import BaseModel

class MyModel(BaseModel):

    def setup(self):
        self.name = "My Model"
        self.param.growth_rate = 0.1
        self.param.time = 100
        self.param.dt = 0.5
        self.setup_ui()

    def setup_ui(self):
        self.plots = [
            {
                "title": "Population",
                "vars": ["population"],
                "markdown": """
                    ### Exponential growth

                    $$
                    \\frac{d}{dt}(population) = growthRate \\times population
                    $$
                """,
            },
        ]
        self.editable_params = [
            {"key": "growth_rate", "max": 1.0},
        ]

    def init_vars(self):
        self.var.population = 100.0

    def calc_aux_vars(self):
        pass  # compute self.aux_var values here

    def calc_dvars(self, t):
        self.dvar.population = self.param.growth_rate * self.var.population
```

Method call order during `self.run()`:

1. `init_vars()` — set initial state
2. For each timestep: `calc_aux_vars()` then `calc_dvars(t)`
3. Results stored in `self.solution` (dict of key → list of floats) and `self.times`

### Compartment (flow) models

For models where variables represent sub-populations with transfers between
them (e.g. SIR epidemiology), express flows instead of raw derivatives:

```python
def setup(self):
    ...
    self.aux_var_flows = [
        ("susceptible", "infected", "infection_rate"),
        ("infected", "recovered", "recovery_rate"),
    ]

def calc_dvars(self, t):
    for key in self.var:
        self.dvar[key] = 0
    self.add_to_dvars_from_flows()
```

`add_to_dvars_from_flows()` subtracts each flow from the source and adds it
to the destination, conserving the total population.

### Plot dictionary fields

| Field | Description |
|---|---|
| `title` | Plot heading |
| `vars` | List of keys from `self.var` or `self.aux_var` to plot |
| `markdown` | Markdown string shown above the graph; supports `$$...$$` LaTeX |
| `ymin` / `ymax` | Fixed y-axis limits |
| `ymin_cutoff` / `ymax_cutoff` | Clamp limits only when data exceeds them |
| `fn` | Key of a function in `self.fn` (plots the function curve instead) |
| `xlims` | `[min, max]` x-range when using `fn` |

### Register your model in the app

```python
# modeldrop/main.py
from mypackage.mymodel import MyModel

MODEL_REGISTRY = {
    ...
    "mymodel": MyModel,
}
```

Or run it standalone:

```python
from modeldrop.app import DashModelAdaptor
from mypackage.mymodel import MyModel

app = DashModelAdaptor([MyModel()])
app.run_server()
```

---

## Package structure

| Module | Purpose |
|---|---|
| `basemodel` | `BaseModel` — integration engine and state management |
| `app` | `DashModelAdaptor` — Dash/Bootstrap UI and callbacks |
| `cli` | `modeldrop` CLI entry point (cyclopts) |
| `main` | Model registry and WSGI `server` export |
| `graphing` | Matplotlib PNG export |
| `modelgraph` | Bridge from `BaseModel` to `graphing` |
