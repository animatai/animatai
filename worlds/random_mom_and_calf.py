# pylint: disable=missing-docstring, global-statement, invalid-name, too-few-public-methods, no-self-use
#
# A random Mother cachelot and calf
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

import random

from agents import Agent
from myutils import DotDict
from myutils import Logging

from .sea import Sea
from .sea import Sing
from .sea import Squid

# Setup logging
# =============

DEBUG_MODE = True
l = Logging('random_mom_and_calf', DEBUG_MODE)

# Mom that moves by random until squid is found. Move forward when there is
# squid and sing.
def mom_program(active_sensors, _):

    action, nsaction = None, None

    if 's' in active_sensors:
        l.info('--- MOM FOUND SQUID, EATING AND SINGING! ---')
        action = 'eat_and_forward'
        nsaction = 'sing'

    if not action:
        if random.random() < 0.5:
            action = 'dive_and_forward'
        else:
            action = 'up_and_forward'

    return (action, nsaction)


# Calf that will by random until hearing song. Dive when hearing song.
# The world will not permit diving below the bottom surface, so it will
# just move forward.
def calf_program(active_sensors, active_ns_sensors):

    action, nsaction = None, None

    if 'S' in active_ns_sensors:
        l.info('--- CALF HEARD SONG, DIVING! ---')
        action = 'dive_and_forward'

    if 's' in active_sensors:
        l.info('--- CALF FOUND SQUID, EATING! ---')
        action = 'eat_and_forward'

    if not action:
        if random.random() < 0.5:
            action = 'dive_and_forward'
        else:
            action = 'up_and_forward'

    return (action, nsaction)


# Main
# =====

# left: (-1,0), right: (1,0), up: (0,-1), down: (0,1)
#MOVES = [(0, -1), (0, 1)]

terrain = ('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')

# the mother and calf have separate and identical lanes
things = ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n' +
          '                                                  \n' +
          '     ss                            ss             \n' +
          'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n' +
          '                                                  \n' +
          '     ss                            ss             \n' +
          'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')

# the mother and calf have separate and identical lanes
exogenous_things = ('                                                  \n' +
                    '                                                  \n' +
                    '     ss                            ss             \n' +
                    '                                                  \n' +
                    '                                                  \n' +
                    '     ss                            ss             \n' +
                    '                                                  ')


mom_start_pos = (0, 1)
calf_start_pos = (0, 4)

# `motors` can perform several `actions`. The Sea Environment has four available
# `actions`: `eat`, `down`, `up`, `forward`. Thre is also one `nsaction` which is `sing`
# `sensors` are boolean variables indicating percepts (`Things` of different kinds)
# that are perceived. Active `sensors` are sent as input to the `program`
OPTIONS = DotDict({
    'terrain': terrain.split('\n'),
    'things': things.split('\n'),
    'exogenous_things': exogenous_things.split('\n'),
    'exogenous_things_prob': 0.01,
    'objectives': {'energy': 1},
    'rewards':{
        'eat_and_forward': {
            Squid: {
                'energy': 0.1
            },
            None: {
                'energy': -0.05
            }
        },
        'forward': {
            None: {
                'energy': -0.001
            }
        },
        'dive_and_forward': {
            None: {
                'energy': -0.002
            }
        },
        'up_and_forward': {
            None: {
                'energy': -0.002
            }
        },
        'sing': {
            None: {
                'energy': -0.001
            }
        },
    },
    'agents': {
        'mom': {
            'sensors': [(Squid, 's')],
            'motors': [('eat_and_forward', ['eat', 'forward']),
                       ('forward', ['forward']),
                       ('dive_and_forward', ['down', 'forward']),
                       ('up_and_forward', ['up', 'forward']),
                       ('sing', ['sing'])
                      ],
        },
        'calf': {
            'sensors': [(Squid, 's'), (Sing, 'S')],
            'motors': [('eat_and_forward', ['eat', 'forward']),
                       ('forward', ['forward']),
                       ('dive_and_forward', ['down', 'forward']),
                       ('up_and_forward', ['up', 'forward'])
                      ],
        }
    },
    'wss_cfg': {
        'numTilesPerSquare': (1, 1),
        'drawGrid': True,
        'randomTerrain': 0,
        'agents': {
            'mom': {
                'name': 'M',
                'pos': mom_start_pos,
                'hidden': False
            },
            'calf': {
                'name': 'c',
                'pos': calf_start_pos,
                'hidden': False
            }
        }
    }
})


# Main
# =====

def run(wss=None, steps=None, seed=None):
    l.debug('Running random_mom_and_calf in', str(steps), 'steps with seed', seed)
    steps = int(steps) if steps else 10

    random.seed(seed)

    options = OPTIONS
    options.wss = wss
    sea = Sea(options)

    mom = Agent(mom_program, 'mom')
    calf = Agent(calf_program, 'calf')

    sea.add_thing(mom, mom_start_pos)
    sea.add_thing(calf, calf_start_pos)

    sea.run(steps)

if __name__ == "__main__":
    run()
