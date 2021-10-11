import time
import board
import digitalio
import adafruit_rgb_display.st7735 as st7735
from adafruit_rgb_display.rgb import color565
from PIL import Image, ImageDraw, ImageFont


class st7735r_display:
    def __init__(self, spi=None, width=160, height=128, rotation=0, cs_pin=None, dc_pin=None, reset_pin=None, baudrate=24000000):
        if spi is None:
            spi = board.SPI()
        if cs_pin is None:
            cs_pin = digitalio.DigitalInOut(board.CE0)
        if dc_pin is None:
            dc_pin = digitalio.DigitalInOut(board.D25)
        if reset_pin is None:
            reset_pin = digitalio.DigitalInOut(board.D24)

        self.display = st7735.ST7735R(spi, rotation=0, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=baudrate) # Rotation doesn't work here
        self.rotation = 0
        self.width = width
        self.height = height

    def draw_pixel(self, p, color=color565(250,0,0)):
        # 0 = landscape, 1 = portraint
        display = self.display
        r = self.rotation

        (x, y) = int(p[0]), int(p[1])
        x_max = display.width - 1
        y_max = display.height - 1
        if r == 1:
            if x > x_max:
                raise ValueError("pixel x coordinate out of bound in physical display")
            if y > y_max:
                raise ValueError("pixel y coordinate out of bound in physical display")
            display.pixel(x, y)
        elif r == 0:
            if x > y_max:
                raise ValueError("pixel x coordinate out of bound in physical display")
            if y > x_max:
                raise ValueError("pixel y coordinate out of bound in physical display")
            x, y = x_max-y, y_max-x
            display.pixel(x, y, color)

    def draw_line(self, p0, p1, color):
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
                self.draw_pixel((y0, x0), color)
            else:
                self.draw_pixel((x0, y0), color)

            err -= dy;
            if (err < 0):
                y0 = y0 + ystep
                err = err + dx


    def draw_square(self, p0, p1, p2, p3, color):
        draw_line(p0, p1, color)
        draw_line(p1, p2, color)
        draw_line(p2, p3, color)
        draw_line(p3, p0, color)

    def clear(self):
        self.display.fill(0)

    def virtual_to_physical_coordinate(self, pv):
        max_x, max_y = self.width, self.height
        (xv, yv) = pv
        m = max_x / 2
        n = max_y / 2
        if xv > m or xv < -m:
            raise ValueError("input virtual coordinate x out of bound of physical display")
        if yv > n or yv < -n:
            raise ValueError("input virtual coordinate y out of bound of physical display")
        # Convertion
        xp = xv + m
        yp = yv + n
        return (xp, yp)

    def fill_square(self, p, square_length, color):
        for i in range(square_length):
            for j in range(square_length):
                tp = (p[0]+i), (p[1]+j)
                self.draw_pixel(tp, color)
    def draw_axis(self):
        xp0 = 0, self.height / 2
        xp1 = self.width, self.height/2
        yp0 = self.width/2, 0
        yp1 = self.width/2, self.height
        color = color565(250,0,0)
        self.draw_line(xp0, xp1, color)
        self.draw_line(yp0, yp1, color)

    def fill_square_around_pv(self, pv, square_len, color=color565(250,0,0)):
        max_x, max_y = self.width, self.height
        (xv, yv) = pv
        m = max_x / 2
        n = max_y / 2
        if xv-square_len < -m or xv+square_len > m:
            raise ValueError("input virtual coordinate x causes square to go out of bound in physical display")
        if yv-square_len < -n or yv+square_len > n:
            raise ValueError("input virtual coordinate y causes square to go out of bound in physical display")

        (xp, yp) = self.virtual_to_physical_coordinate(pv)
        ltp = ((xp - square_len/2), (yp - square_len/2))
        self.fill_square(ltp, square_len, color)


# Configuration for CS and DC pins (these are PiTFT defaults):

display = st7735r_display()
display.clear()
display.draw_axis()
while (True):
    input_str = input("Please enter virtual coordinate separated by a comma: ")
    p = input_str.split(",")
    p = int(p[0]), int(p[1]) 
    display.fill_square_around_pv(p, 5, color565(0,250,0))

# display.draw_pixel((0,0))
# display.draw_pixel((159,0))
# display.draw_pixel((159,127))
# display.draw_pixel((0,127))
# pp = display.virtual_to_physical_coordinate((0,0))
# display.draw_pixel(pp)
# display.fill_square_around_pv((0,0), 6, color565(250,0,0))
# display.draw_axis()
# display.fill_square_around_pv((10,10), 6, color565(250,0,0))
# display.fill_square_around_pv((-40,40), 6, color565(250,0,0))

