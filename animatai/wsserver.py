#!./venv3/bin/python
# pylint: disable=missing-docstring, global-statement, eval-used, invalid-name, len-as-condition, no-self-use, too-few-public-methods
#
# This web sockets server makes it possible to view environments and agents
# from a we browser.
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

import json
import signal
import asyncio
import websockets

import config

from gzutils.gzutils import Logging
from gzutils.gzutils import writef


# Constants and functions
# =======================

# number of second between packges sent to the client
SEND_RATE = 1/100000

DEBUG_MODE = True
l = Logging('wsserver', DEBUG_MODE)


# Websockets server class
# ========================

class WsServer:

    def __init__(self, message_handler):
        self.connected = False
        self.queue = []
        self.message_handler = message_handler

    # install a SIGALRM handler and  emit SIGALRM every 1 sec
    # signum, frame
    def sig_handler(self, _, _2):
        writef('.')
        if not self.connected:
            signal.setitimer(signal.ITIMER_REAL, 1)
        else:
            writef("Connected!\n")

    async def consumer_handler(self, websocket):
        while True:
            message = await websocket.recv()
            message = json.loads(message)

            if len(message) == 3:
                (world, steps, seed) = message
                self.message_handler(self, world, steps, seed)

            if len(message) == 2:
                (world, steps) = message
                self.message_handler(self, world, steps, None)

            await asyncio.sleep(SEND_RATE)

    async def producer_handler(self, websocket):
        while True:
            self.connected = True
            await asyncio.sleep(SEND_RATE)
            if len(self.queue) > 0:
                await websocket.send(self.queue.pop(0))

    # path
    async def handler(self, websocket, _):
        consumer_task = asyncio.ensure_future(self.consumer_handler(websocket))
        producer_task = asyncio.ensure_future(self.producer_handler(websocket))

        # done
        _, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

    def start_wss_server(self):

        # start printing dots while waiting for the client to connect
        signal.signal(signal.SIGALRM, self.sig_handler)
        signal.setitimer(signal.ITIMER_REAL, 1)
        writef('Waiting for client to connect')

        # start the websockets server
        start_server = websockets.serve(self.handler, config.SERVER_ADDRESS, config.SERVER_PORT)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def send(self, msg):
        self.queue.append(msg)

    def send_init(self, cfg):
        self.send('w = new World()')
        self.send('w.initTerrain(' + json.dumps(cfg) + ')')
        self.send('w.start()')

    def send_print_message(self, msg):
        self.send('w.printMessage("' + msg + '")')

    def send_print_escaped_text(self, element, msg):
        self.send('w.printEscapedText("' + element + '","' + msg + '")')

    def send_update_agent(self, agent, state):
        self.send('w.updateAgent("' + agent + '",' + json.dumps(state) + ')')

    def send_update_terrain(self, terrain):
        self.send('w.updateTerrain(' + json.dumps(terrain) + ')')


# Main
# ====

# execute only if run as a script
if __name__ == "__main__":
    wss = WsServer(config.handler)
    wss.start_wss_server()
