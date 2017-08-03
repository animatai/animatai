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
from myutils import DotDict

# Setup logging
# =============

DEBUG_MODE = True
l = Logging('sea', DEBUG_MODE)


# Classes
# ========

class Squid(Thing):
    pass

class Sea(XYEnvironment):

    def __init__(self, options):
        options = DotDict(options)
        self.options = options

        width = len(options.world[0])
        height = len(options.world)
        super().__init__(width, height, options.wss, options.wss_cfg)

        # add the squid
        x, y = 0, 0
        for y in range(0, height):
            for x in range(0, width):
                if options.world[y][x] == 's':
                    self.add_thing(Squid(), (x, y))

                # add the wall between the lanes
                if options.world[y][x] == 'x':
                    self.add_thing(Obstacle(), (x, y))


    def execute_action(self, agent, action, time):
        self.show_message(agent.__name__ + ' doing ' + action + ' at location ' + str(agent.location) + ' and time ' + str(time))
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
        else:
            l.error('execute_action:unknow action', action, 'for agent', agent, 'at time', time)
