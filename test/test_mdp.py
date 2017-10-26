# pylint: disable=missing-docstring, global-statement, invalid-name
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


# Imports
# ======

import unittest
from gzutils.gzutils import Logging
from animatai.mdp import MDP, value_iteration, value_iteration2, best_policy


# Setup logging
# =============

DEBUG_MODE = False
l = Logging('test_mdp', DEBUG_MODE)


# Unit tests
# ==========

#
# Use the grid world from the AIMA book but give the states the names: 'a', ..., 'k'.
#
# +------+------+------+------+
# |   a  |   b  |   c  |   d  |
# +------+------+------+------+
# |   e  |      |   f  |   g  |
# +------+------+------+------+
# |   h  |   i  |   j  |   k  |
# +------+------+------+------+
#

def to_char(c):
    mapping = [['a', 'b', 'c', 'd'],
               ['e', None, 'f', 'g'],
               ['h', 'i', 'j', 'k']]
    mapping.reverse()
    return mapping[c[1]][c[0]]

# P(s'|s, a) modelled with {s: {a: [(prob, s')] }}
transition_model = {'a': {'>': [(0.8, 'b'), (0.1, 'a'), (0.1, 'e')],
                          'v': [(0.8, 'e'), (0.1, 'a'), (0.1, 'b')],
                          '<': [(0.9, 'a'), (0.1, 'e')],
                          '^': [(0.9, 'a'), (0.1, 'b')]},
                    'b': {'<': [(0.8, 'a'), (0.2, 'b')],
                          '>': [(0.8, 'c'), (0.2, 'b')],
                          '^': [(0.8, 'b'), (0.1, 'a'), (0.1, 'c')],
                          'v': [(0.8, 'b'), (0.1, 'a'), (0.1, 'c')]},
                    'c': {'<': [(0.8, 'b'), (0.1, 'c'), (0.1, 'f')],
                          '>': [(0.8, 'd'), (0.1, 'c'), (0.1, 'f')],
                          'v': [(0.8, 'f'), (0.1, 'b'), (0.1, 'd')],
                          '^': [(0.9, 'c'), (0.1, 'b'), (0.1, 'd')]},
                    'd': None,                     # terminal state
                    'e': {'^': [(0.8, 'a'), (0.2, 'e')],
                          'v': [(0.8, 'h'), (0.2, 'e')],
                          '<': [(0.8, 'e'), (0.1, 'a'), (0.1, 'h')],
                          '>': [(0.8, 'e'), (0.1, 'a'), (0.1, 'h')]},
                    'f': {'^': [(0.8, 'c'), (0.1, 'f'), (0.1, 'g')],
                          '>': [(0.8, 'g'), (0.1, 'c'), (0.1, 'j')],
                          'v': [(0.8, 'j'), (0.1, 'f'), (0.1, 'g')],
                          '<': [(0.8, 'f'), (0.1, 'c'), (0.1, 'j')]},
                    'g': None,                     # terminal state
                    'h': {'^': [(0.8, 'e'), (0.1, 'h'), (0.1, 'i')],
                          '>': [(0.8, 'i'), (0.1, 'h'), (0.1, 'e')],
                          'v': [(0.9, 'h'), (0.1, 'i')],
                          '<': [(0.9, 'h'), (0.1, 'e')]},
                    'i': {'<': [(0.8, 'h'), (0.2, 'i')],
                          '>': [(0.8, 'j'), (0.2, 'i')],
                          '^': [(0.8, 'i'), (0.1, 'h'), (0.1, 'j')],
                          'v': [(0.8, 'i'), (0.1, 'h'), (0.1, 'j')]},
                    'j': {'<': [(0.8, 'i'), (0.1, 'j'), (0.1, 'f')],
                          '^': [(0.8, 'f'), (0.1, 'i'), (0.1, 'k')],
                          '>': [(0.8, 'k'), (0.1, 'j'), (0.1, 'f')],
                          'v': [(0.8, 'j'), (0.1, 'i'), (0.1, 'k')]},
                    'k': {'<': [(0.8, 'j'), (0.1, 'k'), (0.1, 'g')],
                          '^': [(0.8, 'g'), (0.1, 'k'), (0.1, 'j')],
                          '>': [(0.9, 'k'), (0.1, 'g')],
                          'v': [(0.9, 'k'), (0.1, 'j')]}
                   }

# R(s, a, s')
reward_model = [('*', '*', 'd', 1.0),
                ('*', '*', 'g', -1.0),
                ('*', '*', '*', -0.04)]

reward_model0 = [('*', '*', 'd', 1.0),
                 ('*', '*', 'g', -1.0),
                 ('*', '*', '*', 0.0)]


mdp = MDP(init='h',
          actlist={'<', '>', '^', 'v'},
          terminals={'d', 'g'},
          states={'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'},
          transitions=transition_model,
          rewards=reward_model)

mdp0 = MDP(init='h',
           actlist={'<', '>', '^', 'v'},
           terminals={'d', 'g'},
           states={'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'},
           transitions=transition_model,
           rewards=reward_model0)


def formatU(U):
    return sorted(list(map(lambda x: (x[0], '{:.3}'.format(x[1])), U.items())), key=lambda x: x[0])

def print_gridU(U):
    l.debug(U[0:4])
    l.debug(U[4:7])
    l.debug(U[7:11])

class TestAgents(unittest.TestCase):

    def setUp(self):
        l.info('Testing mdp...')

    def tearDown(self):
        l.info('...done with test_mdp.')


    def test_everything(self):

        #
        # This requires manual inspection
        #

        l.debug('--- value_iteration ----')
        for i in range(1, 5):
            U = value_iteration(mdp0, .01, i)
            U = formatU(U)
            print_gridU(U)
            l.debug('------------')

        # The result for this algorithm is sligthly different since the action is rewarded
        # and not the state.
        l.debug('--- value_iteration2 ----')
        for i in range(1, 5):
            U = value_iteration2(mdp0, .01, i)
            U = formatU(U)
            print_gridU(U)
            l.debug('------------')

        #
        # Proper tests with asserts
        #

        # Test the first variant of the algorithm with R(s)
        U = value_iteration(mdp, .01)
        pi = best_policy(mdp, U)

        U = sorted(U.items(), key=lambda x: x[0])
        self.assertTrue(U == [('a', 0.5093629397727583),
                              ('b', 0.6495843908408225),
                              ('c', 0.7953617929302039),
                              ('d', 1.0),
                              ('e', 0.39834389554788047),
                              ('f', 0.48643918314388307),
                              ('g', -1.0),
                              ('h', 0.2960365256921101),
                              ('i', 0.25374914831908),
                              ('j', 0.34471132189911213),
                              ('k', 0.12978438666780848)])
        pi = sorted(pi.items(), key=lambda x: x[0])
        self.assertTrue(pi == [('a', '>'), ('b', '>'), ('c', '>'), ('d', None),
                               ('e', '^'), ('f', '^'), ('g', None),
                               ('h', '^'), ('i', '>'), ('j', '^'), ('k', '<')])

        # Test the second variant of the algorithm with R(s,a,s')
        # The selected policy also differs for state 'c', here the acton is '^' instead of
        # '>'. This avoids 'f' with certainty
        U = value_iteration2(mdp, .01)
        pi = best_policy(mdp, U)

        U = sorted(U.items(), key=lambda x: x[0])
        self.assertTrue(U == [('a', 0.6104032664141759),
                              ('b', 0.766204878712025),
                              ('c', 0.9281797699224489),
                              ('d', 0.0),
                              ('e', 0.48704877283097825),
                              ('f', 0.5849324257154256),
                              ('g', 0.0),
                              ('h', 0.3733739174356778),
                              ('i', 0.3263879425767555),
                              ('j', 0.4274570243323468),
                              ('k', 0.1886493185197872)])
        pi = sorted(pi.items(), key=lambda x: x[0])
        self.assertTrue(pi == [('a', '>'), ('b', '>'), ('c', '^'), ('d', None),
                               ('e', '^'), ('f', '^'), ('g', None),
                               ('h', '^'), ('i', '>'), ('j', '^'), ('k', '<')])
