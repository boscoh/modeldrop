
# Modeldrop

Explore dynamical population models with scipy and dash

Modeldrop abstracts out the interface to the numerical solvers
provided by scipy, and allows the focus on the meat of the equations.
Simultaneously, modeldrop uses dash to provide an interactive 
visualization and direct exploration of the model.

Modeldrop provides a glue between:
- numerical solvers in scipy
- plotting with plotly or matplotlib
- dash for interactive parameter exploration
- twitter bootstrap for UI elements

### Installation

Modeldrop is a written in Python 3 and can be installed using the
standard Python installer:

    pip install -r requirements
     
### Quick start

Then run:

    python go -o
      
The `-o` option opens the webbrowser for you.
The `-d` debug option runs the flask server in debug mode, providing
a hot-reloading mechanism for code changes.

### Development Guide

Historically, the approach to implementing differential equations is
to approach each individual equation directly. However, dynamical population models typically model flows of 
populations between compartments. Thus it is better to approach
it by keeping tabs of population flows.

The package consists of three parts:

* `basemodel` core model with hooks into scipy
* `app` dash adaptor to display an interactive model
* `graphing` adaptor to matplotlib to generate .png's

#### The model

`basemodel` provides an object class that allows the easy construction
of a dynamical model, with methods to integrate these equations
easily to watch variables evolve over time. This model is controlled
by a set of parameters, and variation of the parameters represents
an exploration of the different properties of the model.

    AttrDict
    
    this.var - are driving variables and are always accompained with
               a dvar
    this.dvar - holds the changes to the correspond var
    this.aux_var - any extra variables that are calculated to help
              calculate other var or other dvar
    this.init_var - the inital vale of a var for recalculation
    this.param - key parameter values that change the model

#### The plots

There are two plotting approaches provided here.

First is a wrapper around matplotlib to generate images.

The second is a pipe into plotly using dash.

    self.var_plots = [
        {"key": "People", "vars": ["population", "labor"]},
        {"key": "Output", "vars": ["output", "wages"]},
    ]
    self.fn_plots = [
        {"fn": "wageChange", "xlims": [0.8, 0.9999]},
    ]

