import sqlite3
import logging
from sqldirect.sqlite_statement import SQLLiteStatement
from sqldirect.errors import SQLDirectError
from sqldirect.connection import Connection
from sqldirect.type_map import Dictionary

log = logging.getLogger("sqldirect")


class SQLiteConnection(Connection):
    def __init__(self, conn):
        super().__init__(
            sqlite3.connect(conn) if isinstance(conn, str) else conn
        )
        self.conn.row_factory = sqlite3.Row

    def create_statement(self, sql):
        return SQLLiteStatement(sql)

    def fetchone(self, sql, mapper=Dictionary(), args=None):
        cursor = None
        try:
            return super().fetchone(sql, mapper=mapper, args=args)
        except sqlite3.Warning as sqlex:
            log.warning(str(sqlex))
            # do not raise sqlex here, it is just a warning, log is enough
        except (sqlite3.Error, sqlite3.DatabaseError) as sqlex:
            log.exception(sqlex)
            raise SQLDirectError(
                "Cannot execute query {} with args {}".format(
                    str(sql),
                    str(args)
                )
            ) from sqlex
        finally:
            log.debug("Close cursor")
            if cursor:
                cursor.close()

    def fetchall(self, sql, mapper=Dictionary(), args=None):
        cursor = None
        try:
            return super().fetchall(sql, mapper=mapper, args=args)
        except sqlite3.Warning as sqlex:
            log.warning(str(sqlex))
            # do not raise sqlex here, it is just a warning, log is enough
        except (sqlite3.Error, sqlite3.DatabaseError) as sqlex:
            log.exception(sqlex)
            raise SQLDirectError(
                "Cannot execute query {} with args {}".format(
                    str(sql),
                    str(args)
                )
            ) from sqlex
        finally:
            log.debug("Close cursor")
            if cursor:
                cursor.close()
