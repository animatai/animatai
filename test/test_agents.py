# pylint: disable=missing-docstring, global-statement, invalid-name
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


# Imports
# ======

import unittest
from gzutils.gzutils import Logging
from ecosystem.agents import Agent, Thing, Direction, XYEnvironment

# Setup logging
# =============

DEBUG_MODE = True
l = Logging('test_agents', DEBUG_MODE)


# Unit tests
# ==========


class TestAgents(unittest.TestCase):

    def setUp(self):
        l.info('Testing agents...')

    def test_move_forward(self):
        l.info('test_move_forward')

        d = Direction("up")
        l1 = d.move_forward((0, 0))
        self.assertTrue(l1 == (0, -1))

        d = Direction(Direction.R)
        l1 = d.move_forward((0, 0))
        self.assertTrue(l1 == (1, 0))

        d = Direction(Direction.D)
        l1 = d.move_forward((0, 0))
        self.assertTrue(l1 == (0, 1))

        d = Direction("left")
        l1 = d.move_forward((0, 0))
        self.assertTrue(l1 == (-1, 0))

        l2 = d.move_forward((1, 0))
        self.assertTrue(l2 == (0, 0))

    def test_add(self):
        l.info('test_add')

        d = Direction(Direction.U)
        l1 = d + "right"
        l2 = d + "left"
        self.assertTrue(l1.direction == Direction.R)
        self.assertTrue(l2.direction == Direction.L)

        d = Direction("right")
        l1 = d.__add__(Direction.L)
        l2 = d.__add__(Direction.R)
        self.assertTrue(l1.direction == "up")
        self.assertTrue(l2.direction == "down")

        d = Direction("down")
        l1 = d.__add__("right")
        l2 = d.__add__("left")
        self.assertTrue(l1.direction == Direction.L)
        self.assertTrue(l2.direction == Direction.R)

        d = Direction(Direction.L)
        l1 = d + Direction.R
        l2 = d + Direction.L
        self.assertTrue(l1.direction == Direction.U)

        d = Direction(Direction.U)
        l1 = d + Direction.R + Direction.R
        self.assertTrue(l1.direction == Direction.D)

    def test_xyenvironment(self):
        l.info('test_xyenvironment')

        e = XYEnvironment({})
        a = Agent()
        t = Thing()

        e.add_thing(a, (1, 1))
        e.add_thing(t, (2, 2))

        # Down is the default direction
        e.execute_action(a, 'Forward', 1)
        self.assertTrue(a.location == (2, 1))

        e.execute_action(a, 'TurnLeft', 1)
        e.execute_action(a, 'Forward', 1)
        self.assertTrue(a.location == (2, 0))

        e.execute_action(a, 'TurnLeft', 1)
        self.assertTrue(a.direction.direction == Direction.L)

        e.execute_action(a, 'Forward', 1)
        self.assertTrue(a.location == (1, 0))

    def test_ns_action(self):
        l.info('test_ns_action')

        e = XYEnvironment({})
        a = Agent(None, 'cachelot')
        e.add_thing(a, (1, 1))

        # song at time=1 will be heard by other agents at time=2
        e.execute_action(a, 'sing', 1)
        self.assertTrue(len(e.list_nonspatial_at(2)) == 1)

    def test_step(self):
        l.info('test_step')

        def program1(percept):
            self.assertTrue(percept != [])
            return 'do nothing'

        def program2(percept):
            self.assertTrue(percept != [])
            return 'say nothing'

        e = XYEnvironment({})
        a1 = Agent(program1, 'agent1')
        a2 = Agent(program2, 'agent2')
        t = Thing()

        e.add_thing(a1, (1, 1))
        e.add_thing(a2, (1, 1))
        self.assertTrue(e.agents != [])

        e.add_thing(t, (1, 1))

        e.step(1)
        l.debug(e.actions, e.rewards)
        self.assertTrue(len(e.actions) == 2)
        self.assertTrue(e.rewards == [0, 0])

        e.step(2)
        self.assertTrue(len(e.actions) == 2)
        self.assertTrue(e.rewards == [1, 1])

    def tearDown(self):
        l.info('...done with test_agents.')


# Main
# ====

if __name__ == '__main__':
    unittest.main()
