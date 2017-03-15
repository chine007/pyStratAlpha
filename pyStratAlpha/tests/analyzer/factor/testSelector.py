# -*- coding: utf-8 -*-
import datetime
import os
import unittest

import pandas as pd

from pyStratAlpha.analyzer.factor.selector import Selector
from pyStratAlpha.analyzer.indexComp.indexComp import IndexComp


class TestSelector(unittest.TestCase):
    def setUp(self):
        dir_name = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(dir_name, 'data//selector2.csv')

        factor_data = pd.read_csv(file_path)
        index = pd.MultiIndex.from_arrays(
            [[datetime.datetime.strptime(date, '%Y/%m/%d') for date in factor_data['tiaoCangDate1'].dropna().values],
             factor_data['secID1'].dropna().values], names=['tiaoCangDate', 'secID'])
        factor_score = pd.Series(data=factor_data['score'].dropna().values, index=index, name='score')

        index = pd.MultiIndex.from_arrays(
            [[datetime.datetime.strptime(date, '%Y/%m/%d') for date in factor_data['tiaoCangDate2'].dropna().values],
             factor_data['secID2'].dropna().values], names=['tiaoCangDate', 'secID'])
        factor_industry = pd.Series(data=factor_data['INDUSTRY'].dropna().values, index=index, name='INDUSTRY')

        index = pd.MultiIndex.from_arrays(
            [[datetime.datetime.strptime(date, '%Y/%m/%d') for date in factor_data['tiaoCangDate3'].dropna().values],
             factor_data['secID3'].dropna().values], names=['tiaoCangDate', 'secID'])
        factor_ind_wgt = pd.Series(data=factor_data['IND_WGT'].dropna().values, index=index, name='IND_WGT')

        index_comp = IndexComp(industry_weight=factor_ind_wgt)
        selector = Selector(sec_score=factor_score,
                            industry=factor_industry,
                            index_comp=index_comp,
                            nb_sec_selected_per_industry_min=5,
                            use_industry_name=True, nb_sec_selected_total=100,
                            ignore_zero_weight=False)

        selector.industry_neutral = True

        # TODO test case when selector is not industry neutral
        self.selector = selector

        self.test_result_neutral = factor_data['result_neutral'].dropna().values
        self.test_result_non_neutral = factor_data['result_non_neutral'].dropna().values

    def testSecSelectedUniverse(self):
        self.selector.industry_neutral = True
        calculated = self.selector.sec_selected_universe()
        expected = list(self.test_result_neutral)
        self.assertEqual(calculated, expected)

        self.selector.industry_neutral = False
        calculated = self.selector.sec_selected_universe()
        expected = list(self.test_result_non_neutral)
        self.assertEqual(calculated, expected)

    def testSecSelection(self):
        self.selector.industry_neutral = True
        self.selector.sec_selection()
        calculated = self.selector._secSelected
        expected = [['000034.SZ', '600201.SH', '000048.SZ', '002714.SZ', '600598.SH', '600965.SH', '002157.SZ',
                     '600226.SH', '600381.SH', '600583.SH', '600759.SH', '601857.SH', '600157.SH', '601808.SH',
                     '002010.SZ', '601216.SH', '002450.SZ', '600299.SH', '002326.SZ', '600061.SH', '300063.SZ',
                     '300072.SZ', '600176.SH', '002470.SZ', '002004.SZ', '002343.SZ', '600229.SH', '603077.SH',
                     '600688.SH', '600352.SH', '600889.SH', '600096.SH', '000973.SZ', '002002.SZ', '002643.SZ',
                     '002258.SZ', '600426.SH', '000627.SZ', '000707.SZ', '600143.SH', '600399.SH', '002075.SZ',
                     '000761.SZ', '000709.SZ', '600005.SH', '600478.SH', '600338.SH', '002466.SZ', '002460.SZ',
                     '600330.SH', '600549.SH', '600331.SH', '002600.SZ', '601899.SH', '600687.SH', '300032.SZ',
                     '300136.SZ', '600074.SH', '300296.SZ', '300207.SZ', '601231.SH', '002179.SZ', '300115.SZ',
                     '300088.SZ', '002475.SZ', '300014.SZ', '600703.SH', '000670.SZ', '002076.SZ', '600651.SH',
                     '002519.SZ', '002681.SZ', '002508.SZ', '002668.SZ', '000333.SZ', '002568.SZ', '000568.SZ',
                     '000796.SZ', '600090.SH', '600597.SH', '000995.SZ', '600073.SH', '600177.SH', '600398.SH',
                     '002612.SZ', '002640.SZ', '002291.SZ', '002517.SZ', '603001.SH', '002044.SZ', '002071.SZ',
                     '600086.SH', '002078.SZ', '002701.SZ', '000488.SZ', '002572.SZ', '000587.SZ', '002721.SZ',
                     '002263.SZ', '600466.SH', '600666.SH', '300267.SZ', '000078.SZ', '600664.SH', '002437.SZ',
                     '000963.SZ', '300026.SZ', '002019.SZ', '300199.SZ', '300003.SZ', '000590.SZ', '600518.SH',
                     '300244.SZ', '002294.SZ', '600079.SH', '600566.SH', '000591.SZ', '600276.SH', '002252.SZ',
                     '002573.SZ', '300056.SZ', '600452.SH', '600863.SH', '600021.SH', '000690.SZ', '600744.SH',
                     '600674.SH', '600483.SH', '300070.SZ', '600027.SH', '601872.SH', '600026.SH', '600270.SH',
                     '600548.SH', '600020.SH', '601006.SH', '601880.SH', '600751.SH', '000520.SZ', '000540.SZ',
                     '000718.SZ', '000150.SZ', '600340.SH', '000046.SZ', '600064.SH', '600376.SH', '000038.SZ',
                     '000069.SZ', '600606.SH', '000732.SZ', '000620.SZ', '000656.SZ', '600807.SH', '000560.SZ',
                     '600704.SH', '600361.SH', '600120.SH', '000889.SZ', '000062.SZ', '000715.SZ', '603123.SH',
                     '000759.SZ', '300144.SZ', '000430.SZ', '002707.SZ', '000007.SZ', '600054.SH', '600421.SH',
                     '600884.SH', '000068.SZ', '600234.SH', '600277.SH', '600629.SH', '002624.SZ', '002314.SZ',
                     '002619.SZ', '000546.SZ', '002457.SZ', '600585.SH', '601618.SH', '600068.SH', '002542.SZ',
                     '002504.SZ', '601669.SH', '601117.SH', '601668.SH', '002506.SZ', '002074.SZ', '300208.SZ',
                     '600416.SH', '600525.SH', '601727.SH', '002692.SZ', '600869.SH', '601222.SH', '300124.SZ',
                     '300242.SZ', '600312.SH', '300274.SZ', '600151.SH', '601877.SH', '600150.SH', '000801.SZ',
                     '300101.SZ', '600562.SH', '002023.SZ', '300182.SZ', '300033.SZ', '002280.SZ', '300297.SZ',
                     '600446.SH', '002415.SZ', '600654.SH', '002373.SZ', '002657.SZ', '300010.SZ', '002195.SZ',
                     '000555.SZ', '002383.SZ', '600850.SH', '002236.SZ', '002555.SZ', '300336.SZ', '600637.SH',
                     '002400.SZ', '300059.SZ', '300104.SZ', '300392.SZ', '000063.SZ', '300017.SZ', '002231.SZ',
                     '002104.SZ', '300299.SZ', '002089.SZ', '601288.SH', '601009.SH', '601398.SH', '601939.SH',
                     '601328.SH', '601688.SH', '000776.SZ', '601788.SH', '600999.SH', '600109.SH', '002085.SZ',
                     '600418.SH', '000887.SZ', '600686.SH', '600066.SH', '600660.SH', '002594.SZ', '000980.SZ',
                     '000550.SZ', '600166.SH', '002126.SZ', '600835.SH', '600894.SH', '600320.SH', '000008.SZ',
                     '600582.SH', '600499.SH', '300382.SZ', '002595.SZ', '601766.SH', '601717.SH', '300080.SZ',
                     '300266.SZ', '300203.SZ', '600031.SH', '300201.SZ', '002535.SZ', '300116.SZ', '601608.SH',
                     '600848.SH', '002691.SZ', '002526.SZ', '002122.SZ', '300145.SZ', '600243.SH', '600862.SH',
                     '002690.SZ', '600087.SH', '000556.SZ', '000033.SZ', '000805.SZ', '600709.SH']]
        self.assertEqual(list(calculated.values), expected)

        self.selector.industry_neutral = False
        self.selector.sec_selection()
        calculated = self.selector._secSelected
        expected = [
            ['002555.SZ', '002506.SZ', '601872.SH', '002074.SZ', '600177.SH', '300182.SZ', '002573.SZ', '002010.SZ',
             '600466.SH', '601688.SH', '300033.SZ', '300336.SZ', '000776.SZ', '002280.SZ', '601216.SH', '000540.SZ',
             '601788.SH', '600835.SH', '600637.SH', '002450.SZ', '600299.SH', '000718.SZ', '600398.SH', '000150.SZ',
             '300032.SZ', '000560.SZ', '600666.SH', '300297.SZ', '300136.SZ', '300208.SZ', '300267.SZ', '600999.SH',
             '002400.SZ', '600340.SH', '002612.SZ', '600446.SH', '002415.SZ', '600109.SH', '002085.SZ', '000712.SZ',
             '000046.SZ', '002326.SZ', '600064.SH', '600074.SH', '300296.SZ', '600061.SH', '000034.SZ', '600201.SH',
             '600150.SH', '000078.SZ', '600629.SH', '002568.SZ', '600654.SH', '600416.SH', '300059.SZ', '600894.SH',
             '600026.SH', '600418.SH', '300063.SZ', '600664.SH', '002437.SZ', '600376.SH', '000038.SZ', '600320.SH',
             '300104.SZ', '000963.SZ', '300207.SZ', '600704.SH', '601901.SH', '000008.SZ', '600525.SH', '000415.SZ',
             '000063.SZ', '300026.SZ', '300056.SZ', '002019.SZ', '600452.SH', '300072.SZ', '600863.SH', '600381.SH',
             '002519.SZ', '002373.SZ', '300199.SZ', '002624.SZ', '601318.SH', '600021.SH', '000048.SZ', '601601.SH',
             '600176.SH', '000887.SZ', '600361.SH', '002681.SZ', '002508.SZ', '601231.SH', '600478.SH', '300392.SZ',
             '002657.SZ', '600030.SH', '002143.SZ', '000069.SZ', '600686.SH']]
        self.assertEqual(list(calculated.values), expected)
