# -*- coding: utf-8 -*-

import datetime as dt

import pandas as pd
from PyFin.Utilities import pyFinAssert
from empyrical import cum_returns
from matplotlib import font_manager

from pyStratAlpha.enums import DataSource
from pyStratAlpha.enums import DfReturnType
from pyStratAlpha.enums import FreqType
from pyStratAlpha.utils.data_provider import MYSQLDataHandler
from pyStratAlpha.utils.data_provider import TSMarketDataHandler
from pyStratAlpha.utils.data_provider import WindMarketDataHandler

try:
    from WindPy import w
except ImportError:
    pass


def top(df, column=None, n=5):
    """
    :param df: pd.DataFrame/Series
    :param column: str, col name to be sorted
    :param n: int, optional, top n element to be returned
    :return: pd.Series, larget n element in col
    """
    if isinstance(df, pd.Series):
        ret = df.sort_values(ascending=False)[:n]
    else:
        pyFinAssert(column is not None, "Specify the col name or use pandas Series type of data")
        ret = df.sort_values(by=column, ascending=False)[:n]

    return ret


def convert_to_non_cumul_return(returns):
    """
    :param returns: pd.Series, daily cumul returns
    :return: pd.Series, daily non-cumul returns
    """
    daily_returns = returns.pct_change()
    daily_returns.dropna(inplace=True)
    return daily_returns


def time_index_slicer(data, start_date, end_date, date_index_name='tradeDate'):
    """
    :param data: pd.DataFrame, index = datetime.datetime
    :param start_date: str/datetime.datetime, start date of the horizon returned
    :param end_date: str/datetime.datetime, end date of the horizon returned
    :return: pd.DataFrame, time sliced data
    """
    if isinstance(data.index, pd.MultiIndex):
        ret = data.loc[data.index.get_level_values(date_index_name) >= start_date, :]
        ret = ret.loc[ret.index.get_level_values(date_index_name) <= end_date, :]
    else:
        ret = data.loc[data.index >= start_date]
        ret = ret.loc[ret.index <= end_date]
    return ret


def fig_style(ax, legend, x_label, y_label, legend_loc='upper right'):
    font = font_manager.FontProperties(family='SimHei', style='normal', size=16, weight='normal', stretch='normal')
    ax.legend(legend, prop={'size': 12}, loc=legend_loc)
    ax.title.set_font_properties(font)
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    ax.set_facecolor('white')
    ax.grid(color='gray', alpha=0.2, axis='y')
    return ax


def time_counter(func):
    def wrapper(*args, **kwargs):
        start_time = dt.datetime.now()
        print("Start: %s" % start_time)
        ret = func(*args, **kwargs)
        end_time = dt.datetime.now()
        print("End : %s" % end_time)
        print("Elapsed: %s" % (end_time - start_time))
        return ret

    return wrapper


def get_sec_price(start_date, end_date, sec_ids, data_source, freq=FreqType.EOD, field=['close'],
                  return_type=DfReturnType.DateIndexAndSecIDCol, csv_path=None):
    """
    :param start_date: datetime, start date of query date
    :param end_date: datetime, end date of query date
    :param sec_ids: list of str, sec ids
    :param data_source: enum, source of data
    :param freq: FreqType
    :param field: price type
    :param return_type: DfReturnType
    :param csv_path: str, path of csv file if data_source = csv
    :return: pd.DataFrame
    """

    def route(source):
        if source == DataSource.WIND:
            return WindMarketDataHandler.get_sec_price_on_date
        elif source == DataSource.TUSHARE:
            return TSMarketDataHandler.get_sec_price_on_date
        elif source == DataSource.MYSQL_LOCAL:
            return MYSQLDataHandler().load_factor_data

    if data_source == DataSource.WIND or data_source == DataSource.TUSHARE or data_source == DataSource.MYSQL_LOCAL:
        ret = route(data_source)(start_date=start_date,
                                 end_date=end_date,
                                 sec_ids=sec_ids,
                                 freq=freq,
                                 field=field,
                                 return_type=return_type)
    elif data_source == DataSource.CSV:
        ret = pd.read_csv(csv_path)
        ret['tradeDate'] = pd.to_datetime(ret['tradeDate'])
        ret = ret.set_index('tradeDate')
    else:
        raise NotImplementedError

    return ret


def get_sec_return(start_date, end_date, sec_ids, data_source=DataSource.WIND, freq=FreqType.EOD,
                   field=['close'], return_type=DfReturnType.DateIndexAndSecIDCol, is_cumul=False,
                   csv_path=None):
    """
    :param start_date: str, start date of the query period
    :param end_date: str, end date of the query period
    :param sec_ids: list of str, sec IDs
    :param data_source: enum, source of data
    :param field: str, filed of data to be queried
    :param return_type
    :param freq: FreqType
    :param is_cumul: return is cumul or not
    :param csv_path: str, csv file path
    :return: pd.DataFrame, index = date, col = sec ID
    """

    ret = get_sec_price(start_date=start_date,
                        end_date=end_date,
                        sec_ids=sec_ids,
                        data_source=data_source,
                        freq=freq,
                        field=field,
                        return_type=return_type,
                        csv_path=csv_path)
    ret = ret.pct_change()
    if is_cumul:
        ret = ret.fillna(0)
        ret = cum_returns(ret, starting_value=1.0)
    else:
        ret = ret.dropna()
    return ret
