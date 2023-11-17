# ws2812
ws2812 driver for Teensy 4.x board

Initial version.
Driver uses SPI to do "hi-speed" data transfer. But it needs a D-type flip-flop. 
SPI.MOSI and SPI.CLK is connected to 74LVC1G175 (D-type flip-flop). Output (Q) drives WS2812.
