import unittest
from pathlib import Path
from dotenv import load_dotenv

from sqldirect.connection import SQLDirectConnection
from sqldirect.utils import find_connection


class TestReuseExistingDBbAPIConnection(unittest.TestCase):
    def setUp(self):
        self.conn = find_connection()
        self.smrt_conn = SQLDirectConnection.create(self.conn)
        self.hint = self.smrt_conn.db_type()
        print("Use {}".format(self.hint))

    def tearDown(self):
        # if self._db == "postgresql":
        #     self.smrt_conn.close()
        #     self.create_db()
        #     self.smrt_conn.autocommit(True)
        #     drop_create_schema(self.smrt_conn)
        self.smrt_conn.close()

    def test_dictionary(self):
        dictionary = self.smrt_conn.fetchone(
            "select 'a' as a, 1 as b",
            dict
        )
        self.assertEqual({'a': 'a', 'b': 1}, dictionary)





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