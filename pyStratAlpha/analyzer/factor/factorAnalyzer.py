# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyFin import DateUtilities
from PyFin.api.DateUtilities import bizDatesList
from alphalens.performance import mean_return_by_quantile
from alphalens.performance import compute_mean_returns_spread
from alphalens.performance import factor_information_coefficient
from alphalens.utils import get_clean_factor_and_forward_returns
from alphalens.plotting import plot_mean_quantile_returns_spread_time_series
from alphalens.plotting import plot_cumulative_returns_by_quantile
from alphalens.plotting import plot_ic_hist
from alphalens.plotting import plot_monthly_ic_heatmap
from alphalens.tears import GridFigure
from alphalens.plotting import plot_quantile_returns_bar
from pyStratAlpha.analyzer.indexComp import IndexComp
from pyStratAlpha.enums import DataSource
from pyStratAlpha.enums import FreqType
from pyStratAlpha.utils import get_sec_price
from pyStratAlpha.enums import FactorNormType
from pyStratAlpha.utils import time_index_slicer
from pyStratAlpha.analyzer.factor import FactorLoader

_alphaLensFactorIndexName = ['date', 'asset']
_alphaLensFactorColName = 'factor'


class FactorAnalyzer(object):
    def __init__(self,
                 start_date,
                 end_date,
                 factor_raw,
                 industry=None,
                 data_source=DataSource.WIND,
                 calendar='China.SSE',
                 periods=None,
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

        self._calendar = DateUtilities.Calendar(calendar)
        self._start_date = start_date
        self._end_date = end_date
        self._industry = industry
        self._data_source = data_source
        self._periods = [1, 5, 10] if periods is None else periods
        self._factor = time_index_slicer(factor_raw['Factor'], start_date=start_date, end_date=end_date,
                                         date_index_name='tiaoCangDate')
        self._factor_freq = factor_raw['Freq']
        self._factor_daily = None
        self._factor.index = self._factor.index.rename(_alphaLensFactorIndexName)
        self._factor.name = _alphaLensFactorColName
        self._tiaocang_date = sorted(set(self._factor.index.get_level_values(_alphaLensFactorIndexName[0])))
        self._tiaocang_date = pd.to_datetime(self._tiaocang_date)
        self._sec_ID = sorted(set(self._factor.index.get_level_values(_alphaLensFactorIndexName[1])))
        self._csv_path = kwargs.get('csv_path', None)

    def _factor_convert2daily(self):
        tiaocang_date_list = self._tiaocang_date
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

    def _get_clean_factor_and_fwd_return(self, factor_score, freq):
        price = get_sec_price(start_date=str(self._tiaocang_date[0])[:10],
                              end_date=str(self._tiaocang_date[-1])[:10],
                              sec_ids=self._sec_ID,
                              data_source=self._data_source,
                              freq=freq)

        factor_and_return = get_clean_factor_and_forward_returns(factor=factor_score,
                                                                 prices=price,
                                                                 groupby_labels=IndexComp.get_industry_name_dict(),
                                                                 periods=self._periods)
        return factor_and_return

    @staticmethod
    def quantile_tear_sheet(factor_and_return, p):
        gf = GridFigure(rows=1, cols=1)
        mean_quantile_daily, std_quantile_daily = mean_return_by_quantile(factor_and_return,
                                                                          by_date=True,
                                                                          by_group=False,
                                                                          demeaned=True)

        plot_cumulative_returns_by_quantile(mean_quantile_daily[p],
                                            period=p,
                                            ax=gf.next_row())

    @staticmethod
    def top_bottom_tear_sheet(factor_and_return, quantile=None):
        if quantile is None:
            quantile = [1, 5]
        mean_return_by_q_daily, std_err = mean_return_by_quantile(factor_and_return, by_date=True)
        quant_return_spread, std_err_spread = compute_mean_returns_spread(mean_return_by_q_daily,
                                                                          upper_quant=quantile[1],
                                                                          lower_quant=quantile[0],
                                                                          std_err=std_err)
        plot_mean_quantile_returns_spread_time_series(quant_return_spread, std_err_spread)

    @staticmethod
    def mean_return_tear_sheet(factor_and_return):
        mean_return_by_q, std_err_by_q = mean_return_by_quantile(factor_and_return, by_group=False)
        plot_quantile_returns_bar(mean_return_by_q)

    def create_full_return_tear_sheet(self):
        self._factor_daily = self._factor_convert2daily() if self._factor_freq != FreqType.EOD else self._factor
        factor_and_return = self._get_clean_factor_and_fwd_return(self._factor_daily)

        for p in self._periods:
            self.quantile_tear_sheet(factor_and_return, p)
        self.top_bottom_tear_sheet(factor_and_return)
        self.mean_return_tear_sheet(factor_and_return)
        plt.show()
        return

    def create_ic_tear_sheet(self):
        factor_and_return = self._get_clean_factor_and_fwd_return(self._factor, self._factor_freq)
        ic = factor_information_coefficient(factor_and_return)
        plot_ic_hist(ic)
        self.ic_bar_tear_sheet(ic)
        plot_monthly_ic_heatmap(ic)
        plt.show()
        return

    @staticmethod
    def ic_bar_tear_sheet(ic):
        n_groups = len(ic.index)
        plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.35
        opacity = 0.4
        ic_series = []
        for i in range(0, len(ic.values)):
            ic_series.append(ic.values[i][0])
        plt.bar(index, ic_series, bar_width, alpha=opacity, color='b', label='IC')
        plt.xlabel('Date')
        plt.ylabel('Rank_IC')
        plt.xticks(index + bar_width, ic.index[:-1].date)
        plt.ylim(-1, 1)
        plt.legend()
        plt.tight_layout()


if __name__ == "__main__":
    factor = FactorLoader('2014-01-05',
                          '2016-12-30',
                          {'MV': [FactorNormType.Null],
                           'INDUSTRY': [FactorNormType.Null],
                           'ROE': [FactorNormType.IndustryAndCapNeutral],
                           'RETURN': [FactorNormType.IndustryAndCapNeutral]})
    factor_data = factor.get_factor_data()

    analyzer = FactorAnalyzer(start_date='2014-01-30',
                              end_date='2016-07-30',
                              factor_raw={'Factor': factor_data['MV'], 'Freq': FreqType.EOM},
                              data_source=DataSource.WIND,
                              periods=[1, 2, 3])
    analyzer.create_ic_tear_sheet()
