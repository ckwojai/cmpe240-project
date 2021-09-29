import time
import random
import board
import displayio
import digitalio
import adafruit_rgb_display.st7735 as st7735        # pylint: disable=unused-import
from adafruit_rgb_display.rgb import color565

from PIL import Image, ImageDraw

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


while True:
    # Clear the display
    display.fill(0)
    # Draw a red pixel in the center.
    display.pixel(display.width // 2, display.height // 2, color565(255, 0, 0))
    # Pause 2 seconds.
    time.sleep(5)
