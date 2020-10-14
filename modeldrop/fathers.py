from .basemodel import AttrDict, BaseModel


class TurchinFathersAndSonsModel(BaseModel):
    def setup(self):
        self.url = (
            "https://github.com/boscoh/modeldrop/blob/master/modeldrop/fathers.py"
        )

        self.integrate_method = "euler_integrate"
        self.param.time = 100
        self.param.dt = 0.5

        self.param.nAge = 25

        self.param.radicalisation = 0.3
        self.param.aversion = 1
        self.param.disenchantment = 0.5
        self.param.delay = 10

        self.groups = ["naive", "moderate", "radical"]

        self.init_vars()

        self.setup_ui()

    def init_vars(self):
        self.param.nAge = int(self.param.nAge)

        self.pops = AttrDict()
        for group in self.groups:
            self.pops[group] = [f"{group}_{age}" for age in range(self.param.nAge)]

        for age in range(self.param.nAge):
            for group in self.groups:
                key = f"{group}_{age}"
                if group == "naive":
                    self.var[key] = 0.5 / self.param.nAge
                elif group == "radical":
                    self.var[key] = 0.1 / self.param.nAge
                else:
                    self.var[key] = 0.4 / self.param.nAge

    def calc_aux_vars(self):
        for group in self.groups:
            vals = [self.var[n] for n in self.pops[group]]
            vals = [v for v in vals if v is not None]
            self.aux_var[ f"{group}_total"] = sum(vals)

        i = int(self.param.delay / self.param.dt)
        self.aux_var.radical_total_delayed = 0
        for key in self.pops.radical:
            if key not in self.solution:
                continue
            if len(self.solution[key]) > i:
                self.aux_var.radical_total_delayed += self.solution[key][-i]

        self.aux_var.rho = self.param.disenchantment * self.aux_var.radical_total_delayed

        self.aux_var.sigma = self.aux_var.radical_total * (
            self.param.radicalisation - self.param.aversion * self.aux_var.moderate_total
        )

    def calc_dvars(self, t):
        self.dvar = {}

        for k in self.keys:
            self.dvar[k] = -self.var[k]

        self.dvar[f"naive_0"] += 1.0 / self.param.nAge

        for j in range(1, self.param.nAge):
            i = j - 1
            self.dvar[f"naive_{j}"] += self.var[f"naive_{i}"] * (1 - self.aux_var.sigma)
            self.dvar[f"radical_{j}"] += self.var[f"radical_{i}"] * (
                1 - self.aux_var.rho
            )
            self.dvar[f"radical_{j}"] += self.var[f"naive_{i}"] * self.aux_var.sigma
            self.dvar[f"moderate_{j}"] += self.var[f"moderate_{i}"]
            self.dvar[f"moderate_{j}"] += self.var[f"radical_{i}"] * self.aux_var.rho

    def setup_ui(self):
        self.plots = [
            {
                "markdown": """
                
                The fathers-and-sons model assumes that there are basically
                three categories of people:
                
                1. Naives have not been exposed to radicalization
                2. Radicals are angry and prone to protest and violence
                3. Moderates are former radicals who have renounced extremism
                    
                The model carries a number of age groups for each category of people.
                
                ```math
                naive_0, naive_1, ..., naive_{nAge}
                ```
                   
                They do not get radicalized until they move into the 2nd age group, so
                all those of the 1st age group are naive.
                
                Naive people are radicalized by their exposure to other to radicals, 
                and this radicalization rate R, but is reduced if by the number
                of moderates, who are disillusioned radicals and thus have an
                aversion to radicalism:
                
                ```math
                R = \\sum_{age} radical_{age} \\times (
                    radicalisation 
                    - aversion \\times \\sum_{age} moderate_{age})
                ```

                Radicals are disenchanted after a delay of a certain number of years
                of being extermists, and this rate D defines the movement of radicals 
                to moderate:  
                
                ```math
                D = disenchantment \\times \\sum_{age} radical_{age}(t - delay)
                ```

                Thus the changes for each age in each category is:
                
                ```math
                \\frac{d}{dt}(naive_{age}) = 
                    - naive_{age} + naive_{age - 1} \\times ( 1 - R)
                ```
                
                ```math
                \\frac{d}{dt}(radical_{age}) = 
                    - radical_{age} 
                    + radical_{age - 1} \\times ( 1 - D)
                    + naive_{age - 1} \\times R
                ```

                ```math
                \\frac{d}{dt}(moderate_{age}) = 
                    - moderate_{age} 
                    + moderate_{age - 1} 
                    + radical_{age - 1} \\times D
                ```
                

                """,
                "title": "All",
                "vars": ["naive_total", "radical_total", "moderate_total"],
            },
            {"title": "Naive", "vars": self.pops.naive,},
            {"title": "Radical", "vars": self.pops.radical,},
            {"title": "Moderate", "vars": self.pops.moderate,},
        ]
        self.editable_params = [
            {"key": "time", "max": 500,},
            {"key": "nAge", "max": 50,},
        ]
        self.extract_editable_params()
