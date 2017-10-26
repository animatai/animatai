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

from collections import defaultdict
from gzutils.gzutils import Logging

from .agents import Agent


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('network_rl', DEBUG_MODE)


# Network model used by the Network Q-learning Agents
# ===================================================

#
# A variant of a MDP where:
# - actions are generated from motors - (m1:bool, m2:bool, ..., mn:bool)
# - states are represented with sensors - (s1:bool, s2:bool, ..., sn:bool)
# - statuses are used instead of terminal states. Any status less than or equal
#   to zero is equivalent to a terminal state - [(name, float)]
# - init is the initial state of the sensors
#

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
# MotorModel
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
# NetworkDP
# ---------
#
# Holds the network used by the NetworkAgents. It consists of motors, sensors
# and statuses. The SensorModel and MotorModel classes are used to manage the
# sensors and motors (data structure classes).
#
# init         = (s1_init, ..., sn_init) - initial state of sensors
# statuses     = {name1: init_value,..., name_n: init_value}
# motor_model  = {(m1:bool,m2:bool,...,mn:bool): 'action name', '*': 'default_action'}
# sensor_model = {(s1:bool, s2:bool, ..., sn:bool): 'state name' } (Optional)
#
class NetworkDP:
    # pylint: disable=too-many-arguments, too-many-instance-attributes
    def __init__(self, init, statuses, motor_model, gamma=.9, sensor_model=None):
        self.init = init
        self.gamma = gamma
        self.statuses = statuses
        self.motor_model = motor_model
        self.sensor_model = sensor_model
        self.init_statuses = dict(statuses)

        self.actlist = self.actions_from_motors()

        self.history = []
        self.history_headers = [str(list(statuses.keys())), 'state', 'action',
                                str(list(statuses.keys()))]

    def __repr__(self):
        return ('gamma=' + str(self.gamma) + '\n' +
                'init=' + str(self.init) +
                ('(' + self.sensor_model(self.init) if self.sensor_model else '') + ')\n' +
                'sensors=' + str(self.sensor_model.sensors) + '\n' +
                'statuses=' + str(self.statuses) + '\n' +
                'motors=' + str(self.motor_model.motors) + '\n' +
                'motor_model=' + str(self.motor_model) + '\n' +
                'sensor_model=' + str(self.sensor_model) + '\n' +
                'actlist=' + str(self.actlist) + '\n' +
                'actions (using motor_model)=' +
                str([self.motor_model(act) for act in self.actlist]) + '\n' +
                'in_terminal=' + str(self.in_terminal()))

    def update_statuses(self, state, action, rewards):
        if self.motor_model:
            action = self.motor_model(action)
        if self.sensor_model:
            state = self.sensor_model(state)
        self.history.append((list(self.statuses.values()), state, action, list(rewards.values())))

        for k, v in rewards.items():
            self.statuses[k] += v

    def reset(self):
        self.statuses = dict(self.init_statuses)

    def in_terminal(self):
        return min([v for k, v in self.statuses.items()]) <= 0

    #
    # motors=[m1,m2,...,mn] actions=[(m1=T/F,m2=T/F,...,mn=T/F)]
    # actions are tuples where each motor is represented by one position with a
    # boolean indicating if it is active.
    #
    # Generate all possible actions from a list of motors (2^n combinations)
    # [m1,m2,...,mn] -> [(F,F,...,F),...,(T,T,...,T])]
    def actions_from_motors(self):
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

        return list(map(tuple, actions_(self.motor_model.motors)))

# Keeps track of the history of actions performed
class NetworkAgent(Agent):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, program=None, name='nonname', ndp=None, max_iterations=None):

        self.program = program or self

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
        return self.max_iterations and self.iterations >= self.max_iterations

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
        motor_model, sensor_model, statuses = (self.ndp.motor_model, self.ndp.sensor_model,
                                               self.ndp.statuses)

        # save history for statuses, state, action, reward
        if motor_model:
            a = motor_model(a)
        if sensor_model:
            s = sensor_model(s)
        self.history.append((list(statuses.values()), s, a, list(r.values())))

        # save status history
        for status in self.ndp.statuses:
            self.status_history[status].append(r[status])

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
class NetworkQLearningAgent(NetworkAgent):
    # pylint: disable=too-many-instance-attributes, too-many-arguments
    def __init__(self, ndp, Ne, Rplus, alpha=None, delta=0.5, max_iterations=None, name='noname'):

        # Multidimensional Q: Q_status[s, a]
        self.Q = {}
        for status in ndp.statuses:
            self.Q[status] = defaultdict(float)

        self.Ne = Ne                      # iteration limit in exploration function
        self.Nsa = defaultdict(float)
        self.delta = delta
        self.Rplus = Rplus                # large value to assign before iteration limit
        self.gamma = ndp.gamma

        if alpha:
            self.alpha = alpha
        else:
            self.alpha = lambda n: 1./(1+n)  # udacity video

        super().__init__(None, name, ndp, max_iterations)

    def __repr__(self):
        res = ''
        for status in self.ndp.statuses:
            lst = sorted([(self.ndp.sensor_model(k[0]) if k[0] else 'None',
                           self.ndp.motor_model(k[1]), v) for k, v in self.Q[status].items()],
                         key=lambda x: x and x[0])
            lst = list(filter(lambda x: x[2] != 0.0, lst))
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
            U = dict(map(lambda x: (self.ndp.sensor_model(x[0]), x[1]), U.items()))
            pi = dict(map(lambda x: (self.ndp.sensor_model(x[0]),
                                     self.ndp.motor_model(x[1])), pi.items()))
            res[status] = U, pi
        return res

    # check if status is zero or less and keep track of number of
    # iterations and stop after some limit has been reached
    def check_terminal(self):
        self.in_terminal = self.ndp.in_terminal() or self.check_iterations()
        return self.in_terminal

    # Exploration function. Returns fixed Rplus untill agent has visited state,
    # action a Ne number of times.
    def f(self, u, n):
        if n < self.Ne:
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
