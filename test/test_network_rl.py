# pylint: disable=missing-docstring, global-statement, invalid-name
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


# Imports
# ======

import random
import unittest

from gzutils.gzutils import Logging, get_output_dir, save_csv_file

from animatai.mdp import MDP
from animatai.network_rl import NetworkDP, NetworkQLearningAgent

# Setup logging
# =============

random.seed(1)

OUTPUT_DIR = get_output_dir()
DEBUG_MODE = False
l = Logging('test_network_rl', DEBUG_MODE)


# Data models used in the tests
# ============================

# Traditional MDP that is used to model the environment in the tests
# ------------------------------------------------------------------

# Give the states the names: 'a', ..., 'k'.
# state: {action: [(prob,state)]}
#
# +------+------+------+------+
# |   a  |   b  |   c  |   d  |
# +------+------+------+------+
# |   e  |      |   f  |   g  |
# +------+------+------+------+
# |   h  |   i  |   j  |   k  |
# +------+------+------+------+
#

#
# P(s'|s, a) modelled with {s: {a: [(prob, s')] }}
#
# The action '-' is used to model actions without meaning which is the result
# of activating a set of motors that do not correspnd to an action in the
# environment (for instance forward and backward at the same time).
#
TRANSITION_MODEL = {'a': {'>': [(0.8, 'b'), (0.1, 'a'), (0.1, 'e')],
                          'v': [(0.8, 'e'), (0.1, 'a'), (0.1, 'b')],
                          '<': [(0.9, 'a'), (0.1, 'e')],
                          '^': [(0.9, 'a'), (0.1, 'b')],
                          '-': [(1.0, 'a')]},
                    'b': {'<': [(0.8, 'a'), (0.2, 'b')],
                          '>': [(0.8, 'c'), (0.2, 'b')],
                          '^': [(0.8, 'b'), (0.1, 'a'), (0.1, 'c')],
                          'v': [(0.8, 'b'), (0.1, 'a'), (0.1, 'c')],
                          '-': [(1.0, 'b')]},
                    'c': {'<': [(0.8, 'b'), (0.1, 'c'), (0.1, 'f')],
                          '>': [(0.8, 'd'), (0.1, 'c'), (0.1, 'f')],
                          'v': [(0.8, 'f'), (0.1, 'b'), (0.1, 'd')],
                          '^': [(0.9, 'c'), (0.1, 'b'), (0.1, 'd')],
                          '-': [(1.0, 'c')]},
                    'd': {'<': [(1.0, 'h')], '>': [(1.0, 'h')], # terminal state, start over
                          'v': [(1.0, 'h')], '^': [(1.0, 'h')], '-': [(1.0, 'h')]},
                    'e': {'^': [(0.8, 'a'), (0.2, 'e')],
                          'v': [(0.8, 'h'), (0.2, 'e')],
                          '<': [(0.8, 'e'), (0.1, 'a'), (0.1, 'h')],
                          '>': [(0.8, 'e'), (0.1, 'a'), (0.1, 'h')],
                          '-': [(1.0, 'e')]},
                    'f': {'^': [(0.8, 'c'), (0.1, 'f'), (0.1, 'g')],
                          '>': [(0.8, 'g'), (0.1, 'c'), (0.1, 'j')],
                          'v': [(0.8, 'j'), (0.1, 'f'), (0.1, 'g')],
                          '<': [(0.8, 'f'), (0.1, 'c'), (0.1, 'j')],
                          '-': [(1.0, 'f')]},
                    'g': {'<': [(1.0, 'h')], '>': [(1.0, 'h')], # terminal state, start over
                          'v': [(1.0, 'h')], '^': [(1.0, 'h')], '-': [(1.0, 'h')]},
                    'h': {'^': [(0.8, 'e'), (0.1, 'h'), (0.1, 'i')],
                          '>': [(0.8, 'i'), (0.1, 'h'), (0.1, 'e')],
                          'v': [(0.9, 'h'), (0.1, 'i')],
                          '<': [(0.9, 'h'), (0.1, 'e')],
                          '-': [(1.0, 'h')]},
                    'i': {'<': [(0.8, 'h'), (0.2, 'i')],
                          '>': [(0.8, 'j'), (0.2, 'i')],
                          '^': [(0.8, 'i'), (0.1, 'h'), (0.1, 'j')],
                          'v': [(0.8, 'i'), (0.1, 'h'), (0.1, 'j')],
                          '-': [(1.0, 'i')]},
                    'j': {'<': [(0.8, 'i'), (0.1, 'j'), (0.1, 'f')],
                          '^': [(0.8, 'f'), (0.1, 'i'), (0.1, 'k')],
                          '>': [(0.8, 'k'), (0.1, 'j'), (0.1, 'f')],
                          'v': [(0.8, 'j'), (0.1, 'i'), (0.1, 'k')],
                          '-': [(1.0, 'j')]},
                    'k': {'<': [(0.8, 'j'), (0.1, 'k'), (0.1, 'g')],
                          '^': [(0.8, 'g'), (0.1, 'k'), (0.1, 'j')],
                          '>': [(0.9, 'k'), (0.1, 'g')],
                          'v': [(0.9, 'k'), (0.1, 'j')],
                          '-': [(1.0, 'k')]}
                   }

# R(s, a, s')
REWARD_MODEL = [('*', '*', 'd', {'energy': 1.0}),
                ('*', '*', 'g', {'energy': -1.0}),
                ('*', '*', '*', {'energy': -0.04}),
                ('d', '*', '*', {'energy': 1.0}),
                ('g', '*', '*', {'energy': -1.0})]

# R(s, a, s')
MULTI_DIM_REWARD_MODEL = [('*', '*', 'd', {'energy': 0.5, 'water': -0.5}),
                          ('*', '*', 'g', {'energy': -0.5, 'water': 0.5}),
                          ('*', '*', '*', {'energy': -0.04, 'water': -0.04}),
                          ('d', '*', '*', {'energy': 0.5, 'water': -0.5}),
                          ('g', '*', '*', {'energy': -0.5, 'water': 0.5})]


# Test
# ====

def print_grid(U):
    l.info(U[0:4])
    l.info(U[4:7])
    l.info(U[7:11])

def print_q_agent(q_agent):
    for objective in q_agent.ndp.statuses:
        l.debug('iteration:', q_agent.iterations, ' ----- ' + objective + '------ ')
        U, pi = q_agent.Q_to_U_and_pi()[objective]

        U = {k: U[k] if k in U else ' ' for k in TRANSITION_MODEL}
        pi = {k: pi[k] if k in pi else ' ' for k in TRANSITION_MODEL}

        # print the utilities and the policy also
        U1 = sorted(U.items(), key=lambda x: x[0])
        pi1 = sorted(pi.items(), key=lambda x: x[0])
        print_grid(U1)
        print_grid(pi1)


def run_single_trial(q_agent, mdp, sensor_model, motor_model, print_steps=False):
    def take_single_action(mdp, s, a):
        x = random.uniform(0, 1)
        cumulative_probability = 0.0
        for probability_state in mdp.T(s, a):
            probability, state = probability_state
            cumulative_probability += probability
            if x < cumulative_probability:
                break
        #l.debug(s, a, x, cumulative_probability, mdp.T(s, a), state)
        return state

    current_state = mdp.init
    next_action = None
    while True:
        current_reward = mdp.R(current_state)
        percept = (sensor_model.sensors_for_state(current_state), current_reward)
        next_network_action = q_agent(percept)
        l.debug('current_state:', current_state,
                ',current_reward:', current_reward,
                ',next_action:', next_action,
                ',percept:', percept,
                ',next_network_action:', next_network_action
               )
        l.debug('q_agent:', q_agent)
        if next_network_action is None:
            break
        next_action = motor_model(next_network_action)
        current_state = take_single_action(mdp, current_state, next_action)
        if print_steps:
            print_q_agent(q_agent)

#
# SensorModel
# -----------
#
# Holds a model mapping sensors to states: {(s1,..., sn): 'state'}
#
# It is possible to create sensors from a mdp. One sensor is created for each
# state. This is mainly used in simple examples/testing.
#

def mdp_to_simple_sensor_model(mdp):
    # One sensor for each state in the MDP
    sensor_template = [False] * len(mdp.states)
    i = 0
    model = {}
    for state in sorted(mdp.states):
        sensor = list(sensor_template)
        sensor[i] = True
        i += 1
        model[tuple(sensor)] = state
    return model


# sensors = [('sensor name', Thing to recognise)]
# model   = {(s1:bool,...,sn:bool): 'state'} maps sensor tuples to states (for readability)
class SensorModel:
    # pylint: disable=too-few-public-methods
    def __init__(self, sensors, model=None, mdp=None):
        self.sensors = sensors
        if model and mdp:
            raise Exception('Both model and mdp should not be used!')
        if model:
            self.model = model
        if mdp:
            self.model = mdp_to_simple_sensor_model(mdp)

    def __repr__(self):
        return 'SensorModel:' + str(self.model)

    # return the state for a tuple of sensors
    def __call__(self, sensors):
        if not sensors:
            return None
        return self.model[sensors]

    # returns the sensors tuple for a state
    def sensors_for_state(self, state):
        for k, v in self.model.items():
            if v == state:
                return k
        raise Exception('SensorModel.sensors: state not found - ' + state)



#
# MotorModel - generates all possible actions
# ----------
#
# motors - list of motors represented with string ['m1',...,'mn']
# model - maps tuples of motors (bool,...,bool) to actions in the Environemtn used:
#        [ ((m1:bool,m2:bool,...,mn:bool), 'action'),...,('*', 'default_actiom') ]
#        The default action is used when a combination of active motors do not
#        result in any action in the environment
#
def find_in_list_with_tuples(key, default_key, idx, lst):
    r = list(filter(lambda x: x[idx] == key, lst))
    if not r:
        r = list(filter(lambda x: x[idx] == default_key, lst))
    return r

class MotorModel:
    # pylint: disable=too-few-public-methods
    def __init__(self, motors, model):
        self.model = model
        self.motors = motors

    # returns the action for a motors tuple
    def __call__(self, motors):
        if not motors:
            return None
        act = find_in_list_with_tuples(motors, '*', 0, self.model)
        if act:
            return act[0][1]
        return None

    def __repr__(self):
        return 'MotorModel:' + str(self.model)

    #
    # motors=[m1,m2,...,mn] actions=[(m1=T/F,m2=T/F,...,mn=T/F)]
    # actions are tuples where each motor is represented by one position with a
    # boolean indicating if it is active.
    #
    # Generate all possible actions from a list of motors (2^n combinations)
    # [m1,m2,...,mn] -> [(F,F,...,F),...,(T,T,...,T])]
    def all_actions(self):
        def ext(e, lst):
            for v in lst:
                v.insert(0, e)

        def actions_(motors):
            if len(motors) == 1:
                return [[True], [False]]
            a = actions_(motors[1:])
            ext(False, a)
            b = actions_(motors[1:])
            ext(True, b)
            a.extend(b)
            return a

        return list(map(tuple, actions_(self.motors)))


class TestNetworkRL(unittest.TestCase):
    # pylint: disable=too-many-instance-attributes

    def setUp(self):
        l.info('Testing network_rl...')

        self.test_mdp = MDP(init='h',
                            actlist={'<', '>', '^', 'v'},
                            terminals={'d', 'g'},
                            states={'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'},
                            transitions=TRANSITION_MODEL,
                            rewards=REWARD_MODEL)

        self.test_multi_dim_mdp = MDP(init='h',
                                      actlist={'<', '>', '^', 'v'},
                                      terminals={'d', 'g'},
                                      states={'a', 'b', 'c', 'd', 'e', 'f', 'g',
                                              'h', 'i', 'j', 'k'},
                                      transitions=TRANSITION_MODEL,
                                      rewards=MULTI_DIM_REWARD_MODEL)

        sensors = [('a', None), ('b', None), ('c', None), ('d', None), ('e', None),
                   ('f', None), ('g', None), ('h', None), ('i', None), ('j', None),
                   ('k', None)]
        self.sensor_model = SensorModel(sensors, model=None, mdp=self.test_mdp)

        self.statuses = {'energy': 1.0}
        self.multi_dim_statuses = {'energy': 1.0, 'water': 1.0}

        # (m1:bool,m2:bool,...,mn:bool)
        # actions and motors are the same '<','>','^','v'. It is only meaninfful to
        # activate more than one motor at the time in this model. All other combinations of
        # active motors are mapped to the action '-' (do nothing)
        motors0 = ['<', '>', '^', 'v']
        self.motor_model0 = MotorModel(motors0,
                                       [((True, False, False, False), '<'),
                                        ((False, True, False, False), '>'),
                                        ((False, False, True, False), '^'),
                                        ((False, False, False, True), 'v'),
                                        ('*', '-')])

        #
        # Motor model where all actions are meaningfull
        #
        motors = ['m1', 'm2']
        self.motor_model = MotorModel(motors,
                                      [((False, False), '<'),
                                       ((False, True), '>'),
                                       ((True, False), '^'),
                                       ((True, True), 'v'),
                                       ('*', '-')])

        init = (False, False, False, False, False, False, False, True, False, False, False)
        self.ndp = NetworkDP(init, self.statuses, self.motor_model, .9, self.sensor_model)
        self.multi_dim_ndp = NetworkDP(init, self.multi_dim_statuses, self.motor_model,
                                       .9, self.sensor_model)

    def tearDown(self):
        l.info('...done with test_network_rl.')

    def test_networkQLearnigAgentPrintDetails(self):
        for i in range(100):
            l.debug('**** TRIAL: ', i, ' ****')
            q_agent = NetworkQLearningAgent(self.ndp, Ne=5, Rplus=2,
                                            alpha=lambda n: 60./(59+n),
                                            delta=0.5,
                                            max_iterations=100,
                                            calc_status=True)
            q_agent.reset()

            run_single_trial(q_agent, self.test_mdp, self.sensor_model, self.motor_model,
                             DEBUG_MODE)


    def test_networkQLearnigAgent(self):
        # pylint: disable=line-too-long
        self.assertTrue(self.sensor_model.model ==
                        {(True, False, False, False, False, False, False, False, False, False, False): 'a',
                         (False, True, False, False, False, False, False, False, False, False, False): 'b',
                         (False, False, True, False, False, False, False, False, False, False, False): 'c',
                         (False, False, False, True, False, False, False, False, False, False, False): 'd',
                         (False, False, False, False, True, False, False, False, False, False, False): 'e',
                         (False, False, False, False, False, True, False, False, False, False, False): 'f',
                         (False, False, False, False, False, False, True, False, False, False, False): 'g',
                         (False, False, False, False, False, False, False, True, False, False, False): 'h',
                         (False, False, False, False, False, False, False, False, True, False, False): 'i',
                         (False, False, False, False, False, False, False, False, False, True, False): 'j',
                         (False, False, False, False, False, False, False, False, False, False, True): 'k'})

        self.assertTrue(self.ndp.actlist == [(False, True), (False, False), (True, True), (True, False)])

        q_agent = NetworkQLearningAgent(self.ndp, Ne=5, Rplus=2,
                                        alpha=lambda n: 60./(59+n),
                                        delta=0.5,
                                        max_iterations=100,
                                        calc_status=True)

        for i in range(100):
            l.debug('**** TRIAL: ', i, ' ****')
            q_agent.reset()
            run_single_trial(q_agent, self.test_mdp, self.sensor_model, self.motor_model,
                             DEBUG_MODE)

        U, pi = q_agent.Q_to_U_and_pi()['energy']

        # print the utilities and the policy also
        U1 = sorted(U.items(), key=lambda x: x[0])
        pi1 = sorted(pi.items(), key=lambda x: x[0])
        l.debug('------------------')
        print_grid(U1)
        print_grid(pi1)

        l.debug('AAA', U, U1)
        l.debug('BBB', pi, pi1)
        l.debug('CCC', q_agent)
        save_csv_file('one_dim.csv', [self.ndp.history], self.ndp.history_headers, OUTPUT_DIR)


        # check utilities and policy
        # TODO: Seams difficult to get the samt result at each run. Probably due to tests running in parallel
        #self.assertTrue(U == {'h': 0.5675987591078075, 'i': 0.4286810287409787, 'j': 0.3330852421527908, 'k': -0.04, 'g': 0.48303073762721593, 'f': 0.35799047401701395, 'e': 0.7127484585669493, 'c': 1.302492662358114, 'd': 0.4742671906118568, 'a': 0.8593590286870549, 'b': 1.0802110658809299})
        #self.assertTrue(pi == {'h': '^', 'i': '<', 'j': '<', 'k': None, 'g': '<', 'f': '<', 'e': '^', 'c': '>', 'd': '>', 'a': '>', 'b': '>'})

        l.debug('test_networkQLearnigAgent:', self.ndp.statuses)

    def test_multiDimNetworkQLearnigAgent(self):
        # pylint: disable=line-too-long
        q_agent = NetworkQLearningAgent(self.multi_dim_ndp, Ne=5, Rplus=2,
                                        alpha=lambda n: 60./(59+n),
                                        delta=0.5,
                                        max_iterations=100,
                                        calc_status=True)

        for _ in range(101):
            q_agent.reset()
            run_single_trial(q_agent, self.test_multi_dim_mdp, self.sensor_model, self.motor_model)

        for status in ['energy', 'water']:
            l.debug('----- ' + status + '------')
            U, pi = q_agent.Q_to_U_and_pi()[status]

            # print the utilities and the policy also
            U1 = sorted(U.items(), key=lambda x: x[0])
            pi1 = sorted(pi.items(), key=lambda x: x[0])
            print_grid(U1)
            print_grid(pi1)

        save_csv_file('two_dim.csv', [self.multi_dim_ndp.history], self.ndp.history_headers, OUTPUT_DIR)
        l.debug('test_multiDimNetworkQLearnigAgent:', self.multi_dim_ndp.statuses)
