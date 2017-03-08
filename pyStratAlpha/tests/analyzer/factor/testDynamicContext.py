# -*- coding: utf-8 -*-
import datetime
import os as os
import unittest

import numpy as np
import pandas as pd

import pyStratAlpha.analyzer.factor.dynamicContext as dynamicContext
from pyStratAlpha.analyzer.factor.loadData import FactorLoader
from pyStratAlpha.enums.factor import FactorNormType


class TestDynamicContext(unittest.TestCase):
    def setUp(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        zipPath = os.path.join(dirName, 'data')
        factorPathDict = {
            'MV': [zipPath + '//factors.csv', 'm'],  # 总市值, 月度频率 -- 分层因子
            'BP_LF': [zipPath + '//factors.csv', 'm'],  # 最近财报的净资产/总市值, 季度频率 -- 分层因子/alpha测试因子
            'SP_TTM': [zipPath + '//factors.csv', 'q'],  # 过去12 个月总营业收入/总市值, 季度频率 -- alpha测试因子
            'GP2Asset': [zipPath + '//factors.csv', 'q'],  # 销售毛利润/总资产, 季度频率 -- alpha测试因子
            'RETURN': [zipPath + '//factors.csv', 'm']  # 收益,月度频率
        }

        self.factor = FactorLoader(start_date='2010-01-31',
                                   end_date='2010-12-31',
                                   factor_norm_dict={'MV': FactorNormType.Null,
                                                     'BP_LF': FactorNormType.Null,
                                                     'GP2Asset': FactorNormType.Null,
                                                     'SP_TTM': FactorNormType.Null,
                                                     'RETURN': FactorNormType.Null},
                                   zip_path=zipPath,
                                   factor_path_dict=factorPathDict
                                   )

        factorData = self.factor.get_factor_data()

        self.result = pd.read_csv(zipPath + '//result.csv')

        self.analyzer = dynamicContext.DCAMAnalyzer(layer_factor=[factorData['MV']],
                                                    alpha_factor=[factorData['BP_LF'], factorData['SP_TTM'],
                                                                  factorData['GP2Asset']],
                                                    sec_return=factorData['RETURN'],
                                                    tiaocang_date=self.factor.get_tiaocang_date(),
                                                    tiaocang_date_window_size=3)

        tickers = ['000001.SZ', '000002.SZ', '000003.SZ', '000004.SZ', '000005.SZ', '000006.SZ', '000007.SZ',
                   '000008.SZ', '000009.SZ', '000010.SZ']
        tiaoCangDate = [datetime.datetime(2015, 4, 30), datetime.datetime(2015, 4, 30), datetime.datetime(2015, 4, 30),
                        datetime.datetime(2015, 4, 30),
                        datetime.datetime(2015, 6, 30), datetime.datetime(2015, 6, 30), datetime.datetime(2015, 6, 30),
                        datetime.datetime(2015, 6, 30),
                        datetime.datetime(2015, 9, 30), datetime.datetime(2015, 9, 30)]
        index = pd.MultiIndex.from_arrays([tiaoCangDate, tickers], names=['tiaoCangDate', 'secID'])
        factor = [24, 1.0, 1.1, 0.8, 0.5, 1.2, -1.0, -2, 1.0, 0.5]
        factor = pd.Series(factor, index=index)

        self.data = {'factor': factor}

    def testGetSecGroup(self):
        factor = self.data['factor']

        calculated = self.analyzer.get_sec_group(factor, datetime.datetime(2015, 4, 30))
        expected = (['000004.SZ', '000002.SZ'], ['000003.SZ', '000001.SZ'])
        self.assertEqual(calculated, expected)

        calculated = self.analyzer.get_sec_group(factor, datetime.datetime(2015, 6, 30))
        expected = (['000008.SZ', '000007.SZ'], ['000005.SZ', '000006.SZ'])
        self.assertEqual(calculated, expected)

        calculated = self.analyzer.get_sec_group(factor, datetime.datetime(2015, 9, 30))
        expected = (['000010.SZ'], ['000009.SZ'])
        self.assertEqual(calculated, expected)

    def testGetAlphaFactor(self):
        calculated = self.analyzer.get_alpha_factor(['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ', '000767.SZ'],
                                                    datetime.datetime(2010, 7, 30))
        expected = pd.DataFrame(
            data={'BP_LF': [-1.520271174, -2.558324574, 0.652255509, -0.1164599, -0.16154393],
                  'SP_TTM': [np.nan, np.nan, np.nan, np.nan, np.nan],
                  'GP2Asset': [np.nan, np.nan, np.nan, np.nan, np.nan]},
            index=pd.Index(['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ', '000767.SZ'], dtype='object'),
            columns=['BP_LF', 'SP_TTM', 'GP2Asset'])
        pd.util.testing.assert_frame_equal(calculated, expected)

    def testCalcRankIC(self):
        calculated = self.analyzer.calc_rank_ic(self.analyzer._layerFactor[0])
        expected = [
            pd.DataFrame({'BP_LF': [-0.152513, -0.0223357, 0.297609, -0.0403249, 0.0564143, 0.212253, -0.0584238],
                          'SP_TTM': [-0.0228946, -0.113262, 0.194962, 0.161491, -0.136985, -0.126626, -0.0643652],
                          'GP2Asset': [-0.0228946, -0.113262, 0.194962, 0.161491, -0.195667, 0.00415417, 0.14764]},
                         index=pd.DatetimeIndex(['2010-04-30', '2010-05-31', '2010-06-30', '2010-07-30',
                                                 '2010-08-31', '2010-09-30', '2010-10-29'],
                                                dtype='datetime64[ns]', freq=None),
                         columns=['BP_LF', 'SP_TTM', 'GP2Asset'],
                         dtype='object'),
            pd.DataFrame({'BP_LF': [-0.186874, -0.054205, 0.26974, 0.00183407, -0.113112, 0.217987, 0.0209473],
                          'SP_TTM': [0.058461, 0.172165, 0.0347826, -0.0477937, -0.212691, 0.00216965, -0.0353724],
                          'GP2Asset': [0.058461, 0.172165, 0.0347826, -0.0477937, 0.0617111, -0.194023, -0.0986745]},
                         index=pd.DatetimeIndex(['2010-04-30', '2010-05-31', '2010-06-30', '2010-07-30',
                                                 '2010-08-31', '2010-09-30', '2010-10-29'],
                                                dtype='datetime64[ns]', freq=None),
                         columns=['BP_LF', 'SP_TTM', 'GP2Asset'],
                         dtype='object')]
        pd.util.testing.assert_frame_equal(calculated[0], expected[0])
        pd.util.testing.assert_frame_equal(calculated[1], expected[1])

    def testCalcLayerFactorDistance(self):
        calculated = self.analyzer.calc_layer_factor_distance(0.9)
        expected = 4.820137900379084
        self.assertAlmostEqual(calculated, expected, places=6)

        calculated = self.analyzer.calc_layer_factor_distance(0.75)
        expected = 4.2414181997875655
        self.assertAlmostEqual(calculated, expected, places=6)

        calculated = self.analyzer.calc_layer_factor_distance(0.3)
        expected = -3.8079707797788243
        self.assertAlmostEqual(calculated, expected, places=6)

        calculated = self.analyzer.calc_layer_factor_distance(0.05)
        expected = -4.890130573694068
        self.assertAlmostEqual(calculated, expected, places=6)

    def testCalcLayerFactorQuantileOnDate(self):
        calculated = self.analyzer.calc_layer_factor_quantile_on_date(datetime.datetime(2010, 4, 30))
        expected = pd.DataFrame(data=self.result['MV'].values, index=self.result['Unnamed: 0'].values, columns=['MV'])
        pd.util.testing.assert_frame_equal(calculated, expected)

    # def testCalcAlphaFactorRankOnDate(self):
    #     date = datetime.datetime(2010, 12, 31)
    #     alphaWeightLow, alphaWeightHigh = self.analyzer.calc_alpha_factor_weight_on_date(date)
    #     calculated = self.analyzer.calc_alpha_factor_rank_on_date(date, alphaWeightLow, alphaWeightHigh)
    #     indexLow = pd.MultiIndex.from_arrays([['MV'], ['low']], names=['layerFactor', 'lowHigh'])
    #     indexHigh = pd.MultiIndex.from_arrays([['MV'], ['high']], names=['layerFactor', 'lowHigh'])
    #     pd.util.testing.assert_series_equal(calculated['BP_LF'][:]['000007.SZ'],
    #                                         pd.Series(data=[83.], index=indexLow, name='BP_LF'))
    #     pd.util.testing.assert_series_equal(calculated['SP_TTM'][:]['000027.SZ'],
    #                                         pd.Series(data=[8.07142857143], index=indexHigh, name='SP_TTM'))
    #     pd.util.testing.assert_series_equal(calculated['BP_LF'][:]['600697.SH'],
    #                                         pd.Series(data=[43.0], index=indexHigh, name='BP_LF'))
    #     pd.util.testing.assert_series_equal(calculated['SP_TTM'][:]['600717.SH'],
    #                                         pd.Series(data=[8.07142857143], index=indexHigh, name='SP_TTM'))

    def testGetSecReturn(self):
        calculated = self.analyzer.get_sec_return(['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ', '000767.SZ'],
                                                  datetime.datetime(2010, 7, 30))
        expected = pd.DataFrame(
            data=[-0.189065723, -1.088532817, 0.083715309, 0.139473629, -0.53666822],
            index=pd.Index([u'000007.SZ', u'000017.SZ', u'000027.SZ', u'000737.SZ', u'000767.SZ'],
                           dtype='object', name='secID'), columns=['RETURN'])
        pd.util.testing.assert_frame_equal(calculated, expected)



        # def testCalcAlphaFactorWeightOnDate(self):
        #     calculated = self.analyzer.calc_alpha_factor_weight_on_date(datetime.datetime(2011, 3, 31))
        #     # TODO Result is empty
        #     expected = calculated
        #     pd.util.testing.assert_frame_equal(calculated[0], expected[0])
        #     pd.util.testing.assert_frame_equal(calculated[1], expected[1])
