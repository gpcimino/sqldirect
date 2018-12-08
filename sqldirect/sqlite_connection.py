import sqlite3
import logging
from functools import wraps

from sqldirect.sqlite_statement import SQLLiteStatement
from sqldirect.errors import SQLDirectError
from sqldirect.connection import Connection
from sqldirect.type_map import Dictionary, String

log = logging.getLogger("sqldirect")

def exceptionshandling(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except sqlite3.Warning as sqlex:
            log.warning(str(sqlex))
            # do not raise sqlex here, it is just a warning so log is enough
        except (sqlite3.Error, sqlite3.DatabaseError) as sqlex:
            log.exception(sqlex)
            raise SQLDirectError(
                "Cannot execute query {} with args {}".format(
                    str(args[1]),
                    str(kwargs['args']) if 'args' in kwargs else '()'
                )
            ) from sqlex
        return result
    return wrapper


class SQLiteConnection(Connection):
    def __init__(self, conn):
        super().__init__(
            sqlite3.connect(conn) if isinstance(conn, str) else conn
        )
        self.conn.row_factory = sqlite3.Row

    def _create_statement(self, sql):
        return SQLLiteStatement(sql)

    @exceptionshandling
    def fetchone(self, sql, mapper=Dictionary(), args=None):
        return super().fetchone(sql, mapper=mapper, args=args)

    @exceptionshandling
    def fetchall(self, sql, mapper=Dictionary(), args=None):
        return super().fetchall(sql, mapper=mapper, args=args)

    @exceptionshandling
    def execute(self, sql, args=None, getlastid=False):
        # todo: make more robust
        if ";" in sql:
            if args is not None:
                raise SQLDirectError("Cannot execute SQL script with multiple statements and parameters")
            return self._executescript(sql, getlastid=getlastid)
        return super().execute(sql, args=args, getlastid=getlastid)

    @exceptionshandling
    def _executescript(self, sql, getlastid=False):
        sql = self._create_statement(sql)
        cursor = self._cursor()
        log.info("Execute SQL command: %s", sql)
        cursor.executescript(str(sql))
        if getlastid:
            return self.get_last_id(cursor)
        return None

    def get_last_id(self, cursor):
        try:
            return cursor.lastrowid
        except sqlite3.Error as sqlex:
            raise SQLDirectError(
                "Error during last row id retrival, using cursor.lastrowid"
            ) from sqlex

    def tables(self, name_filter=None):
        if name_filter is None:
            return self.fetchall(
                "SELECT name FROM sqlite_master WHERE type='table' AND name <> 'sqlite_sequence' ORDER BY name;",
                String('name'),
            )
        return self.fetchall(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE {par} AND name <> 'sqlite_sequence' ORDER BY name;",
            String('name'),
            args=[name_filter]
        )