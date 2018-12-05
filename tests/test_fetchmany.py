import unittest
import os
import logging
import sys
from dotenv import load_dotenv, find_dotenv

from sqldirect import SQLiteConnection as DbConnection
from sqldirect import Dictionary

class TestFetchMany(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # use find_dotenv as argument to make it working on PyCharm and cmd line
        load_dotenv(find_dotenv())


    def setUp(self):
        self.conn = DbConnection(os.getenv("CONNECTION_STRING"))

    def test_dict(self):
        resultset = self.conn.fetchall(
            "SELECT 1 as id, 'a' as data UNION ALL SELECT 2 as id, 'b' as data UNION ALL SELECT 3 as id, 'c' as data",
        )
        self.assertEqual({'id': 1, 'data': 'a'}, resultset[0])
        self.assertEqual({'id': 2, 'data': 'b'}, resultset[1])
        self.assertEqual({'id': 3, 'data': 'c'}, resultset[2])


    def tearDown(self):
        self.conn.close()


    @classmethod
    def tearDownClass(cls):
        pass

#
# if __name__ == "__main__":
#     logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
#     unittest.main()
