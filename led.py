#!/usr/bin/env python3
# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel

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
    main()

