import unittest
import os
import logging
import sys
from dotenv import load_dotenv, find_dotenv

from sqldirect import SQLiteConnection, Dictionary


class TestFetchOne(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # use find_dotenv as argument to make it working on PyCharm and cmd line
        load_dotenv(find_dotenv())

    def setUp(self):
        self.conn = SQLiteConnection(os.getenv("CONNECTION_STRING"))

    def test_dict(self):
        dictionary = self.conn.fetchone("select 'a' as a, 1 as b")
        self.assertEqual({'a': 'a', 'b': 1}, dictionary)

    def test_dict_mapping(self):
        dictionary = self.conn.fetchone("select 'a' as a, 1 as b", Dictionary({'a': 'A', 'b': 'B'}))
        self.assertEqual({'A': 'a', 'B': 1}, dictionary)
        self.assertFalse('a' in dictionary)
        self.assertFalse('b' in dictionary)

    def test_dict_partial_mapping(self):
        dictionary = self.conn.fetchone("select 'a' as a, 1 as b", Dictionary({'a': 'A'}))
        self.assertEqual({'A': 'a', 'b': 1}, dictionary)
        self.assertFalse('a' in dictionary)


    def tearDown(self):
        self.conn.close()


    @classmethod
    def tearDownClass(cls):
        pass

#
# if __name__ == "__main__":
#     logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
#     unittest.main()
