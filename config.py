# pylint: disable=missing-docstring
#
# Configuration for worlds (environments and agents)
#
# Worlds to be used are configured in this file. Two things are needed:
# 1. import the python file with the world
# 2. update the handler
#
# There are a some examples that shows how this is done.
#

#
# Add the import for the python file for the world here. Place the python code
# in the world folder
#

import worlds.blind_dog
import worlds.random_agents
import worlds.random_mom_and_calf

#
# Add a elif statement for each world like this:
#
#    elif message == 'blind_dog':
#        blind_dog.run(wss_)
#

def handler(wss_, message, param):
    if message == 'random_agents':
        worlds.random_agents.run(wss_, param)

    elif message == 'blind_dog':
        worlds.blind_dog.run(wss_, param)

    elif message == 'random_mom_and_calf':
        worlds.random_mom_and_calf.run(wss_, param)

    #elif message == 'animat':
    #    (outputPath, outputDir) = animats.main.getOutputPath()
    #    animats.main.run(param, outputPath, outputDir, wss_)

    else:
        wss_.send_print_message('unknown message &quot;' + message + '&quot; with param &quot;' + str(param) + '&quot;')
