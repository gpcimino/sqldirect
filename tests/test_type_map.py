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

    def test_dictionary(self):
        self.assertEqual({'a': 'a', 'b': 1}, Dictionary().map({'a': 'a', 'b': 1}))

    def test_dictionary_mapping(self):
        d = Dictionary({'a': 'A', 'b': 'B'}).map({'a': 'a', 'b': 1})
        self.assertEqual({'A': 'a', 'B': 1}, d)
        self.assertFalse('a' in d)
        self.assertFalse('b' in d)

    def test_dictionary_partial_mapping(self):
        d = Dictionary({'a': 'A'}).map({'a': 'a', 'b': 1})
        self.assertEqual({'A': 'a', 'b': 1}, d)
        self.assertFalse('a' in d)

    def test_interger(self):
        i = Integer().map([10])
        self.assertEqual(i, 10)

    def test_interger_name(self):
        i = Integer('a').map({'b': 2, 'a': 1})
        self.assertEqual(i, 1)

    def test_string(self):
        s = String(['abc'])
        self.assertEqual(s, "abc")

    def test_string_name(self):
        s = String('a').map({'b': 1, 'a': 'abc'})
        self.assertEqual(s, 'abc')

    def test_float(self):
        f = Float().map([1.0])
        self.assertEqual(f, 1.0)

    def test_float_name(self):
        f = Float('a').map({'a': 1.0, 'b': 'b'})
        self.assertEqual(f, 1.0)

    def test_type(self):
        class Fake(object):
            def __init__(self, a, b):
                self.member_a = a
                self.member_b = b

        fake = Type(Fake).map({'a': 'a', 'b': 1})
        self.assertEqual(fake.member_a, 'a')
        self.assertEqual(fake.member_b, 1)

    def test_type_extra_field(self):
        class Fake(object):
            def __init__(self, a, b, c):
                self.member_a = a
                self.member_b = b
                self.member_c = c

        fake = Type(Fake, {'c': 100}).map({'a': 'a', 'b': 1})
        self.assertEqual(fake.member_a, 'a')
        self.assertEqual(fake.member_b, 1)
        self.assertEqual(fake.member_c, 100)

    def test_lambda(self):
        eleven = Function(lambda r: r['b'] + 10).map({'a': 'a', 'b': 1})
        self.assertEqual(11, eleven)

    def test_func(self):
        def mapper(record):
            return record['a'].upper()

        A = Function(mapper).map({'a': 'a', 'b': 1})
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

        c = Composite([
                Type(Fake1),
                Type(Fake2),
            ],
            relation=rel
        ).map({'a': 'a', 'b': 1})
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

        c = Composite([
                Type(Fake1),
                Dictionary(),
            ],
            relation=rel
        ).map({'a': 'a', 'b': 1})
        self.assertEqual(c.member_a, 'a')
        self.assertEqual(c.dictionary, {'a': 'a', 'b': 1})

    def test_polimorphic_type(self):
        class Fake1(object):
            def __init__(self, a):
                self.member_a = a

        class Fake2(object):
            def __init__(self, b):
                self.member_b = b

        t = Polymorphic(
            types=[
                Type(Fake1),
                Type(Fake2)
            ],
            type_switch='type_'
        ).map({'a': 'a', 'b': 1, 'type_': 'Fake1'})

        self.assertEqual(type(t), Fake1)
        self.assertEqual(t.member_a, 'a')

    def tearDown(self):
        self.conn.close()

    @classmethod
    def tearDownClass(cls):
        pass

