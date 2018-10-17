import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from sqldirect.connection import SQLDirectConnection, Statement
from sqldirect.errors import SQLDirectError

log = logging.getLogger("sqldirect")


class PostgreSQLStatement(Statement):
    def __init__(self, statement):
        super().__init__(
            statement,
            {
                'par': '%s',
                'return_id': "RETURNING id",
                'autoincrement': "SERIAL PRIMARY KEY NOT NULL"
            }
        )


class SQLDirectPostgreSQLConnection(SQLDirectConnection):
    def __init__(self, conn):
        super().__init__(
            psycopg2.connect(conn, cursor_factory=RealDictCursor) if isinstance(conn, str) else conn
        )
        if isinstance(conn, str):
            log.debug("Open connection to database")
        self._has_dict_cursor = isinstance(self.connection.cursor_factory, RealDictCursor)

    def db_type(self):
        return 'postgresql'

    def _statement_factory(self, statement):
        return PostgreSQLStatement(statement)

    def autocommit(self, state):
        self.connection.autocommit = state

    def cursor(self):
        if self._has_dict_cursor:
            return self.connection.cursor()
        else:
            return self.connection.cursor(cursor_factory=RealDictCursor)

    def tables(self, name_filter=None):
        if name_filter is None:
            return self.fetchall(
                "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema');",
                lambda r: r['table_name']
            )
        else:
            return self.fetchall(
                "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema') AND table_name LIKE {par};",
                lambda r: r['table_name'],
                name_filter
            )

    def drop_create_schema(self):
        clean_up_db = """DROP SCHEMA public CASCADE;
            CREATE SCHEMA public;
            GRANT ALL ON SCHEMA public TO postgres;
            GRANT ALL ON SCHEMA public TO public;
            COMMENT ON SCHEMA public IS 'standard public schema';"""
        self.execute(clean_up_db)

    def handle_exception(self, ex):
        try:
            raise ex #ugly!!!
        except psycopg2.Warning as sqlex:
            log.warning(str(sqlex))
            #do not raise sqlex here, it is just a warning, log is enough
        except psycopg2.Error as sqlex:
            log.exception(sqlex)
            raise SQLDirectError("Cannot execute query") from sqlex
        else:
            raise ex

    def get_last_id(self, cursor):
        try:
            cursor.execute('SELECT LASTVAL()')
            id = cursor.fetchone()['lastval']
            return id
        except psycopg2.Error as sqlex:
            raise SQLDirectError("Error during last row id retrival, using RETURNING id in SQL statement") from sqlex






