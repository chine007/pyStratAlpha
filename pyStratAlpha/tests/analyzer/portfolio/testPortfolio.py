# -*- coding: utf-8 -*-
import os
import unittest
from datetime import datetime

import pandas as pd

from pyStratAlpha.analyzer.portfolio.portfolio import Portfolio


class TestPortfolio(unittest.TestCase):
    def setUp(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(dirName, 'data//sec_selected.csv')
        factor = pd.read_csv(path)
        factor.columns = ['tiaoCangDate', 'secID', 'score', 'weight', 'INDUSTRY']
        index = pd.MultiIndex.from_arrays(
            [[datetime.strptime(date, "%Y/%m/%d") for date in factor['tiaoCangDate'].values], factor['secID'].values],
            names=['tiaoCangDate', 'secID'])
        secSelected = pd.DataFrame({'score': factor['score'].values,
                                    'weight': factor['weight'].values,
                                    'INDUSTRY': factor['INDUSTRY'].values}, index=index)
        endDate = datetime.strptime('2016-2-29', "%Y-%m-%d")
        self.portfolio = Portfolio(secSelected, endDate)

    def testGetSecPriceBetweenTiaoCangDate(self):
        calculated = self.portfolio._get_sec_price_between_tiaocang_date(datetime(2016, 1, 29),
                                                                         datetime(2016, 2, 1))
        dirName = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(dirName, 'data//result.csv')
        expected = pd.read_csv(path)
        expected = pd.DataFrame(data=expected.loc[:, list(expected.columns.values[1:])].values,
                                index=[datetime.strptime(date, "%Y-%m-%d") for date in expected['tradeDate']],
                                columns=expected.columns.values[1:])
        expected.index.names = ['tradeDate']
        pd.util.testing.assert_frame_equal(calculated, expected)

    def testGetWeightOnDate(self):
        calculated = self.portfolio._get_weight_on_date(datetime(2016, 1, 29))
        dirName = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(dirName, 'data//expected.csv')
        expected = pd.read_csv(path)
        expected = pd.Series(data=expected['files'].values, dtype='int32', index=expected['secID'], name='files')
        expected.index.names = ['secID']
        pd.util.testing.assert_series_equal(calculated['files'], expected)

    def testFilterSecOnTiaoCangDate(self):
        calculated = self.portfolio._filter_sec_on_tiaocang_date(datetime(2016, 1, 29),
                                                                 ['000046.SZ', '000048.SZ', '601388.SH'])
        expected = pd.Series(data=[0, 0, 1], index=['000046.SZ', '000048.SZ', '601388.SH'], dtype='int32',
                             name='files')
        expected.index.names = ['secID']
        pd.util.testing.assert_series_equal(calculated, expected)

    def testUpdateWeightAfterFilter(self):
        weight = get_multi_index_data(self.portfolio._secSelected, 'tiaoCangDate', datetime(2016, 1, 29), 'secID',
                                      ['000046.SZ', '000048.SZ', '000062.SZ'])
        weight = weight.reset_index().set_index('secID')
        weight = weight.drop(['tiaoCangDate'], axis=1)
        files = self.portfolio._filter_sec_on_tiaocang_date(datetime(2015, 10, 27), weight.index.tolist())
        calculated = self.portfolio._update_weight_after_filter(weight, files)
        expected = pd.Series(data=[0.005095556, 0.0, 0.005096429], index=['000062.SZ', '000048.SZ', '000046.SZ'],
                             name='weight')
        expected.index.names = ['secID']
        pd.util.testing.assert_series_equal(calculated['weight'], expected)

    def testGetQuantity(self):
        initPtfValue = 10000000
        tiaoCangStartDate = datetime(2016, 1, 29)
        tiaoCangEndDate = datetime(2016, 2, 1)
        priceData = self.portfolio._get_sec_price_between_tiaocang_date(tiaoCangStartDate, tiaoCangEndDate)
        price = self.portfolio._get_sec_price_on_date(priceData, tiaoCangStartDate)
        weight = self.portfolio._get_weight_on_date(tiaoCangStartDate)
        calculated = self.portfolio._get_quantity(initPtfValue, weight, price)
        price = pd.Series(data=[23.79, 8.38, 27.95, 56.9, 9.83325306, 37.13,
                                23.3077714, 14.09744261, 6.34956119, 6.26],
                          index=pd.Index(['000007.SZ', '000008.SZ', '000034.SZ', '000038.SZ', '000046.SZ',
                                          '000048.SZ', '000062.SZ', '000063.SZ', '000069.SZ', '000078.SZ'],
                                         dtype='object'), name='price')
        weight = pd.Series(data=[[0., 0.00201654, 0., 0., 0.00509643, 0.00398625,
                                  0.00509556, 0.00413833, 0.00509643, 0.0060155]],
                           index=pd.Index(['000007.SZ', '000008.SZ', '000034.SZ', '000038.SZ', '000046.SZ',
                                           '000048.SZ', '000062.SZ', '000063.SZ', '000069.SZ', '000078.SZ'],
                                          dtype='object', name='secID'), name='weight')

        pass

    def testCalcPtfValueBetweenTiaoCangDate(self):
        pass

    def testCalcPtfValueCurve(self):
        pass

    def testEvaluatePtfReturn(self):
        pass
