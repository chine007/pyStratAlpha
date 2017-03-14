# -*- coding: utf-8 -*-

import datetime
import os as os
import unittest
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
from pandas.util.testing import assert_series_equal
from pyStratAlpha.analyzer.factor import DCAMAnalyzer
from pyStratAlpha.analyzer.factor import DCAMHelper
from pyStratAlpha.analyzer.factor.dynamicContext import sigmoid_modif
from pyStratAlpha.analyzer.factor.loadData import FactorLoader
from pyStratAlpha.enums import FactorNormType


class TestDynamicContext(unittest.TestCase):
    def setUp(self):
        dir_name = os.path.dirname(os.path.abspath(__file__))
        zip_path = os.path.join(dir_name, 'data')
        factor_path = {
            'MV': {'path': zip_path + '//factors.csv', 'freq': 'm'},  # 总市值, 月度频率 -- 分层因子
            'BP_LF': {'path': zip_path + '//factors.csv', 'freq': 'm'},  # 最近财报的净资产/总市值, 季度频率 -- 分层因子/alpha测试因子
            'SP_TTM': {'path': zip_path + '//factors.csv', 'freq': 'q'},  # 过去12 个月总营业收入/总市值, 季度频率 -- alpha测试因子
            'GP2Asset': {'path': zip_path + '//factors.csv', 'freq': 'q'},  # 销售毛利润/总资产, 季度频率 -- alpha测试因子
            'RETURN': {'path': zip_path + '//factors.csv', 'freq': 'm'}  # 收益,月度频率
        }

        # TODO
        # 从factor_loader / dcam analyer中的几个重要参数进行组合, 生成2-3个独立的dcamanalyer类, 然后每一步分别对这几个类进行测试
        # 这样最大限度的覆盖所有代码以及所有情况
        # 标准结果保存在csv中, 一个一个拿出来对比即可
        factor_loader = FactorLoader(start_date='2010-01-31',
                                     end_date='2010-12-31',
                                     factor_norm_dict={'MV': FactorNormType.Null,
                                                       'BP_LF': FactorNormType.Null,
                                                       'GP2Asset': FactorNormType.Null,
                                                       'SP_TTM': FactorNormType.Null,
                                                       'RETURN': FactorNormType.Null},
                                     zip_path=zip_path,
                                     factor_path_dict=factor_path
                                     )

        factor_data = factor_loader.get_factor_data()
        layer_factor = [factor_data['MV']]
        alpha_factor = [factor_data['BP_LF'], factor_data['SP_TTM'], factor_data['GP2Asset']]

        self.calc_rank_ic_result = pd.read_csv(zip_path + '//calcRankIC.csv')
        self.alpha_weight_result = pd.read_csv(zip_path + '//alphaWeight.csv')
        self.calc_score_result = pd.read_csv(zip_path + '//calcScoreOnDate.csv')

        self.helper = DCAMHelper()
        self.analyzer = DCAMAnalyzer(layer_factor=layer_factor,
                                     alpha_factor=alpha_factor,
                                     sec_return=factor_data['RETURN'],
                                     tiaocang_date=factor_loader.get_tiaocang_date(),
                                     tiaocang_date_window_size=3)

        tickers = ['000001.SZ', '000002.SZ', '000003.SZ', '000004.SZ', '000005.SZ', '000006.SZ', '000007.SZ',
                   '000008.SZ', '000009.SZ', '000010.SZ']
        tiaocang_date = [datetime.datetime(2015, 4, 30), datetime.datetime(2015, 4, 30), datetime.datetime(2015, 4, 30),
                         datetime.datetime(2015, 4, 30),
                         datetime.datetime(2015, 6, 30), datetime.datetime(2015, 6, 30), datetime.datetime(2015, 6, 30),
                         datetime.datetime(2015, 6, 30),
                         datetime.datetime(2015, 9, 30), datetime.datetime(2015, 9, 30)]
        index = pd.MultiIndex.from_arrays([tiaocang_date, tickers], names=['tiaoCangDate', 'secID'])
        simple_factor = [24, 1.0, 1.1, 0.8, 0.5, 1.2, -1.0, -2, 1.0, 0.5]
        simple_factor = pd.Series(simple_factor, index=index)

        self.data = {'simple_factor': simple_factor,
                     'alpha_factor': alpha_factor,
                     'layer_factor': layer_factor}

    def testGetSecGroup(self):
        factor = self.data['simple_factor']

        calculated = self.helper.seperate_sec_group(factor, datetime.datetime(2015, 4, 30))
        expected = (['000004.SZ', '000002.SZ'], ['000003.SZ', '000001.SZ'])
        self.assertEqual(calculated, expected)

        calculated = self.helper.seperate_sec_group(factor, datetime.datetime(2015, 6, 30))
        expected = (['000008.SZ', '000007.SZ'], ['000005.SZ', '000006.SZ'])
        self.assertEqual(calculated, expected)

        calculated = self.helper.seperate_sec_group(factor, datetime.datetime(2015, 9, 30))
        expected = (['000010.SZ'], ['000009.SZ'])
        self.assertEqual(calculated, expected)

    def testGetAlphaFactor(self):
        factor = self.data['alpha_factor']
        calculated = self.helper.get_factor_on_date(factor=factor,
                                                    factor_names=['BP_LF', 'SP_TTM', 'GP2Asset'],
                                                    sec_ids=['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ',
                                                             '000767.SZ'],
                                                    date=datetime.datetime(2010, 7, 30))
        expected = pd.DataFrame(
            data={'BP_LF': [-1.520271174, -2.558324574, 0.652255509, -0.1164599, -0.16154393],
                  'SP_TTM': [np.nan, np.nan, np.nan, np.nan, np.nan],
                  'GP2Asset': [np.nan, np.nan, np.nan, np.nan, np.nan]},
            index=pd.Index(['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ', '000767.SZ'], dtype='object'),
            columns=['BP_LF', 'SP_TTM', 'GP2Asset'])
        assert_frame_equal(calculated, expected)

    def testCalcRankIC(self):
        layer_factor = self.data['layer_factor']
        calculated = self.analyzer.calc_rank_ic(layer_factor)
        expected = [
            pd.DataFrame({'BP_LF': [-0.183456213042, -0.0305530469964, 0.271971968356, -0.0212066069429,
                                    0.0436920786066, 0.157066165089, -0.0661863616898],
                          'SP_TTM': [0.034663998353, -0.0834952859155, 0.242163060362, 0.146234602464, -0.0039090645248,
                                     0.211450321065, -0.161189866694],
                          'GP2Asset': [0.034663998353, -0.0834952859155, 0.242163060362, 0.146234602464, -0.11851837339,
                                       0.0485436893786, 0.192950210391]},
                         index=pd.DatetimeIndex(['2010-04-30', '2010-05-31', '2010-06-30', '2010-07-30',
                                                 '2010-08-31', '2010-09-30', '2010-10-29'],
                                                dtype='datetime64[ns]', freq=None),
                         columns=['BP_LF', 'SP_TTM', 'GP2Asset'],
                         dtype='object'),
            pd.DataFrame({'BP_LF': [-0.227007875789, -0.0525570241212, 0.304225370785, -0.0184604184141,
                                    -0.197740573701, 0.312309789994, 0.00855841777273],
                          'SP_TTM': [0.00561010899152, 0.140184279179, -0.0120753695574, -0.0808010153925,
                                     0.0229829428007, 0.0863833290427, -0.0361170380136],
                          'GP2Asset': [0.00561010899152, 0.140184279179, -0.0120753695574, -0.0808010153925,
                                       0.0602426719273, -0.21308888298, -0.0363467962642]},
                         index=pd.DatetimeIndex(['2010-04-30', '2010-05-31', '2010-06-30', '2010-07-30',
                                                 '2010-08-31', '2010-09-30', '2010-10-29'],
                                                dtype='datetime64[ns]', freq=None),
                         columns=['BP_LF', 'SP_TTM', 'GP2Asset'],
                         dtype='object')]
        assert_frame_equal(calculated[0], expected[0])
        assert_frame_equal(calculated[1], expected[1])

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

    def testSigmoidModif(self):
        calculated = sigmoid_modif(0.9)
        expected = 4.820137900379084
        self.assertAlmostEqual(calculated, expected, places=6)

        calculated = sigmoid_modif(0.75)
        expected = 4.2414181997875655
        self.assertAlmostEqual(calculated, expected, places=6)

        calculated = sigmoid_modif(0.3)
        expected = -3.8079707797788243
        self.assertAlmostEqual(calculated, expected, places=6)

        calculated = sigmoid_modif(0.05)
        expected = -4.890130573694068
        self.assertAlmostEqual(calculated, expected, places=6)

    def testCalcLayerFactorQuantileOnDate(self):
        calculated = self.analyzer.calc_layer_factor_quantile_on_date(datetime.datetime(2010, 4, 30))
        expected = pd.DataFrame(data=self.calc_rank_ic_result['MV'].values,
                                index=self.calc_rank_ic_result['Unnamed: 0'].values, columns=['MV'])
        assert_frame_equal(calculated, expected)

    def testGetSecReturn(self):
        calculated = self.analyzer.get_sec_return(['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ', '000767.SZ'],
                                                  datetime.datetime(2010, 7, 30))
        expected = pd.DataFrame(
            data=[-0.189065723, -1.088532817, 0.083715309, 0.139473629, -0.53666822],
            index=pd.Index(['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ', '000767.SZ'],
                           dtype='object', name='secID'), columns=['RETURN'])
        assert_frame_equal(calculated, expected)

    def testGetAnalysis(self):
        calculated = pd.DataFrame(self.analyzer.get_analysis(layer_factor_name='MV').values)
        expected = pd.DataFrame([[0.02447543, 0.01847538, 0.13927067, 0.20053902, 0.17573999, 0.09212862,
                                  0.06019526, 0.95311014, 0.56026995, 0.46856907, 0.28571429, 0.88274691],
                                 [0.05513111, 0.01802389, 0.14022084, 0.06905323, 0.39317345, 0.26101447,
                                  0.58152748, 0.57555966, 3.6596513, 0.07990185, 0.42857143, 0.42321829],
                                 [0.06607741, -0.01946786, 0.12607813, 0.10286043, 0.52409893, -0.18926478,
                                  1.28779206, 0.22305436, 0.5798409, 0.46107812, 0.42857143, 0.42321829]])
        assert_frame_equal(calculated, expected)

        calculated = pd.DataFrame(self.analyzer.get_analysis().values)
        assert_frame_equal(calculated, expected)

    def testCalcAlphaFactorWeightOnDate(self):
        date = datetime.datetime(2010, 9, 30)
        alpha_weight_low, alpha_weight_high = self.analyzer.calc_alpha_factor_weight_on_date(date)
        expected_high = pd.DataFrame(data=[[0.11534764, -0.44129437, -0.15423205]],
                                     index=pd.Index(['MV'], dtype='object'),
                                     columns=pd.Index(['BP_LF', 'SP_TTM', 'GP2Asset'], dtype='object'))
        expected_low = pd.DataFrame(data=[[0.63739582, 1.03334258, 0.48155794]],
                                    index=pd.Index(['MV'], dtype='object'),
                                    columns=pd.Index(['BP_LF', 'SP_TTM', 'GP2Asset'], dtype='object'))
        assert_frame_equal(alpha_weight_low, expected_low)
        assert_frame_equal(alpha_weight_high, expected_high)

    def testCalcAlphaFactorRankOnDate(self):
        date = datetime.datetime(2010, 9, 30)
        alpha_weight_low, alpha_weight_high = self.analyzer.calc_alpha_factor_weight_on_date(date)
        calculated = self.analyzer.calc_alpha_factor_rank_on_date(date, alpha_weight_low, alpha_weight_high)
        expected = pd.DataFrame(
            data={'BP_LF': self.alpha_weight_result['BP_LF'].values,
                  'SP_TTM': self.alpha_weight_result['SP_TTM'].values,
                  'GP2Asset': self.alpha_weight_result['GP2Asset'].values}, index=pd.MultiIndex.from_arrays(
                [self.alpha_weight_result['secID'].values, self.alpha_weight_result['layerFactor'].values,
                 self.alpha_weight_result['low_high'].values]))
        expected.index.names = ['secID', 'layerFactor', 'low_high']
        expected = expected[['BP_LF', 'SP_TTM', 'GP2Asset']]
        assert_frame_equal(calculated, expected)

    def testCalcSecScoreOnDate(self):
        calculated = self.analyzer.calc_sec_score_on_date(datetime.datetime(2010, 9, 30))
        expected = pd.Series(data=self.calc_score_result['score'].values, index=self.calc_score_result['secID'].values)
        expected.name = datetime.datetime(2010, 9, 30)
        assert_series_equal(calculated.dropna(), expected.dropna())

    def testCalcSecScore(self):
        self.analyzer._saveSecScore = False
        self.analyzer._tiaoCangDateWindowSize = 8
        calculated = self.analyzer.calc_sec_score()
        index = pd.MultiIndex.from_arrays(
            [[datetime.datetime.strptime(date, '%Y/%m/%d') for date in self.calc_score_result['tiaocangdate'].values],
             self.calc_score_result['secID2'].values])
        index.names = ['tiaoCangDate', 'secID']
        expected = pd.Series(data=self.calc_score_result['score2'].values, index=index, name='score')
        assert_series_equal(calculated, expected)
