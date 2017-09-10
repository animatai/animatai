# pylint: disable=missing-docstring, global-statement, invalid-name
#

# Imports
# =======

from myutils import Logging


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('network', DEBUG_MODE)


#
# nodes - a list of booleans consisting of the sensors and other nodes that
#         have been added to the network (AND, SEQ etc.)
#

# func - the function to apply to the percept:[Things], vars:[any type] -> (boolean, [any type])
# vars - the initial state the function executes in, necessary for SEQ (and other
#        function that require a state)
class Node:
    def __init__(self, type, func, vars, inputs):
        self.type = type
        self.vars = vars
        self.func = func
        self.inputs = inputs

    def __call__(self, things):
        res, self.vars = self.func(things, self.vars)
        return res

    def __repr__(self):
        return '(' + self.type + ' - vars:' + str(self.vars) + ',inputs:' + str(self.inputs) + ')'

# Create a sensor that recognise Things of type `cls`
def sensor_factory(cls):
    return Node('SENSOR:' + cls.__name__, lambda things, _: (any([isinstance(x, cls) for x in things]), []),
                [], [])

def AND_factory(indexes, state):
    return Node('AND', lambda _, _2: (all([state[i] for i in indexes]), []),
                [], indexes)

def SEQ_factory(idx1, idx2, state):
    return Node('SEQ', lambda things, vars: (bool(vars[0]) and state[idx2], [state[idx1]]),
                [None], [idx1, idx2])

class Network:

    def __init__(self):
        self.state = []
        self.nodes = []
        self.root_nodes = []

    def __repr__(self):
        return 'state:' + str(self.state)+ ', nodes:' + str(self.nodes) + ', root_nodes:' + str(self.root_nodes)

    def update(self, percept):
        for node in self.root_nodes:
            self.update_node(node, percept)

    def update_node(self, node, percept):
        idx = self.nodes.index(node)
        for i in node.inputs:
            self.update_node(self.nodes[i], percept)
        self.state[idx] = node(percept)

    def get(self):
        return tuple(self.state)

    def add_root_node(self, node):
        self.state.append(None)
        self.nodes.append(node)
        self.root_nodes.append(node)

    def delete_root_nodes(self, indexes):
        for i in indexes:
            self.root_nodes.remove(self.nodes[i])

    def add_sensor_node(self, cls):
        self.add_root_node(sensor_factory(cls))

    def add_AND_node(self, indexes):
        self.add_root_node(AND_factory(indexes, self.state))
        self.delete_root_nodes(indexes)

    def add_SEQ_node(self, idx1, idx2):
        self.add_root_node(SEQ_factory(idx1, idx2, self.state))
        self.delete_root_nodes([idx1, idx2])
