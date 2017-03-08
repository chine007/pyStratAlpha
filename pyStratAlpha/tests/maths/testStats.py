# -*- coding: utf-8 -*-
import unittest

from pyStratAlpha.maths.stats import running_sum


class TestStats(unittest.TestCase):
    def testRunningSum(self):
        calculated = list(running_sum([1, 2, 3, 4], 3))
        expected = [6, 9]
        self.assertListEqual(calculated, expected, "Calculated Running Sum is wrong")

        calculated = list(running_sum([1, 2, 3, 4], 2))
        expected = [3, 5, 7]
        self.assertListEqual(calculated, expected, "Calculated Running Sum is wrong")
