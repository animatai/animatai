# pylint: disable=missing-docstring, global-statement, invalid-name, too-few-public-methods
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


# Imports
# ======

import unittest
from animatai.stats import History
from gzutils.gzutils import DefaultDict, Logging


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('test_stats', DEBUG_MODE)


class TestStats(unittest.TestCase):
    def setUp(self):
        l.info('Testing stats...')

    def tearDown(self):
        l.info('...done with test_stats.')

    def test_collect_history(self):
        hist1 = History()
        hist2 = History()
        hist3 = History()

        hist1.add_dataset('h1', ['h1 text', 'h1 int'])
        hist2.add_dataset('h2', ['h1 text', 'h1 int'])
        hist3.add_dataset('h3', ['h1 text', 'h1 int'])

        for i in range(0, 3):
            hist1.add_row('h1', ['bla', i])
            hist2.add_row('h2', ['ha', i*10])
            hist3.add_row('h3', ['da', i*100])

        l.debug(History().get())
        self.assertTrue(History().get() == (['h1 text', 'h1 int', 'h1 text', 'h1 int', 'h1 text', 'h1 int'],
                                            [['bla', 0, 'ha', 0, 'da', 0],
                                             ['bla', 1, 'ha', 10, 'da', 100],
                                             ['bla', 2, 'ha', 20, 'da', 200]]))
