# pylint: disable=missing-docstring, global-statement, invalid-name
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


# Imports
# ======

import random
import unittest

from myutils import Logging
from network import Network

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
        network.add_sensor_node(Thing1)

        self.assertTrue(network.get() == (None,))

        network.update([Thing2()])
        self.assertTrue(network.get() == (False,))

        network.update([Thing1()])
        self.assertTrue(network.get() == (True,))

        network.add_sensor_node(Thing2)
        network.update([Thing2()])
        self.assertTrue(network.get() == (False, True, ))

        network.update([])
        self.assertTrue(network.get() == (False, False, ))

        network.update([Thing2(), Thing1()])
        self.assertTrue(network.get() == (True, True, ))

        network.add_AND_node([0,1])
        network.update([Thing2(), Thing1()])
        self.assertTrue(network.get() == (True, True, True))

        network.update([Thing2()])
        self.assertTrue(network.get() == (False, True, False))

    def test_SEQ(self):
        network = Network()
        network.add_sensor_node(Thing1)
        network.add_sensor_node(Thing2)
        network.add_SEQ_node(0,1)

        network.update([Thing1()])
        self.assertTrue(network.get() == (True, False, False))

        network.update([Thing2()])
        self.assertTrue(network.get() == (False, True, True))

        network.update([Thing2()])
        self.assertTrue(network.get() == (False, True, False))

        network.update([])
        self.assertTrue(network.get() == (False, False, False))
