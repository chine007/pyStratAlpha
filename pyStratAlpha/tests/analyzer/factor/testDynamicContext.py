# -*- coding: utf-8 -*-

import datetime
import os as os
import unittest

import pandas as pd
from pandas.util.testing import assert_frame_equal
from pandas.util.testing import assert_series_equal

from pyStratAlpha.analyzer.factor import DCAMAnalyzer
from pyStratAlpha.analyzer.factor import DCAMHelper
from pyStratAlpha.analyzer.factor.dynamicContext import sigmoid_modif
from pyStratAlpha.analyzer.factor.loadData import FactorLoader
from pyStratAlpha.enums import DCAMFactorType
from pyStratAlpha.enums import FactorICSign
from pyStratAlpha.enums import FactorNAHandler
from pyStratAlpha.enums import FactorNormType
from pyStratAlpha.enums import FactorWeightType


class TestDynamicContext(unittest.TestCase):
    def setUp(self):
        dir_name = os.path.dirname(os.path.abspath(__file__))
        zip_path = os.path.join(dir_name, 'data')
        factor_path = {
            'MV': {'path': zip_path + '//DCAM_factor_input.csv', 'freq': 'm'},  # 总市值, 月度频率 -- 分层因子
            'BP_LF': {'path': zip_path + '//DCAM_factor_input.csv', 'freq': 'm'},
            # 最近财报的净资产/总市值, 季度频率 -- 分层因子/alpha测试因子
            'SP_TTM': {'path': zip_path + '//DCAM_factor_input.csv', 'freq': 'q'},
            # 过去12 个月总营业收入/总市值, 季度频率 -- alpha测试因子
            'EP2_TTM': {'path': zip_path + '//DCAM_factor_input.csv', 'freq': 'q'},  # 销售毛利润/总资产, 季度频率 -- alpha测试因子
            'RETURN': {'path': zip_path + '//DCAM_factor_input.csv', 'freq': 'm'},  # 收益,月度频率}
        }

        factor_loader = FactorLoader(start_date='2010-04-29',
                                     end_date='2010-10-15',
                                     factor_norm_dict={
                                         'MV': [FactorNormType.Null, DCAMFactorType.layerFactor, FactorICSign.Null],
                                         'BP_LF': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.layerFactor,
                                                   FactorICSign.Null],
                                         'EP2_TTM': [FactorNormType.IndustryNeutral, DCAMFactorType.alphaFactor,
                                                     FactorICSign.Positive],
                                         'SP_TTM': [FactorNormType.Null, DCAMFactorType.alphaFactor,
                                                    FactorICSign.Positive],
                                         'RETURN': [FactorNormType.Null, DCAMFactorType.returnFactor,
                                                    FactorICSign.Null]},
                                     zip_path=zip_path,
                                     factor_path_dict=factor_path
                                     )

        factor_data = factor_loader.get_factor_data()
        layer_factor = [factor_data['MV']]
        alpha_factor = [factor_data['BP_LF'], factor_data['SP_TTM'], factor_data['EP2_TTM']]

        self.calc_rank_ic_result = pd.read_csv(zip_path + '//DCAM_rank_ic_result.csv')
        self.alpha_weight_result = pd.read_csv(zip_path + '//DCAM_alpha_weight_result.csv')
        self.calc_score_result = pd.read_csv(zip_path + '//DCAM_calc_score_result.csv')

        self.helper = DCAMHelper()
        self.analyzer = DCAMAnalyzer(layer_factor=layer_factor,
                                     alpha_factor=alpha_factor,
                                     sec_return=factor_data['RETURN'],
                                     tiaocang_date=factor_loader.get_tiaocang_date(),
                                     tiaocang_date_window_size=3)

        self.data = {'alpha_factor': alpha_factor,
                     'layer_factor': layer_factor}

    def testGetAnalysis(self):
        self.analyzer.na_handler = FactorNAHandler.ReplaceWithMean
        calculated = pd.DataFrame(self.analyzer.get_analysis(layer_factor_name='MV').values)
        expected = pd.DataFrame([[-0.06540587, 0.01165126, 0.04339992, 0.101677334486, -1.50705046, 0.11459057,
                                  -1.3940382, 0.21785553, 2.45390347, 0.15586702, 0.6, 0.20898483],
                                 [-0.01935416, 0.01205348, 0.08014542, 0.0544717528312, -0.24148801, 0.22127952,
                                  -0.64821919, 0.53738798, 0.54515059, 0.48140194, 0.2, 0.99962171],
                                 [-0.05478599, 0.0105286, 0.14913388, 0.0887928872246, - 0.36736114, 0.11857484,
                                  -0.75262051, 0.47796601, 1.40388233, 0.27007692, 0.4, 0.69740488]])
        assert_frame_equal(calculated, expected)

        self.analyzer.na_handler = FactorNAHandler.Drop
        calculated = pd.DataFrame(self.analyzer.get_analysis(layer_factor_name='MV').values)
        expected = pd.DataFrame([[-0.06540587, -0.02045397, 0.04339992, 0.10857475, -1.50705046, -0.18838611,
                                  -0.76888529, 0.47513434, 1.30434481, 0.28644935, 0.6, 0.20898483],
                                 [-0.01935416, 0.03639565, 0.08014542, 0.05374854, -0.24148801, 0.67714666,
                                  -1.15543985, 0.28585986, 0.56898289, 0.47228044, 0.4, 0.69740488],
                                 [-0.05478599, -0.0171354, 0.14913388, 0.12094208, -0.36736114, -0.1416827,
                                  -0.39217292, 0.70559806, 0.40353135, 0.54300921, 0.4, 0.69740488]])
        assert_frame_equal(calculated, expected)

        self.analyzer.na_handler = FactorNAHandler.Ignore
        calculated = pd.DataFrame(self.analyzer.get_analysis(layer_factor_name='MV').values)
        expected = pd.DataFrame([[-6.54058724e-02, 1.68504588e-03, 4.33999219e-02, 1.26133935e-01,
                                  -1.50705046e+00, 1.33591795e-02, -1.00592408e+00, 3.61205089e-01,
                                  1.76106525e+00, 2.21115323e-01, 6.00000000e-01, 2.08984831e-01],
                                 [-1.93541573e-02, -3.17304332e-02, 8.01454167e-02, 5.93249779e-02,
                                  -2.41488012e-01, -5.34857901e-01, 2.48237229e-01, 8.10725317e-01,
                                  2.72026321e-01, 6.16103060e-01, 4.00000000e-01, 6.97404878e-01],
                                 [-5.47859926e-02, -7.43114359e-02, 1.49133881e-01, 1.30693265e-01,
                                  -3.67361142e-01, -5.68594226e-01, 1.96931444e-01, 8.48875115e-01,
                                  2.47629961e-01, 6.32136867e-01, 2.00000000e-01, 9.99621706e-01]])
        assert_frame_equal(calculated, expected)

        self.analyzer.na_handler = FactorNAHandler.ReplaceWithMedian
        calculated = pd.DataFrame(self.analyzer.get_analysis(layer_factor_name='MV').values)
        expected = pd.DataFrame([[-0.06540587, 0.01055843, 0.04339992, 0.10379066, -1.50705046, 0.10172817,
                                  -1.35048696, 0.23110644, 2.22836897, 0.17384458, 0.6, 0.20898483],
                                 [-0.01935416, 0.03635465, 0.08014542, 0.0465449, -0.24148801, 0.78106629,
                                  -1.20216613, 0.27174078, 0.95102408, 0.35802091, 0.4, 0.69740488],
                                 [-0.05478599, -0.01243901, 0.14913388, 0.11683083, -0.36736114, -0.10647025,
                                  -0.44705772, 0.66735199, 0.51378898, 0.49389527, 0.4, 0.69740488]])
        assert_frame_equal(calculated, expected)

        calculated = pd.DataFrame(self.analyzer.get_analysis().values)
        assert_frame_equal(calculated, expected)

    def testGetSecGroup(self):
        factor = self.data['alpha_factor']

        calculated = self.helper.seperate_sec_group(factor[0], datetime.datetime(2010, 4, 30))
        expected = (
            ['600817.SH', '000757.SZ', '000017.SZ', '600757.SH', '000587.SZ', '600217.SH', '000557.SZ', '000007.SZ',
             '600617.SH', '300077.SZ', '600847.SH', '002387.SZ', '600057.SH', '600547.SH', '600157.SH', '002397.SZ',
             '600537.SH', '300067.SZ', '002007.SZ', '600187.SH', '000537.SZ', '600647.SH', '600517.SH', '600707.SH',
             '600107.SH', '600877.SH', '000887.SZ', '000567.SZ', '000607.SZ', '002287.SZ', '000727.SZ', '600127.SH',
             '000777.SZ', '600887.SH', '002207.SZ', '002147.SZ', '600207.SH', '600557.SH', '000997.SZ', '000417.SZ',
             '000657.SZ', '600747.SH', '002167.SZ', '002307.SZ', '300027.SZ', '000987.SZ', '600197.SH', '002237.SZ',
             '600077.SH', '002297.SZ', '002197.SZ', '600807.SH', '002357.SZ', '600257.SH', '601877.SH', '300007.SZ',
             '600687.SH', '600397.SH', '002137.SZ', '600327.SH', '600267.SH', '002227.SZ', '600857.SH', '000627.SZ',
             '000517.SZ', '600467.SH', '300037.SZ', '600697.SH', '002017.SZ', '600287.SH', '002157.SZ', '600767.SH',
             '600997.SH', '600097.SH', '600497.SH', '000877.SZ', '000637.SZ', '600737.SH', '000697.SZ', '600137.SH',
             '601727.SH', '600597.SH', '002107.SZ', '002037.SZ', '000837.SZ', '002247.SZ', '002097.SZ', '600867.SH',
             '002127.SZ', '000617.SZ', '300017.SZ'],
            ['000967.SZ', '600677.SH', '002057.SZ', '002367.SZ', '600247.SH', '000737.SZ', '600667.SH', '000677.SZ',
             '600487.SH', '000957.SZ', '600637.SH', '002317.SZ', '000897.SZ', '600387.SH', '600237.SH', '000917.SZ',
             '600897.SH', '600477.SH', '002187.SZ', '002277.SZ', '600297.SH', '600037.SH', '002267.SZ', '600797.SH',
             '601607.SH', '002177.SZ', '600587.SH', '002117.SZ', '000407.SZ', '600337.SH', '600167.SH', '002327.SZ',
             '600067.SH', '002377.SZ', '600527.SH', '600577.SH', '600507.SH', '300057.SZ', '002077.SZ', '000927.SZ',
             '000687.SZ', '002217.SZ', '002047.SZ', '601107.SH', '000807.SZ', '300047.SZ', '002347.SZ', '000597.SZ',
             '002337.SZ', '000157.SZ', '002027.SZ', '000507.SZ', '000767.SZ', '600117.SH', '600827.SH', '600367.SH',
             '601007.SH', '000547.SZ', '000977.SZ', '600987.SH', '600777.SH', '000937.SZ', '601857.SH', '000797.SZ',
             '600017.SH', '600837.SH', '600967.SH', '600317.SH', '600307.SH', '600007.SH', '000037.SZ', '600657.SH',
             '600377.SH', '000707.SZ', '000667.SZ', '600277.SH', '601117.SH', '000027.SZ', '600027.SH', '600177.SH',
             '002067.SZ', '002087.SZ', '600227.SH', '600717.SH', '600567.SH', '600787.SH', '000717.SZ', '600727.SH',
             '000527.SZ', '000787.SZ', '600087.SH'])
        self.assertEqual(calculated, expected)

        calculated = self.helper.seperate_sec_group(factor[1], datetime.datetime(2010, 6, 30))
        expected = (
            ['000557.SZ', '600817.SH', '600617.SH', '000567.SZ', '600767.SH', '600187.SH', '600807.SH', '300007.SZ',
             '002227.SZ', '002107.SZ', '002287.SZ', '002297.SZ', '000587.SZ', '000667.SZ', '002007.SZ', '300027.SZ',
             '600837.SH', '600537.SH', '600747.SH', '002167.SZ', '300037.SZ', '600107.SH', '300047.SZ', '600007.SH',
             '002357.SZ', '600847.SH', '600467.SH', '300017.SZ', '002317.SZ', '600867.SH', '000017.SZ', '601107.SH',
             '600037.SH', '002247.SZ', '000007.SZ', '002147.SZ', '600167.SH', '002177.SZ', '002347.SZ', '600137.SH',
             '600257.SH', '002337.SZ', '000627.SZ', '000777.SZ', '000897.SZ', '600247.SH', '600777.SH', '000537.SZ',
             '600897.SH', '002207.SZ', '600667.SH', '300057.SZ', '600557.SH', '600217.SH', '600757.SH', '600647.SH',
             '000997.SZ', '600517.SH', '600727.SH', '000547.SZ', '600377.SH', '601007.SH', '000507.SZ', '000517.SZ',
             '600197.SH', '002197.SZ', '002367.SZ', '000687.SZ', '600227.SH', '000727.SZ', '600497.SH', '002017.SZ',
             '600237.SH', '002327.SZ', '002267.SZ', '002217.SZ', '600057.SH', '601877.SH', '600317.SH', '600737.SH',
             '002377.SZ', '600387.SH', '600017.SH', '002137.SZ', '600707.SH', '600397.SH', '002117.SZ', '002097.SZ',
             '000887.SZ'],
            ['600367.SH', '600127.SH', '600077.SH', '600657.SH', '002237.SZ', '600207.SH', '000837.SZ', '600527.SH',
             '002057.SZ', '600487.SH', '600157.SH', '000977.SZ', '002077.SZ', '600687.SH', '000937.SZ', '600857.SH',
             '000407.SZ', '000987.SZ', '600177.SH', '000027.SZ', '000757.SZ', '600267.SH', '000807.SZ', '002277.SZ',
             '000657.SZ', '600337.SH', '600587.SH', '600997.SH', '000677.SZ', '000157.SZ', '002307.SZ', '000617.SZ',
             '000697.SZ', '000967.SZ', '600297.SH', '600877.SH', '600637.SH', '002037.SZ', '002047.SZ', '600097.SH',
             '601857.SH', '002127.SZ', '000607.SZ', '600717.SH', '600547.SH', '600987.SH', '000037.SZ', '000917.SZ',
             '600067.SH', '000767.SZ', '000927.SZ', '600277.SH', '000877.SZ', '601727.SH', '002067.SZ', '000797.SZ',
             '000957.SZ', '600117.SH', '000637.SZ', '601607.SH', '000597.SZ', '600797.SH', '600567.SH', '600597.SH',
             '000707.SZ', '002027.SZ', '000417.SZ', '000737.SZ', '600887.SH', '002087.SZ', '002187.SZ', '601117.SH',
             '600477.SH', '600697.SH', '002157.SZ', '600677.SH', '600967.SH', '600327.SH', '600307.SH', '600287.SH',
             '600027.SH', '600507.SH', '600577.SH', '000717.SZ', '600787.SH', '600827.SH', '000527.SZ', '000787.SZ',
             '600087.SH'])
        self.assertEqual(calculated, expected)

    def testGetAlphaFactor(self):
        factor = self.data['alpha_factor']
        calculated = self.helper.get_factor_on_date(factors=factor,
                                                    sec_ids=['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ',
                                                             '000767.SZ'],
                                                    date=datetime.datetime(2010, 7, 30))
        expected = pd.DataFrame(
            data={'BP_LF': [-0.0411, -0.6198, 0.5706, 0.2535, 0.3694],
                  'SP_TTM': [0.9797, 0.8878, 3.4258, 8.1253, 4.9528],
                  'EP2_TTM': [-3.842, -5.3132, 4.2582, -2.5911, -9.693]},
            index=pd.Index(['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ', '000767.SZ'], name='secID',
                           dtype='object'),
            columns=['BP_LF', 'SP_TTM', 'EP2_TTM'])
        assert_frame_equal(calculated, expected)

    def testCalcRankIC(self):
        calculated = self.analyzer.calc_rank_ic()
        expected = pd.Series(data=[-0.14283439110042284, -0.052533223391815258, -0.0154128495121005,
                                   -0.04007528113048988, -0.076173616975536276],
                             index=pd.DatetimeIndex(['2010-04-30', '2010-05-31', '2010-06-30', '2010-07-30',
                                                     '2010-08-31'],
                                                    dtype='datetime64[ns]', freq=None), name='BP_LF', dtype='object')
        assert_series_equal(calculated[0][0]['BP_LF'], expected)

        expected = pd.Series(data=[-0.21294876950626468, -0.049119183761540001, -0.21454149383784427,
                                   0.024253151753783911, 0.17842633224587792],
                             index=pd.DatetimeIndex(['2010-04-30', '2010-05-31', '2010-06-30', '2010-07-30',
                                                     '2010-08-31'],
                                                    dtype='datetime64[ns]', freq=None), name='EP2_TTM', dtype='object')
        assert_series_equal(calculated[0][0]['EP2_TTM'], expected)

        expected = pd.Series(data=[-0.027558303221317654, 0.11740894625005693, 0.029275646297033137,
                                   0.037517735172113618, 0.025129242936595752],
                             index=pd.DatetimeIndex(['2010-04-30', '2010-05-31', '2010-06-30', '2010-07-30',
                                                     '2010-08-31'],
                                                    dtype='datetime64[ns]', freq=None), name='SP_TTM', dtype='object')
        assert_series_equal(calculated[1][0]['SP_TTM'], expected)

    def testCalcLayerFactorDistance(self):
        self.analyzer.factor_weight_type = FactorWeightType.EqualWeight
        calculated = self.analyzer.calc_layer_factor_distance(0.6)
        expected = 1.0
        self.assertAlmostEqual(calculated, expected, places=6)

        self.analyzer.factor_weight_type = FactorWeightType.ICWeight
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

    def testGetSecReturnOnDate(self):
        calculated = self.helper.get_sec_return_on_date(self.data['alpha_factor'][0],
                                                        ['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ',
                                                         '000767.SZ'],
                                                        datetime.datetime(2010, 7, 30))
        expected = pd.DataFrame(
            data=[-0.0411, -0.6198, 0.5706, 0.2535, 0.3694],
            index=pd.Index(['000007.SZ', '000017.SZ', '000027.SZ', '000737.SZ', '000767.SZ'],
                           dtype='object', name='secID'), columns=['BP_LF'])
        assert_frame_equal(calculated, expected)

    def testCalcAlphaFactorWeightOnDate(self):
        date = datetime.datetime(2010, 9, 30)
        alpha_weight_low, alpha_weight_high = self.analyzer.calc_alpha_factor_weight_on_date(date)
        expected_high = pd.DataFrame(data=[[0.18444988, 4.85894614, 1.37004494]],
                                     index=pd.Index(['MV'], dtype='object'),
                                     columns=pd.Index(['BP_LF', 'SP_TTM', 'EP2_TTM'], dtype='object'))
        expected_low = pd.DataFrame(data=[[-1.43613765, -0.13567264, -0.01997005]],
                                    index=pd.Index(['MV'], dtype='object'),
                                    columns=pd.Index(['BP_LF', 'SP_TTM', 'EP2_TTM'], dtype='object'))
        assert_frame_equal(alpha_weight_low, expected_low)
        assert_frame_equal(alpha_weight_high, expected_high)

    def testCalcAlphaFactorRankOnDate(self):
        date = datetime.datetime(2010, 9, 30)
        alpha_weight_low, alpha_weight_high = self.analyzer.calc_alpha_factor_weight_on_date(date)
        calculated = self.analyzer.calc_alpha_factor_rank_on_date(date, alpha_weight_low, alpha_weight_high)
        expected = pd.DataFrame(
            data={'BP_LF': self.alpha_weight_result['BP_LF'].values,
                  'SP_TTM': self.alpha_weight_result['SP_TTM'].values,
                  'EP2_TTM': self.alpha_weight_result['EP2_TTM'].values}, index=pd.MultiIndex.from_arrays(
                [self.alpha_weight_result['secID'].values, self.alpha_weight_result['layerFactor'].values,
                 self.alpha_weight_result['low_high'].values]))
        expected.index.names = ['secID', 'layerFactor', 'low_high']
        expected = expected[['BP_LF', 'SP_TTM', 'EP2_TTM']]
        assert_frame_equal(calculated, expected)

    def testCalcSecScoreOnDate(self):
        calculated = self.analyzer.calc_sec_score_on_date(datetime.datetime(2010, 9, 30))
        expected = pd.Series(data=self.calc_score_result['score'].values, index=self.calc_score_result['secID'].values)
        expected.name = datetime.datetime(2010, 9, 30)
        assert_series_equal(calculated.dropna(), expected.dropna())

    def testCalcSecScore(self):
        self.analyzer._saveSecScore = False
        self.analyzer._tiaoCangDateWindowSize = 3
        calculated = self.analyzer.calc_sec_score()
        index = pd.MultiIndex.from_arrays(
            [[datetime.datetime.strptime(date, '%Y/%m/%d') for date in
              self.calc_score_result['tiaoCangDate'].values],
             self.calc_score_result['secID2'].values])
        index.names = ['tiaoCangDate', 'secID']
        expected = pd.Series(data=self.calc_score_result['score2'].values, index=index, name='score')
        assert_series_equal(calculated, expected)
