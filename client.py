#!/usr/bin/env python3

import websocket
import json
import led
import threading

websocket.enableTrace(True)

class WebsocketSwitch():
    def __init__(self, url, name):
        self.name = name
        self.url = url
        self.ws = websocket.WebSocketApp(self.url,
                on_message=lambda ws, m: self.on_message(m),
                on_close=lambda ws: self.on_close())
        self.ws.on_open=lambda ws: self.setup()
        self.led = led.View(148, 18)
        self.led.start()

        self.ws.run_forever()

    def setup(self):
        self.add(self.name, 'Lightbulb', Brightness={"minValue": 0, "maxValue": 255, "minStep": 1}, Hue="default", Saturation="default")

    def send(self, topic, payload):
        self.ws.send(json.dumps(dict(topic=topic, payload=payload)))

    def add(self, name, service, **characteristics):
        characteristics['name'] = name
        characteristics['service'] = service
        self.send('add', characteristics)

    def remove(self, name):
        self.send('remove', dict(name=name))

    def on_set(self, payload):
        print('Set %s to %s' % (payload['characteristic'], payload['value']))
        if 'On' == payload['characteristic']:
            self.led.on(payload['value'])

        if 'Brightness' == payload['characteristic']:
            self.led.brightness(payload['value'])

        if 'Hue' == payload['characteristic']:
            self.led.hue(payload['value'])

        if 'Saturation' == payload['characteristic']:
            self.led.saturation(payload['value'])


    def on_get(self, payload):
        if 'On' == payload['characteristic']:
            self.send('callback',
                {"name": self.name,
                 "characteristic": "On",
                 "value": self.led.on()})

        if 'Brightness' == payload['characteristic']:
            self.send('callback',
                {"name": self.name,
                 "characteristic": "Brightness",
                 "value": self.led.brightness()})

        if 'Hue' == payload['characteristic']:
            self.send('callback',
                {"name": self.name,
                 "characteristic": "Hue",
                 "value": self.led.hue()})

        if 'Saturation' == payload['characteristic']:
            self.send('callback',
                {"name": self.name,
                 "characteristic": "Saturation",
                 "value": self.led.saturation()})


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

        self.ws = websocket.create_connection(self.url)
        self.remove(self.name)
        self.ws.close()

switch = WebsocketSwitch('ws://localhost:4050', 'LED')
