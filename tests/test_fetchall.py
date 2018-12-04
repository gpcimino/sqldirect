import unittest
from pathlib import Path
from dotenv import load_dotenv

from sqldirect.connection import SQLDirectConnection
from sqldirect.utils import find_connection
from sqldirect.types import Function, Dictionary, Object

class TestFetchAll(unittest.TestCase):
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
        resultset = self.smrt_conn.fetchall(
            "SELECT 1 as id, 'a' as data UNION ALL SELECT 2 as id, 'b' as data UNION ALL SELECT 3 as id, 'c' as data",
            Dictionary()
        )
        self.assertEqual({'id': 1, 'data': 'a'}, resultset[0])
        self.assertEqual({'id': 2, 'data': 'b'}, resultset[1])
        self.assertEqual({'id': 3, 'data': 'c'}, resultset[2])

    @unittest.skip("Need to work on the aggregations")
    def test_multiple_dictionary(self):
        def merge(t1, t2):
            t1['nested']=t2
            return t1

        resultset = self.smrt_conn.fetchall(
            "SELECT 1 as id, 'a' as data UNION ALL SELECT 2 as id, 'b' as data UNION ALL SELECT 3 as id, 'c' as data",
            [dict, dict],
            merge=merge
        )
        self.assertEqual({'id': 1, 'data': 'a', 'nested': {'id': 1, 'data': 'a'}}, resultset[0])
        self.assertEqual({'id': 2, 'data': 'b', 'nested': {'id': 2, 'data': 'b'}}, resultset[1])
        self.assertEqual({'id': 3, 'data': 'c', 'nested': {'id': 3, 'data': 'c'}}, resultset[2])

    def test_lambda(self):
        resultset = self.smrt_conn.fetchall(
            "SELECT 1 as id, 'a' as data UNION ALL SELECT 2 as id, 'b' as data UNION ALL SELECT 3 as id, 'c' as data",
            Function(lambda r: r['id'] + 10)
        )
        self.assertEqual(11, resultset[0])
        self.assertEqual(12, resultset[1])
        self.assertEqual(13, resultset[2])

    def test_func(self):
        def mapper(record):
            return record['data'].upper()

        resultset = self.smrt_conn.fetchall(
            "SELECT 1 as id, 'a' as data UNION ALL SELECT 2 as id, 'b' as data UNION ALL SELECT 3 as id, 'c' as data",
            Function(mapper)
        )
        self.assertEqual("A", resultset[0])
        self.assertEqual("B", resultset[1])
        self.assertEqual("C", resultset[2])

    def test_map_to_obj(self):
        class Fake(object):
            def __init__(self, id, data):
                self._id = id
                self._data = data

        resultset = self.smrt_conn.fetchall(
            "SELECT 1 as id, 'a' as data UNION ALL SELECT 2 as id, 'b' as data UNION ALL SELECT 3 as id, 'c' as data",
            Object(Fake)
        )
        self.assertEqual(1, resultset[0]._id)
        self.assertEqual(2, resultset[1]._id)
        self.assertEqual(3, resultset[2]._id)

    def test_args(self):
        resultset = self.smrt_conn.fetchall(
            "select * from (select 1 as id union all select 2 union all select 3) as X where id > {par}",
            Dictionary(),
            1
        )
        self.assertEqual({'id': 2}, resultset[0])
        self.assertEqual({'id': 3}, resultset[1])

    @unittest.skip("Need to work on the aggregations")
    def test_polymorphic_object(self):
        class Fake1(object):
            def __init__(self, a, b):
                self.member_a = a
                self.member_b = b

        class Fake2(object):
            def __init__(self, c):
                self.member_c = c

        resultset = self.smrt_conn.fetchall(
            "SELECT 'a' AS a, 1 AS b, 100 AS c, 'Fake1' AS type UNION ALL SELECT 'b' AS a, 2 AS b, 200 AS c, 'Fake2' AS type",
            [Fake1, Fake2],
            switch='type'
        )
        self.assertEqual(resultset[0].member_a, 'a')
        self.assertEqual(resultset[0].member_b, 1)
        self.assertEqual(resultset[1].member_c, 200)


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