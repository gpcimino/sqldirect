import unittest
from pathlib import Path
from dotenv import load_dotenv
import logging
import sys

from sqldirect.connection import SQLDirectConnection
from sqldirect.utils import find_connection
from sqldirect.errors import SQLDirectError


class TestError(unittest.TestCase):
    def setUp(self):
        #disable all logging calls with levels less severe than or equal to CRITICAL
        #this is useful to avoid stack trace print on unittest output when assertRaise is used
        #
        #todo: use self.assertLog("what ever should be in the log") instaed of diable the logger

        logging.disable(logging.CRITICAL)
        self.conn = find_connection()
        self.smrt_conn = SQLDirectConnection.create(self.conn)
        self.hint = self.smrt_conn.db_type()
        print("Use {}".format(self.hint))

    def tearDown(self):
        self.smrt_conn.close()
        #enable the logger again
        logging.disable(logging.NOTSET)


    def test_sql_sysntax_error(self):
        with self.assertRaises(SQLDirectError):
            dictionary = self.smrt_conn.fetchone("all your base are belong to us", dict)




    @classmethod
    def setUpClass(cls):
        #look for .env files in the project (../.env)
        load_dotenv()

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == "__main__":
    unittest.main()