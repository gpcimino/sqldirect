# pylint: disable-msg=R0903
# Too few public methods (1/2) (too-few-public-methods)

class Statement():
    def __init__(self, statement, params):
        self.statement = statement
        self._params = params

    def inject(self):
        return self.statement.format(**self._params)

    def __str__(self):
        return self.inject()

    def __repr__(self):
        self.__str__()
