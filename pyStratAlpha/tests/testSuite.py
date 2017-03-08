# -*- coding: utf-8 -*-

import os
import sys
import unittest

import pyStratAlpha.tests.analyzer as analyzer
import pyStratAlpha.tests.maths as maths
import pyStratAlpha.tests.strat as strat
import pyStratAlpha.tests.utils as utils

thisFilePath = os.path.abspath(__file__)

sys.path.append(os.path.sep.join(thisFilePath.split(os.path.sep)[:-2]))


def test():
    print('Python ' + sys.version)
    suite = unittest.TestSuite()

    tests = unittest.TestLoader().loadTestsFromTestCase(analyzer.TestCleanData)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(analyzer.TestNorm)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(analyzer.TestDynamicContext)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(analyzer.TestFactorLoader)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(analyzer.TestNavAnalyzer)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(maths.TestMatrix)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(maths.TestStats)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(strat.TestPseudoDCAM)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(utils.TestDateUtils)
    suite.addTests(tests)

    res = unittest.TextTestRunner(verbosity=3).run(suite)
    if len(res.errors) >= 1 or len(res.failures) >= 1:
        sys.exit(-1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    test()
