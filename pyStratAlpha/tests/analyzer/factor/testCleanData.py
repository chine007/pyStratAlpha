# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

import pandas as pd

from pyStratAlpha.analyzer.factor.cleanData import adjust_factor_date
from pyStratAlpha.analyzer.factor.cleanData import get_multi_index_data
from pyStratAlpha.analyzer.factor.cleanData import get_report_date


class TestCleanData(unittest.TestCase):
    def testGetReportDate(self):
        actDate = ['2015-01-01', '2015-03-30', '2015-06-20', '2016-09-01', '2016-12-05']
        calculated = [get_report_date(date) for date in actDate]
        expected = [datetime(2014, 9, 30), datetime(2014, 9, 30), datetime(2015, 3, 31),
                    datetime(2016, 6, 30), datetime(2016, 9, 30)]
        for i in range(len(expected)):
            self.assertEqual(calculated[i], expected[i], "Expected report date of {0} is not equal to expected {1}"
                             .format(actDate[i], expected[i]))

        actDate = [datetime(2015, 1, 1), datetime(2015, 3, 30), datetime(2015, 6, 20),
                   datetime(2016, 9, 1), datetime(2016, 12, 5)]
        calculated = [get_report_date(date) for date in actDate]
        expected = [datetime(2014, 9, 30), datetime(2014, 9, 30), datetime(2015, 3, 31),
                    datetime(2016, 6, 30), datetime(2016, 9, 30)]
        for i in range(len(expected)):
            self.assertEqual(calculated[i], expected[i], "Expected report date of {0} is not equal to expected {1}"
                             .format(actDate[i], expected[i]))

    def testAdjustFactorDate(self):

        factorRaw = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], name='factor', index=pd.MultiIndex.from_arrays(
            [[datetime(2015, 3, 31), datetime(2015, 3, 31), datetime(2015, 12, 31),
              datetime(2016, 6, 30), datetime(2016, 9, 30)],
             ['000691.SZ', '002118.SZ', '000691.SZ', '600312.SH', '300518.SZ']], names=['tradeDate', 'secID']))

        calculated = adjust_factor_date(factorRaw, '2015-01-01', '2016-09-30', freq='m')
        expected = pd.Series([1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 4.0, 4.0], name='factor',
                             index=pd.MultiIndex.from_arrays(
                                 [[datetime(2015, 4, 30), datetime(2015, 4, 30),
                                   datetime(2015, 5, 29), datetime(2015, 5, 29),
                                   datetime(2015, 6, 30),
                                   datetime(2015, 6, 30), datetime(2015, 7, 31),
                                   datetime(2015, 7, 31), datetime(2016, 8, 31),
                                   datetime(2016, 9, 30)],
                                  ['000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ', '000691.SZ',
                                   '002118.SZ', '000691.SZ', '002118.SZ', '600312.SH', '600312.SH']],
                                 names=['tiaoCangDate', 'secID']))
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = adjust_factor_date(factorRaw, datetime(2015, 1, 1), datetime(2016, 9, 30),
                                        freq='m')
        expected = pd.Series([1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 4.0, 4.0], name='factor',
                             index=pd.MultiIndex.from_arrays(
                                 [[datetime(2015, 4, 30), datetime(2015, 4, 30),
                                   datetime(2015, 5, 29), datetime(2015, 5, 29),
                                   datetime(2015, 6, 30),
                                   datetime(2015, 6, 30), datetime(2015, 7, 31),
                                   datetime(2015, 7, 31), datetime(2016, 8, 31),
                                   datetime(2016, 9, 30)],
                                  ['000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ', '000691.SZ',
                                   '002118.SZ', '000691.SZ', '002118.SZ', '600312.SH', '600312.SH']],
                                 names=['tiaoCangDate', 'secID']))
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = adjust_factor_date(factorRaw, '2015-01-01', '2016-01-30', freq='m')
        expected = pd.Series([1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0], name='factor',
                             index=pd.MultiIndex.from_arrays(
                                 [[datetime(2015, 4, 30), datetime(2015, 4, 30),
                                   datetime(2015, 5, 29), datetime(2015, 5, 29),
                                   datetime(2015, 6, 30),
                                   datetime(2015, 6, 30), datetime(2015, 7, 31),
                                   datetime(2015, 7, 31)],
                                  ['000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ', '000691.SZ',
                                   '002118.SZ', '000691.SZ', '002118.SZ']],
                                 names=['tiaoCangDate', 'secID']))
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = adjust_factor_date(factorRaw, datetime(2015, 1, 1), datetime(2016, 1, 30),
                                        freq='m')
        expected = pd.Series([1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0], name='factor',
                             index=pd.MultiIndex.from_arrays(
                                 [[datetime(2015, 4, 30), datetime(2015, 4, 30),
                                   datetime(2015, 5, 29), datetime(2015, 5, 29),
                                   datetime(2015, 6, 30),
                                   datetime(2015, 6, 30), datetime(2015, 7, 31),
                                   datetime(2015, 7, 31)],
                                  ['000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ', '000691.SZ',
                                   '002118.SZ', '000691.SZ', '002118.SZ']],
                                 names=['tiaoCangDate', 'secID']))
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = adjust_factor_date(factorRaw, '2015-05-01', '2015-06-30', freq='w')
        expected = pd.Series([1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0],
                             name='factor',
                             index=pd.MultiIndex.from_arrays(
                                 [[datetime(2015, 5, 1), datetime(2015, 5, 1),
                                   datetime(2015, 5, 8), datetime(2015, 5, 8),
                                   datetime(2015, 5, 15), datetime(2015, 5, 15),
                                   datetime(2015, 5, 22), datetime(2015, 5, 22),
                                   datetime(2015, 5, 29), datetime(2015, 5, 29),
                                   datetime(2015, 6, 5), datetime(2015, 6, 5),
                                   datetime(2015, 6, 12), datetime(2015, 6, 12),
                                   datetime(2015, 6, 19), datetime(2015, 6, 19),
                                   datetime(2015, 6, 26), datetime(2015, 6, 26)],
                                  ['000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ',
                                   '000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ',
                                   '000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ']],
                                 names=['tiaoCangDate', 'secID']))
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = adjust_factor_date(factorRaw, datetime(2015, 5, 1), datetime(2015, 6, 30),
                                        freq='w')
        expected = pd.Series([1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0],
                             name='factor',
                             index=pd.MultiIndex.from_arrays(
                                 [[datetime(2015, 5, 1), datetime(2015, 5, 1),
                                   datetime(2015, 5, 8), datetime(2015, 5, 8),
                                   datetime(2015, 5, 15), datetime(2015, 5, 15),
                                   datetime(2015, 5, 22), datetime(2015, 5, 22),
                                   datetime(2015, 5, 29), datetime(2015, 5, 29),
                                   datetime(2015, 6, 5), datetime(2015, 6, 5),
                                   datetime(2015, 6, 12), datetime(2015, 6, 12),
                                   datetime(2015, 6, 19), datetime(2015, 6, 19),
                                   datetime(2015, 6, 26), datetime(2015, 6, 26)],
                                  ['000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ',
                                   '000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ',
                                   '000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ', '000691.SZ', '002118.SZ']],
                                 names=['tiaoCangDate', 'secID']))
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = adjust_factor_date(factorRaw, '2016-05-01', '2017-01-30', freq='y')
        expected = pd.Series([5.0], name='factor',
                             index=pd.MultiIndex.from_arrays([[datetime(2016, 12, 31)], ['300518.SZ']],
                                                             names=['tiaoCangDate', 'secID']))
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = adjust_factor_date(factorRaw, datetime(2016, 5, 1), datetime(2017, 7, 30),
                                        freq='y')
        expected = pd.Series([5.0], name='factor',
                             index=pd.MultiIndex.from_arrays([[datetime(2016, 12, 31)], ['300518.SZ']],
                                                             names=['tiaoCangDate', 'secID']))
        pd.util.testing.assert_series_equal(calculated, expected)

    def testGetMultiIndexData(self):
        index = pd.MultiIndex.from_arrays(
            [[datetime(2015, 1, 1), datetime(2015, 1, 2), datetime(2015, 1, 2),
              datetime(2015, 2, 4), datetime(2015, 2, 4)], ['A', 'B', 'C', 'A', 'C']],
            names=['date', 'category'])
        multi = pd.Series([1.0, 2.0, 3.0, 4.0, 3.0], index=index)

        calculated = get_multi_index_data(multi, 'date', datetime(2015, 1, 2))
        expected = pd.Series([2.0, 3.0], index=pd.MultiIndex.from_arrays(
            [[datetime(2015, 1, 2), datetime(2015, 1, 2)], ['B', 'C']],
            names=['date', 'category']))
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = get_multi_index_data(multi, 'date', [datetime(2015, 1, 2)])
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = get_multi_index_data(multi, 'date', datetime(2015, 1, 2), 'category', 'B')
        expected = pd.Series([2.0], index=pd.MultiIndex.from_tuples([(datetime(2015, 1, 2), 'B')],
                                                                    names=['date', 'category']))
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = get_multi_index_data(multi, 'date', [datetime(2015, 1, 2), datetime(2015, 2, 4)],
                                          'category', 'C')
        expected = pd.Series([3.0, 3.0], index=pd.MultiIndex.from_product(
            [[datetime(2015, 1, 2), datetime(2015, 2, 4)], ['C']],
            names=['date', 'category']))
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = get_multi_index_data(multi, 'date', [datetime(2015, 1, 2), datetime(2015, 2, 4)],
                                          'category', ['B', 'C'])
        expected = pd.Series([2.0, 3.0, 3.0], index=pd.MultiIndex.from_arrays(
            [[datetime(2015, 1, 2), datetime(2015, 1, 2), datetime(2015, 2, 4)],
             ['B', 'C', 'C']],
            names=['date', 'category']))
        pd.util.testing.assert_series_equal(calculated, expected)
