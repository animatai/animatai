# pylint: disable=missing-docstring, global-statement, invalid-name
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


# Imports
# ======

import unittest

from sea import Sea
from agents import Agent
from myutils import Logging
from wsserver import WsServer


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('test_wsserver', DEBUG_MODE)


# Unit tests
# ==========

lane = ('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n' +
        'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww\n' +
        'wwwwwsssswwwwwwwwwwwwwwwwwwwwwwwwwwsssswwwwwwwwwww\n')

# the mother and calf have separate and identical lanes
world = lane + lane + 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

options = {
    'world': [x for x in world.split("\n")]
}

class TestWsserver(unittest.TestCase):

    def setUp(self):
        l.info('Testing wsserver...')

    # No tests yet...

    def tearDown(self):
        l.info('...done with test_wsserver.')


# Main
# ====

if __name__ == '__main__':
    unittest.main()
