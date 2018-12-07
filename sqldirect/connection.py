import logging
from sqldirect.type_map import Dictionary

log = logging.getLogger("sqldirect")


class Connection():
    def __init__(self, conn):
        self.conn = conn

    def close(self):
        self.conn.close()
        log.debug("Connection closed")

    def cursor(self):
        return self.conn.cursor()

    def create_statement(self, sql):
        raise NotImplementedError()

    def fetchone(self, sql, mapper=Dictionary(), args=None):
        args = [] if args is None else args
        sql = self.create_statement(sql)
        log.debug("Open cursor")
        cursor = self.cursor()
        log.info("Execute SQL: %s . With args: %s", sql, args)
        cursor.execute(str(sql), args)
        record = cursor.fetchone()
        if record is None:
            return None
        return mapper.map(record)


    def fetchall(self, sql, mapper=Dictionary(), args=None):
        args = [] if args is None else args
        sql = self.create_statement(sql)
        log.debug("Open cursor")
        cursor = self.cursor()
        log.info("Execute SQL: %s . With args: %s", sql, args)
        cursor.execute(str(sql), args)
        return [mapper.map(r) for r in cursor.fetchall()]
