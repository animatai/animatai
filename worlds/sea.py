# pylint: disable=missing-docstring, global-statement, invalid-name, too-few-public-methods, no-self-use
#
# A random Mother cachelot and calf
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

from agents import Thing
from agents import Obstacle
from agents import Direction
from agents import NSArtifact
from agents import XYEnvironment

from myutils import DotDict
from myutils import Logging
from myutils import get_output_dir, save_csv_file

# Setup constants and logging
# ===========================

DEBUG_MODE = True
l = Logging('sea', DEBUG_MODE)


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
        self.save_history_for = [Squid]
        super().__init__(options)

    # to be used after the __call__ function
    def any_measurement_decreased(self):
        any_obj = list(self.environment_history)[0]
        i, res =  len(self.environment_history[any_obj]), False
        if i < 2:
            return False
        for cls in self.save_history_for:
            res = res or self.environment_history[cls][i] < self.environment_history[cls][i - 1]
        return res

    def check_history(self, agent):
        if agent.any_status_increased() and not self.any_measurement_decreased():
            l.debug('**** SUSPCICOUS *****', obj_incr, env_decr, agent.objective_history[objective][current_pos], agent.objective_history[objective][current_pos-1], self.environment_history[cls][current_pos], self.environment_history[cls][current_pos])

    # reward dict:
    #     'reward':{
    #        'eat_and_forward': {
    #            Squid: { 'energy': 0.1 },
    #            None: { 'energy': -0.05 }
    #        },
    #
    # TODO: Working - Change to: state, action, state1, reward
    # ((s1:bool,...,sn:bool), (m1:bool,...,mn:bool), (s1:bool,...,sn:bool), reward:float)
    # Using the SensorModel and MotorModel to give names to states and actions
    # ('state', 'action', 'future state', reward)
    def calc_performance(self, agent, action):
        reward = {}
        # pylint: disable=len-as-condition
        #if not hasattr(agent, 'objectives'):
        #    agent.objectives = self.options.objectives.copy()
        #    self.save_history(agent)

        for rewarded_action, things_and_objectives in self.options.reward.items():
            if action == rewarded_action:
                for rewarded_thing, obj_and_reward in things_and_objectives.items():
                    if rewarded_thing and len(self.list_things_at(agent.location, rewarded_thing)):
                        for obj, rew in obj_and_reward.items():
                            #agent.objectives[obj] += rew
                            reward[obj] = rew
                    elif rewarded_thing is None:
                        for obj, reward in obj_and_reward.items():
                            #agent.objectives[obj] += reward
                            reward[obj] = rew

        #self.check_is_alive(agent)
        #self.save_history(agent)
        self.check_history(agent)
        l.info(agent.__name__, 'status:', agent.objectives)

        return reward

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

        for nsaction in nsactions:
            self.show_message(('---' + agent.__name__ + ' activating ' +
                               nsaction + ' at location ' +
                               str(agent.location) + ' and time ' + str(time) + '---'))

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
