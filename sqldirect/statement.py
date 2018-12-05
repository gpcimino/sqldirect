class Statement(object):
    def __init__(self, statement, params):
        self.statement = statement
        self._params = params

    def inject(self):
        return self.statement.format(**self._params)

    def __str__(self):
        return self.inject()

    def __repr__(self):
        self._str__()
