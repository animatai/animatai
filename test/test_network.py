# pylint: disable=missing-docstring, global-statement, invalid-name, too-few-public-methods
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


# Imports
# ======

import unittest
from gzutils.gzutils import Logging
from ecosystem.network import Network, MotorNetwork


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('test_network', DEBUG_MODE)


class Thing1:
    pass

class Thing2:
    pass

class Thing3:
    pass

class TestNetwork(unittest.TestCase):

    def setUp(self):
        l.info('Testing network...')

    def tearDown(self):
        l.info('...done with test_network.')

    def test_SENSOR_AND(self):
        network = Network()
        network.add_SENSOR_node(Thing1)

        self.assertTrue(network.get_state() == (None,))

        network.update([(Thing2(), 1.0)])
        self.assertTrue(network.get_state() == (False,))

        network.update([(Thing1(), 1.0)])
        self.assertTrue(network.get_state() == (True,))

        network.add_SENSOR_node(Thing2)
        network.update([(Thing2(), 1.0)])
        self.assertTrue(network.get_state() == (False, True, ))

        network.update([])
        self.assertTrue(network.get_state() == (False, False, ))

        network.update([(Thing2(), 2.0), (Thing1(), 0.5)])
        self.assertTrue(network.get_state() == (True, True, ))

        network.add_AND_node([0, 1])
        network.update([(Thing2(), 1.0), (Thing1(), 0.3)])
        self.assertTrue(network.get_state() == (True, True, True))

        network.update([(Thing2(), 2.0)])
        self.assertTrue(network.get_state() == (False, True, False))

    def test_SEQ(self):
        network = Network([('thing1', Thing1), ('thing2', Thing2)])
        network.add_SEQ_node([0, 1])

        network.update([(Thing1(), 1.0)])
        self.assertTrue(network.get_state() == (True, False, False))

        network.update([(Thing2(), 0.5)])
        self.assertTrue(network.get_state() == (False, True, True))

        network.update([(Thing2(), 1.0)])
        self.assertTrue(network.get_state() == (False, True, False))

        network.update([])
        self.assertTrue(network.get_state() == (False, False, False))

    def test_top_active(self):
        network = Network()
        n1 = network.add_SENSOR_node(Thing1)
        n2 = network.add_SENSOR_node(Thing2)
        n3 = network.add_SENSOR_node(Thing3)
        n4 = network.add_SEQ_node([n1, n2, n3])

        network.update([(Thing1(), 1.0)])
        self.assertTrue(network.get() == set([n1]))
        self.assertTrue(network.top_active() == set([n1]))

        network.update([(Thing2(), 1.0)])
        self.assertTrue(network.get() == set([n2]))
        self.assertTrue(network.top_active() == set([n2]))

        network.update([(Thing3(), 1.0)])
        self.assertTrue(network.get() == set([n3, n4]))
        self.assertTrue(network.top_active() == set([n4]))

        network.update([])
        self.assertTrue(network.get() == set())

        # Check that SEQ can keep track of multiple sequences at the same time
        network.update([(Thing1(), 1.0)])
        network.update([(Thing2(), 1.0), (Thing1(), 1.0)])
        network.update([(Thing3(), 1.0), (Thing2(), 1.0)])
        self.assertTrue(network.get() == set([n3, n2, n4]))
        network.update([(Thing3(), 1.0)])
        self.assertTrue(network.get() == set([n3, n4]))

    def test_RAND_NOT(self):
        network = Network()
        n1 = network.add_RAND_node(0.5)
        n2 = network.add_NOT_node([n1])
        for _ in range(0, 100):
            network.update([])
            state = network.get_state()
            self.assertTrue(state[n1] != state[n2])

    def test_ONE(self):
        network = Network()
        n1 = network.add_SENSOR_node(Thing1)
        n2 = network.add_SENSOR_node(Thing2)
        n3 = network.add_SENSOR_node(Thing3)
        n1T = network.add_ONE_node(n1, [n1, n2, n3])
        n2T = network.add_ONE_node(n2, [n1, n2, n3])
        n3T = network.add_ONE_node(n3, [n1, n2, n3])

        l.debug('TTT', network.update([(Thing1(), 1.0)]))
        self.assertTrue(network.update([(Thing1(), 1.0)]) - set([n1]) == set([n1T]))
        self.assertTrue(network.update([(Thing2(), 1.0)]) - set([n2]) == set([n2T]))
        self.assertTrue(network.update([(Thing3(), 1.0)]) - set([n3]) == set([n3T]))
        self.assertTrue(network.update([(Thing1(), 1.0), (Thing2(), 1.0)]) -
                        set([n1, n2]) == set())
        self.assertTrue(network.update([(Thing1(), 1.0), (Thing2(), 1.0), (Thing3(), 1.0)]) -
                        set([n1, n2, n3]) == set())
        self.assertTrue(network.update([]) == set())

        m1 = network.add_MIN_node(1, [n1, n2, n3])
        m2 = network.add_MIN_node(2, [n1, n2, n3])
        m3 = network.add_MIN_node(3, [n1, n2, n3])

        vs = network.update([(Thing3(), 1.0)])
        self.assertTrue(m1 in vs and not m2 in vs and not m3 in vs)
        vs = network.update([(Thing1(), 1.0), (Thing2(), 1.0)])
        self.assertTrue(m2 in vs and m1 in vs and not m3 in vs)
        vs = network.update([(Thing1(), 1.0), (Thing2(), 1.0), (Thing3(), 1.0)])
        self.assertTrue(m3 in vs and  m2 in vs and  m1 in vs)

        m1 = network.add_MAX_node(1, [n1, n2, n3])
        m2 = network.add_MAX_node(2, [n1, n2, n3])
        m3 = network.add_MAX_node(3, [n1, n2, n3])

        vs = network.update([])
        self.assertTrue(m1 in vs and m2 in vs and  m3 in vs)
        vs = network.update([(Thing3(), 1.0)])
        self.assertTrue(m1 in vs and m2 in vs and  m3 in vs)
        vs = network.update([(Thing1(), 1.0), (Thing2(), 1.0)])
        self.assertTrue(m2 in vs and not m1 in vs and m3 in vs)
        vs = network.update([(Thing1(), 1.0), (Thing2(), 1.0), (Thing3(), 1.0)])
        self.assertTrue(m3 in vs and not m2 in vs and not m1 in vs)


class TestMotorNetwork(unittest.TestCase):

    def setUp(self):
        l.info('Testing MotorNetwork...')

    def tearDown(self):
        l.info('...done with MotorNetwork.')

    def test_MOTOR_AND_SEQ(self):
        mnetwork = MotorNetwork()
        n1 = mnetwork.add_MOTOR_node('m1')
        self.assertTrue(mnetwork.get() == set())

        mnetwork.update(set([n1]))
        self.assertTrue(mnetwork.get() == set([0]))

        mnetwork.update(set())
        self.assertTrue(mnetwork.get() == set())

        n2 = mnetwork.add_MOTOR_node('m2')
        mnetwork.update(set([n2]))
        self.assertTrue(mnetwork.get() == set([n2]))

        mnetwork.update(set([n2, n1]))
        self.assertTrue(mnetwork.get() == set([n1, n2]))

        n3 = mnetwork.add_MAND_node([n1, n2])
        mnetwork.update(set())
        self.assertTrue(mnetwork.get() == set())
        mnetwork.update(set([n3]))
        self.assertTrue(mnetwork.get() == set([n1, n2]))

        n4 = mnetwork.add_MOTOR_node('m3')
        n5 = mnetwork.add_MSEQ_node([n3, n4])
        mnetwork.update(set())
        self.assertTrue(mnetwork.get() == set())
        mnetwork.update(set())
        self.assertTrue(mnetwork.get() == set())
        mnetwork.update(set([n5]))
        self.assertTrue(mnetwork.get() == set([n1, n2]))
        mnetwork.update(set())
        self.assertTrue(mnetwork.get() == set([n4]))
        mnetwork.update(set())
        self.assertTrue(mnetwork.get() == set())

        mnetwork.delete_nodes([n5])
        mnetwork.update(set([n4]))
        self.assertTrue(mnetwork.get() == set([n4]))

    def test_motor_to_action(self):

        # set([(active_motors, action)])
        # each motor is mapped to one action. It is only meaningful to
        # activate one motor at the time. All other combinations of
        # active motors are mapped to the action '-' (do nothing)
        motors = ['<', '>', '^', 'v']
        motors_to_action1 = {frozenset([0]): '<',
                             frozenset([1]): '>',
                             frozenset([2]): '^',
                             frozenset([3]): 'v',
                             '*': '-'}

        mnetwork = MotorNetwork(motors, motors_to_action1)
        mnetwork.update(frozenset([0]))
        self.assertTrue(mnetwork.get_action() == '<')
        mnetwork.update(frozenset([1]))
        self.assertTrue(mnetwork.get_action() == '>')
        mnetwork.update(frozenset([2]))
        self.assertTrue(mnetwork.get_action() == '^')
        mnetwork.update(frozenset([3]))
        self.assertTrue(mnetwork.get_action() == 'v')


        # Motor model where all combinations of active motors have an action
        motors_to_action2 = {frozenset(): '<',
                             frozenset([0]): '>',
                             frozenset([1]): '^',
                             frozenset([0, 1]): 'v'}

        mnetwork = MotorNetwork(motors, motors_to_action2)
        mnetwork.update(frozenset())
        self.assertTrue(mnetwork.get_action() == '<')
        mnetwork.update(frozenset([0]))
        self.assertTrue(mnetwork.get_action() == '>')
        mnetwork.update(frozenset([1]))
        self.assertTrue(mnetwork.get_action() == '^')
        mnetwork.update(frozenset([0, 1]))
        self.assertTrue(mnetwork.get_action() == 'v')
