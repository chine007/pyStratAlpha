# -*- coding: utf-8 -*-
import os
import unittest
from datetime import datetime

import pandas as pd

from pyStratAlpha.analyzer.performance.navAnalyzer import print_perf_stat_by_year
from pyStratAlpha.analyzer.performance.navAnalyzer import ptf_re_balance
from pyStratAlpha.analyzer.performance.navAnalyzer import regroup_by_re_balance_freq
from pyStratAlpha.enums import FreqType
from pyStratAlpha.enums import ReturnType


class TestNavAnalyzer(unittest.TestCase):
    def setUp(self):
        dir_name = os.path.dirname(os.path.abspath(__file__))
        readfile = pd.read_csv(dir_name + "//data//performance.csv")
        readfile.columns = ['tradeDate', 'benchmark', 'strategy']
        strategy = readfile['strategy'].values
        benchmark = readfile['benchmark'].values
        index = [datetime.strptime(date, '%Y/%m/%d') for date in readfile['tradeDate']]
        self.strategy_data_frame = pd.DataFrame(data=strategy, index=index)
        self.strategy_series = pd.Series(data=strategy, index=index)
        self.benchmark_data_frame = pd.DataFrame(data=benchmark, index=index)
        self.returnDict = {'stratReturn': [self.strategy_data_frame, ReturnType.Cumul],
                           'benchmarkReturn': [self.benchmark_data_frame, ReturnType.Cumul]}
        result_file = pd.read_csv(dir_name + "//data//result.csv")
        result_file.columns = ['tradeDate', 'result1', 'result2', 'result3']
        self.index = [datetime.strptime(date, '%Y/%m/%d') for date in result_file['tradeDate']]
        self.result = [result_file['result1'].values, result_file['result2'].values, result_file['result3'].values]

    def testRegroupByBalanceFreq(self):
        group = regroup_by_re_balance_freq(self.strategy_data_frame)
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

        group = regroup_by_re_balance_freq(self.strategy_series)
        calculated = {}
        for (name, value) in group.groups.items():
            calculated[datetime.strptime(str(name), "%Y-%m-%d %H:%M:%S")] = value
        self.assertEqual(calculated, expected)

        group_val = regroup_by_re_balance_freq(self.strategy_data_frame, FreqType.EOM)
        calculated = {}
        for (name, value) in group_val.groups.items():
            calculated[datetime.strptime(str(name), "%Y-%m-%d %H:%M:%S")] = value
        self.assertEqual(calculated, expected)

        group_val = regroup_by_re_balance_freq(self.strategy_series, FreqType.EOM)
        calculated = {}
        for (name, value) in group_val.groups.items():
            calculated[datetime.strptime(str(name), "%Y-%m-%d %H:%M:%S")] = value
        self.assertEqual(calculated, expected)

        group_val = regroup_by_re_balance_freq(self.strategy_data_frame, FreqType.EOY)
        calculated = {}
        for (name, value) in group_val.groups.items():
            calculated[datetime.strptime(str(name), "%Y-%m-%d %H:%M:%S")] = value
        expected = {datetime(2005, 12, 31, 0, 0): 242}
        self.assertEqual(calculated, expected)

        group_val = regroup_by_re_balance_freq(self.strategy_series, FreqType.EOY)
        calculated = {}
        for (name, value) in group_val.groups.items():
            calculated[datetime.strptime(str(name), "%Y-%m-%d %H:%M:%S")] = value
        self.assertEqual(calculated, expected)

    def testPtfRebalance(self):
        return_dict = {'stratReturn': [self.strategy_data_frame, ReturnType.Cumul],
                       'benchmarkReturn': [self.benchmark_data_frame, ReturnType.Cumul]}
        calculated = ptf_re_balance(return_dict)
        expected = pd.Series(data=self.result[0], index=self.index, name='hedgedPtfReturn')
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = ptf_re_balance(return_dict, margin_prop=0.5)
        expected = pd.Series(data=self.result[1], index=self.index, name='hedgedPtfReturn')
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = ptf_re_balance(return_dict, margin_prop=0.5, re_balance_freq=FreqType.EOY)
        expected = pd.Series(data=self.result[2], index=self.index, name='hedgedPtfReturn')
        pd.util.testing.assert_series_equal(calculated, expected)

    def testPrintPerfStatYear(self):
        calculated = print_perf_stat_by_year(self.strategy_series, ReturnType.Cumul)
        expected = pd.DataFrame(data=[-0.101456, -0.295517, -0.343317, -0.289605],
                                index=['annual_return', 'calmar_ratio', 'max_drawdown', 'sharpe_ratio'], columns=[2005])
        pd.util.testing.assert_frame_equal(calculated, expected)

        calculated = print_perf_stat_by_year(self.strategy_series, ReturnType.NonCumul)
        expected = pd.DataFrame(columns=pd.Int64Index([], dtype='int64'),
                                index=['annual_return', 'calmar_ratio', 'max_drawdown', 'sharpe_ratio'])
        pd.util.testing.assert_frame_equal(calculated, expected)

        # def testPerfStat(self):
        #     calculatedStat, calculatedStatSign = perf_stat(self.strategy_series, self.benchmark_data_frame)
        #     expectedStat = pd.Series(data=[0.0, np.nan, float('inf'), 172.035958078, 0.0, 1.40921636381, -96911.555468],
        #                              index=['max_drawdown', 'calmar_ratio', 'annual_return', 'sharpe_ratio',
        #                                     'information_ratio', 'beta', 'alpha'])
        #     expectedStatSign = pd.Series(data=[-1, 1, 1, 1, 1, 1, 1],
        #                                  index=['max_drawdown', 'calmar_ratio', 'annual_return', 'sharpe_ratio',
        #                                         'information_ratio', 'beta', 'alpha'])
        #     pd.util.testing.assert_series_equal(calculatedStat, expectedStat)
        #     pd.util.testing.assert_series_equal(calculatedStatSign, expectedStatSign)
        #
        #     calculatedStat, calculatedStatSign = perf_stat(self.strategy_series)
        #     expectedStat = pd.Series(data=[0.0, np.nan, float('inf'), 172.035958078],
        #                              index=['max_drawdown', 'calmar_ratio', 'annual_return', 'sharpe_ratio'])
        #     expectedStatSign = pd.Series(data=[-1, 1, 1, 1],
        #                                  index=['max_drawdown', 'calmar_ratio', 'annual_return', 'sharpe_ratio'])
        #     pd.util.testing.assert_series_equal(calculatedStat, expectedStat)
        #     pd.util.testing.assert_series_equal(calculatedStatSign, expectedStatSign)
