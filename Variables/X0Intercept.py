from Variables.Variable import Variable


class X0Intercept(Variable):
    def __init__(self):
        super().__init__("Constant")

    def get_covariate(self, node, current_date, nonadopted):
        #print("X0 Finished")
        return 1