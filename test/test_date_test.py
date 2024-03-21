import unittest
from py7za._date_test import create_date_test, ExpressionError
from datetime import datetime


class TestDateTest(unittest.TestCase):
    def test_create_date_test_day(self):
        f = create_date_test('2020-01-01')
        self.assertTrue(f(datetime(2020, 1, 1)))
        self.assertTrue(f(datetime(2020, 1, 1, 12, 34)))
        self.assertFalse(f(datetime(2019, 12, 31)))
        self.assertFalse(f(datetime(2020, 1, 2)))

    def test_create_date_test_month(self):
        f = create_date_test('2020-02')
        self.assertTrue(f(datetime(2020, 2, 1)))
        self.assertTrue(f(datetime(2020, 2, 29)))
        self.assertTrue(f(datetime(2020, 2, 8, 12, 34)))
        self.assertFalse(f(datetime(2020, 1, 31)))
        self.assertFalse(f(datetime(2020, 3, 1)))

    def test_create_date_test_year(self):
        f = create_date_test('2020')
        self.assertTrue(f(datetime(2020, 1, 1)))
        self.assertTrue(f(datetime(2020, 12, 31)))
        self.assertTrue(f(datetime(2020, 8, 29, 12, 34)))
        self.assertFalse(f(datetime(2021, 1, 1)))
        self.assertFalse(f(datetime(2019, 12, 31)))

    def test_create_date_test_time(self):
        f = create_date_test('2020-01-01 12:34')
        self.assertTrue(f(datetime(2020, 1, 1, 12, 34)))
        self.assertTrue(f(datetime(2020, 1, 1, 12, 34, 0)))
        self.assertTrue(f(datetime(2020, 1, 1, 12, 34, 59)))
        self.assertFalse(f(datetime(2020, 1, 1, 12, 35, 0)))
        self.assertFalse(f(datetime(2020, 1, 1, 12, 33, 59)))
        self.assertFalse(f(datetime(2020, 1, 2, 12, 34)))

    def test_create_date_test_prefix(self):
        f = create_date_test('before 2020')
        self.assertTrue(f(datetime(2019, 12, 31, 23, 59, 59)))
        self.assertFalse(f(datetime(2020, 1, 1)))
        f = create_date_test('< 2020')
        self.assertTrue(f(datetime(2019, 12, 31, 23, 59, 59)))
        self.assertFalse(f(datetime(2020, 1, 1)))

        f = create_date_test('after 2020')
        self.assertTrue(f(datetime(2021, 1, 1)))
        self.assertFalse(f(datetime(2020, 12, 31, 23, 59, 59)))
        f = create_date_test('> 2020')
        self.assertTrue(f(datetime(2021, 1, 1)))
        self.assertFalse(f(datetime(2020, 12, 31, 23, 59, 59)))

        f = create_date_test('in or after 2020')
        self.assertTrue(f(datetime(2021, 1, 1)))
        self.assertTrue(f(datetime(2020, 1, 1)))
        self.assertFalse(f(datetime(2019, 12, 31, 23, 59, 59)))
        f = create_date_test('>= 2020')
        self.assertTrue(f(datetime(2021, 1, 1)))
        self.assertTrue(f(datetime(2020, 1, 1)))
        self.assertFalse(f(datetime(2019, 12, 31, 23, 59, 59)))

        f = create_date_test('in or before 2020')
        self.assertTrue(f(datetime(2019, 1, 1)))
        self.assertTrue(f(datetime(2020, 1, 1)))
        self.assertFalse(f(datetime(2021, 1, 1)))
        f = create_date_test('<= 2020')
        self.assertTrue(f(datetime(2019, 1, 1)))
        self.assertTrue(f(datetime(2020, 1, 1)))
        self.assertFalse(f(datetime(2021, 1, 1)))

    def test_create_date_test_logic(self):
        f = create_date_test('before 2020-01-01 or on or after 2022-01-01')
        self.assertTrue(f(datetime(2019, 1, 1)))
        self.assertTrue(f(datetime(2022, 1, 1)))
        self.assertTrue(f(datetime(2023, 1, 1)))
        self.assertFalse(f(datetime(2020, 1, 1)))
        self.assertFalse(f(datetime(2021, 12, 31)))

    def test_invalid_date(self):
        with self.assertRaises(ExpressionError):
            create_date_test('error')
