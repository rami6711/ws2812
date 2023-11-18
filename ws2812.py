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
import uarray

#SPI_FCLK = const(2400000)   # 2.4MHz ~ 0.416us, then 3-bits ~ 1.25us
SPI_FCLK = const(3000000)   # 3MHz ~ 0.333us, then 3-bits ~ 1.0us
BIT_HI = const(6)  # 0b110 -> 0b001 - presentation of Logic 1 signal for WS2812
BIT_LO = const(4)  # 0b100 -> 0b011 - presentation of Logic 0 signal for WS2812
SHIFT  = const(3)  # 3-bits are valid
BYTE_PER_CHIP  = const(6)  # 24-bit * SHIFT / 12-bit
WS_G = const(0)  # green @ WS2812
WS_R = const(1)  # red @ WS2812
WS_B = const(2)  # blue @ WS2812

"""
color order: G-R-B
24 bit => 72 sub-bit = 3x2x2x2x3
12 sub-bit * 6 spi-word = 72 sub-bit

 < 0 >< 1 >< 2 >< 3 >< 4 >< 5 >< 6 >< 7 >< 8 >< 9 ><10 ><11 >
 `````XXXXX_____`````XXXXX_____`````XXXXX_____`````XXXXX_____
      bit 0          bit 1          bit 2          bit 3

SPI with 12-bit data + 1.5 bit dummy time (revealed using a logic analyzer)
SPI.MOSI and SPI.CLK is combined by 74LVC1G175 (D-type flip-flop). Output (Q) drives WS2812
"""

class WS2812():
    def __init__(self, spi_numb, leds):
        self.led_ct = leds
        self.led = leds * [[0,0,0]]
        # self.buf = bytearray(leds * BYTE_PER_CHIP)
        self.buf = uarray.array('H',list(leds*BYTE_PER_CHIP*[0]))
        self.spi = SPI(spi_numb, SPI_FCLK, polarity=0, phase=0, firstbit=SPI.MSB, bits=12)
        self.map = None
        self.spi.write(uarray.array('H',[0x0000]))
        
    def _byteToStream(self,data,offset):
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
        self.buf[offset+0]=(val&0xFFF000)>>12
        self.buf[offset+1]=(val&0x000FFF)
    
    def _transformation(self):
        val=0
        for i in range(len(self.buf)):
            val = self.buf[i]
            self.buf[i]=((val&0x00FF)<<8)|((val&0xFF00)>>8)            

    def update(self):
        tmp = 0x00
        chip = self.led[0]
        for indx in range(self.led_ct):
            if self.map is None:
                chip = self.led[indx]
            else:
                chip = self.led[self.map[indx]]
            # print("update: " + str(chip))
            self._byteToStream(chip[1],BYTE_PER_CHIP*indx)    # Green
            self._byteToStream(chip[0],BYTE_PER_CHIP*indx+2)  # Red
            self._byteToStream(chip[2],BYTE_PER_CHIP*indx+4)  # Blue
        # print(self.buf)
        self._transformation()
        self.spi.write(self.buf)

    def set_rgb(self, idx,r,g,b):
        self.led[idx] = [r,g,b]
        # print("LED{0} = {1}".format(idx,self.led[idx]))

    def set_color(self, idx, c):
        self.led[idx] = [(c&0xFF0000)>>16, (c&0x00FF00)>>8, (c&0x0000FF)]
        # print("LED{0} = {1}".format(idx,self.led[idx]))
    
    def get_rgb(self,idx):
        return self.led[idx]

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

mx = WS2812(0, 5*5)

"""
mx.report()
print("test of 0xF0")
mx.byteToStream(0xF0,0)
print("test of 0x82")
mx.byteToStream(0x82,0)

mx.set_rgb(0, 0x0F, 0, 0)
mx.set_rgb(1, 0, 0x0F, 0)
mx.set_rgb(2, 0, 0, 0x0F)
"""
c=0
for idx in range(8):
    mx.set_rgb(idx,0,0,c)
    c<<=1
    c+=1


# mx.mapping([2,1,0])

mx.update()

"""
mx.set_color(3, 0x800000)
mx.set_color(4, 0x008000)
mx.set_color(5, 0x000080)
mx.set_rgb(6, 0x80, 0x80, 0)
mx.set_rgb(7, 0x80, 0, 0x80)
mx.set_rgb(8, 0, 0x80, 0x80)
"""

i=0
while i<50:
    mx.report()
    mx.update()
    i+=1
    c = int(input("in:"))
    mx.shift_left()
    mx.set_color(0, c)

"""
mx.shift_right()
mx.report()
mx.update()
"""

