# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from PyFin.DateUtilities import Calendar
from PyFin.api.DateUtilities import bizDatesList
from alphalens.performance import mean_return_by_quantile
from alphalens.performance import compute_mean_returns_spread
from alphalens.performance import factor_information_coefficient
from alphalens.utils import get_clean_factor_and_forward_returns
from alphalens.plotting import plot_mean_quantile_returns_spread_time_series
from alphalens.plotting import plot_cumulative_returns_by_quantile
from alphalens.plotting import plot_ic_ts
from alphalens.tears import GridFigure
from alphalens.plotting import plot_quantile_returns_bar
from pyStratAlpha.analyzer.indexComp import IndexComp
from pyStratAlpha.enums import DataSource
from pyStratAlpha.enums import FreqType
from pyStratAlpha.utils import get_sec_price

from pyStratAlpha.analyzer.factor import FactorLoader
from pyStratAlpha.enums import FactorNormType

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
        self._convert_freq = factor_raw['Freq']
        self._factor = factor_raw['Factor']
        self._factor_truncation()
        self._factor_daily = None

        self._factor.index = self._factor.index.rename(_alphaLensFactorIndexName)
        self._factor.name = _alphaLensFactorColName

        self._trade_date = sorted(set(self._factor.index.get_level_values(_alphaLensFactorIndexName[0])))
        self._trade_date = pd.to_datetime(self._trade_date)
        self._sec_ID = sorted(set(self._factor.index.get_level_values(_alphaLensFactorIndexName[1])))

        self._csv_path = kwargs.get('csv_path', None)

    def _factor_truncation(self):
        self._factor = self._factor.loc[self._factor.index.get_level_values('tiaoCangDate') >= self._start_date, :]
        self._factor = self._factor.loc[self._factor.index.get_level_values('tiaoCangDate') <= self._end_date, :]
        self._factor.dropna(inplace=True)
        return

    def _factor_convert2daily(self):
        tiaocang_date_list = self._trade_date
        ret = pd.DataFrame()
        for i in range(0, len(tiaocang_date_list) - 1):
            date = bizDatesList(self._calendar.name, tiaocang_date_list[i], tiaocang_date_list[i + 1])
            date = date if i == len(tiaocang_date_list) - 2 else date[:-1]
            nb_date = len(date)
            tiancang_factor = self._factor.loc[self._factor.index.get_level_values('date') >= tiaocang_date_list[i], :]
            tiancang_factor = tiancang_factor.loc[
                              tiancang_factor.index.get_level_values('date') < tiaocang_date_list[i + 1], :]
            duplicate_date = np.concatenate(map(lambda x: np.tile(x, len(tiancang_factor)), date))
            duplicate_sec_score = np.tile(tiancang_factor.values, nb_date)
            duplicate_sec_id = np.tile(tiancang_factor.index.get_level_values('asset'), nb_date)
            ret = pd.concat([ret, pd.DataFrame(
                {'date': duplicate_date, 'secID': duplicate_sec_id, 'factor': duplicate_sec_score})])

        ret = ret.set_index(['date', 'secID'])
        ret = ret['factor']
        return ret

    def _get_clean_factor_and_fwd_return(self, factor):
        price = get_sec_price(str(self._trade_date[0])[:10], str(self._trade_date[-1])[:10], self._sec_ID,
                              data_source=self._data_source)

        factor_and_return = get_clean_factor_and_forward_returns(factor=factor,
                                                                 prices=price,
                                                                 groupby_labels=IndexComp.get_industry_name_dict(),
                                                                 periods=self._periods)
        return factor_and_return

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
        self._factor_daily = self._factor_convert2daily() if self._convert_freq != FreqType.EOD else self._factor
        factor_and_return = self._get_clean_factor_and_fwd_return(self._factor_daily)

        for p in self._periods:
            self.quantile_tear_sheet(factor_and_return, p)
        self.top_bottom_tear_sheet(factor_and_return)
        self.mean_return_tear_sheet(factor_and_return)
        plt.show()
        return

    def create_ic_tear_sheet(self):
        self._factor_daily = self._factor_convert2daily() if self._convert_freq != FreqType.EOD else self._factor
        factor_and_return = self._get_clean_factor_and_fwd_return(self._factor_daily)
        ic = factor_information_coefficient(factor_and_return)
        plot_ic_ts(ic)
        plt.show()
        return



    def calc_rank_ic(self):
        tiaocang_date = self._trade_date
        ret = pd.Series(name='rank_IC')
        for j in range(0, len(tiaocang_date) - 1):
            date = tiaocang_date[j]
            next_date = tiaocang_date[j + 1]
            next_price = get_sec_price(date, next_date, self._factor[date].index.tolist(),
                                       data_source=self._data_source, csv_path=self._csv_path)
            next_return = (next_price.loc[next_date] - next_price.loc[date]) / next_price.loc[date]
            table_concat = pd.concat([self._factor[date], next_return], axis=1)
            tmp, _ = st.spearmanr(table_concat['factor'], table_concat[0])
            ret[date] = tmp
        n_groups = len(ret)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.35
        opacity = 0.4
        rects = plt.bar(index, ret, bar_width,alpha=opacity, color='b',label=  'IC')
        plt.xlabel('Group')
        plt.ylabel('Scores')
        plt.title('Scores by group and gender')
        plt.xticks(index + bar_width, tiaocang_date[:-1])
        plt.ylim(-1,1)
        plt.legend()
        plt.tight_layout()
        plt.show()
        return ret


if __name__ == "__main__":
    factor = FactorLoader('2014-01-05',
                          '2016-12-30',
                          {'MV': [FactorNormType.Null],
                           'INDUSTRY': [FactorNormType.Null],
                           'ROE': [FactorNormType.IndustryAndCapNeutral],
                           'RETURN': [FactorNormType.IndustryAndCapNeutral]})
    factor_data = factor.get_factor_data()

    analyzer = FactorAnalyzer(start_date='2014-01-30', end_date='2015-07-30', factor_raw={'Factor': factor_data['MV'],
                                                                                          'Freq': FreqType.EOM},
                              data_source=DataSource.WIND)
    analyzer.calc_rank_ic()
