# -*- coding: utf-8 -*-

import unittest
import numpy as np
import pandas as pd
from numpy.testing import assert_array_almost_equal
from pandas.util.testing import assert_series_equal
from pyStratAlpha.analyzer.factor.norm import get_industry_matrix
from pyStratAlpha.analyzer.factor.norm import neutralize
from pyStratAlpha.analyzer.factor.norm import normalize
from pyStratAlpha.analyzer.factor.norm import standardize
from pyStratAlpha.analyzer.factor.norm import winsorize


class TestNorm(unittest.TestCase):
    def setUp(self):
        index = ['000001.SZ', '000002.SZ', '000003.SZ', '000004.SZ', '000005.SZ', '000006.SZ', '000007.SZ', '000008.SZ',
                 '000009.SZ', '000010.SZ']
        factor = [24, 1.0, 1.1, 0.8, 0.5, 1.2, -1.0, -2, 1.0,
                  0.5]
        industry = ['801190.SI', '801190.SI', '801200.SI', '801200.SI', '801200.SI', '801200.SI', '801200.SI',
                    '801200.SI',
                    '801200.SI', '801201.SI']
        cap = [2.0, 2.0, 1.0, 3.0, 5.0, 1.0, 1.0, 1.0, 1.0,
               2.0]
        factor = pd.Series(factor, index=index, name='factor')
        industry1 = pd.Series(industry, index=index)
        industry2 = pd.Series(industry,
                              index=['000001.SZ', '000002.SZ', '100003.SZ', '000004.SZ', '000005.SZ', '000006.SZ',
                                     '000007.SZ', '000008.SZ', '000009.SZ', '000010.SZ'])
        cap = pd.Series(cap, index=index)
        self.data = {'factor': factor,
                     'industry1': industry1,
                     'industry2': industry2,
                     'cap': cap}

    def testWinsorize(self):
        factor = self.data['factor']
        calculated = winsorize(factor, nb_std_or_quantile=3)
        expected = pd.Series([23.5572063591, 1.0, 1.1, 0.8, 0.5, 1.2, -1.0, -2.0, 1.0, 0.5],
                             index=['000001.SZ', '000002.SZ', '000003.SZ', '000004.SZ', '000005.SZ', '000006.SZ',
                                    '000007.SZ', '000008.SZ', '000009.SZ', '000010.SZ'], name='factor')
        assert_series_equal(calculated, expected)

        calculated = winsorize(factor, nb_std_or_quantile=[0.025, 0.975])
        expected = pd.Series([18.87, 1.0, 1.1, 0.8, 0.5, 1.2, -1.0, -1.775, 1.0, 0.5],
                             index=['000001.SZ', '000002.SZ', '000003.SZ', '000004.SZ', '000005.SZ', '000006.SZ',
                                    '000007.SZ', '000008.SZ', '000009.SZ', '000010.SZ'], name='factor')
        assert_series_equal(calculated, expected)

    def testStandardize(self):
        factor = self.data['factor']
        calculated = standardize(factor)
        expected = pd.Series([2.81897066159, -0.226418028714, -0.213177208321, -0.252899669499, -0.292622130677,
                              -0.199936387929, -0.491234436567, -0.623642640493, -0.226418028714, -0.292622130677],
                             index=['000001.SZ', '000002.SZ', '000003.SZ', '000004.SZ', '000005.SZ', '000006.SZ',
                                    '000007.SZ', '000008.SZ', '000009.SZ', '000010.SZ'], name='factor')
        assert_series_equal(calculated, expected)

    def testGetIndustryMatrix(self):
        industry = self.data['industry1']
        calculated = get_industry_matrix(industry)
        expected = np.array([[1.0, 0.0, 0.0],
                             [1.0, 0.0, 0.0],
                             [0.0, 1.0, 0.0],
                             [0.0, 1.0, 0.0],
                             [0.0, 1.0, 0.0],
                             [0.0, 1.0, 0.0],
                             [0.0, 1.0, 0.0],
                             [0.0, 1.0, 0.0],
                             [0.0, 1.0, 0.0],
                             [0.0, 0.0, 1.0]])
        assert_array_almost_equal(calculated, expected)

        cap = self.data['cap']
        calculated = get_industry_matrix(industry, cap)
        expected = np.array([[1.0, 0.0, 0.0, 2.0],
                             [1.0, 0.0, 0.0, 2.0],
                             [0.0, 1.0, 0.0, 1.0],
                             [0.0, 1.0, 0.0, 3.0],
                             [0.0, 1.0, 0.0, 5.0],
                             [0.0, 1.0, 0.0, 1.0],
                             [0.0, 1.0, 0.0, 1.0],
                             [0.0, 1.0, 0.0, 1.0],
                             [0.0, 1.0, 0.0, 1.0],
                             [0.0, 0.0, 1.0, 2.0]])
        assert_array_almost_equal(calculated, expected)

    def testNeutralize(self):
        industry = self.data['industry1']
        factor = self.data['factor']
        calculated = neutralize(factor, industry)
        expected = pd.Series(
            [11.500000, -11.500000, 0.871429, 0.571429, 0.271429, 0.971429, -1.228571, -2.228571, 0.771429, 0.000000],
            index=['000001.SZ', '000002.SZ', '000003.SZ', '000004.SZ', '000005.SZ', '000006.SZ', '000007.SZ',
                   '000008.SZ',
                   '000009.SZ', '000010.SZ'], name='factor')
        assert_series_equal(calculated, expected)

        cap = self.data['cap']
        calculated = neutralize(factor, industry, cap)
        expected = pd.Series(
            [11.5, -11.5, 1.02122019764, 0.2958438702, -0.201944858399, 1.12122019764, -1.07877980236, -2.07877980236,
             0.92122019764, 1.7763568394e-15],
            index=['000001.SZ', '000002.SZ', '000003.SZ', '000004.SZ', '000005.SZ', '000006.SZ', '000007.SZ',
                   '000008.SZ', '000009.SZ', '000010.SZ'], name='factor')
        assert_series_equal(calculated, expected)

        industry = self.data['industry2']
        factor = self.data['factor']
        calculated = neutralize(factor, industry)
        expected = pd.Series(
            [1.15000000e+01, -1.15000000e+01, 2.22044605e-16, 7.16666667e-01,
             4.16666667e-01, 1.11666667e+00, -1.08333333e+00, -2.08333333e+00,
             9.16666667e-01, 0.00000000e+00],
            index=['000001.SZ', '000002.SZ', '000003.SZ', '000004.SZ', '000005.SZ', '000006.SZ', '000007.SZ',
                   '000008.SZ', '000009.SZ', '000010.SZ'], name='factor')
        assert_series_equal(calculated, expected)

    def testNormalize(self):
        factor = self.data['factor']
        industry = self.data['industry1']
        cap = self.data['cap']
        calculated = normalize(factor, industry, cap)
        expected = pd.Series(
            [1.521312e+00, -1.521312e+00, 1.377470e-01, 3.990483e-02, -2.723928e-02, 1.512355e-01, -1.455110e-01,
             -2.803957e-01, 1.242586e-01, 2.775558e-16],
            index=['000001.SZ', '000002.SZ', '000003.SZ', '000004.SZ', '000005.SZ', '000006.SZ', '000007.SZ',
                   '000008.SZ',
                   '000009.SZ', '000010.SZ'], name='factor')
        assert_series_equal(calculated, expected)
