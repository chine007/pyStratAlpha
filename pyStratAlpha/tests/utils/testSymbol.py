# -*- coding: utf-8 -*-

import unittest

from pyStratAlpha.utils import data_yes_convert_to_wind
from pyStratAlpha.utils import remove_suffix
from pyStratAlpha.utils import wind_convert_to_data_yes


class TestSymbol(unittest.TestCase):
    def testDataYesConvert2Wind(self):
        data_yes_id = '000002.XSHE'
        ret = data_yes_convert_to_wind(data_yes_id)
        expected = '000002.sz'
        self.assertEqual(ret, expected)

        data_yes_id = ['000300.XSHG', '600300.XSHG', '000001.XSHE']
        ret = data_yes_convert_to_wind(data_yes_id)
        expected = ['000300.sh', '600300.sh', '000001.sz']
        self.assertEqual(ret, expected)

    def testWindConvert2DataYes(self):
        wind_id = '600300.SH'
        ret = wind_convert_to_data_yes(wind_id)
        expected = '600300.xshg'
        self.assertEqual(ret, expected)

        wind_id = ['000300.SH', '600300.SH', '000001.SZ']
        ret = wind_convert_to_data_yes(wind_id)
        expected = ['000300.xshg', '600300.xshg', '000001.xshe']
        self.assertEqual(ret, expected)

    def testRemoveSuffix(self):
        sec_id = '000300.SH'
        ret = remove_suffix(sec_id)
        expected = '000300'
        self.assertEqual(ret, expected)

        sec_id = ['000300.XSHG', '600300.XSHG', '000001.XSHE']
        ret = remove_suffix(sec_id)
        expected = ['000300', '600300', '000001']
        self.assertEqual(ret, expected)
