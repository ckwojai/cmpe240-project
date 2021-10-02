import time
import random
import board
import displayio
import digitalio
import adafruit_rgb_display.st7735 as st7735        # pylint: disable=unused-import
from adafruit_rgb_display.rgb import color565


def draw_line(display, p0, p1, color):
    x0, y0 = p0
    x1, y1 = p1
    slope = abs(y1 - y0) > abs(x1 - x0)
    if (slope):
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if (x0 > x1):
        x0, x1 = x1, x0
        y0, y1 = y1, y0

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

def draw_square(display, p0, p1, p2, p3, color):
    draw_line(display, p0, p1, color)
    draw_line(display, p1, p2, color)
    draw_line(display, p2, p3, color)
    draw_line(display, p3, p0, color)


def transform_square(p1, p2, p3, p4, scale):
    def translate_pt_on_line(pa, pb, scale):
        x1,y1 = pa
        x2,y2 = pb
        mx = x2-x1
        my = y2-y1
        n_x1 = x1 + scale*mx
        n_y1 = y1 + scale*my
        return (n_x1, n_y1)

    n_p1 = translate_pt_on_line(p1, p2, scale)
    n_p2 = translate_pt_on_line(p2, p3, scale)
    n_p3 = translate_pt_on_line(p3, p4, scale)
    n_p4 = translate_pt_on_line(p4, p1, scale)
    return n_p1, n_p2, n_p3, n_p4



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
# drawLine(display, (0, 40), (40, 40), color565(255, 0, 0))
# drawLine(display, (0, 0), (display.width, display.height), color565(255, 0, 0))
drawLine(display, (30, 0), (30, 90), color565(255, 0, 0))
