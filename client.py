#!/usr/bin/env python3

import websocket
import json
import led
import threading

websocket.enableTrace(True)

class WebsocketSwitch():
    def __init__(self, url, name):
        self.name = name
        self.ws = websocket.WebSocketApp(url,
                on_message=lambda ws, m: self.on_message(m),
                on_close=lambda ws: self.on_close())
        self.ws.on_open=lambda ws: self.setup()
        self.led = led.Strip()
        self.value = False
        self.ws.run_forever()

    def setup(self):
        self.add(self.name, 'Lightbulb')

    def send(self, topic, payload):
        self.ws.send(json.dumps(dict(topic=topic, payload=payload)))

    def add(self, name, service):
        self.send('add', dict(name=name, service=service))

    def remove(self, name):
        self.send('remove', dict(name=name))

    def on_set(self, payload):
        if 'On' != payload['characteristic']:
            return
        if payload['value']:
            self.thread = threading.Thread(target=lambda: self.led.rainbow_cycle(), args=())
            self.thread.start()
            self.value = True
        else:
            self.led.fill((0,0,0))
            self.value = False

    def on_get(self, payload):
        if 'On' != payload['characteristic']:
            return
        self.send('callback',
                {"name": self.name,
                 "characteristic": "On",
                 "value": self.value})


    def on_message(self, raw_message):
        message = json.loads(raw_message)
        reaction = {
                'get': lambda p: self.on_get(p),
                'set': lambda p: self.on_set(p)}.get(message['topic'], None)

        if reaction is None:
            print('Unknown response', message)
            return

        if message['payload']['name'] == self.name:
            reaction(message['payload'])

    def on_close(self):
        self.led.fill((0,0,0))
        self.remove(self.name)

switch = WebsocketSwitch('ws://localhost:4050', 'LED')
