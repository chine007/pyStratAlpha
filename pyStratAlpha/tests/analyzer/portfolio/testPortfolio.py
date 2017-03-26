# -*- coding: utf-8 -*-
import os
import unittest
import pandas as pd
from datetime import datetime
from pyStratAlpha.analyzer.factor.cleanData import get_multi_index_data
from pyStratAlpha.analyzer.portfolio.portfolio import Portfolio
from pyStratAlpha.enums import DataSource
from pandas.util.testing import assert_frame_equal
from pandas.util.testing import assert_series_equal


class TestPortfolio(unittest.TestCase):
    def setUp(self):
        dir_name = os.path.dirname(os.path.abspath(__file__))
        input_path = os.path.join(dir_name, 'data//portfolio_input.csv')
        result_path = os.path.join(dir_name, 'data//portfolio_result.csv')
        filtered_path = os.path.join(dir_name, 'data//filtered_result.csv')
        sec_data = pd.read_csv(input_path)
        sec_selected = sec_data[['weight', 'INDUSTRY', 'score']].dropna()
        sec_selected.index = pd.MultiIndex.from_arrays(
            [pd.to_datetime(sec_data['tiaoCangDate']).values, sec_data['secID'].values],
            names=['tiaoCangDate', 'secID'])

        self.portfolio = Portfolio(sec_selected=sec_selected, end_date='2012-11-30', data_source=DataSource.CSV,
                                   csv_path=result_path)

        self.score_result = pd.read_csv(result_path).set_index('tradeDate')

        self.filtered = pd.read_csv(filtered_path)

    def testGetSecPriceBetweenTiaoCangDate(self):
        calculated = self.portfolio._get_sec_price_between_tiaocang_date(datetime(2012, 6, 29),
                                                                         datetime(2012, 7, 31))
        expected = self.score_result
        assert_frame_equal(calculated, expected)

    def testGetSecPriceOnDate(self):
        calculated = self.portfolio._get_sec_price_on_date(self.score_result, '2012/7/4')
        expected = self.score_result.loc['2012/7/4']
        expected.name = 'price'
        pd.util.testing.assert_series_equal(calculated, expected)

    def testGetWeightOnDate(self):
        calculated = self.portfolio._get_weight_on_date(datetime(2012, 6, 29))

        expected = pd.Series(data=self.filtered['weight2'].values,
                             index=pd.Index(self.filtered['secID2'], name='secID'), name='weight')
        assert_series_equal(calculated, expected)

    def testFilterSecOnTiaoCangDate(self):
        sec_id = ['000702.SZ', '600538.SH', '600975.SH', '002143.SZ', '002286.SZ', '002548.SZ', '002477.SZ',
                  '002124.SZ', '600508.SH', '601001.SH', '600403.SH', '300164.SZ', '600971.SH', '300192.SZ',
                  '600094.SH', '000985.SZ', '002217.SZ', '600378.SH', '300163.SZ', '002455.SZ', '002054.SZ',
                  '002343.SZ', '002113.SZ', '600731.SH', '600985.SH', '000782.SZ', '002361.SZ', '300132.SZ',
                  '300041.SZ', '000953.SZ', '002201.SZ', '300109.SZ', '600527.SH', '002395.SZ', '300019.SZ',
                  '002165.SZ', '002274.SZ', '600784.SH', '000825.SZ', '600399.SH', '002075.SZ', '600019.SH',
                  '002295.SZ', '601137.SH', '600888.SH', '002057.SZ', '600338.SH', '600459.SH', '600219.SH',
                  '002116.SZ', '002082.SZ', '002066.SZ', '002088.SZ', '600562.SH', '600552.SH', '000856.SZ',
                  '600248.SH', '600970.SH', '002062.SZ', '600881.SH', '300040.SZ', '600984.SH', '600847.SH',
                  '600992.SH', '002175.SZ', '600560.SH', '600558.SH', '000967.SZ', '000862.SZ', '000595.SZ',
                  '002031.SZ', '300126.SZ', '002347.SZ', '002150.SZ', '002510.SZ', '300066.SZ', '002158.SZ',
                  '002026.SZ', '300173.SZ', '300018.SZ', '300069.SZ', '600566.SH', '600582.SH', '002090.SZ',
                  '000676.SZ', '002209.SZ', '300099.SZ', '002559.SZ', '601717.SH', '300124.SZ', '002196.SZ',
                  '002204.SZ', '600973.SH', '002214.SZ', '002045.SZ', '300083.SZ', '002139.SZ', '300046.SZ',
                  '002076.SZ', '600237.SH', '000413.SZ', '002402.SZ', '002484.SZ', '300076.SZ', '002414.SZ',
                  '000700.SZ', '002101.SZ', '600148.SH', '002488.SZ', '600081.SH', '002126.SZ', '002472.SZ',
                  '002213.SZ', '600990.SH', '600715.SH', '300008.SZ', '000957.SZ', '300038.SZ', '002152.SZ',
                  '000748.SZ', '000561.SZ', '002197.SZ', '000070.SZ', '000555.SZ', '000851.SZ', '002544.SZ',
                  '002035.SZ', '000921.SZ', '600336.SH', '600854.SH', '000801.SZ', '002495.SZ', '000796.SZ',
                  '000729.SZ', '002557.SZ', '000869.SZ', '002044.SZ', '600987.SH', '002404.SZ', '600689.SH',
                  '002098.SZ', '002425.SZ', '600626.SH', '002117.SZ', '002235.SZ', '000910.SZ', '600356.SH',
                  '600966.SH', '300089.SZ', '002247.SZ', '600210.SH', '600385.SH', '000603.SZ', '600671.SH',
                  '002252.SZ', '300016.SZ', '000756.SZ', '000963.SZ', '600222.SH', '002275.SZ', '600706.SH',
                  '600530.SH', '000605.SZ', '300015.SZ', '600513.SH', '002004.SZ', '600796.SH', '000411.SZ',
                  '600594.SH', '000692.SZ', '300070.SZ', '000695.SZ', '600982.SH', '600758.SH', '600461.SH',
                  '600167.SH', '600780.SH', '600561.SH', '002040.SZ', '000582.SZ', '002357.SZ', '600077.SH',
                  '002245.SZ', '002210.SZ', '300013.SZ', '600734.SH', '600463.SH', '000909.SZ', '000502.SZ',
                  '600791.SH', '000628.SZ', '000546.SZ', '600647.SH', '000732.SZ', '600684.SH', '600340.SH',
                  '600823.SH', '002133.SZ', '600136.SH', '002500.SZ', '601009.SH', '600816.SH', '601818.SH',
                  '601169.SH', '600856.SH', '600738.SH', '000419.SZ', '600735.SH', '600278.SH', '600861.SH',
                  '600694.SH', '002024.SZ', '600729.SH', '000610.SZ', '000430.SZ', '000524.SZ', '000007.SZ',
                  '601007.SH', '000892.SZ', '600571.SH', '600757.SH', '300074.SZ', '600446.SH', '600718.SH',
                  '300058.SZ', '000682.SZ', '300047.SZ', '002253.SZ', '600570.SH', '600588.SH', '000504.SZ',
                  '600892.SH', '000409.SZ', '600656.SH', '000710.SZ', '600701.SH', '000556.SZ', '000832.SZ',
                  '000660.SZ', '600670.SH', '000689.SZ']

        calculated = self.portfolio._filter_sec_on_tiaocang_date(datetime(2012, 6, 29), sec_id)

        expected = pd.Series(data=self.filtered['filtered'].dropna().values,
                             index=self.filtered['sec_id'].dropna(), dtype='int32', name='filters')
        assert_series_equal(calculated, expected)

    def testUpdateWeightAfterFilter(self):
        filtered = pd.Series(data=self.filtered['filtered'].dropna().values,
                             index=self.filtered['sec_id'].dropna(), dtype='int32', name='filters')
        weight = get_multi_index_data(self.portfolio._sec_selected, 'tiaoCangDate', datetime(2012, 6, 29), 'secID',
                                      filtered.index.values)
        weight = weight.reset_index().set_index('secID')
        weight = weight[['weight', 'INDUSTRY']]
        calculated = self.portfolio._update_weight_after_filter(weight, filtered)

        expected = self.filtered[['weight', 'INDUSTRY', 'filters', 'secID']].set_index('secID')
        expected['weight'] = expected['weight'].astype('float64')
        expected['filters'] = expected['filters'].astype('int32')
        assert_frame_equal(calculated, expected)

    def testGetQuantity(self):
        init_ptf_value = 10000000
        filtered = self.filtered[['filtered', 'sec_id']].dropna().set_index('sec_id')
        weight = get_multi_index_data(self.portfolio._sec_selected, 'tiaoCangDate', datetime(2012, 6, 29), 'secID',
                                      filtered.index.values)
        weight = weight.reset_index().set_index('secID')
        weight = weight[['weight', 'INDUSTRY']]
        price = self.score_result.loc['2012/7/4']
        price.name = 'price'
        calculated = self.portfolio._get_quantity(init_ptf_value, weight, price)

        expected = pd.Series(data=self.filtered['quantity'].values,
                             index=pd.Index(self.filtered['secID3'].values, name='secID'), name='quantity')
        assert_series_equal(calculated, expected)
