"""
Test SPI

Checking whether the SPI works as expected.
"""

from machine import SPI
import uarray

SPI_FCLK = const(2400000)

buf = uarray.array('H',[0x7508,])
spi = SPI(0, SPI_FCLK, firstbit=SPI.MSB, bits=12, polarity=0, phase=0)
spi.write(buf)

"""
Check on a logic analyser or oscilloscope whether the sequence 100001110101 comes from the SPI.
"""
