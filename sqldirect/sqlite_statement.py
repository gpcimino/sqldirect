# pylint: disable-msg=R0903
# Too few public methods (1/2) (too-few-public-methods)

import logging
from sqldirect.statement import Statement


log = logging.getLogger("sqldirect")


class SQLLiteStatement(Statement):
    def __init__(self, statement):
        super().__init__(
            statement,
            {
                'par': '?',
                'return_id': "",
                'autoincrement': "INTEGER PRIMARY KEY AUTOINCREMENT"

            }
        )
