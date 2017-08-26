# pylint: disable=missing-docstring, global-statement, invalid-name, too-few-public-methods, no-self-use
#
# A random Mother cachelot and calf
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

import os
import datetime

from agents import Thing
from agents import Obstacle
from agents import Direction
from agents import NSArtifact
from agents import XYEnvironment

from myutils import DotDict
from myutils import Logging


# Setup constants and logging
# ===========================

CSV_SEPARATOR = ';'
DEBUG_MODE = True
l = Logging('sea', DEBUG_MODE)


# Functions
# ========

def getOutputPath():
    try:
        currentDir = os.path.dirname(os.path.abspath(__file__)) + '/..'
        outputDir = currentDir + os.path.join('/output', datetime.datetime.now().isoformat())
        os.makedirs(outputDir)
        return os.path.join(outputDir, "history.csv")

    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# Classes
# ========

class Squid(Thing):
    pass

class Sing(NSArtifact):
    pass


# motors are executed instead of single actions. motors consists of several actions
# and setup in the options for the agent.
class Sea(XYEnvironment):

    # pylint: disable=arguments-differ

    def __init__(self, options):
        self.options = DotDict(options)
        self.ENV_ENCODING = [('s', Squid), ('X', Obstacle)]
        super().__init__(options)

    def percepts_to_sensors(self, agent, percepts_, ns_percept):
        # pylint: disable=cell-var-from-loop
        res = []
        for p in percepts_:
            sensors = list(filter(lambda x: isinstance(p[0] if ns_percept else p, x[0]),
                                  self.options.agents[agent.__name__]['sensors']))
            sensors = list(map(lambda x: x[1], sensors))
            if sensors:
                res += sensors

        return res

    def percept(self, agent):
        things = self.things_near(agent.location)
        return self.percepts_to_sensors(agent, things, True)

    def ns_percept(self, agent, time):
        ns_artifacts = self.list_ns_artifacts_at(time)
        return self.percepts_to_sensors(agent, ns_artifacts, False)

    def save_history(self, agent):
        if not hasattr(agent, 'objective_history'):
            agent.objective_history = {}
            for objective in agent.objectives:
                agent.objective_history[objective] = []

        for objective in agent.objectives:
            agent.objective_history[objective].append(agent.objectives[objective])

    def check_is_alive(self, agent):
        for objective in agent.objectives:
            if agent.objectives[objective] <= 0:
                agent.alive = False

    def calc_performance(self, agent, action_performed, nsaction_performed):
        # pylint: disable=len-as-condition
        if not hasattr(agent, 'objectives'):
            agent.objectives = self.options.objectives.copy()
            self.save_history(agent)

        for rewarded_action, things_and_objectives in self.options.rewards.items():
            if action_performed == rewarded_action or nsaction_performed == rewarded_action:
                for rewarded_thing, obj_and_rewards in things_and_objectives.items():
                    if rewarded_thing and len(self.list_things_at(agent.location, rewarded_thing)):
                        for obj, reward in obj_and_rewards.items():
                            agent.objectives[obj] += reward
                    elif rewarded_thing is None:
                        for obj, reward in obj_and_rewards.items():
                            agent.objectives[obj] += reward

        self.check_is_alive(agent)
        self.save_history(agent)
        l.info(agent.__name__, 'status:', agent.objectives)

    def execute_ns_action(self, agent, motor, time):
        '''change the state of the environment for a non spatial attribute, like sound'''
        if not motor:
            return

        nsactions = list(filter(lambda x: x[0] == motor,
                                self.options.agents[agent.__name__]['motors']))
        if not nsactions:
            l.info('Motor without nsactions:', motor)
            return

        # First item in list, second part of tuple
        nsactions = nsactions[0][1]

        agent.bump = False
        for nsaction in nsactions:
            if nsaction == 'sing':
                self.add_ns_artifact(Sing(), time)
            else:
                l.error('execute_action:unknow nsaction', nsaction,
                        'for agent', agent, 'at time', time)

    def execute_action(self, agent, motor, time):
        if not motor:
            return

        self.show_message((agent.__name__ + ' activating ' + motor + ' at location ' +
                           str(agent.location) + ' and time ' + str(time)))
        def up():
            agent.direction += Direction.L
            agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
            agent.direction += Direction.R

        def down():
            agent.direction += Direction.R
            agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
            agent.direction += Direction.L

        def forward():
            agent.bump = self.move_to(agent, agent.direction.move_forward(agent.location))
            # a torus world
            agent.location = (agent.location[0] % self.width, agent.location[1])

        def eat():
            squid = self.list_things_at(agent.location, Squid)
            if squid:
                self.delete_thing(squid[0])

        # The direction of the agent should always be 'right' in this world
        assert agent.direction.direction == Direction.R

        actions = list(filter(lambda x: x[0] == motor,
                              self.options.agents[agent.__name__]['motors']))
        if not actions:
            l.info('Motor without actions:', motor)
            return

        # First item in list, second part of tuple
        actions = actions[0][1]

        agent.bump = False
        for action in actions:
            if action == 'down':
                down()
            elif action == 'up':
                up()
            elif action == 'forward':
                forward()
            elif action == 'eat':
                eat()
            else:
                l.error('execute_action:unknow action', action, 'for agent', agent, 'at time', time)

    def finished(self):
        """Print some stats"""
        headers = []
        histories = []
        for agent in self.agents:
            for objective, history in agent.objective_history.items():
                headers.append(agent.__name__ + ':' + objective)
                histories.append(history)

        headers = CSV_SEPARATOR.join(headers)
        res = zip(*histories)

        # Save the performance history to file
        outputPath = getOutputPath()
        l.debug(outputPath)
        fp = open(outputPath, 'w')
        print(headers, file=fp)
        print('\n'.join([CSV_SEPARATOR.join([str(x).replace('.',',') for x in line]) for line in res]), file=fp)
        fp.close()

        l.info('Output saved to:', outputPath)
