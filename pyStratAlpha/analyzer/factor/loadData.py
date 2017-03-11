# -*- coding: utf-8 -*-


import pandas as pd
from PyFin.Utilities import pyFinAssert
from pyStratAlpha.analyzer.factor.cleanData import adjust_factor_date
from pyStratAlpha.analyzer.factor.cleanData import get_multi_index_data
from pyStratAlpha.analyzer.factor.cleanData import get_universe_single_factor
from pyStratAlpha.analyzer.factor.norm import normalize
from pyStratAlpha.enums.factor import FactorNormType
from pyStratAlpha.utils.date_utils import get_pos_adj_date
from pyStratAlpha.utils.file_utils import unzip_csv_folder

_factorPathDict = {
    # 总市值, 月度频率 -- 分层因子
    'MV': {'path': '..//..//data//factor//FactorDataMonthly.csv', 'freq': 'm'},
    # 最近财报的净资产/总市值, 季度频率 -- 分层因子/alpha测试因子
    'BP_LF': {'path': '..//..//data//factor//FactorDataMonthly.csv', 'freq': 'm'},
    # 净资产同比增长率, 季度频率 -- 分层因子
    'EquityGrowth_YOY': {'path': '..//..//data//factor//FactorDataQuarterly.csv', 'freq': 'q'},
    # 净资产收益率, 季度频率 -- 分层因子
    'ROE': {'path': '..//..//data//factor//FactorDataQuarterly.csv', 'freq': 'q'},
    # 季度日均换手率, 月度频率 -- 分层因子
    'STDQ': {'path': '..//..//data//factor//FactorDataMonthly.csv', 'freq': 'm'},
    # 剔除非经常性损益的过去12 个月净利润/总市值, 季度频率 -- alpha测试因子
    'EP2_TTM': {'path': '..//..//data//factor//FactorDataMonthly.csv', 'freq': 'm'},
    # 过去12 个月总营业收入/总市值, 季度频率 -- alpha测试因子
    'SP_TTM': {'path': '..//..//data//factor//FactorDataMonthly.csv', 'freq': 'm'},
    # 销售毛利润/总资产, 季度频率 -- alpha测试因子
    'GP2Asset': {'path': '..//..//data//factor//FactorDataQuarterly.csv', 'freq': 'q'},
    # TTM PE/预测未来2 年净利润复合增长率, 月度频率 -- alpha测试因子 朝阳永续数据
    'PEG': {'path': '..//..//data//factor//FactorDataMonthly.csv', 'freq': 'm'},
    # 净利润增长率（季度同比）, 季度频率 - alpha测试因子
    'ProfitGrowth_Qr_YOY': {'path': '..//..//data//factor//FactorDataQuarterly.csv', 'freq': 'q'},
    # 月度换手率, 月度频率 - alpha测试因子
    'TO_adj': {'path': '..//..//data//factor//FactorDataMonthly.csv', 'freq': 'm'},
    # 5 日均价/60 日成交均价, 月度频率 - alpha测试因子
    'PPReversal': {'path': '..//..//data//factor//FactorDataMonthly.csv', 'freq': 'm'},
    # 收益,月度频率
    'RETURN': {'path': '..//..//data//return//monthlyReturn.csv', 'freq': 'm'},
    # 申万行业分类,月度频率
    'INDUSTRY': {'path': '..//..//data//industry//codeSW.csv', 'freq': 'm'},
    # 中证500股票池内按照申万一级行业分类统计的行业权重,月度频率
    'IND_WGT': {'path': '..//..//data//industry//IndustryWeight.csv', 'freq': 'm'}
}


def get_data_div(save_csv_path, numerator='NAV', denominator='CAP', freq='m'):
    """
    :param save_csv_path: str, save path and name of divide result
    :param numerator: str, optional, name of the numerator factor
    :param denominator: str, optional, name of the denominator factor
    :param freq: str, optional, the frequency of the data
    :return: DataFrame, the divide result
    """

    def get_new_factor_series(data, freqs):
        rets = adjust_factor_date(data,
                                  data.index.levels[0][0],
                                  data.index.levels[0][-1],
                                  freqs)
        rets.index.names = ['tradeDate', 'secID']
        return rets

    numerator_data = get_universe_single_factor(_factorPathDict[numerator][0])
    denominator_data = get_universe_single_factor(_factorPathDict[denominator][0])

    if _factorPathDict[numerator][1] == freq:
        numerator_data_adj = numerator_data
    else:
        numerator_data_adj = get_new_factor_series(numerator_data, freq)

    if _factorPathDict[denominator][1] == freq:
        denominator_data_adj = denominator_data
    else:
        denominator_data_adj = get_new_factor_series(denominator_data, freq)

    returns = numerator_data_adj.divide(denominator_data_adj, axis='index')
    returns.to_csv(save_csv_path)
    return returns


class FactorLoader(object):
    def __init__(self,
                 start_date,
                 end_date,
                 factor_norm_dict,
                 freq='m',
                 zip_path="..//..//data",
                 factor_path_dict=_factorPathDict,
                 date_format='%Y%m%d'):
        """
        :param start_date: str/datetime.datetime, 提取因子数据的开始日期
        :param end_date: str/datetime.datetime, 提取因子数据的结束日期
        :param factor_norm_dict: dict, {factorName: factorNormType}
        :param freq: str, optional, 因子数据的频率
        :param zip_path: str, optional, 数据文件压缩包地址
        :param date_format: str, optional, 数据文件中时间格式
        :return: class， 存储清理后的因子数据
        """
        self._startDate = start_date
        self._endDate = end_date
        self._factorNormDict = factor_norm_dict
        self._factorNames = factor_norm_dict.keys()
        self._nbFactor = len(factor_norm_dict)
        self._freq = freq
        self._tiaocangDate = []
        self._factorPathDict = factor_path_dict
        self._dateFormat = date_format
        # 由于因子csv文件较大,所以默认存储为压缩格式的文件, 第一次使用时自动解压缩
        unzip_csv_folder(zip_path)

    def get_tiaocang_date(self):
        return get_pos_adj_date(self._startDate, self._endDate, freq=self._freq)

    def get_factor_data(self):
        returns = pd.Series()
        for name in self._factorNames:
            path_to_use = self._factorPathDict[name]['path']
            original_freq = self._factorPathDict[name]['freq']
            if original_freq != self._freq:
                factor_raw = get_universe_single_factor(path_to_use, factor_name=name, date_format=self._dateFormat)
                factors = adjust_factor_date(factor_raw, self._startDate, self._endDate, self._freq)
            else:
                factor_raw = get_universe_single_factor(path_to_use, index_name=['tiaoCangDate', 'secID'],
                                                        factor_name=name,
                                                        date_format=self._dateFormat)
                factor_raw = factor_raw.loc[factor_raw.index.get_level_values('tiaoCangDate') >= self._startDate]
                factors = factor_raw.loc[factor_raw.index.get_level_values('tiaoCangDate') <= self._endDate]
            factors.name = name
            returns[name] = factors
        return returns

    @staticmethod
    def normalize_single_factor_data(factors, industries=None, caps=None):
        """
        :param factors: pd.Series, multi index = [tiaoCangDate, secID], value = factors
        :param industries:
        :param caps:
        :return: 去极值、中性化、标准化的因子
        """
        returns = pd.Series(name=factors.name)
        tiaocang_date = sorted(set(factors.index.get_level_values('tiaoCangDate')))
        for date in tiaocang_date:
            factor_to_use = get_multi_index_data(factors, 'tiaoCangDate', date)
            industry_to_use = get_multi_index_data(industries, 'tiaoCangDate',
                                                   date) if industries is not None else None
            cap_to_use = get_multi_index_data(caps, 'tiaoCangDate', date) if caps is not None else None
            data_normed = normalize(factor_to_use, industry_to_use, cap_to_use)
            returns = returns.append(data_normed)

        # save in multi index format
        index = pd.MultiIndex.from_tuples(returns.index, names=['tiaoCangDate', 'secID'])
        returns = pd.Series(data=returns.values, index=index, name=factors.name)
        return returns

    def get_norm_factor_data(self):
        factor_data = self.get_factor_data()
        for name in self._factorNames:
            if self._factorNormDict[name][0] == FactorNormType.IndustryAndCapNeutral:
                pyFinAssert(('INDUSTRY' in self._factorNames and 'MV' in self._factorNames),
                            ValueError,
                            'Failed to neutralize because of missing industry and cap data')
                factor_data[name] = self.normalize_single_factor_data(factor_data[name],
                                                                      industries=factor_data['INDUSTRY'],
                                                                      caps=factor_data['MV'])
            elif self._factorNormDict[name][0] == FactorNormType.IndustryNeutral:
                pyFinAssert(('INDUSTRY' in self._factorNames),
                            ValueError,
                            'Failed to neutralize because of missing industry')
                factor_data[name] = self.normalize_single_factor_data(factor_data[name],
                                                                      industries=factor_data['INDUSTRY'])

        return factor_data


if __name__ == "__main__":
    factor = FactorLoader('2015-01-05',
                          '2015-12-30',
                          {'MV': FactorNormType.Null,
                           'INDUSTRY': FactorNormType.Null,
                           'ROE': FactorNormType.IndustryAndCapNeutral,
                           'RETURN': FactorNormType.IndustryAndCapNeutral})
    ret = factor.get_norm_factor_data()
    print ret['RETURN']
