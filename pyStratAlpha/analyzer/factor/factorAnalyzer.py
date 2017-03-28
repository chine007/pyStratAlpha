# -*- coding: utf-8 -*-

from PyFin.DateUtilities import Calendar
from alphalens.utils import get_clean_factor_and_forward_returns
from pyStratAlpha.analyzer.indexComp import IndexComp
from pyStratAlpha.enums import DataSource
from pyStratAlpha.utils import WindMarketDataHandler
import alphalens
from PyFin.api.DateUtilities import bizDatesList
import pandas as pd
import matplotlib.pyplot as plt

_alphaLensFactorIndexName = ['date', 'asset']
_alphaLensFactorColName = 'factor'


class FactorAnalyzer(object):
    def __init__(self,
                 start_date,
                 end_date,
                 factor,
                 industry,
                 data_source=DataSource.WIND,
                 calendar='China.SSE',
                 periods =[1,5,10]):
        """
        :param factor: pd.Series, multi index=[tradeDate, secID]  columns = [factor]
        :param industry: pd.Series/dict, Either A MultiIndex Series indexed by date and asset, containing the period
        wise group codes for each asset, or a dict of asset to group mappings. If a dict is passed, it is assumed that
        group mappings are unchanged for the entire time period of the passed factor data.
        :param data_source: enum, DataSource type
        :param calendar: PyFin.Calendar type
        :return:
        """
        self._calendar = Calendar(calendar)
        self._start_date = start_date
        self._end_date = end_date
        self._factor = factor
        self._industry = industry
        self._data_dource = data_source
        self._periods = periods

        self._factor.index = self._factor.index.rename(_alphaLensFactorIndexName)
        self._factor.name = _alphaLensFactorColName
        self._factor = self._factor.loc[
            self._factor.index.get_level_values(_alphaLensFactorIndexName[0]) >= self._start_date]
        self._factor = self._factor.loc[
            self._factor.index.get_level_values(_alphaLensFactorIndexName[0]) <= self._end_date]

        self._trade_date = sorted(set(self._factor.index.get_level_values(_alphaLensFactorIndexName[0])))
        self._sec_ID = sorted(set(self._factor.index.get_level_values(_alphaLensFactorIndexName[1]).tolist()))



    def _get_price_data(self):
        if self._data_dource == DataSource.WIND:
            price_data = WindMarketDataHandler.get_sec_price_on_date(self._trade_date, self._sec_ID)
        else:
            raise NotImplementedError
        return price_data

    def _get_clean_factor_and_fwd_return(self):
        price = WindMarketDataHandler.get_sec_price_on_date(self._trade_date[0], self._trade_date[-1], self._sec_ID)
        factor = get_clean_factor_and_forward_returns(factor=self._factor,
                                                      prices=price,
                                                      groupby_labels=IndexComp.get_industry_name_dict(),
                                                      periods=self._periods)
        return factor

    def create_full_tear_sheet(self):

        factor = self._get_clean_factor_and_fwd_return()
        for p in self._periods:
            quantile_tear_sheet(factor,p)
        top_bottom_tear_sheet(factor)

        return

def load_sec_daily_score(path):
    ret = pd.read_csv(path, encoding='gbk')
    date_set = ret['tiaoCangDate'].drop_duplicates()
    ret_daily = pd.DataFrame()
    for i in range(0,len(date_set)-1,1):
        date = bizDatesList('China.SSE', date_set.values[i], date_set.values[i+1])
        secID = ret['secID'][date_set.index[i]:date_set.index[i+1]]
        score = ret['score'][date_set.index[i]:date_set.index[i+1]]
        for j in range(0,len(date)-1,1):
            tiaoCangDate = pd.Series([date[j].strftime("%Y-%m-%d")]*(date_set.index[i+1]-date_set.index[i]),name='tiaoCangDate',index=range(date_set.index[i],date_set.index[i+1]))
            ret_daily = pd.concat([ret_daily,pd.DataFrame([tiaoCangDate,secID,score]).T])
    ret_daily ['tiaoCangDate'] = pd.to_datetime(ret_daily ['tiaoCangDate'])
    ret_daily  = ret_daily .set_index(['tiaoCangDate', 'secID'])
    ret_daily  = ret_daily ['score']
    return ret_daily

def quantile_tear_sheet(factor_data,p):
    gf = alphalens.tears.GridFigure(rows=1, cols=1)
    mean_ret_quant_daily, std_quant_daily = alphalens.performance.mean_return_by_quantile(factor_data,
                                                                         by_date=True,
                                                                         by_group=False,
                                                                         demeaned=True)

    alphalens.plotting.plot_cumulative_returns_by_quantile(mean_ret_quant_daily[p],
                                                     period=p,
                                                     ax=gf.next_row())

def top_bottom_tear_sheet(factor_data):
    mean_return_by_q_daily, std_err = alphalens.performance.mean_return_by_quantile(factor_data, by_date=True)
    quant_return_spread, std_err_spread = alphalens.performance.compute_mean_returns_spread(mean_return_by_q_daily,
                                                                                        upper_quant=5,
                                                                                        lower_quant=1,
                                                                                        std_err=std_err)
    alphalens.plotting.plot_mean_quantile_returns_spread_time_series(quant_return_spread, std_err_spread);



if __name__ == "__main__":
    factor = load_sec_daily_score('sec_score.csv')
    fa = FactorAnalyzer('2010-01-01','2016-08-01',factor,None)
    fa.create_full_tear_sheet()