

# Tweaking the rise and fall of empires and economies

What is a model?

Mathematical model?

# Title: Tweaking the rise and fall of empires and economies

## Intended Audience

People who want to be exposed to fascinating mathematical models of the world, and who would like to interactively explore them. For those with a bit more scientific background, this talk will show how easy it can be to make these models in python and may encourage researchers to try python as a plausible tool to use.

## Why I am interested in this?

I am a data-engineer with a specialisation in data viz. I love exploring the visual impact of powerful models that explain some aspect of our world. As such, I love reading about interesting models, and I am willing to wade into the maths as I was previously a computational biologist who built theoretical biological models. The maths is tricky but I believe that it can be made a lot easier with a good python framework, and so I built one to explore these models. I am pleased with the result, and hope that others might also enjoy playing around with these models too.

## Outline

1) show examples of beautiful numerical models of the economy
    a) Peter Turchin's model of empire disintegration
    b) Steve Keen's model of debt-drive collapse in the business cycle
    c) the standard SIR model of how infectious diseases rips through a population
2) show how painful it is to build the models yourself
    a) brief look at how these models are presented in the literature, standard mathematical nomenclature
    b) show select real world examples of yukky mathematical programming, matlab, fortran, even python
3) describe the framework that simplifies this
    a) introduce my pyecon library 
    b) heavy use of string lookup in dictionaries
    c) translation from math to descriptive variable names
    d) outsourcing the solver to scipy
    e) functional abstractions to transform into scipy
    f) use dash and plotly to expose graphs and controls in a transparent manner   
4) contrast the readable code examples of this framework to other examples
5) demonstrate the built-in interactive UI
    a) watch how interest rate increases can destroy an economy
    b) show how empires self-destruct
    c) show how different kinds of infections rip through a population