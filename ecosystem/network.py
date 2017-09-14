# pylint: disable=missing-docstring, global-statement, invalid-name
#

# Imports
# =======

from gzutils.gzutils import Logging


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('network', DEBUG_MODE)

#
# func - the function to apply to the percept:[Things], vars:[any type] -> (boolean, [any type])
# vars - the initial state the function executes in, necessary for SEQ (and other
#        function that require a state)
class Node:
    # pylint: disable=too-few-public-methods
    def __init__(self, type_, func, vars_, inputs):
        self.type_ = type_
        self.vars_ = vars_
        self.func = func
        self.inputs = inputs

    def __call__(self, things):
        res, self.vars_ = self.func(things, self.vars_)
        return res

    def __repr__(self):
        return '(' + self.type_ + ' - vars:' + str(self.vars_) + ',inputs:' + str(self.inputs) + ')'

# Create a sensor that recognise Things of type `cls`
def sensor_factory(cls):
    return Node('SENSOR:' + cls.__name__,
                lambda things, _: (any([isinstance(x, cls) for x in things]), []),
                [], [])

def AND_factory(indexes, state):
    return Node('AND', lambda _, _2: (all([state[i] for i in indexes]), []),
                [], indexes)

def SEQ_factory(idx1, idx2, state):
    return Node('SEQ',
                lambda things, vars: (bool(vars[0]) and state[idx2], [state[idx1]]),
                [None], [idx1, idx2])

#
# state - a list of booleans consisting of the sensors and other nodes that
#         have been added to the network (AND, SEQ etc.)
# nodes - a list of Node objects used to calculate the values for the SENSORS and
#         other types of nodes (AND, SEQ etc.)
# root_nodes - the root Nodes in the trees that makes up the network
#
class Network:

    # sensors = [('sensor name', Thing to recognise)]
    def __init__(self, sensors=None):
        self.state = []
        self.nodes = []
        self.root_nodes = []
        if sensors:
            self.add_sensors(sensors)

    def add_sensors(self, sensors):
        for _, cls in sensors:
            self.add_SENSOR_node(cls)

    def __repr__(self):
        return ('state:' + str(self.state) +
                ', nodes:' + str(self.nodes) +
                ', root_nodes:' + str(self.root_nodes))

    # the state of the network is updated using a depth first search starting
    # in the root nodes. Nodes might be updated several times, but this will do
    # for now.
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

    # when other nodes than SENSORs are added are the nodes below no longer
    # root nodes
    def delete_root_nodes(self, indexes):
        for i in indexes:
            self.root_nodes.remove(self.nodes[i])

    def add_SENSOR_node(self, cls):
        self.add_root_node(sensor_factory(cls))

    def add_AND_node(self, indexes):
        self.add_root_node(AND_factory(indexes, self.state))
        self.delete_root_nodes(indexes)

    def add_SEQ_node(self, idx1, idx2):
        self.add_root_node(SEQ_factory(idx1, idx2, self.state))
        self.delete_root_nodes([idx1, idx2])
