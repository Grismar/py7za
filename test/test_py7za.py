import unittest
from py7za import Py7za
from os import chdir
from pathlib import Path

chdir(Path(__file__).parent)


class TestConfig(unittest.TestCase):
    def test_init(self):
        p = Py7za(r'a test.csv "C:\Some folder\test.zip" -mx0 "-pPass \"with\" quotes"')
        self.assertEqual(p.arguments,
                         ['a', 'test.csv', r'C:\Some folder\test.zip', '-mx0', '-pPass "with" quotes',
                          '-bsp1', '-bso1', '-bb'],
                         msg='options are correctly unpacked, unquoted and defaults are added')
