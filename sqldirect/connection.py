import logging
from sqldirect.type_map import Dictionary

log = logging.getLogger("sqldirect")


class Connection():
    def __init__(self, conn):
        self.conn = conn

    def close(self):
        self.conn.close()
        log.debug("Connection closed")

    def _cursor(self):
        log.debug("Open cursor")
        return self.conn.cursor()

    def prepare(self, args, sql):
        args = [] if args is None else args
        sql = self._create_statement(sql)
        return self._cursor(), sql, args

    def _create_statement(self, sql):
        raise NotImplementedError()

    def get_last_id(self, cursor):
        raise NotImplementedError()

    def fetchone(self, sql, mapper=Dictionary(), args=None):
        cursor, sql, args = self.prepare(args, sql)
        log.info("Execute SQL query: %s . With args: %s", sql, args)
        cursor.execute(str(sql), args)
        record = cursor.fetchone()
        if record is None:
            return None
        return mapper.map(record)

    def fetchall(self, sql, mapper=Dictionary(), args=None):
        cursor, sql, args = self.prepare(args, sql)
        log.info("Execute SQL query: %s . With args: %s", sql, args)
        cursor.execute(str(sql), args)
        return [mapper.map(r) for r in cursor.fetchall()]

    def execute(self, sql, args=None, getlastid=False):
        cursor, sql, args = self.prepare(args, sql)
        log.info("Execute SQL command: %s . With args: %s", sql, args)
        cursor.execute(str(sql), args)
        if getlastid:
            return self.get_last_id(cursor)
        return None

    def tables(self, name_filter=None):
        raise NotImplementedError()

    def table_exists(self, table_name):
        return table_name in self.tables()
