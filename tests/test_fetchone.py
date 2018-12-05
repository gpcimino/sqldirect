import unittest
import os
import logging
import sys
from dotenv import load_dotenv

from sqldirect import SQLiteConnection


class TestFetchOne(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #look for .env files in the project (../.env)
        load_dotenv()


    def setUp(self):
        self.conn = SQLiteConnection(os.getenv("CONNECTION_STRING"))

    def test_dict(self):
        dictionary = self.conn.fetchone("select 'a' as a, 1 as b")
        self.assertEqual({'a': 'a', 'b': 1}, dictionary)


    def tearDown(self):
        self.conn.close()


    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
    unittest.main()
