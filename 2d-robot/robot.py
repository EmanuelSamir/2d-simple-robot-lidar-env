#!/usr/bin/python

import numpy as np
from utils import *
import time
from matplotlib import pyplot as plt

MAX_RANGE = 2.

# class Lidar:
#     def __init__(self, robot_state, obstacles, min_range, max_range):
#         self.min_range = min_range
#         self.max_range = max_range

#     def scanning(self):
#     def obtain_scan(xr, yr, min_range, max_range):       

#plt.ion()

class Robot:
    def __init__(self, x0, y0, dT = 0.01, is_render = True):
        self.xr = x0
        self.yr = y0
        self.size = 0.4
        self.dT = dT
        self.max_range = MAX_RANGE
        self.xls = []
        self.yls = []
        self.is_render = is_render

        self.fig = None
        self.ax = None
        if is_render:
            plt.ion()
            self.fig, self.ax = plt.subplots(figsize=(10,10))
            self.ax.set_xlim((-5, 5))
            self.ax.set_ylim((-5, 5))
            circle = plt.Circle((self.xr, self.yr), self.size, color='r', fill=True)
            self.ax.add_patch(circle)
            plt.pause(0.5)

            

    def step(self, vx, vy):
        self.xr = self.xr + self.dT * vx
        self.yr = self.yr + self.dT * vy
 
    def is_crashed(self, env):
        xcs = env.xcs
        ycs = env.ycs
        rcs = env.rcs

        for xc, yc, rc in zip(xcs, ycs, rcs):
            if ( np.sqrt( (xc - self.xr ) ** 2 + (yc - self.yr) ** 2) ) < rc + self.size:
                print("Crashed")
                return True
        return False


    def scanning(self, env):
        xcs = env.xcs
        ycs = env.ycs
        rcs = env.rcs

        r = MAX_RANGE
        self.xls = []
        self.yls = []
        ths = np.arange(0,360, 4) 
        for th in ths:
            thr = np.deg2rad(th)
            self.xls.append(self.xr + r * np.cos(thr))
            self.yls.append(self.yr + r * np.sin(thr))  
         
        for i, (xl, yl, th) in enumerate(zip(self.xls, self.yls, ths)):
            for xc, yc, rc in zip(xcs, ycs, rcs):   
                is_inter, result = obtain_intersection_points(self.xr, self.yr, xl, yl, xc, yc, rc) 
                if is_inter:
                    cond = validate_point(result[0] - self.xr, result[1] - self.yr, self.xls[i] - self.xr, self.yls[i] - self.yr, th, MAX_RANGE)
                    if cond:
                        self.xls[i] = result[0]
                        self.yls[i] = result[1]


    def render(self, env):
        if self.is_render:
            xcs = env.xcs
            ycs = env.ycs
            rcs = env.rcs
            self.ax.clear()
            self.ax.set_xlim((-5, 5))
            self.ax.set_ylim((-5, 5))
            circle = plt.Circle((self.xr, self.yr), self.size, color='r', fill=True,zorder=10)
            self.ax.add_patch(circle)
            self.ax.scatter( self.xls, self.yls , color = 'r')
            for xc, yc, rc in zip(xcs, ycs, rcs):
                circle = plt.Circle((xc, yc), rc, color='b', fill=False)
                self.ax.add_patch(circle)
            for xl, yl in zip(self.xls, self.yls):
                self.ax.plot([self.xr, xl] ,[self.yr, yl])
            
            plt.pause(0.02) 
            self.fig.canvas.draw()


class Environment:
    def __init__(self, xcs  = [], ycs  = [], rcs  = []):
        # obstacles 3- x, y, radius
        self.xcs = xcs 
        self.ycs = ycs
        self.rcs = rcs

    def get_random_obstacles(self, n = 10, min_x = -4, max_x = 4, min_y = -4, max_y = 4, r = 0.3):
        self.xcs = np.random.uniform(low = min_x, high = max_x, size = n)
        self.ycs = np.random.uniform(low = min_y, high = max_y, size = n)
        self.rcs = np.array( n * [r] )


if __name__ == '__main__':
    robot = Robot(0., 0.)
    env = Environment()

    env.get_random_obstacles()
    N = 100

    vx = 1.2
    vy = 1.4

    print('Start process')
    for i in range(N):
        robot.step(vx, vy)
        robot.is_crashed(env)
        robot.scanning(env)
        robot.render(env)
        time.sleep(robot.dT)
        print('step {}'.format(i))
    time.sleep(2)
    plt.ioff()