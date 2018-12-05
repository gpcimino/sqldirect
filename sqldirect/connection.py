import logging
from sqldirect.type_map import Dictionary

log = logging.getLogger("sqldirect")


class Connection(object):
    def __init__(self, conn):
        self.conn = conn

    def close(self):
        self.conn.close()
        log.debug("Connection closed")

    def cursor(self):
        return self.conn.cursor()

    def fetchone(self, sql, mapper=Dictionary(), args=None):
        pass
