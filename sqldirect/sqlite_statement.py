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
