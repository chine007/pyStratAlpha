# -*- coding: utf-8 -*-
import os
import unittest
from datetime import datetime
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
from pandas.util.testing import assert_series_equal
from pyStratAlpha.analyzer.performance.navAnalyzer import perf_stat
from pyStratAlpha.analyzer.performance.navAnalyzer import print_perf_stat_by_year
from pyStratAlpha.analyzer.performance.navAnalyzer import ptf_re_balance
from pyStratAlpha.analyzer.performance.navAnalyzer import regroup_by_re_balance_freq
from pyStratAlpha.enums import FreqType
from pyStratAlpha.enums import ReturnType


class TestNavAnalyzer(unittest.TestCase):
    def setUp(self):
        dir_name = os.path.dirname(os.path.abspath(__file__))
        return_data = pd.read_csv(dir_name + '//data//performance.csv')
        return_data.columns = ['tradeDate', 'benchmark', 'strategy']
        return_data['tradeDate'] = pd.to_datetime(return_data['tradeDate'], format='%Y/%m/%d')
        return_data.set_index('tradeDate', inplace=True)

        self.strategy = return_data['strategy']
        self.benchmark = return_data['benchmark']

        self.returnDict = {'stratReturn': [self.strategy, ReturnType.Cumul],
                           'benchmarkReturn': [self.benchmark, ReturnType.Cumul]}

        result_data = pd.read_csv(dir_name + "//data//result.csv")
        result_data.columns = ['tradeDate', 'result1', 'result2', 'result3']
        result_data['tradeDate'] = pd.to_datetime(result_data['tradeDate'], format='%Y/%m/%d')
        result_data.set_index('tradeDate', inplace=True)
        self.result = result_data

    def testRegroupByBalanceFreq(self):
        group = regroup_by_re_balance_freq(self.strategy)
        calculated = {}
        for (name, value) in group.groups.items():
            calculated[datetime.strptime(str(name), "%Y-%m-%d %H:%M:%S")] = value
        expected = {datetime(2005, 2, 28, 0, 0): 33, datetime(2005, 8, 31, 0, 0): 160,
                    datetime(2005, 6, 30, 0, 0): 116, datetime(2005, 4, 30, 0, 0): 77,
                    datetime(2005, 12, 31, 0, 0): 242, datetime(2005, 3, 31, 0, 0): 56,
                    datetime(2005, 11, 30, 0, 0): 220, datetime(2005, 7, 31, 0, 0): 137,
                    datetime(2005, 10, 31, 0, 0): 198, datetime(2005, 1, 31, 0, 0): 20,
                    datetime(2005, 9, 30, 0, 0): 182, datetime(2005, 5, 31, 0, 0): 94}
        self.assertEqual(calculated, expected)

        group_val = regroup_by_re_balance_freq(self.strategy, FreqType.EOM)
        calculated = {}
        for (name, value) in group_val.groups.items():
            calculated[datetime.strptime(str(name), "%Y-%m-%d %H:%M:%S")] = value
        expected = {datetime(2005, 2, 28, 0, 0): 33, datetime(2005, 8, 31, 0, 0): 160,
                    datetime(2005, 6, 30, 0, 0): 116, datetime(2005, 4, 30, 0, 0): 77,
                    datetime(2005, 12, 31, 0, 0): 242, datetime(2005, 3, 31, 0, 0): 56,
                    datetime(2005, 11, 30, 0, 0): 220, datetime(2005, 7, 31, 0, 0): 137,
                    datetime(2005, 10, 31, 0, 0): 198, datetime(2005, 1, 31, 0, 0): 20,
                    datetime(2005, 9, 30, 0, 0): 182, datetime(2005, 5, 31, 0, 0): 94}
        self.assertEqual(calculated, expected)

        group_val = regroup_by_re_balance_freq(self.strategy, FreqType.EOY)
        calculated = {}
        for (name, value) in group_val.groups.items():
            calculated[datetime.strptime(str(name), "%Y-%m-%d %H:%M:%S")] = value
        expected = {datetime(2005, 12, 31, 0, 0): 242}
        self.assertEqual(calculated, expected)

    def testPtfRebalance(self):
        return_dict = {'stratReturn': [self.strategy, ReturnType.Cumul],
                       'benchmarkReturn': [self.benchmark, ReturnType.Cumul]}
        calculated = ptf_re_balance(return_dict)
        expected = self.result['result1']
        expected.name = 'hedgedPtfReturn'
        assert_series_equal(calculated, expected)

        calculated = ptf_re_balance(return_dict, margin_prop=0.5)
        expected = self.result['result2']
        expected.name = 'hedgedPtfReturn'
        assert_series_equal(calculated, expected)

        calculated = ptf_re_balance(return_dict, margin_prop=0.5, re_balance_freq=FreqType.EOY)
        expected = self.result['result3']
        expected.name = 'hedgedPtfReturn'
        assert_series_equal(calculated, expected)

    def testPrintPerfStatYear(self):
        calculated = print_perf_stat_by_year(self.strategy, ReturnType.Cumul, risk_free=0.00)
        expected = pd.DataFrame(data=[-0.101456, -0.295517, -0.343317, -0.289605],
                                index=['annual_return', 'calmar_ratio', 'max_drawdown', 'sharpe_ratio'], columns=[2005])
        assert_frame_equal(calculated, expected)

        calculated = print_perf_stat_by_year(self.strategy, ReturnType.Cumul, risk_free=0.02)
        expected = pd.DataFrame(data=[-0.10145577, -0.29551673, -0.34331652, -19.94066624],
                                index=['annual_return', 'calmar_ratio', 'max_drawdown', 'sharpe_ratio'], columns=[2005])
        assert_frame_equal(calculated, expected)

        calculated = print_perf_stat_by_year(self.strategy, ReturnType.NonCumul, risk_free=0.00)
        expected = pd.DataFrame(columns=pd.Int64Index([], dtype='int64'),
                                index=['annual_return', 'calmar_ratio', 'max_drawdown', 'sharpe_ratio'])
        assert_frame_equal(calculated, expected)

    def testPerfStat(self):
        calculated_stat, calculated_stat_sign = perf_stat(self.strategy, self.benchmark)
        expected_stat = pd.Series(
            data=[172.035958078, 0.0, np.NaN, float('inf'), -96911.555468, -0.157454881152, 1.40921636381],
            index=['sharpe_ratio', 'max_drawdown', 'calmar_ratio', 'annual_return',
                   'alpha', 'information_ratio', 'beta'])
        expected_stat_sign = pd.Series(data=[1, -1, 1, 1, 1, 1, 1],
                                       index=['sharpe_ratio', 'max_drawdown', 'calmar_ratio', 'annual_return',
                                              'alpha', 'information_ratio', 'beta'])
        pd.util.testing.assert_series_equal(calculated_stat, expected_stat)
        pd.util.testing.assert_series_equal(calculated_stat_sign, expected_stat_sign)

        calculated_stat, calculated_stat_sign = perf_stat(self.strategy)
        expected_stat = pd.Series(data=[172.035958078, 0.0, np.NaN, float('inf')],
                                  index=['sharpe_ratio', 'max_drawdown', 'calmar_ratio', 'annual_return'])
        expected_stat_sign = pd.Series(data=[1, -1, 1, 1],
                                       index=['sharpe_ratio', 'max_drawdown', 'calmar_ratio', 'annual_return'])
        pd.util.testing.assert_series_equal(calculated_stat, expected_stat)
        pd.util.testing.assert_series_equal(calculated_stat_sign, expected_stat_sign)
