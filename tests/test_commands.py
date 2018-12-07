import unittest
import os
import logging
import sys
from dotenv import load_dotenv, find_dotenv

from sqldirect import SQLiteConnection as DbConnection
from sqldirect import Dictionary, String, Integer
from sqldirect import SQLDirectError

class TestCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # use find_dotenv as argument to make it working on PyCharm and cmd line
        load_dotenv(find_dotenv())

    def setUp(self):
        self.conn = DbConnection(os.getenv("CONNECTION_STRING"))
        logging.disable(logging.CRITICAL)

    def test_create_table(self):
        self.conn.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
        self.assertTrue(self.conn.table_exists('test'))

    def test_sql_script(self):
        s = """
                CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_test_data ON test (data);
                INSERT INTO test (num, data) VALUES (100, 'test data');
            """
        self.conn.execute(s)

        data_field = self.conn.fetchone(
            "SELECT data FROM test WHERE num=100;",
            String('data')
        )
        self.assertTrue('test data', data_field)

    def test_get_last_id(self):
        self.conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT, num integer, data varchar)")
        last_id = self.conn.execute(
            "INSERT INTO test (num, data) VALUES ({par}, {par})",
            [100, "abc def"],
            getlastid=True
        )
        self.assertTrue(1, last_id)

    def test_auto_increment(self):
        self.conn.execute("CREATE TABLE test (id {autoincrement}, num integer, data varchar)")
        self.conn.execute("INSERT INTO test (num, data) VALUES ({par}, {par})", args=[100, "abc'def"])
        self.conn.execute("INSERT INTO test (num, data) VALUES ({par}, {par})", args=[200, "abc'def"])
        id_field = self.conn.fetchone("SELECT id FROM test WHERE num=200", Integer('id'))
        self.assertTrue(2, id_field)

    def test_delete(self):
        self.conn.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar)")
        self.conn.execute(
            "INSERT INTO test (num, data) VALUES ({par}, {par}) {return_id}",
            args=[100, "abc'def"]
        )
        self.conn.execute("DELETE FROM test")
        self.assertEqual(0, self.conn.fetchone("SELECT COUNT(*) FROM test", Integer()))

    def test_delete_last_id(self):
        self.conn.execute(
            "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar)"
        )

        last_id = self.conn.execute(
            "INSERT INTO test (num, data) VALUES ({par}, {par}) {return_id}",
            args=[100, "abc'def"]
        )

        deleted_id = self.conn.execute(
            "DELETE FROM test WHERE num={par} {return_id}",
            args=[last_id]
        )

        self.assertTrue(100, deleted_id)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        self.conn.close()

    @classmethod
    def tearDownClass(cls):
        pass

