# import unittest
# from sqlite3 import Connection
#
# from sqldirect import fetchone_direct
#
# class TestFacade(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         pass
#
#
#     def test_sqlite(self):
#         conn = Connection(":memory:")
#         d = fetchone_direct(conn, "select 1 as i", dict)
#         self.assertEqual(d['i'], 1)
#
#
#     @classmethod
#     def setUpClass(cls):
#         pass
#
#     @classmethod
#     def tearDownClass(cls):
#         pass
#
#
# if __name__ == "__main__":
#     # import logging
#     # import sys
#     # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
#     unittest.main()