# pylint: disable=missing-docstring, global-statement, invalid-name, too-few-public-methods
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


# Imports
# ======

import unittest

from gzutils.gzutils import get_output_dir, Logging
from animatai.agents import Agent, Thing, XYEnvironment
from animatai.history import History


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('test_stats', DEBUG_MODE)

output_dir = get_output_dir('/../output', file=__file__)

class TestStats(unittest.TestCase):
    def setUp(self):
        l.info('Testing stats...')

    def tearDown(self):
        l.info('...done with test_stats.')

    def test_collect_history(self):
        hist1 = History()
        hist2 = History()
        hist3 = History()

        hist1.add_dataset('h1', ['h1 text', 'h1 int'], 'hist1.csv')
        hist2.add_dataset('h2', ['h1 text', 'h1 int'], 'hist1.csv')
        hist3.add_dataset('h3', ['h1 text', 'h1 int'], 'hist1.csv')

        History().add_dataset('recording', ['actions'], 'recording.csv')

        for i in range(0, 3):
            hist1.add_row('h1', ['bla', i])
            hist2.add_row('h2', ['ha', i*10])
            hist3.add_row('h3', ['da', i*100])
            History().add_row('recording', ['action' + str(i)])

        self.assertTrue(History().get('hist1.csv') == (['h1 text', 'h1 int', 'h1 text', 'h1 int', 'h1 text', 'h1 int'],
                                                       [['bla', 0, 'ha', 0, 'da', 0],
                                                        ['bla', 1, 'ha', 10, 'da', 100],
                                                        ['bla', 2, 'ha', 20, 'da', 200]]))

        History().save('hist1.csv', output_dir=output_dir)
        History().save('recording.csv', output_dir=output_dir)

    def test_agent_step(self):
        l.info('test_agent_step')

        def program1(percept):
            self.assertTrue(percept != [])
            return 'do nothing'

        def program2(percept):
            self.assertTrue(percept != [])
            return 'say nothing'

        class Observer:
            def agent_step(self, agent, percept, action, time):
                pass

        e = XYEnvironment()
        a1 = Agent(program1, 'agent1')
        a2 = Agent(program2, 'agent2')
        t = Thing()
        obs = Observer()
        hist = History()

        e.add_observer(obs, a1)
        e.add_observer(obs, a2)
        e.add_observer(hist, a1)
        e.add_observer(hist, a2)

        e.add_thing(a1, (1, 1))
        e.add_thing(a2, (1, 1))
        e.add_thing(t, (1, 1))

        e.step(1)
        e.step(2)

        self.assertTrue(hist.get() == (['agent1', 'agent2'], [['([(<alive:True, direction:right, name:agent1 (Agent)>, 0), (<alive:True, direction:right, name:agent2 (Agent)>, 0), (<noname (1, 1) (Thing)>, 0)], {})', 'do nothing', '1', '([(<alive:True, direction:right, name:agent1 (Agent)>, 0), (<alive:True, direction:right, name:agent2 (Agent)>, 0), (<noname (1, 1) (Thing)>, 0)], {})', 'say nothing', '1'], ['([(<alive:True, direction:right, name:agent1 (Agent)>, 0), (<alive:True, direction:right, name:agent2 (Agent)>, 0), (<noname (1, 1) (Thing)>, 0)], 1)', 'do nothing', '2', '([(<alive:True, direction:right, name:agent1 (Agent)>, 0), (<alive:True, direction:right, name:agent2 (Agent)>, 0), (<noname (1, 1) (Thing)>, 0)], 1)', 'say nothing', '2']]))

        History().save()

    def test_env_step(self):
        l.info('test_env_step')

        def program1(percept):
            self.assertTrue(percept != [])
            return 'do nothing'

        class Observer:
            def env_step(self, env):
                pass


        class T(Thing):
            pass

        e = XYEnvironment()
        e.add_thing(Agent(program1, 'agent1'), (1, 1)) # Need an agent that is alive for stop to run

        obs = Observer()
        hist = History()
        hist.add_env_classes(e, [T])

        e.add_observer(obs, e)
        e.add_observer(hist, e)

        e.add_thing(T(1), (1, 1))
        e.step(1)
        self.assertTrue(hist.get_dataset(e.__name__)[1][1] == 1)

        e.add_thing(T(2), (1, 1))
        e.step(2)
        self.assertTrue(hist.get_dataset(e.__name__)[2][1] == 2)

        e.add_thing(T(3), (1, 1))
        e.step(3)
        self.assertTrue(hist.get_dataset(e.__name__)[3][1] == 3)

        History().save()
