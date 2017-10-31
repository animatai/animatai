# pylint: disable=missing-docstring, global-statement, invalid-name
#

# Imports
# =======

import math
import os
from random import random
from gzutils.gzutils import Logging, get_output_dir


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('network', DEBUG_MODE)

#
# type - a string speciying the type of node (for information only)
# func - the function to apply to the percept:[(Thing|NonSpatial, radius)],
#        vars:[any type] -> (boolean, [any type])
# vars - the initial state the function executes in, necessary for SEQ (and other
#        function that require a state)
# children - indexes if the nodes that the nodes takes input from (used in the update function)
#
class Node:
    # pylint: disable=too-few-public-methods
    def __init__(self, type_, func, vars_, children):
        self.type_ = type_
        self.vars_ = vars_
        self.func = func
        self.children = children
        self.last_res = None

    def __call__(self, percept):
        # This is necessary for nodes where the state is updated in each call (SEQ and RAND)
        if self.last_res is not None:
            return self.last_res
        self.last_res, self.vars_ = self.func(percept, self.vars_)
        return self.last_res

    def __repr__(self):
        return ('(' + self.type_ + ' - vars:' + str(self.vars_) +
                ',children:' + str(self.children) + ')')

# Create a sensor that recognise Things of type `cls`, radius is ignored
def SENSOR_factory(cls, name=None):
    if name is None:
        return Node('SENSOR:' + cls.__name__,
                    lambda things, _: (any([isinstance(x, cls) for x, _ in things]), []),
                    [], [])
    return Node('SENSOR:' + cls.__name__ + ":" + name,
                lambda things, _: (any([isinstance(x, cls) and x.__name__ == name for x, _ in things]), []),
                [], [])


def AND_factory(indexes, state):
    return Node('AND', lambda _, _2: (all([state[i] for i in indexes]), []),
                [], indexes)

def OR_factory(indexes, state):
    return Node('OR', lambda _, _2: (any([state[i] for i in indexes]), []),
                [], indexes)

def ONE_factory(index, indexes, state):
    return Node('ONE:'+str(index),
                lambda _, _2: (all([state[index] if i == index
                                    else not state[i]
                                    for i in indexes]), []),
                [], indexes)

def MIN_factory(n, indexes, state):
    return Node('MIN:'+str(n), lambda _, _2: ([state[i] for i in indexes].count(True) >= n, []),
                [], indexes)

def MAX_factory(n, indexes, state):
    return Node('MAX:'+str(n), lambda _, _2: ([state[i] for i in indexes].count(True) <= n, []),
                [], indexes)

# _=indexes, _2=state
def RAND_factory(prob):
    return Node('RAND-'+str(prob), lambda _, _2: (random() < prob, []),
                [], [])

def NOT_factory(indexes, state):
    return Node('NOT', lambda _, _2: (all([not state[i] for i in indexes]), []),
                [], indexes)

# t:state[idx1] followed by t+1:state[idx2]
# NOTE: the value of t:state[idx2] and t+1:state[idx1] makes no difference
#def SEQ_factory(idx1, idx2, state):
#    return Node('SEQ',
#                lambda things, vars_: (bool(vars_[0]) and state[idx2], [state[idx1]]),
#                [None], [idx1, idx2])

# Create a counter initially set to 0 each time state[index] is true.
# Update state[children[counter]] each time update is called.
# Increase the counter until all children have been updated, then delete it.
# Many counters can exist at the same time.
# vars = [counter1, ..., countern]
def SEQ_factory(children, state):
    def update(_, vars_):
        # the (seq, counter) tuples are stored in reverse order in vars_
        if state[children[0]]:
            vars_.insert(0, (True, 0))
        new_vars = []
        seq = False
        counter = math.inf
        for seq, counter in vars_:
            seq = seq and state[children[counter]]
            if counter < len(children) - 1:
                new_vars.append((seq, counter + 1))

        return (seq and counter == len(children) - 1, new_vars)
    return Node('SEQ', update, [], children)


#
# state - a list of booleans consisting of the sensors and other nodes that
#         have been added to the network (AND, SEQ etc.)
# nodes - a list of Node objects used to calculate the values for the SENSORS and
#         other types of nodes (AND, SEQ etc.)
# root_nodes - the root Nodes in the trees that makes up the network
#
class Network:
    # pylint: disable=too-many-public-methods

    # sensors = [('sensor name', Thing to recognise)]
    def __init__(self, sensors=None, needs=None):
        self.state = []
        self.nodes = []
        self.root_nodes = []
        if sensors:
            self.add_sensors(sensors)
        self.needs = {}
        self.needs_initial = {}
        if needs:
            self.add_NEEDs(needs)

    def add_sensors(self, sensors):
        for _, cls in sensors:
            self.add_SENSOR_node(cls)

    def __repr__(self):
        res = 'nodes - '
        for i in range(0, len(self.nodes)):
            node = self.nodes[i]
            res += (str(i) + ':' + node.type_ + ':' + str(node.vars_) + ':' +
                    str(self.state[i]) + ':' + str(node.children) + ';')

        res += 'root nodes - '
        for node in self.root_nodes:
            res += str(self.nodes.index(node)) + ','
        return res

    def toGraphviz(self, color_edges=False):
        colors = ['black', 'blue', 'brown', 'cyan', 'darkgreen', 'deeppink', 'gold']
        res = 'digraph G {\n\tsize ="8,8";\n'
        for i in range(0, len(self.nodes)):
            res += '\t{} [label="{}\\n{}\\n{}"];\n'.format(i, i,
                                                           self.nodes[i].type_,
                                                           self.state[i])
            res += '\tedge [color={}];\n'.format(colors[i % len(colors)]) if color_edges else ''
            for child in self.nodes[i].children:
                res += '\t{}->{};\n'.format(child, i)
        res += '}'
        return res

    def saveGraphviz(self, filename, output_dir=None):
        # Save the performance history to file
        if not output_dir:
            output_dir = get_output_dir('/../output', __file__)
        output_path = os.path.join(output_dir, filename)
        filep = open(output_path, 'w')
        print(self.toGraphviz(), file=filep)
        filep.close()

    # the state of the network is updated using a depth first search starting
    # in the root nodes.
    def update(self, percept):
        percepts, rewards = percept
        self.update_NEEDs(rewards)
        for node in self.nodes:
            node.last_res = None
        for node in self.root_nodes:
            self.update_node(node, percepts)
        return (self.get(), rewards)

    def update_node(self, node, percept):
        idx = self.nodes.index(node)
        for i in node.children:
            self.update_node(self.nodes[i], percept)
        self.state[idx] = node(percept)

    def get_state(self):
        return tuple(self.state)

    # return a set of indexes for the nodes that are active
    def get(self):
        res = set()
        for i in range(0, len(self.state)):
            if self.state[i]:
                res |= {i}
        return frozenset(list(res))

    def add_root_node(self, node):
        self.state.append(None)
        self.nodes.append(node)
        self.root_nodes.append(node)
        return len(self.state) - 1

    # when other nodes than SENSORs are added are the nodes below no longer
    # root nodes
    def delete_root_nodes(self, indexes):
        for i in indexes:
            if self.nodes[i] in self.root_nodes:
                self.root_nodes.remove(self.nodes[i])

    def add_SENSOR_node(self, cls, name=None):
        return self.add_root_node(SENSOR_factory(cls, name))

    def add_RAND_node(self, prob):
        return self.add_root_node(RAND_factory(prob))

    def add_AND_node(self, indexes):
        idx = self.add_root_node(AND_factory(indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx

    def add_OR_node(self, indexes):
        idx = self.add_root_node(OR_factory(indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx

    def add_ONE_node(self, index, indexes):
        idx = self.add_root_node(ONE_factory(index, indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx

    def add_MIN_node(self, n, indexes):
        idx = self.add_root_node(MIN_factory(n, indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx

    def add_MAX_node(self, n, indexes):
        idx = self.add_root_node(MAX_factory(n, indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx

    def add_NOT_node(self, indexes):
        idx = self.add_root_node(NOT_factory(indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx

#    def add_SEQ_node(self, idx1, idx2):
#        idx = self.add_root_node(SEQ_factory(idx1, idx2, self.state))
#        self.delete_root_nodes([idx1, idx2])
#        return idx

    def add_SEQ_node(self, indexes):
        idx = self.add_root_node(SEQ_factory(indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx

    def add_NEEDs(self, objective_initial):
        self.needs = {**self.needs, **objective_initial}
        self.needs_initial = {**self.needs_initial, **objective_initial}
        return self.needs

    def get_NEEDs(self):
        return self.needs

    def update_NEEDs(self, rewards):
        for objective, reward in rewards.items():
            self.needs[objective] += reward
            self.needs[objective] = min(self.needs_initial[objective], self.needs[objective])

    def delete_nodes(self, indexes):
        self.delete_root_nodes(indexes)
        for idx in indexes:
            for child in self.nodes[idx].children:
                self.root_nodes.append(self.nodes[child])
            self.nodes[idx] = self.state[idx] = None

    def top_active_(self, node):
        idx = self.nodes.index(node)
        if self.state[idx]:
            return {idx}
        res = set()
        for child in node.children:
            res |= self.top_active_(self.nodes[child])
        return res

    def top_active(self, percept=None):
        if percept:
            self.update(percept)
        res = set()
        for node in self.root_nodes:
            res |= self.top_active_(node)
        return frozenset(list(res))


#
# MotorNetwork
#
# Similar to Network but with MOTORS in the leafes. The network nodes can be
# MAND, MSEQ etc. Nodes are added in the same way as in the Network class
# (and the root nodes updated as more nodes are added). Updating starts with
# a tuple representing the state for the root nodes.#
#
# TODO: Should separate out the common parts rather than inheriting Network
#       (add_SENSOR_node etc. makes little sense in this class)
#

# The Node class is used in a different way here.
#
# func - a function that updates the state of the nodes. The only input is the
#        current state of the nodes which has been set by the update method.
#        (vars: [any type] -> [])

# Create a motor
def MOTOR_factory(name):
    return Node('MOTOR:' + name,
                lambda _, _2: (None, []),
                [], [])

def MAND_factory(index, children, state):
    def update(_, _2):
        for idx in children:
            state[idx] = state[index]
        return (None, [])
    return Node('MAND', update, [], children)

# Create a counter initially set to 0 each time state[index] is true.
# Update state[children[counter]] each time update is called.
# Increase the counter until all children have been updated, then delete it.
# Many counters can exist at the same time.
# vars = [counter1, ..., countern]
def MSEQ_factory(index, children, state):
    def update(_, vars_):
        if state[index]:
            vars_.append(0)
        new_vars = []
        for counter in vars_:
            state[children[counter]] = True
            if counter < len(children) - 1:
                new_vars.append(counter + 1)

        return (None, new_vars)
    return Node('MSEQ', update, [], children)


class MotorNetwork(Network):

    # motors = ['motor name']
    def __init__(self, motor_names=None, motors_to_action=None):
        super().__init__()

        motor_names = motor_names or []

        # indexes of each MOTOR in self.state
        self.motors = []
        self.motor_names = []
        self.motors_to_action = motors_to_action or {'*': '-'}

        for name in motor_names:
            self.add_MOTOR_node(name)

    def __repr__(self):
        return ('state:' + str(self.state) +
                ', motor_names:' + str(self.motor_names) +
                ', nodes:' + str(self.nodes) +
                ', root_nodes:' + str(self.root_nodes) +
                ', motors:' + str(self.motors))

    # indexes is a set with the indexes of the nodes that should be True
    def update(self, percept):
        # pylint disable=arguments-differ
        for idx in range(0, len(self.state)):
            self.state[idx] = idx in percept if percept else False
        for node in self.root_nodes:
            self.update_node(node, None)
        return self.get_action()

    def update_node(self, node, percept):
        node(None)
        for i in node.children:
            self.update_node(self.nodes[i], None)

    # return a (frozen)set of indexes for the motors that are active
    def get(self):
        res = set()
        for i in self.motors:
            if self.state[i]:
                res |= {i}
        return frozenset(list(res))

    def get_action(self):
        action = self.motors_to_action.get(self.get(), None)
        return action or self.motors_to_action['*']

    def add_MOTOR_node(self, name):
        self.motor_names.append(name)
        idx = self.add_root_node(MOTOR_factory(name))
        self.motors.append(idx)
        return idx

    def add_MAND_node(self, indexes):
        idx = self.add_root_node(MAND_factory(len(self.state), indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx

    def add_MSEQ_node(self, indexes):
        idx = self.add_root_node(MSEQ_factory(len(self.state), indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx
