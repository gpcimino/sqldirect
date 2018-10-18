import unittest
from pathlib import Path
from dotenv import load_dotenv

from sqldirect.connection import SQLDirectConnection
from sqldirect.utils import find_connection

from sqldirect.types import Function, Dictionary, Object


class TestFetchOne(unittest.TestCase):
    def setUp(self):
        self.conn = find_connection()
        self.smrt_conn = SQLDirectConnection.create(self.conn)
        self.hint = self.smrt_conn.db_type()
        print("Use {}".format(self.hint))

    def tearDown(self):
        self.smrt_conn.close()


    def test_dictionary(self):
        dictionary = self.smrt_conn.fetchone("select 'a' as a, 1 as b", Dictionary())
        self.assertEqual({'a': 'a', 'b': 1}, dictionary)

    def test_multiple_dictionary(self):
        def merge(t1, t2):
            t1['nested']=t2
            return t1

        dictionary = self.smrt_conn.fetchone("select 'a' as a, 1 as b", [dict, dict], merge=merge)
        self.assertEqual({'a': 'a', 'b': 1, 'nested': {'a': 'a', 'b': 1}}, dictionary)

    def test_lambda(self):
        eleven = self.smrt_conn.fetchone("select 'a' as a, 1 as b", Function(lambda r: r['b'] + 10))
        self.assertEqual(11, eleven)

    def test_func(self):
        def mapper(record):
            return record['a'].upper()

        A = self.smrt_conn.fetchone("select 'a' as a, 1 as b", Function(mapper))
        self.assertEqual('A', A)

    def test_map_to_obj(self):
        class Fake(object):
            def __init__(self, a, b):
                self.member_a = a
                self.member_b = b

        fake = self.smrt_conn.fetchone("select 'a' as a, 1 as b", Object(Fake))
        self.assertEqual(fake.member_a, 'a')
        self.assertEqual(fake.member_b, 1)

    def test_args(self):
        dictionary = self.smrt_conn.fetchone(
            "select * from (select 1 as id union all select 2 as id union all select 3 as id) as X where id = {par}",
            Dictionary(),
            2
        )
        self.assertEqual({'id': 2}, dictionary)

    def test_lower_upper_case(self):
        if self.hint != 'postgresql':
            raise unittest.SkipTest("Skiped because is not postgresql, only postgresql mess up with string case")
        #if field name is between double quotes case is kept as-is, otherwise is forced to lower case
        #note this is a feature of postgresql, see: https://www.postgresql.org/docs/current/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
        dictionary = self.smrt_conn.fetchone(
            'select 1 as "DATA", 2 as Number',
            Dictionary()
        )
        self.assertEqual({'DATA': 1, 'number': 2}, dictionary)


    def test_polymorphic_object(self):
        class Fake1(object):
            def __init__(self, a, b):
                self.member_a = a
                self.member_b = b

        class Fake2(object):
            def __init__(self, c):
                self.member_c = c

        fake1 = self.smrt_conn.fetchone(
            "select 'a' as a, 1 as b, 100 as c, 'Fake1' as type",
            [Fake1, Fake2],
            switch='type'
        )
        self.assertEqual(fake1.member_a, 'a')
        self.assertEqual(fake1.member_b, 1)

    def test_polymorphic_object2(self):
        class Fake1(object):
            def __init__(self, a, b):
                self.member_a = a
                self.member_b = b

        class Fake2(object):
            def __init__(self, c):
                self.member_c = c

        fake2 = self.smrt_conn.fetchone(
            "select 'a' as a, 1 as b, 100 as c, 'Fake2' as type",
            [Fake1, Fake2],
            switch='type'
        )
        self.assertEqual(fake2.member_c, 100)


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