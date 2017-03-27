# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
import pandas as pd
from PyFin.Utilities import pyFinAssert
from pyStratAlpha.enums import FreqType
from pyStratAlpha.enums import DfReturnType

_user = 'root'
_pwd = 'admin#123'
_server = '10.200.200.37'
_port = '3306'
_db_name = 'lhtz'


class MYSQLDataHandler(object):
    def __init__(self,
                 user=_user,
                 pwd=_pwd,
                 server=_server,
                 port=_port,
                 db_name=_db_name):
        self._conn_template = 'mysql+pymysql://{user}:{pwd}@{server}:{port}/{db_name}'
        self._user = user
        self._pwd = pwd
        self._server = server
        self._port = port
        self._db_name = db_name
        self._engine = self._create_conn(db_name=_db_name)

    def _create_conn(self, db_name):
        conn = create_engine(self._conn_template.format(user=self._user,
                                                        pwd=self._pwd,
                                                        server=self._server,
                                                        port=self._port,
                                                        db_name=db_name), echo=True)

        return conn

    def load_factor_data(self, start_date, end_date, sec_ids, field='close', freq=FreqType.EOD,
                         return_type=DfReturnType.DateIndexAndSecIDCol, table_name='sec_close'):
        """
        :param start_date: str, start date of the query period
        :param end_date: str, end date of the query period
        :param sec_ids: list of str, sec IDs
        :param freq: enum, optional, FreqType
        :param return_type: enum, optional, DfReturnType
        :param field: str, optional, filed of data to be queried
        :param table_name: str, optional, table name in sql database to be queried
        :return: pd.DataFrame, index = date, col = sec ID
        """
        pyFinAssert(freq == FreqType.EOD, ValueError, "for the moment the function only accepts freq type = EOD")
        sql = 'select tradeDate, secID, {field} from {table} where tradeDate >= \'{start_date}\' and ' \
              'tradeDate <= \'{end_date}\' '.format(field=field,
                                                    table=table_name,
                                                    start_date=start_date,
                                                    end_date=end_date)
        if len(sec_ids) > 1:
            sql += 'and secID in {tp_sec_ids}'.format(tp_sec_ids=tuple(sec_ids))
        else:
            sql += 'and secID in (\'{tp_sec_ids}\')'.format(tp_sec_ids=sec_ids[0])

        raw_data = pd.read_sql(sql, self._engine)
        ret = format_raw_data(raw_data, freq, field, return_type=return_type)
        return ret


def format_raw_data(raw_data, freq, field, return_type):
    ret = pd.DataFrame()
    if len(raw_data) > 0:
        if freq == FreqType.EOD:
            raw_data['tradeDate'] = pd.to_datetime(raw_data['tradeDate'])
        if return_type == DfReturnType.DateIndexAndSecIDCol:
            ret = raw_data.pivot(index='tradeDate', columns='secID', values=field)
        else:
            ret = raw_data['tradeDate', 'secID', field]
            ret = ret.set_index('tradeDate')

    return ret


if __name__ == "__main__":
    mysql = MYSQLDataHandler()
    print mysql.load_factor_data('2011-01-01', '2011-02-01', ['000001.SZ'])
