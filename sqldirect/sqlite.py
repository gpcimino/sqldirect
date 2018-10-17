import logging
import sqlite3

from sqldirect.connection import SQLDirectConnection, Statement
from sqldirect.errors import SQLDirectError


log = logging.getLogger("sqldirect")

def create_connection(connection):
    if isinstance(connection, str):
        connection = sqlite3.connect(connection)
    connection.row_factory = sqlite3.Row
    return SQLDirectSQLiteConnection(connection)

class SQLLiteStatement(Statement):
    def __init__(self, statement):
        super().__init__(
            statement,
            {
                'par': '?',
                'return_id': "",
                'autoincrement' : "INTEGER PRIMARY KEY AUTOINCREMENT"

            }
        )


class SQLDirectSQLiteConnection(SQLDirectConnection):
    def __init__(self, connection):
        super().__init__(
            sqlite3.connect(connection) if isinstance(connection, str) else connection
        )
        self.connection.row_factory = sqlite3.Row
        if isinstance(connection, str):
            log.debug("Open connection to database")

    def _statement_factory(self, statement):
        return SQLLiteStatement(statement)

    def db_type(self):
        return 'sqlite'

    def autocommit(self, state):
        if state:
            self.connection.isolation_level = None
        else:
            self.connection.isolation_level = ""

    def execute(self, sql, *args, getlastid=False):
        sql = self._statement(sql)
        #todo: count the number of semicolon to detect a multiple statement is wrong, but simple!
        #todo: should detect all the SQL keywords like SELECT, INSERT, CREATE, ALTER etc and count them
        if str(sql).count(";") > 1:
            if args is not None and len(args)>0:
                raise SQLDirectError("Cannot pass parameter to multiple SQL statement for SQLite database")
            return self._execute_script(sql)
        else:
            return super().execute(sql, *args, getlastid=getlastid)

    def _execute_script(self, sql):
        cursor = None
        sql = self._statement(sql)
        try:
            log.debug("Open cursor")
            cursor = self.cursor()
            log.info("Execute SQL: %s", sql)
            cursor.executescript(str(sql))
        except Exception as ex:
            raise ex
        finally:
            log.debug("Close cursor")
            if cursor:
                cursor.close()

    def tables(self, name_filter=None):
        if name_filter is None:
            return self.fetchall(
                "SELECT name FROM sqlite_master WHERE type='table' AND name <> 'sqlite_sequence' ORDER BY name;",
                lambda r: r['name'],
            )
        else:
            return self.fetchall(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE {par} AND name <> 'sqlite_sequence' ORDER BY name;",
                lambda r: r['name'],
                name_filter
            )

    def drop_create_schema(self):
        log.error("Cannot drop/craete schema in sqlite")



    def handle_exception(self, ex):
        try:
            raise ex #ugly!!!
        except sqlite3.Warning as sqlex:
            log.warning(str(sqlex))
            #do not raise sqlex here, it is just a warning, log is enough
        except sqlite3.Error as sqlex:
            log.exception(sqlex)
            raise SQLDirectError("Cannot execute query") from sqlex
        else:
            raise ex

    def get_last_id(self, cursor):
        try:
            id = cursor.lastrowid
            return id
        except sqlite3.Error as sqlex:
            raise SQLDirectError("Error during last row id retrival, using cursor.lastrowid") from sqlex
