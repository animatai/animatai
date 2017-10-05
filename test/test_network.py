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

class TestNetwork(unittest.TestCase):

    def setUp(self):
        l.info('Testing network...')

    def tearDown(self):
        l.info('...done with test_network.')

    def test_SENSOR_AND(self):
        network = Network()
        network.add_SENSOR_node(Thing1)

        self.assertTrue(network.get() == (None,))

        network.update([(Thing2(), 1.0)])
        self.assertTrue(network.get() == (False,))

        network.update([(Thing1(), 1.0)])
        self.assertTrue(network.get() == (True,))

        network.add_SENSOR_node(Thing2)
        network.update([(Thing2(), 1.0)])
        self.assertTrue(network.get() == (False, True, ))

        network.update([])
        self.assertTrue(network.get() == (False, False, ))

        network.update([(Thing2(), 2.0), (Thing1(), 0.5)])
        self.assertTrue(network.get() == (True, True, ))

        network.add_AND_node([0, 1])
        network.update([(Thing2(), 1.0), (Thing1(), 0.3)])
        self.assertTrue(network.get() == (True, True, True))

        network.update([(Thing2(), 2.0)])
        self.assertTrue(network.get() == (False, True, False))

    def test_SEQ(self):
        network = Network([('thing1', Thing1), ('thing2', Thing2)])
        #network.add_SENSOR_node(Thing1)
        #network.add_SENSOR_node(Thing2)
        network.add_SEQ_node(0, 1)

        network.update([(Thing1(), 1.0)])
        self.assertTrue(network.get() == (True, False, False))

        network.update([(Thing2(), 0.5)])
        self.assertTrue(network.get() == (False, True, True))

        network.update([(Thing2(), 1.0)])
        self.assertTrue(network.get() == (False, True, False))

        network.update([])
        self.assertTrue(network.get() == (False, False, False))


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
