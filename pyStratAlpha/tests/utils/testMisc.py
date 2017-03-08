# -*- coding: utf-8 -*-

import unittest

import pandas as pd

from pyStratAlpha.utils import convert_to_non_cumul_return
from pyStratAlpha.utils import top


class TestMisc(unittest.TestCase):
    def testTop(self):
        data = pd.Series([10, 5, 3, 2, 1, 11, 22, -1])
        calculated = top(data, n=3)
        expected = pd.Series([22, 11, 10], index=pd.Int64Index([6, 5, 0], dtype='int64'))
        pd.util.testing.assert_series_equal(calculated, expected)

        data = pd.DataFrame({'a': [-1, 1, 2, 3, 10, 11, 100, 30, 50], 'b': [-1, 100, 20, 30, 10, 11, 10, 3, 5]})
        calculated = top(data, column='b', n=5)
        expected = pd.DataFrame({'a': [1, 3, 2, 11, 10], 'b': [100, 30, 20, 11, 10]},
                                index=pd.Int64Index([1, 3, 2, 5, 4], dtype='int64'))
        pd.util.testing.assert_frame_equal(calculated, expected)

    def testConvert2NonCumulReturn(self):
        data = pd.Series([1.0, 1.1, 1.2, 0.9])
        calculated = convert_to_non_cumul_return(data)
        expected = pd.Series([0.1, 0.0909090909091, -0.25], index=pd.Int64Index([1, 2, 3], dtype='int64'))
        pd.util.testing.assert_series_equal(calculated, expected)
