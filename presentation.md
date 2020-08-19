

# Title: Tweaking the rise and fall of empires and economies

## Intended Audience

People who want to be exposed to fascinating mathematical models of the world, and who would like to interactively explore them. For those with a bit more scientific background, this talk will show how easy it can be to make these models in python and may encourage researchers to try python as a plausible tool to use.

What is a model?

Mathematical model?


## Outline

1. Background in modelling -> worked in 3 epidemiology labs Burnet, Monash, James Cook University
  1. love modelling
  2. love python - rework traditional ODE modleing in PYthon
  3. learnt the basic calculus approach to populations 
  4. explored all sorts of models based on ODE's
  5. Discovered a whole world of analytical models
1. show examples of beautiful numerical models of the economy
  1. Peter Turchin's model of empire disintegration
  2. Steve Keen's model of debt-drive collapse in the business cycle
  3. the standard SIR model of how infectious diseases rips through a population
1. show how painful it is to build the models yourself
    1. brief look at how these models are presented in the literature, standard mathematical nomenclature
    2. show select real world examples of yukky mathematical programming, matlab, fortran, even python
      1. global variables
      2. global expressions
      3. mixed variables
      4. equations are expressed ad-hoc
      5. terrible variable names
      6. everything checked by hand
      7. lots of crossreferencing
      8. low readability 
      9. good matching of equations!
      7. no reusability    
1. describe the framework that simplifies this
    1. introduce my modeldrop library 
      - originally python from work on SIR using matplotlib
      - then a javascript for UI dev and plots
      - back to python because of scipy and dash plotly
    2. outsourcing the solver to scipy 
      - thousands of man hours of work - FORTRAN library odepack
      - hide the FOTRAN interface
    1. grouped variables
    2. vars - state variables
    4. heavy use of string lookup in dictionaries
      - groups related things together
      - allow iteration over vars, dvars, aux_vars, params
      - allow meta construction
    3. consistency checks 
    5. translation from math to descriptive variable names
    6. use a lot of humanizing to generate controls UI
    6. use dash and plotly to expose graphs and controls in a transparent manner   
1. run through the transformation using predator/prey and/or sir
    - start with differential equation
    - code in python/fortran
    - introudce basemodel
    - parameters
      + allows pulling up to controls
    - vars and dvars
      + allows consistency checks
    - dvars dictionary 
      + allows wrapping into function
    - vars and aux_vars
      + allows extra-curricular mapping
      + plots are easy to construct
    - transformation
      + into something readable!
1. demonstrate the built-in interactive UI
    1. Keen model of economy - workers/bankers/capitalists
      - workers demands wages if employment rate goes up
      - capitalists borrow money if profit goes up
      - bankers can lend as much as demand
      - capitalists pay off loans according to interest rate
    1. watch how interest rate increases can destroy an economy
    2. Turchin model
      - state revenue increases carrying capacity
      - carrying capacity increases population
      - population increases increases state revenue
      - imperial collapse
    3. show how different kinds of infections rip through a population
