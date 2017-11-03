# pylint: disable=missing-docstring, global-statement, invalid-name
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

#
# A variant of Q-learning where the agents have sensors and motors. Distal
# stimula (Things) are perceived using boolean sensors and thereby create
# proximal stimula that are perceived by the agent. Sensors can also be combined
# using operators such as AND and SEQ operators (a SEQ b = a is true and then b)
# and thereby creating a network (not fully implemented yet).
#
# Actions are modelled based on motors. Combinations of motors
# that are activaed gives the different actions. Motors can be though of as
# parts of a body of an animal or simply motors on a robot/vehicle.
#
# There are no terminal states/nodes. Status values (between 0 and 1) are used
# instead. The agent has reached a terminal state when one status is zero or
# less
#

# Imports
# =======

import math
import random

from collections import defaultdict
from gzutils.gzutils import DefaultDict, Logging

from .agents import Agent


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('network_rl', DEBUG_MODE)


# Network model used by the Network Q-learning Agents
# ===================================================

#
# A variant of a MDP where:
# - actions are generated from active motors - frozenset([m0,...,mn])
# - states are represented with active network nodes - frozenset([s1,..., sn])
# - statuses are used instead of terminal states. Any status less than or equal
#   to zero is equivalent to a terminal state - [(name, float)]
# - init is the initial state of the sensors
#

# Use like this: NetworkModel({frozenset([0]): state, ...})
class NetworkModel(dict):
    def __call__(self, key):
        if key in self:
            return self.get(key)
        return key


# Use like this: MotorModel({north: '^', south: 'v', east: '>', west: '<', '*': '-'})
class MotorModel(dict):
    def __call__(self, key):
        if key in self:
            return self.get(key)
        elif '*' in self:
            return self.get('*')
        return key

    def all_actions(self):
        res = list(self.keys())
        if '*' in res:
            res.remove('*')
        return res


#
# NetworkDP
# ---------
#
# Holds the network used by the NetworkAgents. It consists of motors, sensors
# and statuses. The SensorModel and MotorModel classes are used to manage the
# sensors and motors (data structure classes).
#
# init         = (s1_init, ..., sn_init) - initial state of sensors
# statuses     = {name1: init_value,..., name_n: init_value} - SHOULD BE THE STATUSES IN THE NETWORK
# motor_model  = {(m1:bool,m2:bool,...,mn:bool): 'action name', '*': 'default_action'}
# network_model = {(s1:bool, s2:bool, ..., sn:bool): 'state name' } (Optional)
#
class NetworkDP:
    # pylint: disable=too-many-arguments, too-many-instance-attributes
    def __init__(self, init, statuses, motor_model, gamma=.9, network_model=None):
        self.init = init
        self.gamma = gamma
        self.statuses = statuses
        self.motor_model = motor_model
        self.network_model = network_model
        self.init_statuses = dict(statuses)
        self.actlist = motor_model.all_actions()

        self.history = []
        self.history_headers = [str(list(statuses.keys())), 'state', 'action',
                                str(list(statuses.keys()))]

    def __repr__(self):
        return ('gamma=' + str(self.gamma) + '\n' +
                'init=' + str(self.init) +
                ('(' + self.network_model(self.init) if self.network_model else '') + ')\n' +
                #'sensors=' + str(self.network_model.sensors) + '\n' +
                'statuses=' + str(self.statuses) + '\n' +
                'motors=' + str(self.motor_model.motors) + '\n' +
                'motor_model=' + str(self.motor_model) + '\n' +
                'network_model=' + str(self.network_model) + '\n' +
                'actlist=' + str(self.actlist) + '\n' +
                'actions (using motor_model)=' +
                str([self.motor_model(act) for act in self.actlist]) + '\n' +
                'in_terminal=' + str(self.in_terminal()))

    def update_statuses(self, state, action, rewards):
        if self.motor_model:
            action = self.motor_model(action)
        if self.network_model:
            state = self.network_model(state)
        self.history.append((list(self.statuses.values()), state, action, list(rewards.values())))

        for k, v in rewards.items():
            self.statuses[k] += v

    def reset(self):
        self.statuses = dict(self.init_statuses)

    def in_terminal(self):
        return min([v for k, v in self.statuses.items()]) <= 0


# Keeps track of the history of actions performed
class NetworkAgent(Agent):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, program=None, name='nonname', ndp=None, max_iterations=None,
                 calc_status=False):

        self.program = program or self
        self.calc_status = calc_status

        self.ndp = ndp
        self.all_act = ndp.actlist

        # (s)tate, (p)revious (s), (a)ction, (p)revious (a), (r)eward, (p)revious (r)
        self.s = self.ps = None
        self.a = self.pa = None
        self.r = self.pr = {}

        self.iterations = 0
        self.in_terminal = False
        self.max_iterations = max_iterations

        # history of statuses, state, action, reward
        self.history = []
        self.history_headers = [str(list(ndp.statuses.keys())), 'state', 'action',
                                str(list(ndp.statuses.keys()))]

        # history of statuses only
        self.status_history = {}
        for status in ndp.statuses:
            self.status_history[status] = []

        super().__init__(name, self.program)

    def __repr__(self):
        return ('statuses:' + str(self.ndp.statuses) +
                ',iterations:' + str(self.iterations) +
                ',in_terminal:' + str(self.in_terminal))

    def reset(self):
        self.iterations = 0
        self.in_terminal = False
        self.ndp.reset()

    # keep count of the number of iterations and check if the limit is reached
    def check_iterations(self):
        self.iterations += 1
        res = self.max_iterations and self.iterations >= self.max_iterations
        if res:
            l.info('--- MAXIMUIM NUMBER OF ITERATIONS REACHED ---')
        return res

    # Check if status is zero or less and keep track of number of
    # iterations and stop after some limit has been reached
    # The iterations counter is increased so the function should be called once
    def check_terminal(self):
        self.alive = not (self.ndp.in_terminal() or self.check_iterations())
        return not self.alive

    def actions_in_state(self, state):
        # pylint: disable=unused-argument
        return self.all_act

    # update the status after the action has been perfomred and the new state reached
    def update_statuses(self):
        s, a, r = self.s, self.a, self.r
        motor_model, network_model, statuses = (self.ndp.motor_model, self.ndp.network_model,
                                                self.ndp.statuses)

        # save history for statuses, state, action, reward
        if motor_model:
            a = motor_model(a)
        if network_model:
            s = network_model(s)
        self.history.append((list(statuses.values()), s, a, list(r.values())))

        # save status history
        for status in self.ndp.statuses:
            self.status_history[status].append(r[status])

        if self.calc_status:
            self.ndp.update_statuses(s, a, r)

        self.ps, self.pa, self.pr = s, a, dict(r)

    # to be used after the __call__ function
    def any_status_increased(self):
        i, res = self.iterations, False
        if i < 2:
            return False
        for status in self.ndp.statuses:
            res = res or self.status_history[status][i] > self.status_history[status][i-1]
        return res


    # To be overridden when not supplying the program in the constructor.
    # Environment expects a program function with the type:
    # action = program(percept=([string|Thing|NSArtifact], reward for previous actopn))
    def __call__(self, percept):
        a1 = None
        s1, r = self.update_state(percept)
        if self.program:
            a1 = self.program(percept)

        self.s, self.a, self.r = s1, a1, r
        self.update_statuses()
        return a1

    # To be overridden in most cases. The default case assumes the percept
    # to be of type (state, reward)
    def update_state(self, percept):
        # pylint: disable=no-self-use
        return percept


#
# NetworkQLearningAgent
# =====================
#
# Implements multi-dimensional Q-learning using the NetworkDP class instead of a MDP.
#
# Ne >= 1: f (exploration function) returns Rplus until each (state, action) has been tested Ne number of times
# Ne < 1: f (exploration function) explores with probability epsilon
class NetworkQLearningAgent(NetworkAgent):
    # pylint: disable=too-many-instance-attributes, too-many-arguments
    def __init__(self, ndp, Ne, Rplus, alpha=None, delta=0.5, epsilon=0.3,
                 max_iterations=None, name='noname', calc_status=False):

        # Multidimensional Q: Q_status[s, a]
        self.Q = {}
        for status in ndp.statuses:
            self.Q[status] = DefaultDict(0.0)

        self.Ne = Ne                      # iteration limit in exploration function
        self.Nsa = defaultdict(float)
        self.delta = delta
        self.Rplus = Rplus                # large value to assign before iteration limit
        self.gamma = ndp.gamma
        self.epsilon = epsilon

        if alpha:
            self.alpha = alpha
        else:
            self.alpha = lambda n: 1./(1+n)  # udacity video

        super().__init__(None, name, ndp, max_iterations, calc_status)

    def __repr__(self):
        res = ''
        for status in self.ndp.statuses:
            lst = [(self.ndp.network_model(k[0]),
                    self.ndp.motor_model(k[1]), '{0:.3f}'.format(v))
                   for k, v in self.Q[status].items()]
            #lst = sorted(lst, key=lambda x: x and x[0])
            res += status + ':' + str(lst)
        return ('Q:' + res  +
                ',statuses:' + str(self.ndp.statuses) +
                ',iterations:' + str(self.iterations) +
                ',in_terminal:' + str(self.in_terminal))

    def Q_to_U_and_pi(self):
        res = {}
        for status in self.ndp.statuses:
            U = defaultdict(lambda: -math.inf) # Very Large Negative Value for Comparison see below.
            pi = {}
            for state_action, value in self.Q[status].items():
                state, action = state_action
                if U[state] < value:
                    U[state] = value
                    pi[state] = action
            U = dict(map(lambda x: (self.ndp.network_model(x[0]), x[1]), U.items()))
            pi = dict(map(lambda x: (self.ndp.network_model(x[0]),
                                     self.ndp.motor_model(x[1])), pi.items()))
            res[status] = U, pi
        return res

    # check if status is zero or less and keep track of number of
    # iterations and stop after some limit has been reached
    def check_terminal(self):
        self.in_terminal = self.ndp.in_terminal() or self.check_iterations()
        return self.in_terminal

    # Exploration function. Returns fixed Rplus untill agent has visited state,
    # action a Ne number of times or explores randomly with probability epsilon
    def f(self, u, n):
        if (self.Ne >= 1 and n < self.Ne) or random.random() <= self.epsilon:
            return self.Rplus
        return u



    def visited_states(self):
        return sorted(set(map(lambda x: x[0], list(self.Q))))

    def __call__(self, percept):
        # pylint: disable=too-many-locals
        s1, r = self.update_state(percept)
        Q, Nsa, s, a = self.Q, self.Nsa, self.s, self.a
        alpha, gamma, delta, in_terminal = self.alpha, self.gamma, self.delta, self.check_terminal()
        actions_in_state, statuses = self.actions_in_state, self.ndp.statuses

        if in_terminal:
            for objective in statuses:
                Q[objective][(s, None)] = r[objective]
        if s is not None:
            Nsa[s, a] += 1
            for objective in statuses:
                Q[objective][(s, a)] += (alpha(Nsa[s, a]) *
                                         (r[objective] +
                                          gamma * max([Q[objective][(s1, a1)]
                                                       for a1 in actions_in_state(s1)]) -
                                          Q[objective][(s, a)]))

        if in_terminal:
            self.s = self.a = self.r = None
        else:
            self.s, self.r = s1, r

            best_action = {}
            for objective in statuses:
                best_action[objective] = max([(self.f(statuses[objective] +
                                                      delta * Q[objective][(s1, a1)],
                                                      Nsa[s1, a1]), a1)
                                              for a1 in actions_in_state(s1)],
                                             key=lambda x: x[0])
            self.a = min(list(best_action.items()), key=lambda x: x[1][0])[1][1]

            # original version
            # self.a = argmax(actions_in_state(s1),
            #                 key=lambda a1: self.f(Q[objective][(s1, a1)], Nsa[s1, a1]))
            if self.calc_status:
                self.ndp.update_statuses(self.s, self.a, self.r)
        return self.a


#
# LocalQLearningAgent
# ===================
#
# An agent where Q-values are connected to the nodes in the network rather than
# to states. The boolean nodes in the network can be seen as small MDPs. The
# transition model (with correspodning probabilities and rewards) might be unknow,
# but this does not differ compared to ordinary Q-learning. If the environment
# the agent lives in can be modelled with an MDP, then the sensors will also model
# this MDP (perhaps not completely depending on if the sensors covers all aspects of
# the environment).
#
class LocalQLearningAgent:
    pass
