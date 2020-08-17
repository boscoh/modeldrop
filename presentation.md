

# Title: Tweaking the rise and fall of empires and economies

## Intended Audience

People who want to be exposed to fascinating mathematical models of the world, and who would like to interactively explore them. For those with a bit more scientific background, this talk will show how easy it can be to make these models in python and may encourage researchers to try python as a plausible tool to use.

What is a model?

Mathematical model?


## Outline

1. Background in modelling -> worked in 3 epidemilogy labs Burnet, Monash, James Cook University
   1. love modeling
   2. love python - rework traditional ODE modleing in PYthon
   2. learnt the basic calculus approach to populations 
   3. explored all sorts of models based on ODE's
   4. Discovered a whole world of analytical models
2. Examples of typical approach:
   - global variables
   - global expressions
   - mixed variables
   - equations are expressed ad-hoc
   - terrible variable names
   
1. show examples of beautiful numerical models of the economy
    1. Peter Turchin's model of empire disintegration
    2. Steve Keen's model of debt-drive collapse in the business cycle
    3. the standard SIR model of how infectious diseases rips through a population
2. show how painful it is to build the models yourself
    1. brief look at how these models are presented in the literature, standard mathematical nomenclature
    2. show select real world examples of yukky mathematical programming, matlab, fortran, even python
3. describe the framework that simplifies this
    1. introduce my pyecon library 
    2. heavy use of string lookup in dictionaries
    3. translation from math to descriptive variable names
    4. outsourcing the solver to scipy
    5. functional abstractions to transform into scipy
    6. use dash and plotly to expose graphs and controls in a transparent manner   
4. contrast the readable code examples of this framework to other examples
5. demonstrate the built-in interactive UI
    1. watch how interest rate increases can destroy an economy
    2. show how empires self-destruct
    3. show how different kinds of infections rip through a population
