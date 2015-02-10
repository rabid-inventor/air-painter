# Copyright (C) 2010  Sean McKean
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import pygame as pg
import numpy as np


def BelowFraction(x):
    "Calculate fractional part of scalar or array of floats."

    return np.modf(x)[0]


def AboveFraction(x):
    "Calculate inverse of fractional part of scalar or array of floats."

    return 1.0 - np.modf(x)[0]


def DrawPixels(dst_sfc, x_ary, y_ary, levels):
    """
    Draws basic pixel information to given pygame surface.

    dst_sfc: Surface to draw onto.
    x_ary, y_ary: Two numpy.ndarrays that give the x and y coordinates
        of each pixel to render. Coords can be floating-points.
    levels: A numpy array of values from 0.0 to 1.0, giving the
        brightness level of each pixel.
    """

    # Get brightness values from levels, between 0 and 255.
    bright_ary = np.maximum(0.0, np.minimum(levels, 1.0)) * 255.0
    bright_ary = bright_ary.astype(np.uint8)
    # Get integer values for coordinates.
    x_int = x_ary.astype(int)
    y_int = y_ary.astype(int)
    # srt_ord set to hold indices of brightness array in sorted order.
    srt_ord = np.argsort(bright_ary)

    # Get 2-dimensional array of surface pixel information.
    dst_ary = pg.surfarray.pixels2d(dst_sfc)
    # Set surface pixels sorted from darkest to brightest values.
    dst_ary[x_int[srt_ord], y_int[srt_ord]] = bright_ary[srt_ord]
    # Delete temporary array to finish changes to surface.
    del dst_ary


def DrawPixelQuads(dst_sfc, x_ary, y_ary, levels):
    """
    Draws anti-aliased pixel quads to given pygame surface.

    dst_sfc: Surface to draw onto.
    x_ary, y_ary: Two numpy.ndarrays that give the x and y coordinates
        of each pixel quad to render. Coords can be floating-points.
    levels: A numpy array of values from 0.0 to 1.0, giving the
        brightness level of each pixel. One value per quad needed.
    """

    bright_ary = np.maximum(0.0, np.minimum(levels, 1.0)) * 255.0
    bright_ary = bright_ary.astype(np.uint8)

    # Hold an x/y coord array for each corner of every pixel quad.
    fx, cx = np.floor(x_ary), np.ceil(x_ary)
    fy, cy = np.floor(y_ary), np.ceil(y_ary)
    # Join x/y arrays, to be rendered in one go.
    x_all = np.concatenate((fx, fx, cx, cx)).astype(int)
    y_all = np.concatenate((fy, cy, fy, cy)).astype(int)
    # Each of the four inner arrays in c_ary holds a corner fraction of
    # each of the pixel quads to draw.
    c_ary = np.array( [
        (AboveFraction(x_ary) + AboveFraction(y_ary)) / 2.0,
        (AboveFraction(x_ary) + BelowFraction(y_ary)) / 2.0,
        (BelowFraction(x_ary) + AboveFraction(y_ary)) / 2.0,
        (BelowFraction(x_ary) + BelowFraction(y_ary)) / 2.0,
        ] )
    # Multiply each fraction by the corresponding brightness level and
    # concatenate values, clipping to 8-bit amounts.
    c_ary = np.concatenate((c_ary * bright_ary).astype(np.uint8))
    srt_ord = np.argsort(c_ary)

    dst_ary = pg.surfarray.pixels2d(dst_sfc)
    dst_ary[x_all[srt_ord], y_all[srt_ord]] = c_ary[srt_ord]
    del dst_ary


def DrawWuLine(dst_sfc, x1, y1, x2, y2, level=1.0):
    """
    Draws an anti-aliased Wu-line to given pygame surface.
    This is the numpy version, which is slower than calling
    pygame.draw.aaline().

    dst_sfc: Surface to draw onto.
    x1, y1: Floating points giving first coordinate.
    x2, y2: Floats giving second coord.
    level: Relative brightness level of line drawn: 0.0 <= level <= 1.0
    """

    bright = int(max(0.0, min(level, 1.0)) * 255.0)
    xd, yd = abs(x2 - x1), abs(y2 - y1)

    dst_ary = pg.surfarray.pixels2d(dst_sfc)

    if xd < 1.0 and yd < 1.0:
        # single anti-aliased pixel
        c_ary = np.array( [
            (AboveFraction(x1) + AboveFraction(y1)) / 2.0,
            (AboveFraction(x1) + BelowFraction(y1)) / 2.0,
            (BelowFraction(x1) + AboveFraction(y1)) / 2.0,
            (BelowFraction(x1) + BelowFraction(y1)) / 2.0,
            ] )
        fx, cx = int(np.floor(x1)), int(np.ceil(x1))
        fy, cy = int(np.floor(y1)), int(np.ceil(y1))
        if fx == cx and fy == cy:
            c_ary = np.repeat(np.max(c_ary), 4)
        elif fx == cx:
            c_ary[[0, 2]] = np.max(c_ary[0], c_ary[2])
            c_ary[[1, 3]] = np.max(c_ary[1], c_ary[3])
        elif fy == cy:
            c_ary[[0, 1]] = np.max(c_ary[0], c_ary[1])
            c_ary[[2, 3]] = np.max(c_ary[2], c_ary[3])
        c_ary = (c_ary * bright).astype(np.uint8)

        dst_ary[(fx, fx, cx, cx), (fy, cy, fy, cy)] = c_ary

    elif xd > yd:
        # x-major line
        xd = np.round(xd) + 1
        # np.linspace calculates endpoints and points in between into a
        # one-dimensional array, depending on arguments given.
        x_ary = np.linspace(x1, x2, xd, True)
        y_ary = np.linspace(y1, y2, xd, True)
        c_ary = BelowFraction(y_ary)
        c_ary = (c_ary * bright).astype(np.uint8)
        x_ary = x_ary.astype(int)
        y_ary = y_ary.astype(int)

        dst_ary[x_ary, y_ary] = bright - c_ary
        dst_ary[x_ary, y_ary + 1] = c_ary

    else:
        # y-major line
        yd = np.round(yd) + 1
        x_ary = np.linspace(x1, x2, yd, True)
        y_ary = np.linspace(y1, y2, yd, True)
        c_ary = BelowFraction(x_ary)
        c_ary = (c_ary * bright).astype(np.uint8)
        x_ary = x_ary.astype(int)
        y_ary = y_ary.astype(int)

        dst_ary[x_ary, y_ary] = bright - c_ary
        dst_ary[x_ary + 1, y_ary] = c_ary

    del dst_ary


class Main:
    """ Main program class and routines for testing above functions. """

    def __init__(self, width, height, depth, scale, show_counts=False):
        self.w, self.h = width, height
        self.fw, self.fh = width * scale, height * scale
        self.scale = scale
        self.bpp = depth
        self.show_counts = show_counts
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.display.init()
        self.screen = pg.display.set_mode((self.fw, self.fh), 0, self.bpp)
        self.pal = [ (q, q, q) for q in range(256) ]
        self.screen.set_palette(self.pal)
        self.scl_sfc = pg.Surface((self.w, self.h)).convert()
        self.scl_sfc.set_palette(self.pal)
        self.px, self.py = self.w / 2, self.h / 2
        self.method = 0
        self.frames = 0


    def Begin(self):
        self.Run()


    def Run(self):
        while True:
            c = 0
            t = time()
            if self.method == 0:
                while time() - t < 0.02:
                    x_ary = randint(0, self.w, 256)
                    y_ary = randint(0, self.h, 256)
                    levels = rand(256)
                    DrawPixels(self.scl_sfc, x_ary, y_ary, levels)
                    c += 256
            elif self.method == 1:
                while time() - t < 0.02:
                    x_ary = rand(256) * (self.w - 1.0)
                    y_ary = rand(256) * (self.h - 1.0)
                    levels = rand(256)
                    DrawPixelQuads(self.scl_sfc, x_ary, y_ary, levels)
                    c += 256
            elif self.method == 2:
                while time() - t < 0.02:
                    x1, y1 = rand() * (self.w - 1), rand() * (self.h - 1)
                    x2, y2 = rand() * (self.w - 1), rand() * (self.h - 1)
                    level = rand()
                    DrawWuLine(self.scl_sfc, x1, y1, x2, y2, level)
                    c += 1
            if self.show_counts:
                print c
            temp_sfc = pg.transform.scale(self.scl_sfc, (self.fw, self.fh))
            self.screen.blit(temp_sfc, (0, 0))
            pg.display.update()
            self.frames += 1
            for evt in pg.event.get():
                if evt.type == pg.QUIT:
                    return
                elif evt.type == pg.KEYDOWN:
                    if evt.key in (pg.K_ESCAPE, pg.K_RETURN):
                        return
                    elif evt.key == pg.K_SPACE:
                        self.method = (self.method + 1) % 3
                        self.scl_sfc.fill(0)


if __name__ == '__main__':
    from numpy.random import rand, randint
    from time import time

    program = Main(320, 240, 8, 2, show_counts=False)
    program.Begin()
