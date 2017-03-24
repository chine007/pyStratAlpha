# -*- coding: utf-8 -*-

from PyFin.DateUtilities import Calendar
from alphalens.performance import factor_returns
from alphalens.performance import mean_return_by_quantile
from alphalens.utils import get_clean_factor_and_forward_returns
from pyStratAlpha.analyzer.indexComp import IndexComp
from pyStratAlpha.enums import DataSource
from pyStratAlpha.utils import WindMarketDataHandler
import pandas as pd
from pyStratAlpha.strat.alpha.pseudoDCAM import load_sec_score
import numpy as np
import alphalens
from PyFin.api.DateUtilities import bizDatesList

_alphaLensFactorIndexName = ['date', 'asset']
_alphaLensFactorColName = 'factor'


class FactorAnalyzer(object):
    def __init__(self,
                 start_date,
                 end_date,
                 factor,
                 industry,
                 data_source=DataSource.WIND,
                 calendar='China.SSE'):
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
        self._startDate = start_date
        self._endDate = end_date
        self._factor = factor
        self._industry = industry
        self._dataSource = data_source

        self._factor.index = self._factor.index.rename(_alphaLensFactorIndexName)
        self._factor.name = _alphaLensFactorColName
        self._factor = self._factor.loc[
            self._factor.index.get_level_values(_alphaLensFactorIndexName[0]) >= self._startDate]
        self._factor = self._factor.loc[
            self._factor.index.get_level_values(_alphaLensFactorIndexName[0]) <= self._endDate]

        self._tradeDate = sorted(set(self._factor.index.get_level_values(_alphaLensFactorIndexName[0])))
        self._secID = sorted(set(self._factor.index.get_level_values(_alphaLensFactorIndexName[1]).tolist()))



    def _get_price_data(self):
        if self._dataSource == DataSource.WIND:
            price_data = WindMarketDataHandler.get_sec_price_on_date(self._tradeDate, self._secID)
        else:
            raise NotImplementedError
        return price_data

    def _get_clean_factor_and_fwd_return(self):
        factor = get_clean_factor_and_forward_returns(factor=self._factor,
                                                      prices=WindMarketDataHandler.get_sec_price_on_date(self._tradeDate[0],self._tradeDate[-1], self._secID),
                                                      groupby_labels=IndexComp.get_industry_name_dict())
        return factor

    def create_full_tear_sheet(self):

        factor = self._get_clean_factor_and_fwd_return()
        #factor_return = factor_returns(factor, long_short=True)
        #mean_quantile, std_qauntile = mean_return_by_quantile(factor,
                                                              #by_group=False,
                                                              #demeaned=True)


        alphalens.tears.create_turnover_tear_sheet(factor)

        print factor
        print type(factor)

        return

def load_sec_daily_score(path):
    ret = pd.read_csv(path, encoding='gbk')
    date_set = ret['tiaoCangDate'].drop_duplicates()
    ret_daily = pd.DataFrame()
    for i in range(0,6,1):
    #for i in range(0,len(date_set)-1,1):
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


if __name__ == "__main__":
    factor = load_sec_daily_score('sec_score.csv')
    print factor
    fa = FactorAnalyzer('2010-01-01','2016-08-01',factor,None)
    fa.create_full_tear_sheet()