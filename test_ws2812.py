"""
Test application
"""

import ws2812
from machine import Pin

# 5x5 WS2812B chips @ SPI0
mx = ws2812.WS2812(0, 5*5)
mx.mapping([0,1,2,3,4,
            9,8,7,6,5])

# Dummy function of MISO pin
miso_gpio = Pin(12,Pin.OUT)
miso_gpio.off()

mx.set_color(1, 0x800000)       # red
mx.set_color(2, 0x008000)       # green
mx.set_color(3, 0x000080)       # blue
mx.set_rgb(4, 0x80, 0x80, 0)    # yellow
mx.set_rgb(5, 0x80, 0, 0x80)    # cyan
mx.set_rgb(6, 0, 0x80, 0x80)    # magenta

# mx.mapping([2,1,0])

mx.update()

cmd="h"
color = 0x00
while 1:
    if cmd == "exit":
        break
    elif cmd == "p":
        mx.report()
    elif cmd == "h":
        print("exit = program termination, p = print report, h = this help, c = turn off all")
        print("r = shift right, l = shift left, f = fill with last color")
        print("0x123456 = set RGB color (use any number)")
    elif cmd == "c":
        mx.fill(0x000000)
    elif cmd == "r":
        mx.shift_right()
    elif cmd == "l":
        mx.shift_left()
    elif cmd == "f":
        mx.fill(color)
    else:
        color = int(cmd)
        mx.set_color(0, color)
    mx.update()
    cmd = input("in:")

