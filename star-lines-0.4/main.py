#!/usr/bin/python

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

import skywriter
import sys
import os
import pygame as pg
import numpy as np
from numpy.random import rand, randint
from time import time

from primitives import DrawPixels, DrawPixelQuads
skyx = 0
skyy = 0
skyz = 0

@skywriter.move()
def move(xa,ya,za):
  #print(x,y,z)
  global skyx,skyy,skyz
  skyx =  10 - xa * 20
  skyy =  10 - ya * 20
  skyz = za * 255

class Starfield (object):
    """
    Sets values for arrays of star information based on given
    constraints.
    """

    def __init__(self, width, height, min_z, max_z, n_stars):
        """ Initialize constraints and arrays. """

        # Set star-field constraints as given through function arguments.
        self.w, self.h, self.d = width, height, max_z - min_z
        self.n_stars = n_stars
        self.min_x, self.max_x = -float(self.w / 2), float(self.w / 2)
        self.min_y, self.max_y = -float(self.h / 2), float(self.h / 2)
        self.min_z, self.max_z = float(min_z), float(max_z)

        # Initialize four velocity/position arrays to correct size,
        # filled with zeros (floating points).
        for ary_name in ('vel_ary', 'x_ary', 'y_ary', 'z_ary'):
            setattr(self, ary_name, np.zeros(n_stars, dtype=float))

        # Make sure all elements of z_ary are beyond sight so that the
        # whole array is initialized to random values in the call to
        # ResetPastStars().
        #self.z_ary += min_z - 1.0
        self.ResetPastStars(True)


    def ResetPastStars(self, reset_all=False):
        """ All stars past beyond sight are reset to random values. """

        if reset_all == True:
            # Initial reset, all star-field arrays will be randomized.
            size = self.z_ary.size
            indices = np.arange(size)
        else:
            # Get array indices of all cases where z_ary < min_z.
            indices = np.nonzero(self.z_ary < self.min_z)
            size = indices[0].size
        # Set x, y, and z arrays as well as star velocities to
        # constrained random values.
        self.vel_ary[indices] = (0.1 + 9.9 * rand(size)) ** -1.5
        if size > 0:
            # Update velocity square-root values if needed.
            self.vel_sqrt_ary = np.sqrt(self.vel_ary)
        self.x_ary[indices] = self.min_x + rand(size) * self.w
        self.y_ary[indices] = self.min_y + rand(size) * self.h
        if reset_all == True:
            # Star z-values are sort of evenly distributed ahead and
            # behind camera.
            self.z_ary[indices] = self.min_z + rand(size) * self.d
        else:
            # Place new stars ahead.
            self.z_ary[indices] = rand(size) * self.max_z

        # Indices of reset stars might be useful in the future,
        # so return here.
        return indices


    def RotateX(self, x_amt):
        """
        Calculate and set roll rotation.

        x_amt is angle in radians to rotate stars.
        """

        # numpy's universal functions are helpful in making these
        # calculations go smoothly.
        tan2_ary = np.arctan2(self.y_ary, self.x_ary)
        dist_ary = np.hypot(self.x_ary, self.y_ary)
        angle_inc = x_amt / 256.0
        self.x_ary = dist_ary * np.cos(tan2_ary + angle_inc)
        self.y_ary = dist_ary * np.sin(tan2_ary + angle_inc)


class Main:
    """ Main program lies here. """

    def __init__(self, width, height, flags, depth, method, n_stars, effect):
        """ Initialize display and prepare for main loop. """

        self.w, self.h = width, height
        self.cx, self.cy = self.w / 2, self.h / 2
        self.bpp = depth
        self.method = method
        self.n_stars = n_stars
        self.show_star_lines = effect
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.display.init()
        self.screen = pg.display.set_mode((self.w, self.h),flags,self.bpp)
        # The next five calls make sure the star-field is facing in the
        # right direction to start with.
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        pg.mouse.set_pos((0, 0))
        pg.event.pump()
        pg.mouse.get_rel()
        # Set the display palette to a basic black-grey-white scheme.
        self.pal = [ (q, q, q) for q in range(256) ]
        self.screen.set_palette(self.pal)

        z = 4.0 * self.h
        self.s = Starfield(self.w, self.w, -z, z, n_stars)
        # Old x/y arrays of values for drawing star-lines.
        # Set to infinite amounts at first to draw stars and not lines
        # until one frame has passed.
        self.old_x = np.zeros(self.n_stars, dtype=float) + np.inf
        self.old_y = np.zeros(self.n_stars, dtype=float) + np.inf
        self.zoom = self.cx * 1.5
        self.cam_speed = 240.0
        self.max_star_len = self.w / 10
        self.mxr = 0
        self.myr = 0
        self.yaw_ang = 0.0

        self.frames = 0


    def Begin(self):
        """ Start timers and begin main function. """

        self.start = time()
        self.ticks = time()
        return self.Run()


    def Run(self):
        """ Main control loop. """
        global skyx,skyy,skyz
        while True:
            skyx =- 0.1 
            skyy =- 0.1
            if(skyx <  0):
              skyx = 0
            if(skyy <  0):
              skyy = 0

            self.cam_speed = 200 + (255 - skyz)
            skyz = 0
            # Start with a blank screen each frame.
            self.screen.fill(0)

            # t is the time taken since the last frame, and won't go
            # above approximately 40 milliseconds.
            t = min(0.04, time() - self.ticks)
            copy_z = np.copy(self.s.z_ary)
            # Change the distance of each star from camera based on
            # speed, time past, and the relative velocity of each star.
            self.s.z_ary -= self.cam_speed * t * self.s.vel_ary
            self.ticks = time()

            # Reset all stars that have "disappeared". If star-lines are
            # being drawn, the old x/y values at these indices are
            # reset, to keep lines from being drawn for one frame
            # (prevents a major slowdown).
            indices = self.s.ResetPastStars()
            if self.show_star_lines:
                self.old_x[indices] = self.old_y[indices] = np.inf

            # Calculate rotated coord arrays based on camera yaw angle.
            cos_ang, sin_ang = np.cos(self.yaw_ang), np.sin(self.yaw_ang)
            rx_ary = self.s.x_ary
            ry_ary = self.s.y_ary * cos_ang + self.s.z_ary * sin_ang
            rz_ary = self.s.z_ary * cos_ang - self.s.y_ary * sin_ang

            # Draw stars that appear ahead of the camera.
            prep = rz_ary > 0.0
            rx, ry, rz = rx_ary[prep], ry_ary[prep], rz_ary[prep]
            # Get x and y screen coordinates.
            x = self.cx + rx / rz * self.zoom
            y = self.cy + ry / rz * self.zoom
            # Get bright amount for visible stars.
            # Multiply by the square-root of the relative star velocity
            # for a nice depth-effect.
            b = (2.0 - rz / self.w) * self.s.vel_sqrt_ary[prep]

            if self.show_star_lines:
                # Find stars that are crossing front to back.
                diff = np.logical_and(self.s.z_ary <= 0.0, copy_z > 0.0)
                ox, oy = self.old_x[prep], self.old_y[prep]
                # Set old screen coords to current coords here.
                self.old_x[prep] = x
                self.old_y[prep] = y
                if np.pi / 2.0 < self.yaw_ang < np.pi * 7.0 / 6.0:
                    # A fix for a weird effect that makes the lines draw
                    # incorrectly if the camera angle is pointed
                    # backward a certain amount.
                    x[diff[prep]] = -x[diff[prep]]
                    y[diff[prep]] = -y[diff[prep]]
                    ox[diff[prep]] = -ox[diff[prep]]
                    oy[diff[prep]] = -oy[diff[prep]]
                # Make sure old x/y screen coords are within screen.
                x_in = np.logical_and(ox > 1, ox < self.w - 1)
                y_in = np.logical_and(oy > 1, oy < self.h - 1)
                inside = np.logical_and(x_in, y_in)
                # Test if x or y coords are different enough to justify
                # drawing a line.
                test = np.logical_or(abs(x - ox) > 2.0, abs(y - oy) > 2.0)
                a = np.nonzero(np.logical_and(inside, test))
                # Get the line pixels and add them to the arrays of star
                # pixels to draw.
                lines = self.ExtendLines(x[a], y[a], ox[a], oy[a], b[a])
                ax = np.concatenate((x[inside], lines[0]))
                ay = np.concatenate((y[inside], lines[1]))
                ab = np.concatenate((b[inside], lines[2]))
            else:
                ax = x
                ay = y
                ab = b

            x_in = np.logical_and(ax > 1, ax < self.w - 2)
            y_in = np.logical_and(ay > 1, ay < self.h - 2)
            draw = np.nonzero(np.logical_and(x_in, y_in))

            # Call appropriate draw method on screen with given arrays.
            self.method(self.screen, ax[draw], ay[draw], ab[draw])
            pg.display.update()
            self.frames += 1

            #self.mxr, self.myr = pg.mouse.get_rel()
            self.mxr, self.myr = skyx , skyy 
            if self.show_star_lines and self.mxr != 0 or self.myr != 0:
                # If rotating camera, stop drawing lines for a frame.
                self.old_x[...] = self.old_y[...] = np.inf
            if self.mxr != 0:
                self.s.RotateX(-self.mxr)
            self.yaw_ang -= self.myr * 0.01
            # Keep yaw angle between 0 and 2 * pi radians
            self.yaw_ang %= 2.0 * np.pi

            # Left and right mouse buttons speed up and slow down camera
            # speed
            self.mb = pg.mouse.get_pressed()
            if self.mb[0]:
                # Cap to max and min speeds, and accelerate according to
                # time past.
                self.cam_speed = min(32768.0, self.cam_speed * (1.0 + t))
            if self.mb[2]:
                self.cam_speed = max(1.0, self.cam_speed / (1.0 + t))
            
            # Event handling loop.
            for evt in pg.event.get():
                if evt.type == pg.QUIT:
                    return self.GetAverageFPS()
                elif evt.type == pg.KEYDOWN:
                    if evt.key in (pg.K_ESCAPE, pg.K_RETURN):
                        return self.GetAverageFPS()
                    elif evt.key == pg.K_SPACE:
                        self.show_star_lines = not self.show_star_lines
                        if not self.show_star_lines:
                            self.old_x[...] = self.old_y[...] = np.inf
                elif evt.type == pg.MOUSEBUTTONDOWN:
                    exit()
                    if evt.button == 2:
                        print self.yaw_ang


    def ExtendLines(self, x, y, ox, oy, b):
        """
        Calculate and return pixels of extended lines based on given
        arrays.

        x, y: New arrays of screen x/y coordinates.
        ox, oy: Old arrays. Lines will be attempted from x/y to ox/oy.
        b: Brightness level of each coord.
        """

        # Get absolute difference between old and new arrays.
        abs_dx = abs(ox - x).astype(int) + 1
        abs_dy = abs(oy - y).astype(int) + 1
        # Get maximum of previous two arrays at each element.
        abs_max_d = np.maximum(abs_dx, abs_dy)
        # Cap maximums to a safe value, to conserve computer time and
        # memory, and not be overly sluggish; this limits the length of
        # each star line, though.
        sizes = np.minimum(self.max_star_len, abs_max_d)
        # Initialize return arrays to correct size totals.
        ret_x, ret_y, ret_b = (np.zeros(np.sum(sizes)) for q in range(3))

        # Compute interpolated x- and y-coords and store line
        # information in return arrays.
        # Brightness level of each line is uniform.
        i = 0
        for q in range(sizes.size):
            cap = sizes[q]
            s = slice(i, i + cap)
            ret_x[s] = np.linspace(x[q], ox[q], abs_max_d[q], True)[: cap]
            ret_y[s] = np.linspace(y[q], oy[q], abs_max_d[q], True)[: cap]
            ret_b[s] = np.zeros(cap) + b[q]
            i += cap

        return ret_x, ret_y, ret_b


    def GetAverageFPS(self):
        """ Return average FPS based on start timer and frames counted. """

        elapsed = time() - self.start
        if elapsed > 0.0:
            return self.frames / elapsed
        else:
            return 0.0


if __name__ == '__main__':
    if 'settings.cfg' in os.listdir('.'):
        # Config file found, read options.
        from ConfigParser import RawConfigParser

        cfg_parser = RawConfigParser()
        cfg_parser.read('settings.cfg')

        w = cfg_parser.getint('Display', 'width')
        h = cfg_parser.getint('Display', 'height')

        flags = cfg_parser.get('Display', 'flags').lower()
        if flags == 'none':
            f = 0
        else:
            try:
                f = eval(flags)
            except NameError:
                flag_list = flags.upper().split(',')
                f = 0
                for flag in flag_list:
                    f |= eval('.'.join(('pg', flag)))

        method = cfg_parser.get('Display', 'method').lower()
        if method == 'fast':
            m = DrawPixels
        else:
            m = DrawPixelQuads

        stars = cfg_parser.getint('Display', 'stars')

        e = cfg_parser.getboolean('Display', 'lines')
    else:
        # Set options to reasonable values.
        w, h = 640, 480
        f = 0
        m = DrawPixelQuads
        stars = 2048
        e = False

    # Instantiate main program with options.
    program = Main(w, h, f, 8, m, stars, e)

    # Begin the main loop.
    fps = program.Begin()

    # Print out an average frames-per-second for the run.
    print "Average FPS: %.2f" % fps
