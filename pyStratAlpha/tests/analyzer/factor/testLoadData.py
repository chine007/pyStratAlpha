# -*- coding: utf-8 -*-
import os
import unittest
from datetime import datetime

import pandas as pd

from pyStratAlpha.analyzer.factor import FactorLoader
from pyStratAlpha.analyzer.factor.cleanData import get_universe_single_factor
from pyStratAlpha.enums import DCAMFactorType
from pyStratAlpha.enums import FactorICSign
from pyStratAlpha.enums import FactorNormType


class TestLoadData(unittest.TestCase):
    def setUp(self):
        dir_name = os.path.dirname(os.path.abspath(__file__))
        zip_path = os.path.join(dir_name, 'data')
        factor_path_dict = {
            'MV': [zip_path + '//factors.csv', 'm'],  # 总市值, 月度频率 -- 分层因子
            'BP_LF': [zip_path + '//factors.csv', 'm'],  # 最近财报的净资产/总市值, 季度频率 -- 分层因子/alpha测试因子
            'SP_TTM': [zip_path + '//factors.csv', 'q'],  # 过去12 个月总营业收入/总市值, 季度频率 -- alpha测试因子
            'GP2Asset': [zip_path + '//factors.csv', 'q'],  # 销售毛利润/总资产, 季度频率 -- alpha测试因子
            'RETURN': [zip_path + '//factors.csv', 'm'],  # 收益,月度频率
            'INDUSTRY': [zip_path + '//codeSW.csv', 'm'],  # 申万行业分类,月度频率
            'IND_WGT': [zip_path + '//IndustryWeight.csv', 'm'],  # 中证500股票池内按照申万一级行业分类统计的行业权重,月度频率
            'RETS': [zip_path + '//rets.csv', '']
        }

        factor_norm_dict = {'MV': [FactorNormType.Null, DCAMFactorType.layerFactor, FactorICSign.Null],  # 分层因子
                            'BP_LF': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.layerFactor,
                                      FactorICSign.Null],  # 分层因子
                            'SP_TTM': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.alphaFactor,
                                       FactorICSign.Positive],  # alpha 因子
                            'GP2Asset': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.alphaFactor,
                                         FactorICSign.Negative],  # alpha因子
                            'RETURN': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.returnFactor,
                                       FactorICSign.Null],
                            'INDUSTRY': [FactorNormType.Null, DCAMFactorType.industryFactor, FactorICSign.Null]}

        factor_loader_params = {'startDate': '2010-01-31',
                                'endDate': '2011-12-31',
                                'factorNormDict': factor_norm_dict}

        # FactorLoader params
        start_date = factor_loader_params['startDate']
        end_date = factor_loader_params['endDate']
        factor_norm_dict = factor_loader_params['factorNormDict']

        self.factor = FactorLoader(start_date=start_date,
                                   end_date=end_date,
                                   factor_norm_dict=factor_norm_dict,
                                   factor_path_dict=factor_path_dict,
                                   zip_path=zip_path)

    def testGetTiaoCangDate(self):
        calculated = self.factor.get_tiaocang_date()
        expected = [datetime(2010, 1, 29, 0, 0), datetime(2010, 2, 26, 0, 0), datetime(2010, 3, 31, 0, 0),
                    datetime(2010, 4, 30, 0, 0), datetime(2010, 5, 31, 0, 0), datetime(2010, 6, 30, 0, 0),
                    datetime(2010, 7, 30, 0, 0), datetime(2010, 8, 31, 0, 0), datetime(2010, 9, 30, 0, 0),
                    datetime(2010, 10, 29, 0, 0), datetime(2010, 11, 30, 0, 0), datetime(2010, 12, 31, 0, 0),
                    datetime(2011, 1, 31, 0, 0), datetime(2011, 2, 28, 0, 0), datetime(2011, 3, 31, 0, 0),
                    datetime(2011, 4, 29, 0, 0), datetime(2011, 5, 31, 0, 0), datetime(2011, 6, 30, 0, 0),
                    datetime(2011, 7, 29, 0, 0), datetime(2011, 8, 31, 0, 0), datetime(2011, 9, 30, 0, 0),
                    datetime(2011, 10, 31, 0, 0), datetime(2011, 11, 30, 0, 0)]
        self.assertEqual(calculated, expected)

    def testGetFactorData(self):
        factors = self.factor.get_factor_data()

        calculated = list(factors.index.values)
        expected = ['RETURN', 'INDUSTRY', 'BP_LF', 'MV', 'GP2Asset', 'SP_TTM']
        self.assertEqual(calculated, expected)

        calculated = factors['RETURN']
        expected = get_universe_single_factor(self.factor._factorPathDict['RETURN'][0],
                                              index_name=['tiaoCangDate', 'secID'], factor_name='RETURN')
        expected.name = 'RETURN'
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = factors['BP_LF']
        expected = get_universe_single_factor(self.factor._factorPathDict['BP_LF'][0],
                                              index_name=['tiaoCangDate', 'secID'], factor_name='BP_LF')
        expected.name = 'BP_LF'
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = factors['MV']
        expected = get_universe_single_factor(self.factor._factorPathDict['MV'][0],
                                              index_name=['tiaoCangDate', 'secID'], factor_name='MV')
        expected.name = 'MV'
        pd.util.testing.assert_series_equal(calculated, expected)

    def testNormalizeSingleFactorData(self):
        factors = self.factor.get_factor_data()

        calculated = self.factor.normalize_single_factor_data(factors["BP_LF"], industries=factors['INDUSTRY'])
        expected = get_universe_single_factor(self.factor._factorPathDict['RETS'][0],
                                              index_name=['tiaoCangDate', 'secID'], factor_name='RET1',
                                              date_format='%Y/%m/%d')
        expected.name = 'BP_LF'
        pd.util.testing.assert_series_equal(calculated, expected)

        calculated = self.factor.normalize_single_factor_data(factors["BP_LF"], industries=factors['INDUSTRY'],
                                                              caps=factors['MV'])
        expected = get_universe_single_factor(self.factor._factorPathDict['RETS'][0],
                                              index_name=['tiaoCangDate', 'secID'], factor_name='RET2',
                                              date_format='%Y/%m/%d')
        expected.name = 'BP_LF'
        pd.util.testing.assert_series_equal(calculated, expected)
