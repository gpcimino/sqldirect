import logging

from sqldirect.errors import SQLDirectError

log = logging.getLogger("sqldirect")

class ConnectionFactory(object):

    def __init__(self, connection, hint=None):
        self.connection = connection
        self.hint = hint

    def create(self):
        if self.hint is None:
            if isinstance(self.connection, str):
                self.hint = self.guess_conn_str()
            else:
                self.hint = self.guess_conn()
        if self.hint == 'postgresql':
            #todo: make import dynamic to avoid dependencies with sub classes (eg postgresql, sqlite)
            from sqldirect.postgresql import SQLDirectPostgreSQLConnection
            return SQLDirectPostgreSQLConnection(self.connection)
        elif self.hint == 'sqlite':
            from sqldirect.sqlite import SQLDirectSQLiteConnection
            return SQLDirectSQLiteConnection(self.connection)
        else:
            raise SQLDirectError("Cannot figure out hit %s for create db connection", self.hint)

    def guess_conn_str(self):
        if isinstance(self.connection, str):
            if "postgres" in self.connection:
                return "postgresql"
            else:
                return "sqlite"

    def guess_conn(self):
        #todo: use some other way to detect if is postgresql; this is bad, if any other db-api driver for postgresql will be used this if will fail
        if 'psycopg' in type(self.connection).__module__:
            return 'postgresql'
        elif 'sqlite' in type(self.connection).__module__:
                return 'sqlite'
        else:
            raise Exception("cannot guess db type from conn string")
