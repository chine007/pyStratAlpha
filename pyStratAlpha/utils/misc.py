# -*- coding: utf-8 -*-

import datetime as dt

import pandas as pd
from PyFin.Utilities import pyFinAssert
from matplotlib import font_manager
from pyStratAlpha.utils.data_provider import WindMarketDataHandler
from pyStratAlpha.utils.data_provider import TSMarketDataHandler
from pyStratAlpha.utils.data_provider import MYSQLDataHandler
from pyStratAlpha.enums import DataSource
from pyStratAlpha.enums import DfReturnType
from pyStratAlpha.enums import FreqType


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


def time_index_slicer(data, start_date, end_date):
    """
    :param data: pd.DataFrame, index = datetime.datetime
    :param start_date: str/datetime.datetime, start date of the horizon returned
    :param end_date: str/datetime.datetime, end date of the horizon returned
    :return: pd.DataFrame, time sliced data
    """

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
    if data_source == DataSource.WIND:
        price_data = WindMarketDataHandler.get_sec_price_on_date(start_date=start_date,
                                                                 end_date=end_date,
                                                                 sec_ids=sec_ids,
                                                                 freq=freq,
                                                                 field=field,
                                                                 return_type=return_type)
    elif data_source == DataSource.TUSHARE:
        price_data = TSMarketDataHandler.get_sec_price_on_date(start_date=start_date,
                                                               end_date=end_date,
                                                               sec_ids=sec_ids,
                                                               freq=freq,
                                                               field=field,
                                                               return_type=return_type)
    elif data_source == DataSource.CSV:
        price_data = pd.read_csv(csv_path, index_col=0)
        price_data.index = pd.to_datetime(price_data.index)
    elif data_source == DataSource.MYSQL_LOCAL:
        data_loader = MYSQLDataHandler()
        price_data = data_loader.load_factor_data(start_date=start_date,
                                                  end_date=end_date,
                                                  sec_ids=sec_ids,
                                                  freq=freq,
                                                  field=field,
                                                  return_type=return_type)
    else:
        raise NotImplementedError

    return price_data
