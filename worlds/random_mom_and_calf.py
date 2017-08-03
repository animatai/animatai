# pylint: disable=missing-docstring, global-statement, invalid-name, too-few-public-methods, no-self-use
#
# A random Mother cachelot and calf
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

import random

from sea import Sea
from sea import Squid
from agents import Agent
from myutils import Logging
from myutils import DotDict

# Setup logging
# =============

DEBUG_MODE = True
l = Logging('random_mom_and_calf', DEBUG_MODE)

def mom_program(percepts, _):
    ''' Mom that moves by random until squid is found. Move forward when there is
        squid and sing.
    '''
    l.debug('mom_program', percepts)
    action, nsaction = None, None

    for p in percepts:
        if isinstance(p, Squid):
            action = 'Forward'
            nsaction = 'Sing'
            break

    if not action:
        if random.random() < 0.5:
            action = 'DiveAndForward'
        else:
            action = 'UpAndforward'

    return (action, nsaction)


def calf_program(_, nspercepts):
    ''' Calf that will by random until hearing song. Dive when hearing song.
        The world will not permit diving below the bottom surface, so it will
        just move forward. '''

    l.debug('calf_program', nspercepts)
    action, nsaction = None, None

    for p in nspercepts:
        if p.action == 'sing':
            action = 'DiveAndForward'
            break

    if not action:
        if random.random() < 0.5:
            action = 'DiveAndForward'
        else:
            action = 'UpAndforward'

    return (action, nsaction)


# Main
# =====

# left: (-1,0), right: (1,0), up: (0,-1), down: (0,1)
#MOVES = [(0, -1), (0, 1)]

lane = ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n' +
        'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
        'WWWWWssssWWWWWWWWWWWWWWWWWWWWWWWWWWssssWWWWWWWWWWW\n')

# the mother and calf have separate and identical lanes
world = lane + lane + 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

options = DotDict({
    'world': world.split('\n'),
    'objectives': ['energy'],
    'blocks': {
        'w': {'w':1},
        's': {'s':1}
    },
    'rewards':{
        'eat_and_forward': {
            's': {
                'energy': 0.1
            },
            '*': -0.05
        },
        'forward': {
            '*': -0.001
        },
        'dive_and_forward': {
            '*': -0.002
        },
    },
    'agent':{
        'network': {
            'sensors': ['w', 's'],
            'motors': ['eat_and_forward', 'forward', 'dive_and_forward', 'up_and_forward'],
        }
    }
})

mom_start_pos = (0, 1)
calf_start_pos = (0, 4)

CFG = {
    'numTilesPerSquare': (1, 1),
    'drawGrid': True,
    'randomTerrain': 0,
    'terrain': world,
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

# Main
# =====

def run(wss=None, param=None):
    l.debug('Running random_mom_and_calf with param:', str(param))
    param = int(param) if param else 10

    options.wss = wss
    options.wss_cfg = CFG
    sea = Sea(options)

    mom = Agent(mom_program, 'mom')
    calf = Agent(calf_program, 'calf')

    sea.add_thing(mom, mom_start_pos)
    sea.add_thing(calf, calf_start_pos)

    l.debug('zzz', sea.is_done())
    sea.run(param)

if __name__ == "__main__":
    run()
