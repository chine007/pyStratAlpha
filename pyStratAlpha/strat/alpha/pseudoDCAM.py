# -*- coding: utf-8 -*-
from pprint import pprint

import pandas as pd
from PyFin.DateUtilities import Calendar
from PyFin.DateUtilities import Date

from pyStratAlpha.analyzer.factor import DCAMAnalyzer
from pyStratAlpha.analyzer.factor import FactorLoader
from pyStratAlpha.analyzer.factor import Selector
from pyStratAlpha.analyzer.indexComp import IndexComp
from pyStratAlpha.analyzer.portfolio import Portfolio
from pyStratAlpha.enums import DCAMFactorType
from pyStratAlpha.enums import DataSource
from pyStratAlpha.enums import FactorICSign
from pyStratAlpha.enums import FactorNormType
from pyStratAlpha.enums import FactorWeightType
from pyStratAlpha.enums import FreqType
from pyStratAlpha.utils import time_counter

_secSelectedPath = 'sec_selected.csv'
_secScorePath = 'secScore.csv'
_secPricePath = 'priceData.csv'


def load_sec_score(path):
    ret = pd.read_csv(path, encoding='gbk')
    ret['tiaoCangDate'] = pd.to_datetime(ret['tiaoCangDate'])
    ret = ret.set_index(['tiaoCangDate', 'secID'])
    ret = ret['score']
    return ret


def load_sec_selected(path):
    ret = pd.read_csv(path, encoding='gbk')
    ret['tiaoCangDate'] = pd.to_datetime(ret['tiaoCangDate'])
    ret = ret.set_index(['tiaoCangDate', 'secID'])
    ret = ret[['weight', 'INDUSTRY']]
    return ret


@time_counter
def dcam_strat_main(factor_loader_params,
                    analyzer_params,
                    selector_params,
                    portfolio_params,
                    update_params):
    # FactorLoader params
    start_date = factor_loader_params['start_date']
    end_date = factor_loader_params['end_date']
    factor_norm_dict = factor_loader_params['factor_norm_dict']

    # dcam analyzer params
    factor_weight_type = analyzer_params.get('factor_weight_type', FactorWeightType.ICWeight)
    tiaocang_date_window_size = analyzer_params.get('tiaocang_date_window_size', 12)
    save_sec_score = analyzer_params.get('save_sec_score', True)

    # selector params
    save_sec_selected = selector_params.get('save_sec_selected', True)
    nb_sec_selected_per_industry_min = selector_params.get('nb_sec_selected_per_industry_min', 5)
    use_industry_name = selector_params.get('use_industry_name', True)
    nb_sec_selected_total = selector_params.get('nb_sec_selected_total', 100)
    ignore_zero_weight = selector_params.get('ignore_zero_weight', False)

    # portfolio params
    benchmark_sec_id = portfolio_params.get('benchmark_sec_id', '000905.SH')
    re_balance_freq = portfolio_params.get('re_balance_freq', FreqType.EOM)
    initial_capital = portfolio_params.get('initial_capital', 1000000000.0)
    filter_return_on_tiaocang_date = portfolio_params.get('filter_return_on_tiaocang_date', 0.09)
    data_source = portfolio_params.get('data_source', DataSource.WIND)

    update_factor = update_params.get('update_factor', False)
    update_sec_score = update_params.get('update_sec_score', False)
    update_sec_select = update_params.get('update_sec_select', False)

    if update_factor:

        factor = FactorLoader(start_date=start_date,
                              end_date=end_date,
                              factor_norm_dict=factor_norm_dict)
        factor_data = factor.get_factor_data()
    else:
        # TODO
        factor = None
        factor_data = None
        pass

    if update_sec_score:
        layer_factor = [factor_data[name] for name in factor_norm_dict.keys() if
                        factor_norm_dict[name][1] == DCAMFactorType.layerFactor]
        alpha_factor = [factor_data[name] for name in factor_norm_dict.keys() if
                        factor_norm_dict[name][1] == DCAMFactorType.alphaFactor]
        alpha_factor_sign = [factor_data[name][2] for name in factor_norm_dict.keys() if
                             factor_norm_dict[name][1] == DCAMFactorType.alphaFactor]
        analyzer = DCAMAnalyzer(layer_factor=layer_factor,
                                alpha_factor=alpha_factor,
                                sec_return=factor_data['RETURN'],
                                tiaocang_date=factor.get_tiaocang_date(),
                                tiaocang_date_window_size=tiaocang_date_window_size,
                                save_sec_score=save_sec_score,
                                factor_weight_type=factor_weight_type,
                                alpha_factor_sign=alpha_factor_sign)

        sec_score = analyzer.calc_sec_score()
    else:
        sec_score = load_sec_score(_secScorePath)

    if update_sec_select:
        index_comp = IndexComp(industry_weight=factor_data['IND_WGT'])
        selector = Selector(sec_score=sec_score,
                            industry=factor_data['INDUSTRY'],
                            nb_sec_selected_per_industry_min=nb_sec_selected_per_industry_min,
                            index_comp=index_comp,
                            save_sec_selected=save_sec_selected,
                            use_industry_name=use_industry_name,
                            nb_sec_selected_total=nb_sec_selected_total,
                            ignore_zero_weight=ignore_zero_weight)
        selector.industry_neutral = True
        selector.sec_selection()
        sec_selected = selector.sec_selected_full_info
        pprint(selector.sec_selected_full_info)
    else:
        sec_selected = load_sec_selected(_secSelectedPath)

    # construct strategy ptf
    # 价格数据需要使用到最后一个调仓日的后一个月末
    sse_cal = Calendar('China.SSE')
    end_date_for_price_data = str(sse_cal.advanceDate(Date.strptime(end_date), '1m'))
    strategy = Portfolio(sec_selected=sec_selected,
                         end_date=end_date_for_price_data,
                         initial_capital=initial_capital,
                         filter_return_on_tiaocang_date=filter_return_on_tiaocang_date,
                         data_source=data_source,
                         benchmark_sec_id=benchmark_sec_id,
                         re_balance_freq=re_balance_freq)
    strategy.evaluate_ptf_return()


if __name__ == "__main__":
    factor_norm_dict_parameters = {'MV': [FactorNormType.Null, DCAMFactorType.layerFactor, FactorICSign.Null],
                                   'BP_LF': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.layerFactor,
                                             FactorICSign.Null],
                                   'EquityGrowth_YOY': [FactorNormType.IndustryAndCapNeutral,
                                                        DCAMFactorType.layerFactor,
                                                        FactorICSign.Null],
                                   'ROE': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.layerFactor,
                                           FactorICSign.Null],
                                   'STDQ': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.layerFactor,
                                            FactorICSign.Null],
                                   'EP2_TTM': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.alphaFactor,
                                               FactorICSign.Positive],
                                   'SP_TTM': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.alphaFactor,
                                              FactorICSign.Positive],
                                   'GP2Asset': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.alphaFactor,
                                                FactorICSign.Negative],
                                   'PEG': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.alphaFactor,
                                           FactorICSign.Positive],
                                   'ProfitGrowth_Qr_YOY': [FactorNormType.IndustryAndCapNeutral,
                                                           DCAMFactorType.alphaFactor,
                                                           FactorICSign.Positive],
                                   'TO_adj': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.alphaFactor,
                                              FactorICSign.Negative],
                                   'PPReversal': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.alphaFactor,
                                                  FactorICSign.Negative],
                                   'RETURN': [FactorNormType.IndustryAndCapNeutral, DCAMFactorType.returnFactor,
                                              FactorICSign.Null],
                                   'INDUSTRY': [FactorNormType.Null, DCAMFactorType.industryFactor, FactorICSign.Null],
                                   'IND_WGT': [FactorNormType.Null, DCAMFactorType.indexWeight, FactorICSign.Null]}

    factor_loader_parameters = {'start_date': '2010-12-05',
                                'end_date': '2013-12-30',
                                'factor_norm_dict': factor_norm_dict_parameters}

    analyzer_parameters = {'factor_weight_type': FactorWeightType.EqualWeight,
                           'tiaocang_date_window_size': 12}

    selector_parameters = {'save_sec_selected': True}

    portfolio_parameters = {'benchmark_sec_id': '000905.SH',
                            're_balance_freq': FreqType.EOM}

    update_parameters = {'update_factor': True,
                         'update_sec_score': True,
                         'update_sec_select': True}

    dcam_strat_main(factor_loader_params=factor_loader_parameters,
                    analyzer_params=analyzer_parameters,
                    selector_params=selector_parameters,
                    portfolio_params=portfolio_parameters,
                    update_params=update_parameters)
