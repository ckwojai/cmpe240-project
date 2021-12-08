import time
from warnings import warn
import board
import digitalio
import adafruit_rgb_display.st7735 as st7735
from adafruit_rgb_display.rgb import color565
from math import sin, cos, radians
import random

import numpy as np
import mahotas

from scipy import interpolate

import math
class vector_helper:
    @staticmethod
    def virtual_to_physical_coordinate(display_dimension, pv):
        max_x, max_y = display_dimension
        (xv, yv) = pv
        m = max_x / 2
        n = max_y / 2
        if xv > m or xv < -m:
            warn(f"input virtual coordinate x ({xv}) out of bound of physical display")
        if yv > n or yv < -n:
            warn(f"input virtual coordinate y ({yv}) out of bound of physical display")
        # Convertion
        xp = xv + m
        yp = -yv + n
        return (xp, yp)

    @staticmethod
    def rotate_around_center(pc, p, degree):
        alpha = radians(degree)
        pcx, pcy = pc
        dx, dy = -pcx, -pcy
        x, y = p
        sa, ca = sin(alpha), cos(alpha)
        xp = ca*x - sa*y + dx*ca-dy*sa-dx
        yp = sa*x + ca*y + dx*sa+dy*ca-dy
        return (xp, yp)

    @staticmethod
    def translate_pt_on_line(pa, pb, scale, translate_pt=0):
        x1,y1 = pa
        x2,y2 = pb
        mx = x2-x1
        my = y2-y1
        if translate_pt == 0:
            n_x = x1 + scale*mx
            n_y = y1 + scale*my
        elif translate_pt == 1:
            n_x = x2 + scale*mx
            n_y = y2 + scale*my
        else:
            raise ValueError("invalid translate_pt, it needs to be either 0 or 1")
        return (n_x, n_y)

    @staticmethod
    def world_to_viewer_transform(pw, pv):
        pvx, pvy, pvz = pv
        pwx, pwy, pwz = pw
        rho = math.sqrt(pvx**2+pvy**2+pvz**2)
        mu = math.sqrt(pvx**2+pvy**2)
        st = pvy/mu
        ct = pvx/mu
        sp = mu/rho
        cp = pvz/rho
        ptx = -st*pwx + ct*pwy
        pty = -cp*ct*pwx - cp*st*pwy + sp*pwz
        ptz = -sp*ct*pwx - sp*ct*pwy - cp*pwz + rho
        return (ptx,pty,ptz)

    @staticmethod
    def perspective_projection(pt, D):
        ptx, pty, ptz = pt
        ppx = D*ptx/ptz
        ppy = D*pty/ptz
        return (ppx,ppy)

    @staticmethod
    def get_shadow_on_xy_plane(pc, pl):
        pcx, pcy, pcz = pc
        plx, ply, plz = pl
        lda = - pcz / (plz - pcz)
        psx = pcx + lda * (plx-pcx)
        psy = pcy + lda * (ply-pcy)
        psz = pcz + lda * (plz-pcz)
        return (psx, psy, psz)

    @staticmethod
    def get_diffusion_intensity(pc, pl, kd):
        kd_r, kd_g, kd_b = kd
        pcx, pcy, pcz = pc
        plx, ply, plz = pl
        rx, ry, rz = (plx-pcx, ply-pcy, plz-pcz)
        ca = rz / math.sqrt(rx**2+ry**2+rz**2)
        i = ca / (rx**2+ry**2+rz**2)
        ir, ig, ib = kd_r*i, kd_g*i, kd_b*i
        return (ir, ig, ib)

    @staticmethod
    def transform_world_to_viewer_to_physical(pw, pv, D, dimension):
        p = vector_helper.world_to_viewer_transform(pw, pv)
        pp = vector_helper.perspective_projection(p, D)
        ppp = vector_helper.virtual_to_physical_coordinate(dimension,pp)
        return ppp

    @staticmethod
    def get_all_points_in_polygon(poly):
        """Return polygon as grid of points inside polygon.

        Input : poly (list of lists)
        Output : output (list of lists)
        """
        xs, ys = zip(*poly)
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)

        newPoly = [(int(x - minx), int(y - miny)) for (x, y) in poly]

        X = maxx - minx + 1
        Y = maxy - miny + 1

        grid = np.zeros((X, Y), dtype=np.int8)
        mahotas.polygon.fill_polygon(newPoly, grid)

        return [(x + minx, y + miny) for (x, y) in zip(*np.nonzero(grid))]

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
        self.rotation = rotation
        self.width = width
        self.height = height

    def draw_pixel(self, p, color=color565(250,0,0)):
        # 0 = landscape, 1 = portraint
        display = self.display
        r = self.rotation

        (x, y) = int(p[0]), int(p[1])
        x_max = self.width - 1
        y_max = self.height - 1
        if r == 1:
            if x > x_max:
                warn(f"pixel coordinate x ({x}) out of bound in physical display")
                return
            if y > y_max:
                warn(f"pixel coordinate y ({y}) out of bound in physical display")
                return
            display.pixel(x, y, color)
        elif r == 0:
            if x > x_max:
                warn(f"pixel coordinate x ({x}) out of bound in physical display")
                return
            if y > y_max:
                warn(f"pixel coordinate y ({y}) out of bound in physical display")
                return
            x, y = y_max-y, x
            display.pixel(x, y, color)

    def draw_line(self, p0, p1, color=color565(250,0,0)):
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


    def fill_square(self, p, square_length, color):
        for i in range(square_length):
            for j in range(square_length):
                tp = (p[0]+i), (p[1]+j)
                self.draw_pixel(tp, color)
    def draw_axis(self):
        xp0 = 0, self.height / 2
        xp1 = self.width-1, self.height/2
        yp0 = self.width/2, 0
        yp1 = self.width/2, self.height-1
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

        (xp, yp) = vector_helper.virtual_to_physical_coordinate((self.width, self,height), pv)
        ltp = ((xp - square_len/2), (yp - square_len/2))
        self.fill_square(ltp, square_len, color)




def branch_tree(root, top, scale, branch_angles, lines):
    translated_top = vector_helper.translate_pt_on_line(root, top, scale, translate_pt=1)
    new_tops = [translated_top]
    for degree in branch_angles:
        rotated_top = vector_helper.rotate_around_center(top, translated_top, degree)
        new_tops.append(rotated_top)

    # ptop = vector_helper.virtual_to_physical_coordinate(dimension, top)
    # pnew_tops = list(map(lambda p: vector_helper.virtual_to_physical_coordinate((display.width, display.height), p), new_tops))
    for new_top in new_tops:
        lines.append([top, new_top])
    return top, new_tops

def draw_tree(display, parent_root, parent_top, pv, D, branch_factor=3, level=7, dimension=(128,160)):
    def convert_2d_to_3d(p2d, const):
        return (p2d[0], const, p2d[1])
    # Draw Tree Trunk
    pparent_root = convert_2d_to_3d(parent_root, 25)
    pparent_top = convert_2d_to_3d(parent_top, 25)
    pparent_root = vector_helper.transform_world_to_viewer_to_physical(pparent_root, pv, D, dimension)
    pparent_top = vector_helper.transform_world_to_viewer_to_physical(pparent_top, pv, D, dimension)
    display.draw_line(pparent_root, pparent_top, color_brown)

    line_levels = []
    new_tops = [(parent_root, [parent_top])]
    for i in range(level):
        lines = []
        next_new_tops = []
        for root, tops in new_tops:
            for top in tops:
                # Randomize lambda
                scale = random.uniform(0.7, 0.9)
                # Randomize branch_angle
                branch_angles = [ random.uniform(-60, 60) for i in range(branch_factor-1)]
                next_new_tops.append(branch_tree(root, top, scale, branch_angles, lines))
        line_levels.append(lines)
        new_tops = next_new_tops


    for i, lines in enumerate(line_levels):
        if i >= 1:
            color = color_green
        else:
            color = color_brown
        for line in lines:
            pa, py = line
            pa = convert_2d_to_3d(pa, 25) 
            py = convert_2d_to_3d(py, 25)
            ppa = vector_helper.transform_world_to_viewer_to_physical(pa, pv, D, dimension)
            ppy = vector_helper.transform_world_to_viewer_to_physical(py, pv, D, dimension)
            display.draw_line(ppa, ppy, color)

def draw_cube(display, cube, color):
    p1, p2, p3, p4, p5, p6, p7 = cube
    display.draw_line(p1, p2, color)
    display.draw_line(p2, p3, color)
    display.draw_line(p3, p4, color)
    display.draw_line(p4, p1, color)
    display.draw_line(p1, p5, color)
    display.draw_line(p2, p6, color)
    display.draw_line(p3, p7, color)
    display.draw_line(p5, p6, color)
    display.draw_line(p6, p7, color)

def draw_top_with_diffusion(display, top_w, top_phy, pl, kd):
    intensity = []
    intensity_map = {}
    color_map = {}
    for p_w in top_w:
        intensity.append(vector_helper.get_diffusion_intensity(p_w, pl, kd)[0])
    intensity_f = interpolate.interp2d([c[0] for c in top_phy], [c[1] for c in top_phy], intensity)
    pts = vector_helper.get_all_points_in_polygon(top_phy)
    for pt in pts:
        intensity_map[pt] = intensity_f(pt[0], pt[1])
    min_intensity = min(intensity_map.values())[0]
    max_intensity = max(intensity_map.values())[0]
    color_f = interpolate.interp1d([min_intensity, max_intensity], [20, 255])
    for pt in pts:
        color_map[pt] = int(color_f(intensity_map[pt])[0])
    for pt, red in color_map.items():
        color = color565(0, 0, red)
        display.draw_pixel(pt, color)

def fill_polygon(display, poly, color):
    pts = vector_helper.get_all_points_in_polygon(poly)
    for pt in pts:
        display.draw_pixel(pt, color)

def draw_shadow(display, shadow, color):
    p1, p2, p3, p4 = shadow
    fill_polygon(display, shadow, color)

def draw_initials(display, color, pv, D, dimension=(128,160)):
    def convert_2d_to_3d(p2d, const):
        return (const, p2d[0], p2d[1])
    lines = []
    # K
    lines.append([(-15, 40), (-15, 56)])
    lines.append([(-15, 48), (-3, 56)])
    lines.append([(-15, 48), (-3, 40)])
    # C
    lines.append([(6, 40), (6, 56)])
    lines.append([(6, 40), (15, 40)])
    lines.append([(6, 56), (15, 56)])
    lines.append([(15, 56), (15, 52)])
    lines.append([(15, 40), (15, 44)])
    for line in lines:
        pa, pb = line
        pa = convert_2d_to_3d(pa, 25) 
        pb = convert_2d_to_3d(pb, 25) 
        ppa = vector_helper.transform_world_to_viewer_to_physical(pa, pv, D, dimension)
        ppb = vector_helper.transform_world_to_viewer_to_physical(pb, pv, D, dimension)
        display.draw_line(ppb, ppa, color)

# Configuration for CS and DC pins (these are PiTFT defaults):
width = 160
height = 128
dimension = (width, height)
display = st7735r_display(width=width, height=height, rotation=0)
dimension = display.width, display.height
display.clear()

color_brown = color565(45, 82, 160)
color_green = color565(0, 200, 0)
color_blue = color565(200, 0, 0)
color_white = color565(255, 255, 255)
color_shadow = color565(105,105,105)

p1 = (25,-25,60)
p2 = (25,25,60)
p3 = (25,25,10)
p4 = (25,-25,10)
p5 = (-25,-25,60)
p6 = (-25,25,60)
p7 = (-25,25,10)
cube_w = [p1, p2, p3, p4, p5, p6, p7]
D = 125 
pv = (80, 100, 100)
pl = (-100, 0, 320)
# pl = (60, -60, 320)
cube_v = [ vector_helper.world_to_viewer_transform(pw, pv) for pw in cube_w ]
cube_p = [ vector_helper.perspective_projection(pv, D) for pv in cube_v ]
cube_phy = [ vector_helper.virtual_to_physical_coordinate(dimension, pp) for pp in cube_p ]

cube_s = [p1, p2, p6, p5]
shadow_w = [ vector_helper.get_shadow_on_xy_plane(pc, pl) for pc in cube_s ]
shadow_v = [ vector_helper.world_to_viewer_transform(pw, pv) for pw in shadow_w ]
shadow_p = [ vector_helper.perspective_projection(pv, D) for pv in shadow_v ]
shadow_phy = [ vector_helper.virtual_to_physical_coordinate(dimension, pp) for pp in shadow_p ]
shadow_phy = [(int(p[0]), int(p[1])) for p in shadow_phy]
top_w = [p1, p2, p6, p5]
top_phy = [cube_phy[0], cube_phy[1], cube_phy[5], cube_phy[4]]
top_phy = [(int(p[0]), int(p[1])) for p in top_phy]
kd = (0.8, 0, 0)

height = 17 
parent_root = (0,10)
parent_top = (parent_root[0], parent_root[1]+height)
draw_shadow(display, shadow_phy, color_shadow)
draw_cube(display, cube_phy, color_blue)
draw_tree(display, parent_root, parent_top, pv, D, level=2, branch_factor=10, dimension=dimension)
draw_top_with_diffusion(display, top_w, top_phy, pl, kd)
draw_initials(display, color_white, pv, D, dimension=dimension)
