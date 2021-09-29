import time
import random
import board
import displayio
import digitalio
import adafruit_rgb_display.st7735 as st7735        # pylint: disable=unused-import
from adafruit_rgb_display.rgb import color565

def drawLine(display, x0, y0, x1, y1, color):
    slope = abs(y1 - y0) > abs(x1 - x0)
    if (slope):
        swap(x0, y0)
        swap(x1, y1)

    if (x0 > x1):
        swap(x0, x1)
        swap(y0, y1)

    dx = x1 - x0
    dy = abs(y1 - y0)

    err = dx / 2

    ystep = 0

    if (y0 < y1):
        ystep = 1
    else:
        ystep = -1

    for x0 in range(x0, x1):
        if (slope):
            display.pixel(y0, x0, color)
        else:
            display.pixel(x0, y0, color)

        err -= dy;
        if (err < 0):
            y0 = y0 + ystep
            err = err + dx

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

BAUDRATE = 24000000

spi = board.SPI()

display = st7735.ST7735R(spi, rotation=90, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE)                           # 1.8" ST7735R

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if display.rotation % 180 == 90:
    height = display.width   # we swap height/width to rotate it to landscape!
    width = display.height
else:
    width = display.width   # we swap height/width to rotate it to landscape!
    height = display.height


# Clear the display
display.fill(0)
# Draw a red pixel in the center.
print(display.width, display.height)
drawLine(display, 0, 0, display.widht, display.height, color565(255, 0, 0))
