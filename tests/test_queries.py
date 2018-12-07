import unittest
import os
import logging
from dotenv import load_dotenv, find_dotenv

from sqldirect import SQLiteConnection as DbConnection
from sqldirect import SQLDirectError

class TestFetch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # use find_dotenv as argument to make it working on PyCharm and cmd line
        load_dotenv(find_dotenv())


    def setUp(self):
        self.conn = DbConnection(os.getenv("CONNECTION_STRING"))
        logging.disable(logging.CRITICAL)

    def test_fetchone_success(self):
        record = self.conn.fetchone("select 'a' as a, 1 as b")
        self.assertEqual({'a': 'a', 'b': 1}, record)

    def test_fetchone_wrong_sql(self):
        with self.assertRaises(SQLDirectError):
            reocord = self.conn.fetchone(
                "SELECT all your base are belong to us",
            )

    def test_fetchone_empty(self):
        record = self.conn.fetchone(
            "SELECT * FROM sqlite_master WHERE type='something that doesnt exist... hopefully!'",
        )
        self.assertEqual(record, None)

    def test_fetchmany_success(self):
        resultset = self.conn.fetchall(
            "SELECT 1 as id, 'a' as data UNION ALL SELECT 2 as id, 'b' as data UNION ALL SELECT 3 as id, 'c' as data",
        )
        self.assertEqual({'id': 1, 'data': 'a'}, resultset[0])
        self.assertEqual({'id': 2, 'data': 'b'}, resultset[1])
        self.assertEqual({'id': 3, 'data': 'c'}, resultset[2])

    def test_fetchmany_wrong_sql(self):
        with self.assertRaises(SQLDirectError):
            resultset = self.conn.fetchall(
                "SELECT all your base are belong to us",
            )

    def test_fetchmany_empty(self):
        resultset = self.conn.fetchall(
            "SELECT * FROM sqlite_master WHERE type='something that doesnt exist... hopefully!'",
        )
        self.assertEqual(resultset, [])

    def tearDown(self):
        logging.disable(logging.NOTSET)
        self.conn.close()


    @classmethod
    def tearDownClass(cls):
        pass

