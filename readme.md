
# Modeldrop

Explore dynamical population models with scipy and dash.

Modeldrop abstracts out the UI interface and integration to allow
you to focus on the logic of the equations. 

Modeldrop uses:

- numerical solvers in scipy
- plotting with plotly or matplotlib
- dash for interactive parameter exploration
- twitter bootstrap for UI elements

Demo at [modeldrop.io](http://modeldrop.io).

Talk about modeldrop from pycon.au "[Tweaking the rise and fall of empires and economies][1]".

[1]: https://www.youtube.com/watch?v=2-it3crJYu0&ab_channel=PyConAU "Tweaking the rise and fall of empires and economies"

### Quick start

### Installation

Modeldrop is a written in Python 3 and can be installed using the
standard Python installer:

    pip install -r requirements
    
Then run:

    python go -o
      
- `-o` option opens the webbrowser for you.
- `-d` option runs the flask server in debug mode, allowing code hot-reloading

If you want it to run it in a wsgi server, use `go:server`

### Development Guide

The package consists of two parts:

* `basemodel` core model to integrate the equations of a model
* `app` dash adaptor to expose the model with an interactive UI and plots

There is an optional package to use `basemodel` to generate .png's of the solutions:

* `graphing` an adaptor to matplotlib to generate .png's

#### The model

`basemodel` provides an object class that allows the easy construction
of a dynamical model, with built-in methods to integrate these equations
 to model state variables evolving over time. 

The information to represent the differential equations at any time point are defined in 
the following `AttrDict` (a dictionary where the keys can also be accessed as properties):
    
* `self.var` - contains the values of the driving variables
* `self.dvar` - contains the value of the differentials of the corresponding `self.var`
* `self.aux_var` - any extra variables that are either used to calculate the above or for diagnostics
* `self.param` - contains any parameter values of the equations that will not change over time
* `self.fn` - contains any convenient functional forms that will be used to calculate the above

#### Setting up a model

The general approach to setting up a model is to override these methods of `BaseModel`:

1. `self.setup()` - setup values of `self.param`, making sure to call `self.setup_ui()` for
   adding plots and GUI controls.
2. `self.init_vars()` - initializes `self.var` at the beginning of the run, either using
   hard-coded constants or reads from a `self.param` value. As well, any functional
   forms used in calculations based on `self.param` values can be defined here.
3. `self.calc_aux_vars()` -  this method will be called at every time-point where
   we calculate any useful `self.aux_var` for further calculations and 
   diagnostics. The calculations can use existing values of `self.var` or `self.dvar`
   from the last time-point, and return values from functionals in `self.fn` using pre-existing values.
4. `self.calc_dvars(t)` - this method will be called at every time-point where
   we calculate `self.calc_dvar` using any
   preexisting `self.var`, and `self.dvar` or `self.fn`, from the
   last time-point, and any `self.aux_var` calculated from `self.calc_aux_var`. 
   The `self.dvar` can be expressed as a single line expression,
   or built up progressively.
5. Once defined, we call `self.run`, which will first clear `self.solution` 
   and re-intialize using `self.init_vars()`,
    then integrate the equation over a period
   of time from 0 to `self.param.time` in increments of `self.param.dt`. 
6. After the calculation, the solutions are contained in a dictionary `self.solution`
   where the keys are any key found in `self.var` or `self.aux_var`. And the value
   of the dictionaries are the list of floats for every time point specified in the 
   last step.

#### Optional flow compartments

For certain models, there are exact transfers of value between differentials. 
Such models are sometimes called compartment models where the driving variables
represents sub-populations where `self.dvar` correspond to flows of population
between sub-populations.

In such cases, it makes it much easier to express `self.dvar` in terms of flows.

```python
self.aux_var_flows = [
   ('population1', 'population2', 'some_aux_var')
]
```
Then in `self.calc_dvar()`, one calls:

```python
def calc_dvars(self, t):
    for key in self.var.keys():
        self.dvar[key] = 0
    self.add_to_dvars_from_flows()
```

where `self.add_to_dvars_from_flows` will ensure that the same
flow will be subtracted from `self.var.population1` and then added
to `self.var.population2`, thus conserving the overall population.

#### UI setup

To setup the UI from your `BaseModel`-derived class, override the `setup_ui` method:

```python
def setup_ui(self):
    self.plots = [
        {"key": "People", "vars": ["population", "labor"]},
        {"key": "Output", "vars": ["output", "wages"]},
        {"fn": "wageChange", "xlims": [0.8, 0.9999]},
    ]
    
    self.editable_params = [
        { "key": "param1", "max": 10 },
        ... 
    ]
```

The `self.editable_params` must use keys that exist in `self.param`. Alternatively,
one could simply call `self.extract_editable_params()`, which will automatically
populate `self.eidtable_params` from the `self.param` dictionary.

Once your model and ui setup is done, they can be setup as a dash server:

```python
dash = DashModelAdaptor([ YourModel(), ...])
dash.run_server()
```

which will run on `http://127.0.0.1:8000`.

### Plot dictionaries

The `self.plots` dictionary is used to configure the plots shown in the Dash app.

Each plot has several fields:

   - `title` - the name of the plot
   - `vars` - list of the `var` to plot, and these keys should be in `self.var` or `self.aux_var`
   - `markdown` - a multi-line string containing markdown that will be converted to HTML
      to display before the graph. Also allows katex inline equations
   - `ymin`/`ymax` - limits to the y-axis
   - `ymin_cutoff`/`ymax_cutoff` - limits that only apply if the data exceeds these cutoffs

Alternatively, the plot could display functional forms in `self.fn`:

   - `fn` - key of the function in `self.fn`, will be used to title graph
   - `xlims` - max/min x-value for the argument of the function

### Integration flow

By default integration will be delegated to the odeint
integrator through the `self.run()` method. In this method, 
a new derivative function is built that will return
the derivate in a form that odeint will recognize.

This function has the signature `list(float) -> list(float)`. It
will receive a vector carrying the current state `x` of
the model a particular time, and return a vector representing the derivatives.
The steps in the function are:

1. Takes `x` to repopulate `self.var`.
2. Calls `self.aux_vars()` that use only `self.var`.
3. Empties `self.dvar` to zero.
4. Calls `self.calc_dvars()` to fill out the `self.dvar`.
5. If `self.aux_var_flows` exists  then calls `self.add_to_dvars_from_flows()`
  to calculate `self.dvar` from the flows.
6. Convert `self.dvar` to an array of floats and returns it.



