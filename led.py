#!/usr/bin/env python3
# Simple test for NeoPixels on Raspberry Pi
import time
import copy
import board
import neopixel
import rpi_ws281x
import threading
import itertools

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

    def on(self, on=None):
        if not on in (None, self._on):
            self._on = on
            if on:
                self.iter = self.cycle_wheel()
            else:
                self.fill(0x000000)
        return self._on

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

class Strip():
    def __init__(self):
        # Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
        # NeoPixels must be connected to D10, D12, D18 or D21 to work.
        pixel_pin = board.D18

        # The number of NeoPixels
        num_pixels = 149


        # The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
        # For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
        order = neopixel.GRB

        self.pixels = neopixel.NeoPixel(
            pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=order
        )

    def wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b) if self.pixels.byteorder in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


    def rainbow_cycle(self, speed=0.5, scale=0.5, rate=60):
        change = speed * 255 / rate
        for t in range(int(255)):
            for i in range(self.pixels.n):
                self.pixels[i] = self.wheel((i / scale + t * change) % 255)
            self.pixels.show()
            time.sleep(1 / rate)

    def fill(self, color):
        self.pixels.fill(color)
        self.pixels.show()

def main():
    s = Strip()
    while True:
        try:
            s.rainbow_cycle()  # rainbow cycle with 1ms delay per step
        except KeyboardInterrupt:
            print('Stopping')

            n_steps = 30
            step = s.pixels.brightness / n_steps
            for i in range(n_steps):
                s.pixels.brightness -= step
                s.pixels.show()
                time.sleep(0.016)
            s.pixels.deinit()
            exit()


if __name__ == "__main__":
    view()

