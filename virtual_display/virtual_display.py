import time
import board
import digitalio
import adafruit_rgb_display.st7735 as st7735
from adafruit_rgb_display.rgb import color565


def draw_line(display, p0, p1, color):
    x0, y0 = p0
    x1, y1 = p1
    x0 = int(x0)
    y0 = int(y0)
    x1 = int(x1)
    y1 = int(y1)
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

def virtual_to_physical_coordinate(pv, display_dimension):
    (width, height) = display_dimension
    (xv, yv) = pv
    m = width / 2
    n = height / 2
    if xv > m or xv < -m:
        raise ValueError("input virtual coordinate x out of bound of physical display")
    if yv > n or yv < -n:
        raise ValueError("input virtual coordinate y out of bound of physical display")
    # Convertion
    xp = xv + m
    yp = yv + n
    return (xp, yp)

def fill_square_around_pv(display, pv, display_dimension, square_length, color):
    (width, height) = display_dimension
    (xv, yv) = pv
    m = width / 2
    n = height / 2
    if xv-square_length < -m or xv+square_length > m:
        raise ValueError("input virtual coordinate x causes square to go out of bound in physical display")
    if yv-square_lenght < -n or yv+square_length > n:
        raise ValueError("input virtual coordinate y causes square to go out of bound in physical display")

    (xp, yp) = virtual_to_physical_coordinate(pv, display_dimension)
    ltp = ((xp - square_len), (yp - square_len))
    display.fill(ltp[0], ltp[1], square_length, square_length, color)


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


# Initial square of length 100 pixels in the middle of the board
p1 = (114, 130)
p2 = (14, 130)
p3 = (14, 30)
p4 = (114, 30)

square_list = []
scale = 0.8
for i in range(20): # Transform 19 times (level 19)
    if i==0:
        nps = [p1, p2, p3, p4]
    square_list.append(nps)
    np1, np2, np3, np4 = nps
    nps = transform_square(np1, np2, np3, np4, scale)

# Clear the display
display.fill(0)
# Draw the square according to the 4 vertices in list, one by one
for pts in square_list:
    p1, p2, p3, p4 = pts
    draw_square(display, p1, p2, p3, p4, color565(250, 0, 0))
# Remove these squares (draw black) in reverse order
for pts in reversed(square_list):
    p1, p2, p3, p4 = pts
    draw_square(display, p1, p2, p3, p4, color565(0, 0, 0))
