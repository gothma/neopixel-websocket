#!/usr/bin/env python3
# Simple test for NeoPixels on Raspberry Pi
import time
import copy
import board
import neopixel
import rpi_ws281x
import threading
import itertools
import math

def view():
    n_led = 148
    v = View(n_led, 18)
    v.iter = v.cycle_wheel()
    v.start()
    v.join()

class View(threading.Thread):
    def __init__(self, n_pixel, pin):
        self.strip = rpi_ws281x.PixelStrip(
              num=n_pixel,
              pin=pin,
              strip_type=rpi_ws281x.WS2811_STRIP_RGB)
        self.strip.begin()

        self.fill(0x000000)
        self._on = False
        self._brightness = 255
        self._hue = 0
        self._saturation = 0
        self.fill_iter = iter([])
        self.brightness_iter = iter([self._brightness])

        self.rate = 1/60
        threading.Thread.__init__(self)

    def run(self):
        while(True):
            self.draw()

    def linspace(a, b, n):
        n = int(n)
        if n < 2:
            return iter([b])
        d = (b - a) / (n - 1)
        return (int(d * i + a) for i in range(n))

    def brightness(self, brightness=None, anim_duration=0.2):
        if brightness is not None:
            self.brightness_iter = View.linspace(self._brightness, brightness, anim_duration / self.rate)
            self._brightness = brightness
        return self._brightness

    def hue(self, hue=None):
        if hue is not None:
            self._hue = hue
        return self._hue

    def saturation(self, saturation=None):
        if saturation is not None:
            self._saturation = saturation / 100
            self.color(self._hue, self._saturation)
        return self._saturation

    def color(self, hue, saturation):
        print(hue, saturation)
        def f(n):
            k = (n + hue / 60) % 6
            return 1 - saturation * max(0, min(k, 4 - k, 1))
        r = int(0xff0000 * f(5))
        g = int(0x00ff00 * f(3))
        b = int(0x0000ff * f(1))
        print("%x, %x, %x" % (r,g,b))
        self.fill(r+g+b)

    def on(self, on=None, anim_duration=0.2):
        if not on in (None, self._on):
            steps = anim_duration / self.rate
            self._on = on
            if on:
                self.brightness_iter = View.linspace(0, self._brightness, steps)
                self.iter = self.cycle_wheel()
            else:
                self.brightness_iter = View.linspace(self._brightness, 0, steps)
        return self._on

    def draw(self):
        draw = False
        try:
            fill_iter = next(self.iter)
            for i, f in zip(range(self.strip.numPixels()), fill_iter):
                if type(f) is not int:
                    f = rpi_ws281x.Color(*f)
                self.strip.setPixelColor(i, f)
            #print("#%6x" % f)
            draw = True
        except StopIteration:
            pass

        try:
            brightness = next(self.brightness_iter)
            self.strip.setBrightness(brightness)
            draw = True
            #print(brightness)
        except StopIteration:
            pass

        if draw:
            self.strip.show()

        time.sleep(self.rate)

    def cycle_wheel(self):
        max_pos = 3*0xff
        step = max_pos // self.strip.numPixels()

        def wheel(pos):
            parts = [
                lambda x: 0x00ff00 * x + 0x00ff00,
                lambda x: -0x00ffff * x + 0xff0000,
                lambda x: 0x0000ff * x + 0x0000ff,
                    ]
            for i in pos:
                i = int(i)
                part = (i // 0xff) % 3
                yield parts[part](i % 0xff)

        while True:
            #print("Cycle")
            for i in range(0, max_pos, 6):
                yield wheel(range(i, max_pos + i, step))


    def fill(self, fill):
        try:
            fill_iter = itertools.cycle(fill)
        except TypeError:
            fill_iter = itertools.cycle([fill])

        self.iter = iter([fill_iter])

    def __del__(self):
        print('Deleting')
        self.fill(0x000000)
        self.draw()
        del(self.strip)


if __name__ == "__main__":
    view()

