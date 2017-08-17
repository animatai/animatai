# pylint: disable=missing-docstring, global-statement, invalid-name, too-few-public-methods, no-self-use
#
# A random Mother cachelot and calf
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


from agents import Thing
from agents import Obstacle
from agents import Direction
from agents import XYEnvironment

from myutils import Logging


# Setup constants and logging
# ===========================

DEBUG_MODE = True
l = Logging('sea', DEBUG_MODE)


# Classes
# ========

class Squid(Thing):
    pass


class Sea(XYEnvironment):

    def __init__(self, options):
        self.ENV_ENCODING = [('s', Squid), ('X', Obstacle)]
        super().__init__(options)

    def execute_action(self, agent, action, time):
        self.show_message((agent.__name__ + ' doing ' + action + ' at location ' +
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

        agent.bump = False
        if action == 'DiveAndForward':
            down()
            forward()
        elif action == 'UpAndforward':
            up()
            forward()
        elif action == 'Forward':
            forward()
        elif action == 'Eat':
            eat()
        else:
            l.error('execute_action:unknow action', action, 'for agent', agent, 'at time', time)
