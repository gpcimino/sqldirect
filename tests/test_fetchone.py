import unittest
import os
import logging
import sys
from dotenv import load_dotenv, find_dotenv

from sqldirect import SQLiteConnection
from sqldirect import Dictionary, Integer, String
from sqldirect import Float, Type, Function, Composite, Polymorphic


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

    def test_interger(self):
        i = self.conn.fetchone("SELECT 1", Integer())
        self.assertEqual(i, 1)

    def test_interger_name(self):
        i = self.conn.fetchone("SELECT 1 as a, 'b' as b", Integer('a'))
        self.assertEqual(i, 1)

    def test_string(self):
        s = self.conn.fetchone("SELECT 'abc'", String())
        self.assertEqual(s, "abc")

    def test_string_name(self):
        s = self.conn.fetchone("SELECT 'abc' as a, 'b' as b", String('a'))
        self.assertEqual(s, 'abc')

    def test_float(self):
        f = self.conn.fetchone("SELECT 1.0", Float())
        self.assertEqual(f, 1.0)

    def test_float_name(self):
        f = self.conn.fetchone("SELECT 1.0 as a, 'b' as b", Float('a'))
        self.assertEqual(f, 1.0)

    def test_type(self):
        class Fake(object):
            def __init__(self, a, b):
                self.member_a = a
                self.member_b = b

        fake = self.conn.fetchone("select 'a' as a, 1 as b", Type(Fake))
        self.assertEqual(fake.member_a, 'a')
        self.assertEqual(fake.member_b, 1)

    def test_type_extra_field(self):
        class Fake(object):
            def __init__(self, a, b, c):
                self.member_a = a
                self.member_b = b
                self.member_c = c

        fake = self.conn.fetchone("select 'a' as a, 1 as b", Type(Fake, {'c': 100}))
        self.assertEqual(fake.member_a, 'a')
        self.assertEqual(fake.member_b, 1)
        self.assertEqual(fake.member_c, 100)

    def test_lambda(self):
        eleven = self.conn.fetchone("select 'a' as a, 1 as b", Function(lambda r: r['b'] + 10))
        self.assertEqual(11, eleven)

    def test_func(self):
        def mapper(record):
            return record['a'].upper()

        A = self.conn.fetchone("select 'a' as a, 1 as b", Function(mapper))
        self.assertEqual('A', A)

    def test_composite(self):
        class Fake1(object):
            def __init__(self, a):
                self.member_a = a
                self.fake2 = None

        class Fake2(object):
            def __init__(self, b):
                self.member_b = b

        def rel(f1, f2):
            f1.fake2 = f2
            return f1

        c = self.conn.fetchone(
            "select 'a' as a, 1 as b",
            Composite([
                    Type(Fake1),
                    Type(Fake2),
                ],
                relation=rel
            ),

        )
        self.assertEqual(c.member_a, 'a')
        self.assertEqual(c.fake2.member_b, 1)

    def test_composite_type_dict(self):
        class Fake1(object):
            def __init__(self, a):
                self.member_a = a
                self.dictionary = None

        def rel(f1, d):
            f1.dictionary = d
            return f1

        c = self.conn.fetchone(
            "select 'a' as a, 1 as b",
            Composite([
                    Type(Fake1),
                    Dictionary(),
                ],
                relation=rel
            ),
        )
        self.assertEqual(c.member_a, 'a')
        self.assertEqual(c.dictionary, {'a': 'a', 'b': 1})

    def test_polimorphic_type(self):
        class Fake1(object):
            def __init__(self, a):
                self.member_a = a

        class Fake2(object):
            def __init__(self, b):
                self.member_b = b

        t = self.conn.fetchone(
            "select 'a' as a, 1 as b, 'Fake1' as type_",
            Polymorphic(
                types=[
                    Type(Fake1),
                    Type(Fake2)
                ],
                type_switch='type_'
            )
        )
        self.assertEqual(type(t), Fake1)
        self.assertEqual(t.member_a, 'a')

    def tearDown(self):
        self.conn.close()

    @classmethod
    def tearDownClass(cls):
        pass

