#!/usr/bin/env python3
# Simple test for NeoPixels on Raspberry Pi
import time
import copy
import rpi_ws281x
import threading
import itertools

def test():
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

        self.rate = 1/5
        threading.Thread.__init__(self)

    def run(self):
        while(True):
            self.draw()

    def brightness(self, brightness=None):
        if brightness is not None:
            self._brightness = brightness
            self.strip.setBrightness(self._brightness)
        return self._brightness


    def draw(self):
        try:
            fill_iter = next(self.iter)
            for i, f in zip(range(self.strip.numPixels()), fill_iter):
                if type(f) is not int:
                    f = rpi_ws281x.Color(*f)
                self.strip.setPixelColor(i, f)
            #print("#%x" % f)
            self.strip.show()
        except StopIteration:
            pass

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


    def cycle(self, fill):
        while True:
            yield copy.copy(fill)

    def fill(self, fill):
        try:
            fill_iter = itertools.cycle(fill)
        except TypeError:
            fill_iter = itertools.cycle([fill])

        self.iter = iter([fill_iter])

    def __del__(self):
        self.fill(0x000000)
        self.draw()
        del(self.strip)


if __name__ == "__main__":
    test()

