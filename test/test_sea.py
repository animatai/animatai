# pylint: disable=missing-docstring, global-statement, invalid-name
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


# Imports
# ======

import unittest

from sea import Sea
from agents import Agent
from agents import Obstacle
from myutils import Logging


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('test_cachalot', DEBUG_MODE)


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

class TestCachalot(unittest.TestCase):

    def setUp(self):
        l.info('Testing cachalot...')

    def test_add_squid(self):
        l.info('test_add_squid')

        sea = Sea(options)

        for i in range(5, 4):
            self.assertTrue(len(sea.list_things_at((i, 2))) == 1)
            self.assertTrue(len(sea.list_things_at((i, 5))) == 1)

        for i in range(0, 50):
            self.assertTrue(isinstance(sea.list_things_at((i, 3))[0], Obstacle))


    def test_moving_cachalot(self):
        l.info('test_moving_cachalot')

        e = Sea(options)
        a = Agent()
        e.add_thing(a, (1, 1))

        self.assertTrue(a.location == (1, 1))
        e.execute_action(a, 'DiveAndForward', 1)
        self.assertTrue(a.location == (2, 2))

        # Should hit the wall
        e.execute_action(a, 'DiveAndForward', 1)
        self.assertTrue(a.location == (3, 2))

        e.execute_action(a, 'Forward', 1)
        self.assertTrue(a.location == (4, 2))

        e.execute_action(a, 'UpAndforward', 1)
        self.assertTrue(a.location == (5, 1))

        # check that the world is torus, should get back to the same location
        for _ in range(0, 50):
            e.execute_action(a, 'Forward', 1)

        self.assertTrue(a.location == (5, 1))

    def test_singing_cachalot(self):
        l.info('test_singing_cachalot')

        e = Sea(options)
        a = Agent()
        e.add_thing(a, (1, 1))

        # song at time=1 will be heard by other agents at time=2
        e.execute_ns_action(a, 'sign', 1)
        self.assertTrue(len(e.list_ns_artifacts_at(2)) == 1)


    def tearDown(self):
        l.info('...done with test_sea.')


# Main
# ====

if __name__ == '__main__':
    unittest.main()
