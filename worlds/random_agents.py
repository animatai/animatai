# pylint: disable=missing-docstring, global-statement, eval-used, invalid-name, len-as-condition, no-self-use, too-few-public-methods
#
# Example of how wsserver can be used
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

import random

# Example of how the Field JS class can be used
# ---------------------------------------------

# left: (-1,0), right: (1,0), up: (0,-1), down: (0,1)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

TERRAIN = ('GGGGGGGGGG\nDDDDDDDDDD\nWWWWWWWWWW\nGGGGGGGGGG\nGGGGGGGGGG\n'
           'GGGGGGGGGG\nGGGGGGGGGG\nGGGGGGGGGG\nGGGGGGGGGG\nGGGGGGGGGG')
TERRAIN_SIZE = (10, 10)

CFG = {
    'numTilesPerSquare': (1, 1),
    'drawGrid': True,
    'randomTerrain': 0,
    'terrain': TERRAIN,
    'agents': {
        'A': {
            'name': 'A',
            'pos': (0, 0),
            'hidden': False
        },
        'B': {
            'name': 'B',
            'pos': (1, 0),
            'hidden': False
            }
        }
    }

def update_agent_pos(cfg, agent, pos):
    cfg['agents'][agent]['pos'] = pos

def get_agent_pos(cfg, agent):
    return cfg['agents'][agent]['pos']

def add_pos(pos1, pos2):
    return (pos1[0]+ pos2[0], pos1[1] + pos2[1])

def check_pos(pos):
    return pos[0] >= 0 and pos[0] < TERRAIN_SIZE[0] and pos[1] >= 0 and pos[1] < TERRAIN_SIZE[1]

def random_move(from_pos):
    move = random.choice(MOVES)
    new_pos = add_pos(from_pos, move)

    # Make sure we are within the field
    if not check_pos(new_pos):
        new_pos = random_move(from_pos)

    return new_pos

def run(wss_, param):
    wss_.send_init(CFG)
    for _ in range(0, int(param)):
        for agent in CFG['agents']:
            update_agent_pos(CFG, agent, random_move(get_agent_pos(CFG, agent)))
            wss_.send_update_agent(agent, CFG['agents'][agent])
