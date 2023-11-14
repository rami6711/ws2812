"""
MicroPython WS2812 LED driver
https://github.com/rami6711/ws2812

MIT License

Copyright (c) 2023 Rastislav Michalek

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Work in progress!!!

from machine import SPI

SPI_FCLK = const(2400000)   # 2.4MHz ~ 0.416us, then 3-bits ~ 1.25us
BIT_HI = const(6)  # 0b110 -> 0b001 - presentation of Logic 1 signal for WS2812
BIT_LO = const(4)  # 0b100 -> 0b011 - presentation of Logic 0 signal for WS2812
SHIFT  = const(3)  # 3-bits are valid
BYTE_PER_LED    = const(9)  # 24-bit * SHIFT / 8-bit
BYTE_PER_COLOR  = const(3)  # 9/3

# GRB


class WS2812():
    def __init__(self, spi_numb, leds):
        self.led_ct = leds
        self.led = leds * [[0,0,0]]
        self.buf = bytearray(leds * BYTE_PER_LED)
        self.spi = SPI(spi_numb, SPI_FCLK, firstbit=SPI.MSB, bits=8)
        self.map = None

    def byteToStream(self,data,offset):
        val=0
        # print("byteToStream: "+str(data)+" @ "+str(offset))
        for bit in range(8):
            if (data&0x80)!=0:
                val+=BIT_HI
            else:
                val+=BIT_LO
            data<<=1
            val<<=SHIFT
        val>>=SHIFT
        # print("=> "+str(val))
        self.buf[offset+0]=(val&0xFF0000)>>16
        self.buf[offset+1]=(val&0x00FF00)>>8
        self.buf[offset+2]=(val&0x0000FF)

    def update(self):
        tmp = 0x00
        chip = self.led[0]
        for indx in range(self.led_ct):
            if self.map is None:
                chip = self.led[indx]
            else:
                chip = self.led[self.map[indx]]
            # print("update: " + str(chip))
            self.byteToStream(chip[1],BYTE_PER_LED*indx)    # Green
            self.byteToStream(chip[0],BYTE_PER_LED*indx+3)  # Red
            self.byteToStream(chip[2],BYTE_PER_LED*indx+6)  # Blue
        # print(self.buf)
        self.spi.write(self.buf)

    def set_rgb(self, chip,r,g,b):
        self.led[chip] = [r,g,b]
        # print("LED{0} = {1}".format(chip,self.led[chip]))

    def set_color(self, chip, c):
        self.led[chip] = [(c&0xFF0000)>>16, (c&0x00FF00)>>8, (c&0x0000FF)]
        # print("LED{0} = {1}".format(chip,self.led[chip]))

    def shift_left(self):
        bkp = self.led[self.led_ct-1]
        for x in range(self.led_ct-1, 0, -1):
            self.led[x] = self.led[x-1]
        self.led[0] = bkp

    def shift_right(self):
        bkp = self.led[0]
        for x in range(0, self.led_ct-1, 1):
            self.led[x] = self.led[x+1]
        self.led[self.led_ct-1] = bkp
    
    def fill(self,color):
        for x in range(self.led_ct-1):
            self.set_color(x,color)

    def mapping(self,map):
        if map is None:
            self.map = None
        else:
            self.map = list(range(self.led_ct))
            for x in range(self.led_ct):
                if len(map)>x :
                    self.map[x]=map[x]

    def report(self):
        print(self.led)
        print(self.map)

# Test application

mx = WS2812(0, 5)   #5*5)

"""
mx.report()
print("test of 0xF0")
mx.byteToStream(0xF0,0)
print("test of 0x82")
mx.byteToStream(0x82,0)
"""

mx.set_rgb(0, 0x0F, 0, 0)
mx.set_rgb(1, 0, 0x0F, 0)
mx.set_rgb(2, 0, 0, 0x0F)

mx.mapping([2,1,0])

mx.update()

"""
mx.set_color(3, 0x800000)
mx.set_color(4, 0x008000)
mx.set_color(5, 0x000080)
mx.set_rgb(6, 0x80, 0x80, 0)
mx.set_rgb(7, 0x80, 0, 0x80)
mx.set_rgb(8, 0, 0x80, 0x80)
"--""

i=0
while i<50:
    mx.report()
    mx.update()
    i+=1
    c = int(input("in:"))
    mx.shift_left()
    mx.set_color(0, c)

"--""
mx.shift_right()
mx.report()
mx.update()
"""

"""

update: [112, 112, 255] -> 0x70,0x70,0xFF
update: [128, 128, 255] -> 0x80,0x80,0xFF
update: [15, 0, 0]


0x9b6924	01110000	G=70
0x9b6924	01110000	R=70
0xdb6db6	11111111	B=FF

0xd24924	10000000	G=80
0xd24924	10000000	R=80
0xdb6db6	11111111	B=FF

0x924924	00000000	G=0
0x924db6	00001111	R=F
0x924924	00000000	B=0


"""
