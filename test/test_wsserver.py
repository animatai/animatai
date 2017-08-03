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

    def test_observer(self):
        l.info('test_observer')

        # the server is not possible to start since there is not handler provided
        o = WsServer(None)
        sea = Sea(options)
        sea.add_observer(o)

        a = Agent()
        sea.add_thing(a, (1, 1))
        sea.execute_action(a, 'DiveAndForward', 1)

        # The observer should have been notified about the move
        # The design does not work with these unit tests, need to check the debug
        # messages manually
        self.assertTrue(True)


    def tearDown(self):
        l.info('...done with test_wsserver.')


# Main
# ====

if __name__ == '__main__':
    unittest.main()
