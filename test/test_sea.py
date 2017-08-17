# pylint: disable=missing-docstring, global-statement, invalid-name
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


# Imports
# ======

import unittest

from worlds.sea import Sea
from worlds.sea import Squid
from agents import Agent
from agents import Obstacle
from myutils import Logging


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('test_cachalot', DEBUG_MODE)


# Unit tests
# ==========

lane = ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n' +
        '                                                  \n' +
        '     ssss                          ssss           \n')

# the mother and calf have separate and identical lanes
things = lane + lane + 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

options = {
    'things': things.split('\n'),
    'width': 50,
    'height': 7,
    'agents': {
        'cachelot': {
            'sensors': [None, Squid],
            'motors': [('eat_and_forward', ['eat', 'forward']),
                       ('forward', ['forward']),
                       ('dive_and_forward', ['down', 'forward']),
                       ('up_and_forward', ['up', 'forward']),
                       ('sing', ['sing'])
                      ],
        }
    },
}

class TestCachalot(unittest.TestCase):

    def setUp(self):
        l.info('Testing cachalot...')

    def test_add_squid(self):
        l.info('test_add_squid')

        sea = Sea(options)

        for i in range(5, 9):
            self.assertTrue(len(sea.list_things_at((i, 2))) == 1)
            self.assertTrue(len(sea.list_things_at((i, 5))) == 1)

        for i in range(0, 50):
            self.assertTrue(isinstance(sea.list_things_at((i, 3))[0], Obstacle))


    def test_moving_cachalot(self):
        l.info('test_moving_cachalot')

        e = Sea(options)
        a = Agent(None, 'cachelot')
        e.add_thing(a, (1, 1))

        self.assertTrue(a.location == (1, 1))
        e.execute_action(a, 'dive_and_forward', 1)
        self.assertTrue(a.location == (2, 2))

        # Should hit the wall
        e.execute_action(a, 'dive_and_forward', 1)
        self.assertTrue(a.location == (3, 2))

        e.execute_action(a, 'forward', 1)
        self.assertTrue(a.location == (4, 2))

        e.execute_action(a, 'up_and_forward', 1)
        self.assertTrue(a.location == (5, 1))

        # check that the world is torus, should get back to the same location
        for _ in range(0, 50):
            e.execute_action(a, 'forward', 1)

        self.assertTrue(a.location == (5, 1))

    def test_singing_cachalot(self):
        l.info('test_singing_cachalot')

        e = Sea(options)
        a = Agent(None, 'cachelot')
        e.add_thing(a, (1, 1))

        # song at time=1 will be heard by other agents at time=2
        e.execute_ns_action(a, 'sing', 1)
        self.assertTrue(len(e.list_ns_artifacts_at(2)) == 1)


    def tearDown(self):
        l.info('...done with test_sea.')


# Main
# ====

if __name__ == '__main__':
    unittest.main()
