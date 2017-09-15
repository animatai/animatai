# pylint: disable=missing-docstring, global-statement, eval-used, too-few-public-methods, no-self-use, invalid-name, line-too-long
#
# Adapted from https://github.com/aimacode/aima-python


# Imports
# =======

import random

from gzutils.gzutils import DotDict, Logging, save_csv_file

from .utils import turn_heading, distance_squared


# Setup constants and logging
# ===========================

PERCEPTIBLE_DISTANCE = 0
DEBUG_MODE = True
l = Logging('agents', DEBUG_MODE)

# The code
# =========

class NamedObject:
    def __init__(self, name=None):
        self.__name__ = name

    def __repr__(self):
        return '<{} ({})>'.format(self.__name__, self.__class__.__name__)

    def __eq__(self, other):
        return self.__name__ == other.__name__

    def __hash__(self):
        return hash(self.__name__)


# This represents any physical object that can appear in an Environment.
# You subclass Thing to get the things you want.  Each thing can have a
# .__name__  slot (used for output only)
class Thing(NamedObject):
    def __init__(self, name='noname'):
        self.alive = None
        self.location = None
        self.__name__ = name

    def __repr__(self):
        return '<{} {} ({})>'.format(self.__name__, self.location, self.__class__.__name__)

    # Things that are 'alive' should return true
    def is_alive(self):
        return hasattr(self, 'alive') and self.alive


# This represents any non-spatial/physical artifact that can appear in an Environment.
class NSArtifact(NamedObject):
    pass

# Use for actions involving Things
class Action(NamedObject):
    pass

# Use for actions involving NsArtifacts
class NsAction(NamedObject):
    pass


# An Agent is a subclass of Thing with one required slot,
# .program, which should hold a function that takes one argument, the
# percept, and returns an action. (What counts as a percept or action
# will depend on the specific environment in which the agent exists.)
# Note that 'program' is a slot, not a method.  If it were a method,
# then the program could 'cheat' and look at aspects of the agent.
# It's not supposed to do that: the program can only look at the
# percepts.  An agent program that needs a model of the world (and of
# the agent itself) will have to build and maintain its own model.
# There is an optional slot, .performance, which is a number giving
# the performance measure of the agent in its environment.
class Agent(Thing):
    # pylint: disable=too-many-instance-attributes

    def __init__(self, program=None, name='noname'):
        super().__init__()
        self.bump = False
        self.alive = True
        self.holding = []
        self.__name__ = name
        self.direction = Direction(Direction.R)
        self.performance = 0
        if program:
            self.program = program

    def __repr__(self):
        return '<alive:{}, direction:{}, name:{} ({})>'.format(self.alive,
                                                               self.direction,
                                                               self.__name__,
                                                               self.__class__.__name__)

    # Returns True if this agent can grab this thing. Override for appropriate
    # subclasses of Agent and Thing.
    # _=thing
    def can_grab(self, _):
        return False


# Wrap the agent's program to print its input and output. This will let
# you see what the agent is doing in the environment.
def trace_agent(agent):
    old_program = agent.program

    def new_program(percept):
        action = old_program(percept)
        print('{} perceives {} and does {}'.format(agent, percept, action))
        return action
    agent.program = new_program
    return agent



# Abstract class representing an Environment.  'Real' Environment classes
# inherit from this. Your Environment will typically need to implement:
# percept:           Define the percept that an agent sees.
# execute_action:    Define the effects of executing an action.
#                   Also update the agent.performance slot.
# The environment keeps a list of .things and .agents (which is a subset
# of .things). Each agent has a .performance slot, initialized to 0.
# Each thing has a .location slot, even though some environments may not
# need this.
class Environment:
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        self.things = []
        self.agents = []
        self.ns_artifacts = {} # indexed with time
        self.actions = None
        self.rewards = None

        # These needs to be set in the subclass when rendering in the browser
        self.wss = None
        self.world = None
        self.wss_cfg = None

    def __repr__(self):
        return '<things:{s.things}, agents:{s.agents}, ns_artifacts:{s.ns_artifacts} ({s.__class__.__name__}>)'.format(s=self)

    def thing_classes(self):
        return []  # List of classes that can go into environment

        # Return the percept that the agent sees at this point. (Implement this)
    def percept(self, agent, time):
        raise NotImplementedError

    # Change the world to reflect this action. (Implement this)
    def execute_action(self, agent, action, time):
        raise NotImplementedError

    # Return the reward for `agent` taking `action`. ALways return 1 for testing
    # purposes, Implement this.
    # _ = agent, _2 = action
    def calc_performance(self, _, _2):
        return 1

    # Default location to place a new thing with unspecified location
    # param=thing
    def default_location(self, _):
        return None

    # If there is spontaneous change in the world, override this
    def exogenous_change(self):
        pass

    # Needs to be overridden
    def build_world(self):
        pass

    # By default, we're done when we can't find a live agent
    def is_done(self):
        return not any(agent.is_alive() for agent in self.agents)

    # Run the environment for one time step. If the
    # actions and exogenous changes are independent, this method will
    # do. If there are interactions between them, you'll need to
    # override this method.
    def step(self, time):
        if not self.is_done():
            actions, actions1, rewards = self.actions, [], [0]*len(self.agents)

            # calc reward for previous actions
            if actions:
                rewards = []
                for (agent, action) in zip(self.agents, actions):
                    rewards.append(self.calc_performance(agent, action))

            # determine new actions
            for agent, reward in zip(self.agents, rewards):
                l.debug('step  - agent', agent, ', location:', agent.location, ', reward:', reward)

                action = None
                if agent.alive:
                    percept = (self.percept(agent, time), reward)
                    action = agent.program(percept)
                actions1.append(action)

            # execute actions
            for (agent, action1) in zip(self.agents, actions1):
                self.execute_action(agent, action1, time)

            self.actions = actions1
            self.rewards = rewards

            self.exogenous_change()

            # render the updated world in the browser
            self.build_world()
            if self.world and self.wss and self.wss_cfg:
                self.wss.send_update_terrain('\n'.join(self.world))
            for thing in self.things:
                if self.wss and thing.__name__ in self.wss_cfg.agents:
                    self.wss_cfg.agents[thing.__name__]['pos'] = thing.location
                    self.wss.send_update_agent(thing.__name__, self.wss_cfg.agents[thing.__name__])


    # Override to calculate stats etc. at the end
    def finished(self):
        pass

    # Run the Environment for given number of time steps
    def run(self, steps=1000):
        for i in range(steps):
            if self.is_done():
                self.finished()
                return
            self.step(i)

        self.finished()

    # Return all things of a given type
    def list_things(self, tclass=Thing):
        return [thing for thing in self.things if isinstance(thing, tclass)]

    # Return all things exactly at a given location
    def list_things_at(self, location, tclass=Thing):
        return [thing for thing in self.things
                if thing.location == location and isinstance(thing, tclass)]

    # Return all non spatial artifacts at a given point in time
    def list_ns_artifacts_at(self, time, tclass=NSArtifact):
        if not self.ns_artifacts.get(time, False):
            return []
        return [nsartifact for nsartifact in self.ns_artifacts[time]
                if isinstance(nsartifact, tclass)]

    # Return true if at least one of the things at location
    # is an instance of class tclass (or a subclass)
    def some_things_at(self, location, tclass=Thing):
        return self.list_things_at(location, tclass) != []

    # Add a thing to the environment, setting its location. For
    # convenience, if thing is an agent program we make a new agent
    # for it. (Shouldn't need to override this
    def add_thing(self, thing, location=None):
        if not isinstance(thing, Thing):
            thing = Agent(thing)
        if thing in self.things:
            l.error("Can't add the same thing twice")
        else:
            thing.location = location if location is not None else self.default_location(thing)
            self.things.append(thing)
            if isinstance(thing, Agent):
                thing.performance = 0
                self.agents.append(thing)

    # Add a non spatial artifact to the environment, setting its time.
    # artifacts added at time are available as percepts at time+1
    def add_ns_artifact(self, nsartifact, time):
        if self.ns_artifacts.get(time+1, False) and nsartifact in self.ns_artifacts:
            l.error("Can't add the same ns artifact twice")
        else:
            if not self.ns_artifacts.get(time+1, False):
                self.ns_artifacts[time+1] = []
            self.ns_artifacts[time+1].append(nsartifact)

    # Remove a thing from the environment
    def delete_thing(self, thing):
        try:
            self.things.remove(thing)
        except ValueError as err:
            l.error(err)
            l.error("in Environment.delete_thing. Thing to be removed: {} at {} from list: {}".format(thing, thing.location, [(thing, thing.location) for thing in self.things]))
        if thing in self.agents:
            self.agents.remove(thing)

# A direction class for agents that want to move in a 2D plane
#    Usage:
#        d = Direction("down")
#        To change directions:
#        d = d + "right" or d = d + Direction.R #Both do the same thing
#        Note that the argument to __add__ must be a string and not a Direction object.
#        Also, it (the argument) can only be right or left.
class Direction:

    R = "right"
    L = "left"
    U = "up"
    D = "down"

    def __init__(self, direction):
        self.direction = direction

    def __repr__(self):
        return '{}'.format(self.direction)

    def __add__(self, heading):
        if self.direction == self.R:
            return{
                self.R: Direction(self.D),
                self.L: Direction(self.U),
            }.get(heading, None)
        elif self.direction == self.L:
            return{
                self.R: Direction(self.U),
                self.L: Direction(self.D),
            }.get(heading, None)
        elif self.direction == self.U:
            return{
                self.R: Direction(self.R),
                self.L: Direction(self.L),
            }.get(heading, None)
        elif self.direction == self.D:
            return{
                self.R: Direction(self.L),
                self.L: Direction(self.R),
            }.get(heading, None)

    def move_forward(self, from_location):
        x, y = from_location
        if self.direction == self.R:
            return (x + 1, y)
        elif self.direction == self.L:
            return (x - 1, y)
        elif self.direction == self.U:
            return (x, y - 1)
        elif self.direction == self.D:
            return (x, y + 1)


# This class is for environments on a 2D plane, with locations
# labelled by (x, y) points, either discrete or continuous.
# Agents perceive things within a radius. Each agent in the
# environment has a .location slot which should be a location such
# as (0, 1), and a .holding slot, which should be a list of things
# that are held.
class XYEnvironment(Environment):

    # pylint: disable=too-many-instance-attributes, arguments-differ, too-many-public-methods

    def __init__(self, options):
        super().__init__()

        options = DotDict(options)
        self.options = options
        self.width = options.width or 10
        self.height = options.height or 10
        self.observers = []
        self.thing_counter = 0
        self.environment_history = {}

        # Needs to be set in the subclass when used
        if not hasattr(self, 'ENV_ENCODING'):
            self.ENV_ENCODING = []

        # Sets iteration start and end (no walls).
        self.x_start, self.y_start = (0, 0)
        self.x_end, self.y_end = (self.width, self.height)

        if options.terrain:
            self.width = len(options.terrain[0])
            self.height = len(options.terrain)
            self.x_end, self.y_end = (self.width, self.height)

        # build world from things and terrain
        if options.things:
            self.add_things(options.things)

        if options.save_history_for:
            for cls in options.save_history_for:
                self.environment_history[cls] = []

        # setup rendering in browser if options are there
        if options.wss:
            self.wss = options.wss
            self.wss_cfg = DotDict(options.wss_cfg)


            self.options.wss_cfg['terrain'] = '\n'.join(self.options.terrain)

            self.build_world()
            if self.world:
                self.options.wss_cfg['terrain'] = '\n'.join(self.world)

            self.wss.send_init(self.options.wss_cfg)

    def envcode2class(self, code):
        if not hasattr(self, 'ENV_ENCODING'):
            return None
        res = [cls for cd, cls in self.ENV_ENCODING if cd == code]
        if res:
            return res[0]
        return None

    def class2envcode(self, class_):
        if not hasattr(self, 'ENV_ENCODING'):
            return None
        res = [code for code, cls in self.ENV_ENCODING if cls == class_]
        if res:
            return res[0]
        return None

    # If there is spontaneous change in the world, override this
    def exogenous_change(self):
        if self.options.exogenous_things_prob and random.random() < self.options.exogenous_things_prob:
            self.add_things(self.options.exogenous_things)

    # Adds things to the world using the spec. (list of strings) in the options
    def add_things(self, env):
        if not env:
            return
        width = len(env[0])
        height = len(env)
        x, y = 0, 0
        for y in range(0, height):
            for x in range(0, width):
                class_ = self.envcode2class(env[y][x])
                if class_:
                    self.add_thing(class_(str(self.thing_counter)), (x, y))
                    self.thing_counter += 1

    # build a spec. (list of strings) to be used by the browser when rendering the world
    def build_world(self):
        if not self.options.terrain:
            return
        world = list(map(list, self.options.terrain))
        for thing in self.things:
            x, y = thing.location
            s = self.class2envcode(thing.__class__)
            if s:
                world[y][x] = s
        self.world = list(map(''.join, world))

    # Return all things within radius of location.
    def things_near(self, location, radius=None):
        if radius is None:
            radius = PERCEPTIBLE_DISTANCE
        radius2 = radius * radius
        return [(thing, radius2 - distance_squared(location, thing.location))
                for thing in self.things if distance_squared(location, thing.location) <= radius2]

    # By default, agent perceives things within a default radius.
    def percept(self, agent, time):
        percepts = self.things_near(agent.location)
        percepts.extend(self.list_ns_artifacts_at(time))
        return percepts

    def show_message(self, msg):
        if self.wss:
            self.wss.send_print_message(msg)
        l.info(msg)

    def execute_action(self, agent, action, time):
        if action and isinstance(action, NsAction):
            self.add_ns_artifact(NSArtifact(action.__name__), time)
            return

        agent.bump = False
        if action == Action('TurnRight'):
            agent.direction += Direction.R
        elif action == Action('TurnLeft'):
            agent.direction += Direction.L
        elif action == Action('Forward'):
            agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
#         elif action == 'Grab':
#             things = [thing for thing in self.list_things_at(agent.location)
#                     if agent.can_grab(thing)]
#             if things:
#                 agent.holding.append(things[0])
        elif action == Action('Release'):
            if agent.holding:
                agent.holding.pop()

    # _=thing
    def default_location(self, _):
        return (random.choice(self.width), random.choice(self.height))

    # Move a thing to a new location. Returns True on success or False if there is an Obstacle.
    # If thing is holding anything, they move with him
    def move_to(self, thing, destination):
        thing.bump = self.some_things_at(destination, Obstacle)
        if not thing.bump:
            thing.location = destination
            if self.wss and self.wss_cfg.agents[thing.__name__]:
                self.wss_cfg.agents[thing.__name__]['pos'] = thing.location
                self.wss.send_update_agent(thing.__name__, self.wss_cfg.agents[thing.__name__])
            for o in self.observers:
                o.thing_moved(thing)
            for t in thing.holding:
                self.delete_thing(t)
                self.add_thing(t, destination)
                t.location = destination
        return thing.bump

    # Adds things to the world. If (exclude_duplicate_class_items) then the item won't be
    # added if the location has at least one item of the same class
    def add_thing(self, thing, location=(1, 1), exclude_duplicate_class_items=False):
        if self.is_inbounds(location):
            if (exclude_duplicate_class_items and
                    any(isinstance(t, thing.__class__) for t in self.list_things_at(location))):
                return
            super().add_thing(thing, location)

    # Checks to make sure that the location is inbounds (within walls if we have walls)
    def is_inbounds(self, location):
        x, y = location
        return not (x < self.x_start or x >= self.x_end or y < self.y_start or y >= self.y_end)

    # Returns a random location that is inbounds (within walls if we have walls)
    def random_location_inbounds(self, exclude=None):
        location = (random.randint(self.x_start, self.x_end),
                    random.randint(self.y_start, self.y_end))
        if exclude is not None:
            while location == exclude:
                location = (random.randint(self.x_start, self.x_end),
                            random.randint(self.y_start, self.y_end))
        return location

    # Deletes thing, and everything it is holding (if thing is an agent)
    def delete_thing(self, thing):
        if isinstance(thing, Agent):
            for obj in thing.holding:
                super().delete_thing(obj)
                for obs in self.observers:
                    obs.thing_deleted(obj)

        super().delete_thing(thing)
        for obs in self.observers:
            obs.thing_deleted(thing)

    # Put walls around the entire perimeter of the grid.
    def add_walls(self):
        for x in range(self.width):
            self.add_thing(Wall(), (x, 0))
            self.add_thing(Wall(), (x, self.height - 1))
        for y in range(self.height):
            self.add_thing(Wall(), (0, y))
            self.add_thing(Wall(), (self.width - 1, y))

        # Updates iteration start and end (with walls).
        self.x_start, self.y_start = (1, 1)
        self.x_end, self.y_end = (self.width - 1, self.height - 1)

    # Save history for environment
    def save_history(self):
        for cls in self.options.save_history_for:
            self.environment_history[cls].append(len(self.list_things(cls)))

    # Save some stats
    def finished(self):
        headers = []
        histories = []
        for agent in self.agents:
            if hasattr(agent, 'status_history'):
                for objective, history in agent.status_history.items():
                    headers.append(agent.__name__ + ':' + objective)
                    histories.append(history)

        for cls, history in self.environment_history.items():
            headers.append(str(cls))
            histories.append(history)

        # Save the performance history to file
        save_csv_file('history.csv', histories, headers)
        l.info('Collected history of ', len(list(zip(*histories))), 'steps')

    # Adds an observer to the list of observers.
    # An observer is typically an EnvGUI.
    # Each observer is notified of changes in move_to and add_thing,
    # by calling the observer's methods thing_moved(thing)
    # and thing_added(thing, loc).
    def add_observer(self, observer):
        self.observers.append(observer)

    # Return the heading to the left (inc=+1) or right (inc=-1) of heading.
    def turn_heading(self, heading, inc):
        return turn_heading(heading, inc)


# Something that can cause a bump, preventing an agent from
# moving into the same square it's in.
class Obstacle(Thing):
    pass


class Wall(Obstacle):
    pass
