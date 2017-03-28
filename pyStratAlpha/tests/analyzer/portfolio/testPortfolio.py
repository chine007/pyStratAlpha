# -*- coding: utf-8 -*-
import os
import unittest
from datetime import datetime

import pandas as pd
from pandas.util.testing import assert_frame_equal
from pandas.util.testing import assert_series_equal

from pyStratAlpha.analyzer.factor.cleanData import get_multi_index_data
from pyStratAlpha.analyzer.portfolio.portfolio import Portfolio
from pyStratAlpha.enums import DataSource


class TestPortfolio(unittest.TestCase):
    def setUp(self):
        dir_name = os.path.dirname(os.path.abspath(__file__))
        input_path = os.path.join(dir_name, 'data//portfolio_input.csv')
        price_data_path = os.path.join(dir_name, 'data//price_data.csv')
        filtered_path = os.path.join(dir_name, 'data//filtered_result.csv')
        sec_data = pd.read_csv(input_path)
        sec_data['tiaoCangDate'] = pd.to_datetime(sec_data['tiaoCangDate'])
        sec_selected = sec_data.set_index(['tiaoCangDate', 'secID'])

        self.portfolio = Portfolio(sec_selected=sec_selected,
                                   end_date='2012/11/30',
                                   data_source=DataSource.CSV,
                                   csv_path=price_data_path)

        price_data = pd.read_csv(price_data_path)
        price_data['tradeDate'] = pd.to_datetime(price_data['tradeDate'])
        price_data.set_index('tradeDate', inplace=True)
        self.price_data = price_data

        self.filtered = pd.read_csv(filtered_path)

        def get_filtered_result(col_sec_id, col_weight):
            ret = self.filtered.set_index(col_sec_id)
            ret = ret[col_weight]
            ret.name = 'weight'
            ret.index.name = 'secID'
            return ret

        self.get_filtered_result = get_filtered_result

    def testGetSecPriceBetweenTiaoCangDate(self):
        calculated = self.portfolio._get_sec_price_between_tiaocang_date(datetime(2012, 8, 31),
                                                                         datetime(2012, 9, 30))
        expected = self.price_data[self.price_data.index >= datetime(2012, 7, 31)]
        expected = expected[expected.index <= datetime(2012, 8, 31)]
        assert_frame_equal(calculated, expected)

    def testGetSecPriceOnDate(self):
        calculated = self.portfolio._get_sec_price_on_date(self.price_data, datetime(2012, 8, 6))
        expected = self.price_data.loc[datetime(2012, 8, 6)]
        expected.name = 'price'
        assert_series_equal(calculated, expected)

    def testGetWeightOnDate(self):
        calculated = self.portfolio._get_weight_on_date(datetime(2012, 8, 31))
        expected = self.get_filtered_result('secID2', 'weight2')
        assert_series_equal(calculated, expected)

    def testFilterSecOnTiaoCangDate(self):
        sec_id = ['000702.SZ', '600538.SH', '600975.SH', '002143.SZ', '002286.SZ', '002548.SZ', '002477.SZ',
                  '002124.SZ', '600508.SH', '601001.SH', '600403.SH', '300164.SZ', '600971.SH', '300192.SZ',
                  '600094.SH', '000985.SZ', '002217.SZ', '600378.SH', '300163.SZ', '002455.SZ', '002054.SZ',
                  '002343.SZ', '002113.SZ', '600731.SH', '600985.SH', '000782.SZ', '002361.SZ', '300132.SZ']

        calculated = self.portfolio._filter_sec_on_tiaocang_date(datetime(2012, 8, 31), sec_id)

        expected = pd.Series(data=self.filtered['filtered'].dropna().values,
                             index=pd.Index(self.filtered['sec_id'].dropna(), name='secID'), name='filters',
                             dtype='int32')
        assert_series_equal(calculated, expected)

    def testUpdateWeightAfterFilter(self):
        filtered = pd.Series(data=self.filtered['filtered'].dropna().values,
                             index=pd.Index(self.filtered['sec_id'].dropna(), name='secID'), name='filters')
        weight = get_multi_index_data(self.portfolio._sec_selected, 'tiaoCangDate', datetime(2012, 8, 31), 'secID',
                                      filtered.index.values)
        weight = weight.reset_index().set_index('secID')
        weight = weight[['weight', 'INDUSTRY']]
        calculated = self.portfolio._update_weight_after_filter(weight, filtered)

        expected = self.filtered[['weight', 'INDUSTRY', 'filters', 'secID4']].set_index('secID4').dropna()
        expected['weight'] = expected['weight']
        expected.index.name = 'secID'
        assert_frame_equal(calculated, expected)

    def testGetQuantity(self):
        init_ptf_value = 10000000
        filtered = self.filtered[['filtered', 'sec_id']].dropna().set_index('sec_id')
        weight = get_multi_index_data(self.portfolio._sec_selected, 'tiaoCangDate', datetime(2012, 8, 31), 'secID',
                                      filtered.index.values)
        weight = weight.reset_index().set_index('secID')
        weight = weight[['weight', 'INDUSTRY']]
        price = self.price_data.loc[datetime(2012, 8, 6)]
        price.name = 'price'
        calculated = self.portfolio._get_quantity(init_ptf_value, weight, price)

        expected = pd.Series(data=self.filtered['quantity'].dropna().values,
                             index=pd.Index(self.filtered['secID3'].dropna().values, name='secID'), dtype='int64',
                             name='quantity')
        assert_series_equal(calculated, expected)
