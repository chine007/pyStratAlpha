# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from PyFin.Utilities import pyFinAssert
from PyFin.DateUtilities import Calendar
from PyFin.api.DateUtilities import bizDatesList
from alphalens.performance import mean_return_by_quantile
from alphalens.performance import compute_mean_returns_spread
from alphalens.utils import get_clean_factor_and_forward_returns
from alphalens.plotting import plot_mean_quantile_returns_spread_time_series
from alphalens.plotting import plot_cumulative_returns_by_quantile
from alphalens.tears import GridFigure
from alphalens.plotting import plot_quantile_returns_bar
from pyStratAlpha.analyzer.indexComp import IndexComp
from pyStratAlpha.analyzer.factor.loadData import FactorLoader
from pyStratAlpha.enums import DataSource
from pyStratAlpha.enums import FactorNormType
from pyStratAlpha.utils import get_sec_price

_alphaLensFactorIndexName = ['date', 'asset']
_alphaLensFactorColName = 'factor'
_sec_score_path = 'sec_score.csv'


class FactorAnalyzer(object):
    def __init__(self,
                 start_date,
                 end_date,
                 factor_raw,
                 industry=None,
                 data_source=DataSource.WIND,
                 calendar='China.SSE',
                 periods=[1, 5, 10],
                 **kwargs):
        """
        :param factor_raw: pd.Series, multi index=[tradeDate, secID]  columns = [factor]
        :param industry: pd.Series/dict, Either A MultiIndex Series indexed by date and asset, containing the period
        wise group codes for each asset, or a dict of asset to group mappings. If a dict is passed, it is assumed that
        group mappings are unchanged for the entire time period of the passed factor data.
        :param data_source: enum, DataSource type
        :param calendar: optional, PyFin.Calendar type
        :param periods: optional, list of int, fwd return periods
        :return:
        """
        self._calendar = Calendar(calendar)
        self._start_date = start_date
        self._end_date = end_date
        self._industry = industry
        self._data_source = data_source
        self._periods = periods
        self._converto2daily = kwargs.get('convert2daily', True)
        self._factor = convert_factor(factor=factor_raw, start_date=start_date,
                                      end_date=end_date, convert2daily=self._converto2daily)
        self._factor.index = self._factor.index.rename(_alphaLensFactorIndexName)
        self._factor.name = _alphaLensFactorColName

        self._trade_date = sorted(set(self._factor.index.get_level_values(_alphaLensFactorIndexName[0])))
        self._sec_ID = sorted(set(self._factor.index.get_level_values(_alphaLensFactorIndexName[1])))

    def _get_clean_factor_and_fwd_return(self):
        price = get_sec_price(str(self._trade_date[0])[:10], str(self._trade_date[-1])[:10], self._sec_ID,
                              data_source=self._data_source)

        factor_data = get_clean_factor_and_forward_returns(factor=self._factor,
                                                           prices=price,
                                                           groupby_labels=IndexComp.get_industry_name_dict(),
                                                           periods=self._periods)
        return factor_data

    @classmethod
    def quantile_tear_sheet(cls, factor, p):
        gf = GridFigure(rows=1, cols=1)
        mean_quantile_daily, std_quantile_daily = mean_return_by_quantile(factor,
                                                                          by_date=True,
                                                                          by_group=False,
                                                                          demeaned=True)

        plot_cumulative_returns_by_quantile(mean_quantile_daily[p],
                                            period=p,
                                            ax=gf.next_row())

    @classmethod
    def top_bottom_tear_sheet(cls, factor, quantile=[1, 5]):
        mean_return_by_q_daily, std_err = mean_return_by_quantile(factor, by_date=True)
        quant_return_spread, std_err_spread = compute_mean_returns_spread(mean_return_by_q_daily,
                                                                          upper_quant=quantile[1],
                                                                          lower_quant=quantile[0],
                                                                          std_err=std_err)
        plot_mean_quantile_returns_spread_time_series(quant_return_spread, std_err_spread)

    @classmethod
    def mean_return_tear_sheet(cls, factor):
        mean_return_by_q, std_err_by_q = mean_return_by_quantile(factor, by_group=False)
        plot_quantile_returns_bar(mean_return_by_q)

    def create_full_tear_sheet(self):
        factor_data = self._get_clean_factor_and_fwd_return()

        for p in self._periods:
            self.quantile_tear_sheet(factor_data, p)
        self.top_bottom_tear_sheet(factor_data)
        self.mean_return_tear_sheet(factor_data)
        plt.show()
        return

    def calc_rank_ic(self):
        tiaocang_date = self._trade_date
        ret = pd.Series()
        for j in range(0, len(tiaocang_date) - 1):
            date = tiaocang_date[j]
            next_date = tiaocang_date[j + 1]
            next_return = get_sec_price(date, next_date, self._factor[date].index,
                                        data_source=self._data_source)
            next_return = (next_return._values[-1] - next_return._values[0]) / next_return._values[0]
            tmp, _ = st.spearmanr(self._factor[date].values, next_return)
            ret[date] = tmp
        return ret


def convert_factor(factor, start_date, end_date, convert2daily,
                   calendar='China.SSE'):
    """
    :param factor: dataframe, col = [tiaoCangDate, secID, score/factor]
    :param start_date: str, start date of sec_score to be used
    :param end_date: str, end date of sec_score to be used
    :param calendar: str, calendar defined in PyFin
    :return: ret: dataframe, col = [tiaoCangDate, secID, score/factor] frequency of tiaoCangDate is Day
    """

    factor = factor.loc[factor.index.get_level_values('tiaoCangDate') >= start_date, :]
    factor = factor.loc[factor.index.get_level_values('tiaoCangDate') <= end_date, :]
    factor.dropna(inplace=True)
    tiaocang_date_list = sorted(set(factor.index.get_level_values('tiaoCangDate')))
    pyFinAssert(len(tiaocang_date_list) > 1, ValueError, 'length of tiaocang_date must be larger than 1')
    if not convert2daily:
        return factor

    ret = pd.DataFrame()
    for i in range(0, len(tiaocang_date_list) - 1):
        date = bizDatesList(calendar, tiaocang_date_list[i], tiaocang_date_list[i + 1])
        date = date if i == len(tiaocang_date_list) - 2 else date[:-1]
        nb_date = len(date)
        tiancang_factor = factor.loc[factor.index.get_level_values('tiaoCangDate') >= tiaocang_date_list[i], :]
        tiancang_factor = tiancang_factor.loc[
                          tiancang_factor.index.get_level_values('tiaoCangDate') < tiaocang_date_list[i + 1], :]
        duplicate_date = np.concatenate(map(lambda x: np.tile(x, len(tiancang_factor)), date))
        duplicate_sec_score = np.tile(tiancang_factor.values, nb_date)
        duplicate_sec_id = np.tile(tiancang_factor.index.get_level_values('secID'), nb_date)
        ret = pd.concat([ret, pd.DataFrame(
            {'tiaoCangDate': duplicate_date, 'secID': duplicate_sec_id, 'factor': duplicate_sec_score})])

    ret = ret.set_index(['tiaoCangDate', 'secID'])
    ret = ret['factor']
    return ret


if __name__ == "__main__":
    factor = FactorLoader('2014-01-05',
                          '2016-5-30',
                          {'MV': [FactorNormType.Null],
                           'INDUSTRY': [FactorNormType.Null],
                           'ROE': [FactorNormType.IndustryAndCapNeutral],
                           'RETURN': [FactorNormType.IndustryAndCapNeutral]}).get_factor_data()['MV']
    analyzer = FactorAnalyzer(start_date='2014-01-05', end_date='2016-05-01', factor_raw=factor,
                              data_source=DataSource.MYSQL_LOCAL, convert2daily=True)
    print analyzer.create_full_tear_sheet()
