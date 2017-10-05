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

    def __call__(self, percept):
        res, self.vars_ = self.func(percept, self.vars_)
        return res

    def __repr__(self):
        return ('(' + self.type_ + ' - vars:' + str(self.vars_) +
                ',children:' + str(self.children) + ')')

# Create a sensor that recognise Things of type `cls`, radius is ignored
def SENSOR_factory(cls):
    return Node('SENSOR:' + cls.__name__,
                lambda things, _: (any([isinstance(x, cls) for x, _ in things]), []),
                [], [])

def AND_factory(indexes, state):
    return Node('AND', lambda _, _2: (all([state[i] for i in indexes]), []),
                [], indexes)

# t:state[idx1] followed by t+1:state[idx2]
# NOTE: the value of t:state[idx2] and t+1:state[idx1] makes no difference
def SEQ_factory(idx1, idx2, state):
    return Node('SEQ',
                lambda things, vars_: (bool(vars_[0]) and state[idx2], [state[idx1]]),
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
        for i in node.children:
            self.update_node(self.nodes[i], percept)
        self.state[idx] = node(percept)

    def get(self):
        return tuple(self.state)

    # return a set of indexes for the nodes that are active
    def getS(self):
        res = set()
        for i in range(0, len(self.state)):
            if self.state[i]:
                res |= {i}
        return res

    def add_root_node(self, node):
        self.state.append(None)
        self.nodes.append(node)
        self.root_nodes.append(node)
        return len(self.state) - 1

    # when other nodes than SENSORs are added are the nodes below no longer
    # root nodes
    def delete_root_nodes(self, indexes):
        for i in indexes:
            self.root_nodes.remove(self.nodes[i])

    def add_SENSOR_node(self, cls):
        return self.add_root_node(SENSOR_factory(cls))

    def add_AND_node(self, indexes):
        idx = self.add_root_node(AND_factory(indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx

    def add_SEQ_node(self, idx1, idx2):
        idx = self.add_root_node(SEQ_factory(idx1, idx2, self.state))
        self.delete_root_nodes([idx1, idx2])
        return idx

    def delete_nodes(self, indexes):
        self.delete_root_nodes(indexes)
        for idx in indexes:
            for child in self.nodes[idx].children:
                self.root_nodes.append(self.nodes[child])
            self.nodes[idx] = self.state[idx] = None

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
    def __init__(self, motor_names=None):
        super().__init__()
        # indexes of the MOTOR:s in self.state
        self.motors = []
        self.motor_names = motor_names or []
        for name in self.motor_names:
            self.motors.append(self.add_MOTOR_node(name))

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
            self.state[idx] = idx in percept
        for node in self.root_nodes:
            self.update_node(node, None)

    def update_node(self, node, percept):
        node(None)
        for i in node.children:
            self.update_node(self.nodes[i], None)

    # return a set of indexes for the motors that are active
    def get(self):
        res = set()
        for i in self.motors:
            if self.state[i]:
                res |= {i}
        return res

    def add_MOTOR_node(self, name):
        self.motor_names.append(name)
        self.motors.append(len(self.state))
        return self.add_root_node(MOTOR_factory(name))

    def add_MAND_node(self, indexes):
        idx = self.add_root_node(MAND_factory(len(self.state), indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx

    def add_MSEQ_node(self, indexes):
        idx = self.add_root_node(MSEQ_factory(len(self.state), indexes, self.state))
        self.delete_root_nodes(indexes)
        return idx
