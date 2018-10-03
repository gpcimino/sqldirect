import logging

from sqldirect.connection_factory import ConnectionFactory
from sqldirect.errors import SQLDirectError
from sqldirect.types import record_factory

log = logging.getLogger("sqldirect")

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


class SQLDirectConnection(object):

    @staticmethod
    def create(connection, hint=None):
        return ConnectionFactory(connection, hint).create()

    def __init__(self, conn):
        self.connection = conn

    def _statement(self, statement):
        if issubclass(type(statement), Statement):
            return statement
        if isinstance(statement, str):
            return self._statement_factory(statement)
        #elif isinstance(statement, registry):
        else:
            raise SQLDirectError("Unknown statement type")

    def _statement_factory(self, statement):
        pass

    def close(self):
        self.connection.close()

    def cursor(self):
        return self.connection.cursor()

    def autocommit(self, state):
        pass

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def fetchone(self, sql, types, *args, merge=None, switch=None):
        #smart_record = record_factory(types, merge, switch)
        smart_record = types
        sql = self._statement(sql)
        try:
            log.debug("Open cursor")
            cursor = self.cursor()
            log.info("Execute SQL: %s . With args: %s", sql, args)
            cursor.execute(str(sql), args)
            #[x for x in cursor.execute("PRAGMA database_list").fetchall()[0]]
            record = cursor.fetchone()
            if record is None:
                return None
            return smart_record.map(record)
        except Exception as ex:
            self.handle_exception(ex)
        finally:
            log.debug("Close cursor")
            if cursor:
                cursor.close()

    def fetchall(self, sql, types, *args, merge=None, switch=None):
        #smart_record = record_factory(types, merge, switch)
        smart_record = types
        sql = self._statement(sql)
        try:
            log.debug("Open cursor")
            cursor = self.cursor()
            log.info("Execute SQL: %s . With args: %s", sql, args)
            cursor.execute(str(sql), args)
            return [smart_record.map(r) for r in cursor.fetchall()]
        except Exception as ex:
            self.handle_exception(ex)
        finally:
            log.debug("Close cursor")
            if cursor:
                cursor.close()

    def execute(self, sql, *args, getlastid=False):
        id = None
        sql = self._statement(sql)
        try:
            log.debug("Open cursor")
            cursor = self.cursor()
            log.info("Execute SQL: %s . With args: %s", sql, args)
            cursor.execute(str(sql), args)
            if getlastid:
                id = self.get_last_id(cursor)
        except Exception as ex:
            self.handle_exception(ex)
        finally:
            log.debug("Close cursor")
            if cursor:
                cursor.close()
        return id

    def db_type(self):
        pass

    def tables(self):
        pass

    def table_exists(self, table_name):
        return table_name in self.tables()

    def drop_create_schema(self):
        pass

    def handle_exception(self, ex):
        pass

    def get_last_id(self, cursor):
        pass
