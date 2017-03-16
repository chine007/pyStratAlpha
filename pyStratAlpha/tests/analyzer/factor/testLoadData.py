# -*- coding: utf-8 -*-

import os
import unittest
from datetime import datetime

import pandas as pd
from pandas.util.testing import assert_series_equal

from pyStratAlpha.analyzer.factor import FactorLoader
from pyStratAlpha.enums import DCAMFactorType
from pyStratAlpha.enums import FactorICSign
from pyStratAlpha.enums import FactorNAHandler
from pyStratAlpha.enums import FactorNormType


class TestLoadData(unittest.TestCase):
    def setUp(self):
        dir_name = os.path.dirname(os.path.abspath(__file__))
        zip_path = os.path.join(dir_name, 'data')
        factor_path_dict = {
            'MV': {'path': zip_path + '//factors.csv', 'freq': 'm'},  # 总市值, 月度频率 -- 分层因子
            'BP_LF': {'path': zip_path + '//factors.csv', 'freq': 'm'},  # 最近财报的净资产/总市值, 季度频率 -- 分层因子/alpha测试因子
            'SP_TTM': {'path': zip_path + '//factors.csv', 'freq': 'q'},  # 过去12 个月总营业收入/总市值, 季度频率 -- alpha测试因子
            'GP2Asset': {'path': zip_path + '//factors.csv', 'freq': 'q'},  # 销售毛利润/总资产, 季度频率 -- alpha测试因子
            'RETURN': {'path': zip_path + '//factors.csv', 'freq': 'm'},  # 收益,月度频率
            'INDUSTRY': {'path': zip_path + '//codeSW.csv', 'freq': 'm'},  # 申万行业分类,月度频率
            'IND_WGT': {'path': zip_path + '//IndustryWeight.csv', 'freq': 'm'},  # 中证500股票池内按照申万一级行业分类统计的行业权重,月度频率
            'RETS': {'path': zip_path + '//factors.csv', 'freq': ''},
            'FactorLoader': {'path': zip_path + '//GetFactorDataRets.csv', 'freq': ''},
            'NormFactorData': {'path': zip_path + '//NormFactorData.csv', 'freq': ''}
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
                                'endDate': '2011-01-31',
                                'factorNormDict': factor_norm_dict,
                                'na_handler': FactorNAHandler.Drop}

        self.factor_loader = FactorLoader(start_date=factor_loader_params['startDate'],
                                          end_date=factor_loader_params['endDate'],
                                          factor_norm_dict=factor_norm_dict,
                                          factor_path_dict=factor_path_dict,
                                          zip_path=zip_path,
                                          na_handler=factor_loader_params['na_handler'])


        # TODO test other cases when na_handler is not 'Drop'

    def testGetTiaoCangDate(self):
        calculated = self.factor_loader.get_tiaocang_date()
        expected = [datetime(2010, 1, 29, 0, 0), datetime(2010, 2, 26, 0, 0), datetime(2010, 3, 31, 0, 0),
                    datetime(2010, 4, 30, 0, 0), datetime(2010, 5, 31, 0, 0), datetime(2010, 6, 30, 0, 0),
                    datetime(2010, 7, 30, 0, 0), datetime(2010, 8, 31, 0, 0), datetime(2010, 9, 30, 0, 0),
                    datetime(2010, 10, 29, 0, 0), datetime(2010, 11, 30, 0, 0), datetime(2010, 12, 31, 0, 0)]
        self.assertEqual(calculated, expected)

    def testGetFactorData(self):
        self.factor_loader._na_handler = FactorNAHandler.Drop
        factors = self.factor_loader.get_factor_data()

        data_factors = pd.read_csv(self.factor_loader._factorPathDict['RETURN']['path'])
        index = pd.MultiIndex.from_arrays(
            [[datetime.strptime(str(date), '%Y%m%d') for date in data_factors['tiaoCangDate']], data_factors['secID']])
        index.names = ['tiaoCangDate', 'secID']

        calculated = list(factors.index.values)
        expected = ['RETURN', 'INDUSTRY', 'BP_LF', 'MV', 'GP2Asset', 'SP_TTM']
        self.assertEqual(calculated, expected)

        calculated = factors['RETURN']
        expected = pd.Series(data_factors['RETURN'].values, index=index, name='RETURN').dropna()
        assert_series_equal(calculated, expected)

        calculated = factors['BP_LF']
        expected = pd.Series(data_factors['BP_LF'].values, index=index, name='BP_LF').dropna()
        assert_series_equal(calculated, expected)

        calculated = factors['MV']
        expected = pd.Series(data_factors['MV'].values, index=index, name='MV').dropna()
        assert_series_equal(calculated, expected)

        data_factors = pd.read_csv(self.factor_loader._factorPathDict['FactorLoader']['path'])
        index = pd.MultiIndex.from_arrays(
            [[datetime.strptime(str(date), '%Y/%m/%d') for date in data_factors['tiaoCangDate'].dropna()],
             data_factors['secID'].dropna()])
        index.names = ['tiaoCangDate', 'secID']

        calculated = factors['GP2Asset']
        expected = pd.Series(data_factors['GP2Asset'].dropna().values, index=index, name='GP2Asset').dropna()
        assert_series_equal(calculated, expected)

        data_factors = pd.read_csv(self.factor_loader._factorPathDict['FactorLoader']['path'])
        index = pd.MultiIndex.from_arrays(
            [[datetime.strptime(str(date), '%Y/%m/%d') for date in data_factors['tiaoCangDate2'].dropna()],
             data_factors['secID2'].dropna()])
        index.names = ['tiaoCangDate', 'secID']

        calculated = factors['SP_TTM']
        expected = pd.Series(data_factors['SP_TTM'].dropna().values, index=index, name='SP_TTM').dropna()
        assert_series_equal(calculated, expected)

        # 测试不剔除NA值的情况
        self.factor_loader._na_handler = FactorNAHandler.Ignore
        factors = self.factor_loader.get_factor_data()

        data_factors = pd.read_csv(self.factor_loader._factorPathDict['FactorLoader']['path'])
        index = pd.MultiIndex.from_arrays(
            [[datetime.strptime(str(date), '%Y/%m/%d') for date in data_factors['tiaoCangDate3'].dropna()],
             data_factors['secID3'].dropna()])
        index.names = ['tiaoCangDate', 'secID']

        calculated = factors['SP_TTM']
        expected = pd.Series(data_factors['SP_TTM_NA'].values, index=index, name='SP_TTM')
        assert_series_equal(calculated, expected)

    def testGetNormFactorData(self):
        norm_factor = self.factor_loader.get_norm_factor_data()

        calculated = norm_factor['RETURN']
        data_factors = pd.read_csv(self.factor_loader._factorPathDict['NormFactorData']['path'])
        index = pd.MultiIndex.from_arrays(
            [[datetime.strptime(str(date), '%Y/%m/%d') for date in data_factors['tiaoCangDate'].dropna()],
             data_factors['secID'].dropna()])
        index.names = ['tiaoCangDate', 'secID']
        expected = pd.Series(data_factors['RETURN'].dropna().values, index=index, name='RETURN').dropna()
        assert_series_equal(calculated, expected)
