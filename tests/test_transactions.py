import unittest
from pathlib import Path
from dotenv import load_dotenv
import logging

from sqldirect.connection import SQLDirectConnection
from sqldirect.utils import find_connection



class TestAutoCommmit(unittest.TestCase):
    def setUp(self):
        #disable all logging calls with levels less severe than or equal to CRITICAL
        #this is useful to avoid stack trace print on unittest output when assertRaise is used
        #
        #todo: use self.assertLog("what ever should be in the log") instaed of diable the logger

        logging.disable(logging.CRITICAL)
        self.open_connection()

    def open_connection(self):
        self.conn = find_connection()
        self.smrt_conn = SQLDirectConnection.create(self.conn)
        self.hint = self.smrt_conn.db_type()
        print("Use {}".format(self.hint))


    def tearDown(self):
        self.smrt_conn.close()

    def test_autocommit_write_data(self):
        self.smrt_conn.autocommit(True)
        self.smrt_conn.execute("DROP TABLE IF EXISTS test")
        self.smrt_conn.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
        self.smrt_conn.execute("INSERT INTO test (num, data) VALUES ({par}, {par});", 100, "abc'def")
        data_field = self.smrt_conn.fetchone("SELECT data FROM test WHERE num=100;",lambda r: r['data'])
        self.assertTrue("abc'def", data_field)
        self.smrt_conn.execute("DROP TABLE test")


    def test_dont_commit_and_lose(self):
        if self.hint == 'sqlite':
            raise unittest.SkipTest("Do not test transaction on sqlite memory db")


        self.smrt_conn.autocommit(False)
        self.smrt_conn.execute("DROP TABLE IF EXISTS test")
        self.smrt_conn.commit()
        self.smrt_conn.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
        self.smrt_conn.execute("INSERT INTO test (num, data) VALUES ({par}, {par});", 100, "abc'def")
        self.smrt_conn.close()

        self.open_connection()
        #sqlite: sqlite3.OperationalError
        #postgresql: psycopg2.ProgrammingError
        with self.assertRaises(Exception):
            data_field = self.smrt_conn.fetchone("SELECT data FROM test WHERE num=100;", lambda r: r['data'])


    def test_commit_write_data(self):
        if self.hint == 'sqlite':
            raise unittest.SkipTest("Do not test transaction on sqlite memory db")

        self.smrt_conn.autocommit(False)
        self.smrt_conn.execute("DROP TABLE IF EXISTS test")
        self.smrt_conn.commit()
        self.smrt_conn.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
        self.smrt_conn.execute("INSERT INTO test (num, data) VALUES ({par}, {par});", 100, "abc'def")
        self.smrt_conn.commit()
        self.smrt_conn.close()

        self.open_connection()
        data_field = self.smrt_conn.fetchone("SELECT data FROM test WHERE num=100;",lambda r: r['data'])
        self.assertTrue("abc'def", data_field)
        self.smrt_conn.execute("DROP TABLE test")

    def test_rollback_doesnt_write_data(self):
        if self.hint == 'sqlite':
            raise unittest.SkipTest("Do not test transaction on sqlite memory db")

        self.smrt_conn.autocommit(False)
        self.smrt_conn.execute("DROP TABLE IF EXISTS test")
        self.smrt_conn.commit()
        self.smrt_conn.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
        self.smrt_conn.execute("INSERT INTO test (num, data) VALUES ({par}, {par});", 100, "abc'def")
        self.smrt_conn.rollback()
        self.smrt_conn.close()

        self.open_connection()
        #sqlite: sqlite3.OperationalError
        #postgresql: psycopg2.ProgrammingError
        with self.assertRaises(Exception):
            data_field = self.smrt_conn.fetchone("SELECT data FROM test WHERE num=100;",lambda r: r['data'])


    def test_begin_trans_without_commit(self):
        self.smrt_conn.autocommit(False)
        self.smrt_conn.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
        self.smrt_conn.close()

        self.open_connection()
        self.assertFalse(self.smrt_conn.table_exists('test'))

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