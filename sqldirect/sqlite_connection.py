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

    def fetchone(self, sql, mapper=Dictionary(), args=None):
        cursor = None
        args = [] if args is None else args
        sql = SQLLiteStatement(sql)
        try:
            log.debug("Open cursor")
            cursor = self.cursor()
            log.info("Execute SQL: %s . With args: %s", sql, args)
            cursor.execute(str(sql), args)
            record = cursor.fetchone()
            if record is None:
                return None
            return mapper.map(record)
        except sqlite3.Warning as sqlex:
            log.warning(str(sqlex))
            # do not raise sqlex here, it is just a warning, log is enough
        except sqlite3.Error as sqlex:
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
        args = [] if args is None else args
        sql = SQLLiteStatement(sql)
        try:
            log.debug("Open cursor")
            cursor = self.cursor()
            log.info("Execute SQL: %s . With args: %s", sql, args)
            cursor.execute(str(sql), args)
            return [mapper.map(r) for r in cursor.fetchall()]
        except sqlite3.Warning as sqlex:
            log.warning(str(sqlex))
            # do not raise sqlex here, it is just a warning, log is enough
        except sqlite3.Error as sqlex:
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
