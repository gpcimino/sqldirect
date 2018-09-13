import unittest
from pathlib import Path
from dotenv import load_dotenv

from sqldirect.connection import SQLDirectConnection
from sqldirect.utils import find_connection


class TestExecute(unittest.TestCase):
    def setUp(self):
        self.conn = find_connection()
        self.smrt_conn = SQLDirectConnection.create(self.conn)
        self.hint = self.smrt_conn.db_type()
        print("Use {}".format(self.hint))


    def tearDown(self):
        self.smrt_conn.execute("DROP TABLE test")
        self.smrt_conn.close()

    def test_create_table(self):
        self.smrt_conn.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
        self.assertTrue(self.smrt_conn.table_exists('test'))


    def test_insert(self):
        self.smrt_conn.execute(
            "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"
        )

        self.smrt_conn.execute(
            "INSERT INTO test (num, data) VALUES ({par}, {par});",
            100,
            "abc'def"
        )

        data_field = self.smrt_conn.fetchone(
            "SELECT data FROM test WHERE num=100;",
            lambda r: r['data']
        )

        self.assertTrue("abc'def", data_field)

    def test_insert_getlastid(self):
        self.smrt_conn.execute(
            "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"
        )

        last_id = self.smrt_conn.execute(
            "INSERT INTO test (num, data) VALUES ({par}, {par}) {return_id};",
            100,
            "abc'def"
        )

        self.assertTrue(100, last_id)

    def test_delete(self):
        self.smrt_conn.execute(
            "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"
        )

        last_id = self.smrt_conn.execute(
            "INSERT INTO test (num, data) VALUES ({par}, {par}) {return_id};",
            100,
            "abc'def"
        )

        deleted_id = self.smrt_conn.execute(
            "DELETE FROM test WHERE num={par} {return_id};",
            last_id
        )

        self.assertTrue(100, deleted_id)

    def test_execute_script(self):
        s = """
                CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_test_data ON test (data); 
                INSERT INTO test (num, data) VALUES (100, 'test data');
            """
        self.smrt_conn.execute(s)

        data_field = self.smrt_conn.fetchone(
            "SELECT data FROM test WHERE num=100;",
            lambda r: r['data']
        )

        self.assertTrue('test data', data_field)


    @classmethod
    def setUpClass(cls):
        load_dotenv(dotenv_path=Path('..') / 'db.env')

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == "__main__":
    # import logging
    # import sys
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
    unittest.main()