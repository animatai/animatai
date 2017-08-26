# pylint: disable=missing-docstring, invalid-name, too-many-arguments
#
# A Markov Decision Process (MDP)
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

from utils import argmax

def find_in_col(val, col, l):
    return list(filter(lambda x: x[col] == val, l))

class MDP:
    def __init__(self, init, actlist, terminals, transitions, states, rewards, gamma=.9):
        if not 0 < gamma <= 1:
            raise ValueError("An MDP must have 0 < gamma <= 1")

        self.init = init
        self.gamma = gamma
        self.states = states
        self.rewards = rewards
        self.actlist = actlist
        self.terminals = terminals
        self.transitions = transitions

    # R(s, a, s') modelled with [ (s, a, s', reward) ]. '*' specifies any state/action
    def R(self, state, action='*', statep='*'):
        rewards = self.rewards
        s = state if find_in_col(state, 0, rewards) else '*'
        a = action if find_in_col(action, 1, rewards) else '*'
        sp = statep if find_in_col(statep, 2, rewards) else '*'
        r = list(filter(lambda x: x[0] == s and x[1] == a and x[2] == sp, rewards))
        if not r:
            return None
        return r[0][3]

    def T(self, state, action):
        if action is None:
            return [(0.0, state)]
        return self.transitions[state][action]

    def actions(self, state):
        if state in self.terminals:
            return [None]
        return self.actlist

# calculates utilities when rewards are connected to states only, R(s)
def value_iteration(mdp, epsilon=0.001, max_steps=1000):
    U1 = {s: 0.0 for s in mdp.states}
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    steps = 0
    while True:
        U = U1.copy()
        delta = 0
        steps += 1
        for s in mdp.states:
            U1[s] = R('*', '*', s) + gamma * max([sum([p * U[s1] for (p, s1) in T(s, a)])
                                                  for a in mdp.actions(s)])
            delta = max(delta, abs(U1[s] - U[s]))
        if delta < epsilon * (1 - gamma) / gamma or steps == max_steps:
            return U1

# calculates utilities when rewards are connected to states, actions and future states
# R(s, a, s')
def value_iteration2(mdp, epsilon=0.001, max_steps=1000):
    U1 = {s: 0.0 for s in mdp.states}
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    steps = 0
    while True:
        U = U1.copy()
        delta = 0
        steps += 1
        for s in mdp.states:
            U1[s] = max([sum([p * (R(s, a, s1) + gamma * U[s1]) for (p, s1) in T(s, a)])
                         for a in mdp.actions(s)])

            delta = max(delta, abs(U1[s] - U[s]))
        if delta < epsilon * (1 - gamma) / gamma or steps == max_steps:
            return U1

def best_policy(mdp, U):
    # pylint: disable=cell-var-from-loop
    pi = {}
    for s in mdp.states:
        pi[s] = argmax(mdp.actions(s), key=lambda a: expected_utility(a, s, U, mdp))
    return pi

def expected_utility(a, s, U, mdp):
    return sum([p * U[s1] for (p, s1) in mdp.T(s, a)])
