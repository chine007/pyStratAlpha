# -*- coding: utf-8 -*-
import os
import unittest
from datetime import datetime

import pandas as pd

from pyStratAlpha.analyzer.factor.cleanData import get_universe_single_factor
from pyStratAlpha.analyzer.indexComp.indexComp import IndexComp


class TestIndexComp(unittest.TestCase):
    def setUp(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(dirName, 'data//indexComp.csv')
        industryWeight = get_universe_single_factor(path, factor_name='Weight', index_name=['tiaoCangDate', 'secID'],
                                                    date_format='%Y/%m/%d')
        self.indexComp = IndexComp(industryWeight)

    def testGetIndustryWeightOnDate(self):
        calculated = self.indexComp.get_industry_weight_on_date(datetime(2015, 1, 30))
        expected = {'801720.SI': 2.6000000000000001, '801030.SI': 6.1600000000000001, '801780.SI': 0.0,
                    '801730.SI': 5.04, '801180.SI': 9.0600000000000005, '801790.SI': 2.8199999999999998,
                    '801110.SI': 1.3200000000000001, '801740.SI': 1.3799999999999999, '801710.SI': 2.3999999999999999,
                    '801880.SI': 3.5299999999999998, '801230.SI': 1.8300000000000001, '801210.SI': 0.88,
                    'other': 0.079999999999998295, '801020.SI': 1.96, '801080.SI': 5.5599999999999996,
                    '801150.SI': 9.3100000000000005, '801750.SI': 5.9400000000000004, '801760.SI': 3.1499999999999999,
                    '801170.SI': 4.3499999999999996, '801010.SI': 3.5699999999999998, '801040.SI': 0.31,
                    '801120.SI': 2.4399999999999999, '801160.SI': 3.9199999999999999, '801130.SI': 2.0699999999999998,
                    '801140.SI': 2.9700000000000002, '801770.SI': 1.6899999999999999, '801050.SI': 5.2199999999999998,
                    '801890.SI': 6.7000000000000002, '801200.SI': 3.7400000000000002}
        self.assertEqual(calculated, expected)

    def testGetIndustryWeightOnName(self):
        calculated = self.indexComp.get_industry_weight_on_name("801080.SI")
        index = pd.MultiIndex.from_arrays(
            [[datetime(2014, 12, 31), datetime(2015, 1, 30), datetime(2015, 2, 27),
              datetime(2015, 3, 31), datetime(2015, 4, 30), datetime(2015, 5, 29),
              datetime(2015, 6, 30), datetime(2015, 7, 31), datetime(2015, 8, 31),
              datetime(2015, 9, 30), datetime(2015, 10, 30), datetime(2015, 11, 30),
              datetime(2015, 12, 31), datetime(2016, 1, 29)],
             ['801080.SI', '801080.SI', '801080.SI', '801080.SI', '801080.SI', '801080.SI', '801080.SI', '801080.SI',
              '801080.SI', '801080.SI', '801080.SI', '801080.SI', '801080.SI', '801080.SI']],
            names=['tiaoCangDate', 'secID'])

        expected = pd.Series([5.44, 5.56, 5.54, 5.31, 5.1, 5.81, 5.409, 5.206, 5.09, 4.971, 5.116, 5.759, 6.48, 6.687],
                             index=index, name='factor')
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = self.indexComp.get_industry_weight_on_name("电子")
        pd.util.testing.assert_series_equal(calculated, expected)

    def testMapIndustryCodeToName(self):
        industry = pd.Series(['801200.SI', '801090.SI'], index=['300158.SZ', '600328.SH'])
        calculated = self.indexComp.map_industry_code_to_name(industry)
        expected = pd.Series(['商业贸易', '交运设备'], index=['300158.SZ', '600328.SH'])
        pd.util.testing.assert_series_equal(calculated, expected)
