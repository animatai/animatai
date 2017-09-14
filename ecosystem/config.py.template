# pylint: disable=missing-docstring, wrong-import-position
#
# Configuration for worlds (environments and agents)
#
# Worlds to be used are configured in this file. Two things are needed:
# 1. import the python file with the world
# 2. update the handler
#
# There are a some examples that shows how this is done.
#

# Change to the IP address of the server when using a public server
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 5678

#
# Import the exmaples, these are found here: https://github.com/animatai/examples
#

import blind_dog
import random_agents
import random_mom_and_calf

#
# Add a elif statement for each world like this:
#
#    elif message == 'blind_dog':
#        blind_dog.run(wss_)
#

def handler(wss_, world, steps, seed):
    if world == 'random_agents':
        random_agents.run(wss_, steps)

    elif world == 'blind_dog':
        blind_dog.run(wss_, steps)

    elif world == 'random_mom_and_calf':
        random_mom_and_calf.run(wss_, steps, seed)

    #elif message == 'animat':
    #    (outputPath, outputDir) = animats.main.getOutputPath()
    #    animats.main.run(param, outputPath, outputDir, wss_)

    else:
        wss_.send_print_message(('unknown world &quot;' + world +
                                 '&quot; with param &quot;' + str(steps) + '&quot;'))
