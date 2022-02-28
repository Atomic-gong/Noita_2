#cython: language_level=3
from copy import deepcopy
from curses.ascii import ESC
from threading import Thread
from time import sleep
import pygame
from random import randint, random
from enum import Enum, auto
import colorama
from typing import Tuple
print("Imports successful")

pygame.init()
colorama.init()
print("Modules initialised")

class Comp(Enum):
    FALLDOWN = auto()
    FLOATUP = auto()
    STATIC = auto()
    SAND_SPREAD = auto()
    WATER_SPREAD = auto()
    STEAM_SPREAD = auto()
    ACID_SPREAD = auto()
    LAVA_SPREAD = auto()
    FIRE_SPREAD = auto()
    ACID_VAPOUR_SPREAD = auto()
    GLASS_SPREAD = auto()
    MOLTEN_GLASS_SPREAD = auto()
    STONE_SPREAD = auto()

cols = 640
rows = 480
res = (cols, rows)
print(f"Screen res: {res}")

world = [None for _ in range(res[0] * res[1])]

print(f"World size: {len(world)}")

scr = pygame.display.set_mode(res)

brush_size = 20

print(f"Brush size: {brush_size}")

class Element:
    def __init__(self, density: float, colour: Tuple, comps: Tuple[Comp]) -> None:
        self.density = density
        self.comps = comps[:]
        self.colour = colour[:]

class Particle:
    def __init__(self, element: Element, x: int, y: int, temp: int) -> None:
        self.element = element
        self.temp = temp
        self.x = x
        self.y = y
    def update(self, buffer_world, rev_world):
        moved_down = False

        for c in self.element.comps:
            if self.y > rows:
                self.y = rows
            if self.y < 0:
                self.y = 0

            if c == Comp.STATIC:
                continue
            elif c == Comp.FALLDOWN:
                if self.y > 2:
                    #print(rev_world[self.y-1 * cols + self.x])
                    if rev_world[self.y+1 * cols + self.x] != None:
                        #print("a")
                        i = rev_world[self.y+1 * cols + self.x]
                        if i.element.density > self.element.density:
                            print("Density swap (Comp.FALLDOWN)")
                            rev_world[self.y * cols + self.x] = None
                            rev_world[self.y-1 * cols + self.x] = None
                            self.y -= 1
                            i.y += 1
                            buffer_world[self.y-1 * cols + self.x] = self
                            buffer_world[self.y+1 * cols + self.x] = i
                if self.y >= rows - 1: continue
                if buffer_world[(self.y + 1) * cols + self.x] is not None: continue
                buffer_world[self.y * cols + self.x] = None
                self.y += 1
                moved_down = True
                buffer_world[self.y * cols + self.x] = self
            elif c == Comp.FLOATUP:
                if self.y <= rows-3:
                    if rev_world[self.y+1 * cols + self.x] != None:
                        #print("a")
                        i = rev_world[self.y+1 * cols + self.x]
                        if i.element.density > self.element.density:
                            print("Density swap (Comp.FLOATUP)")
                            rev_world[self.y * cols + self.x] = None
                            rev_world[self.y-1 * cols + self.x] = None
                            self.y -= 1
                            i.y += 1
                            buffer_world[self.y-1 * cols + self.x] = self
                            buffer_world[self.y+1 * cols + self.x] = i
                if self.y <= 0: continue
                if buffer_world[(self.y - 1) * cols + self.x] is not None: continue
                buffer_world[self.y * cols + self.x] = None
                self.y -= 1
                buffer_world[self.y * cols + self.x] = self
            elif c == Comp.SAND_SPREAD:
                if do_temp:
                    if not buffer_world[self.y-1 * cols + self.x] == None:
                        if buffer_world[self.y-1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y-1 * cols + self.x].temp += (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                    if not buffer_world[self.y+1 * cols + self.x] == None:
                        if buffer_world[self.y+1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y+1 * cols + self.x].temp += (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                    if self.x < cols:
                        if not buffer_world[self.y * cols + self.x+1] == None:
                            if buffer_world[self.y * cols + self.x+1].temp < self.temp:
                                buffer_world[self.y * cols + self.x+1].temp += (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                    if self.x > 0:
                        if not buffer_world[self.y * cols + self.x-1] == None:
                            if buffer_world[self.y * cols + self.x-1].temp < self.temp:
                                buffer_world[self.y * cols + self.x-1].temp += (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                    if ambient_temp_loss:
                        self.temp -= randint(0,2)
                    if ambient_temp_spread:
                        pass
                    if self.temp > 1700:
                        buffer_world[self.y * cols + self.x] = Particle(molten_glass, self.x, self.y, self.temp)
                if self.x < 1 or self.x > cols - 2 or moved_down or self.y >= rows-1: continue
                if randint(0, 1) == 0:
                    if buffer_world[(self.y+1) * cols + self.x + 1] is None:
                        buffer_world[self.y * cols + self.x] = None
                        self.y += 1
                        self.x += 1
                        buffer_world[self.y * cols + self.x] = self
                elif buffer_world[(self.y+1) * cols + self.x - 1] is None:
                    buffer_world[self.y * cols + self.x] = None
                    self.x -= 1
                    self.y += 1
                    buffer_world[self.y * cols + self.x] = self
            elif c == Comp.WATER_SPREAD:
                if do_temp:
                    if not buffer_world[self.y-1 * cols + self.x] == None:
                        if buffer_world[self.y-1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y-1 * cols + self.x].temp += (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                    if not buffer_world[self.y+1 * cols + self.x] == None:
                        if buffer_world[self.y+1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y+1 * cols + self.x].temp += (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                    if self.x < cols:
                        if not buffer_world[self.y * cols + self.x+1] == None:
                            if buffer_world[self.y * cols + self.x+1].temp < self.temp:
                                buffer_world[self.y * cols + self.x+1].temp += (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                    if self.x > 0:
                        if not buffer_world[self.y * cols + self.x-1] == None:
                            if buffer_world[self.y * cols + self.x-1].temp < self.temp:
                                buffer_world[self.y * cols + self.x-1].temp += (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                    if ambient_temp_loss:
                        self.temp -= randint(0,2)
                    if ambient_temp_spread:
                        pass
                    if self.temp > 99:
                        buffer_world[self.y * cols + self.x] = Particle(steam, self.x, self.y, self.temp)
                if self.x < 1 or self.x > cols - 2 or moved_down: continue
                if randint(0, 1) == 0:
                    if buffer_world[(self.y) * cols + self.x + 1] is None and self.x < cols:
                        buffer_world[self.y * cols + self.x] = None
                        self.x += 1
                        buffer_world[self.y * cols + self.x] = self
                elif buffer_world[(self.y) * cols + self.x - 1] is None and self.x > 0:
                    buffer_world[self.y * cols + self.x] = None
                    self.x -= 1
                    buffer_world[self.y * cols + self.x] = self
            elif c == Comp.STEAM_SPREAD:
                if do_temp:
                    if not buffer_world[self.y-1 * cols + self.x] == None:
                        if buffer_world[self.y-1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y-1 * cols + self.x].temp += (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                    if not buffer_world[self.y+1 * cols + self.x] == None:
                        if buffer_world[self.y+1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y+1 * cols + self.x].temp += (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                    if self.x < cols:
                        if not buffer_world[self.y * cols + self.x+1] == None:
                            if buffer_world[self.y * cols + self.x+1].temp < self.temp:
                                buffer_world[self.y * cols + self.x+1].temp += (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                    if self.x > 0:
                        if not buffer_world[self.y * cols + self.x-1] == None:
                            if buffer_world[self.y * cols + self.x-1].temp < self.temp:
                                buffer_world[self.y * cols + self.x-1].temp += (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                    if ambient_temp_loss:
                        self.temp -= randint(0,2)
                    if ambient_temp_spread:
                        pass
                    if self.temp < 100:
                        buffer_world[self.y * cols + self.x] = Particle(water, self.x, self.y, self.temp)
                if self.x < 1 or self.x > cols - 2: continue
                if randint(0, 1) == 0:
                    if buffer_world[(self.y) * cols + self.x + 1] is None:
                        buffer_world[self.y * cols + self.x] = None
                        self.x += 1
                        buffer_world[self.y * cols + self.x] = self
                elif buffer_world[(self.y) * cols + self.x - 1] is None:
                    buffer_world[self.y * cols + self.x] = None
                    self.x -= 1
                    buffer_world[self.y * cols + self.x] = self
            elif c == Comp.ACID_SPREAD:
                if do_temp:
                    if not buffer_world[self.y-1 * cols + self.x] == None:
                        if buffer_world[self.y-1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y-1 * cols + self.x].temp += (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                    if not buffer_world[self.y+1 * cols + self.x] == None:
                        if buffer_world[self.y+1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y+1 * cols + self.x].temp += (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                    if self.x < cols:
                        if not buffer_world[self.y * cols + self.x+1] == None:
                            if buffer_world[self.y * cols + self.x+1].temp < self.temp:
                                buffer_world[self.y * cols + self.x+1].temp += (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                    if self.x > 0:
                        if not buffer_world[self.y * cols + self.x-1] == None:
                            if buffer_world[self.y * cols + self.x-1].temp < self.temp:
                                buffer_world[self.y * cols + self.x-1].temp += (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                    if ambient_temp_loss:
                        self.temp -= randint(0,2)
                    if ambient_temp_spread:
                        pass
                    if self.temp > 99:
                        buffer_world[self.y * cols + self.x] = Particle(acid_vapour, self.x, self.y, self.temp)
                if self.x < 1 or self.x > cols - 2 or moved_down: continue
                if randint(0, 1) == 0:
                    if buffer_world[(self.y) * cols + self.x + 1] is None:
                        buffer_world[self.y * cols + self.x] = None
                        self.x += 1
                        buffer_world[self.y * cols + self.x] = self
                    elif not buffer_world[(self.y) * cols + self.x + 1].element == acid and not Comp.FLOATUP in buffer_world[(self.y) * cols + self.x + 1].element.comps:
                        buffer_world[self.y * cols + self.x] = None
                        self.x += 1
                        buffer_world[self.y * cols + self.x] = self
                        world[self.y * cols + self.x] = None
                elif buffer_world[(self.y) * cols + self.x - 1] is None:
                    buffer_world[self.y * cols + self.x] = None
                    self.x -= 1
                    buffer_world[self.y * cols + self.x] = self
                elif not buffer_world[(self.y) * cols + self.x - 1].element == acid:
                        buffer_world[self.y * cols + self.x] = None
                        self.x -= 1
                        buffer_world[self.y * cols + self.x] = self
                        world[self.y * cols + self.x] = None
            elif c == Comp.LAVA_SPREAD:
                if do_temp:
                    if not buffer_world[self.y-1 * cols + self.x] == None:
                        if buffer_world[self.y-1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y-1 * cols + self.x].temp += (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                    if not buffer_world[self.y+1 * cols + self.x] == None:
                        if buffer_world[self.y+1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y+1 * cols + self.x].temp += (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                    if self.x < cols:
                        if not buffer_world[self.y * cols + self.x+1] == None:
                            if buffer_world[self.y * cols + self.x+1].temp < self.temp:
                                buffer_world[self.y * cols + self.x+1].temp += (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                    if self.x > 0:
                        if not buffer_world[self.y * cols + self.x-1] == None:
                            if buffer_world[self.y * cols + self.x-1].temp < self.temp:
                                buffer_world[self.y * cols + self.x-1].temp += (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                    if ambient_temp_loss:
                        self.temp -= randint(0,2)
                    if ambient_temp_spread:
                        pass
                if self.x < 1 or self.x > cols - 2 or moved_down: continue
                if randint(0, 1) == 0:
                    if buffer_world[(self.y) * cols + self.x + 1] is None:
                        buffer_world[self.y * cols + self.x] = None
                        self.x += 1
                        buffer_world[self.y * cols + self.x] = self
                elif buffer_world[(self.y) * cols + self.x - 1] is None:
                    buffer_world[self.y * cols + self.x] = None
                    self.x -= 1
                    buffer_world[self.y * cols + self.x] = self
                if self.temp < 700:
                        buffer_world[self.y * cols + self.x] = Particle(stone, self.x, self.y, self.temp)
            elif c == Comp.MOLTEN_GLASS_SPREAD:
                if do_temp:
                    if not buffer_world[self.y-1 * cols + self.x] == None:
                        if buffer_world[self.y-1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y-1 * cols + self.x].temp += (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                    if not buffer_world[self.y+1 * cols + self.x] == None:
                        if buffer_world[self.y+1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y+1 * cols + self.x].temp += (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                    if self.x < cols:
                        if not buffer_world[self.y * cols + self.x+1] == None:
                            if buffer_world[self.y * cols + self.x+1].temp < self.temp:
                                buffer_world[self.y * cols + self.x+1].temp += (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                    if self.x > 0:
                        if not buffer_world[self.y * cols + self.x-1] == None:
                            if buffer_world[self.y * cols + self.x-1].temp < self.temp:
                                buffer_world[self.y * cols + self.x-1].temp += (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                    if ambient_temp_loss:
                        self.temp -= randint(0,2)
                    if ambient_temp_spread:
                        pass
                if self.x < 1 or self.x > cols - 2 or moved_down: continue
                if randint(0, 1) == 0:
                    if buffer_world[(self.y) * cols + self.x + 1] is None:
                        buffer_world[self.y * cols + self.x] = None
                        self.x += 1
                        buffer_world[self.y * cols + self.x] = self
                elif buffer_world[(self.y) * cols + self.x - 1] is None:
                    buffer_world[self.y * cols + self.x] = None
                    self.x -= 1
                    buffer_world[self.y * cols + self.x] = self
                if self.temp < 1400:
                        buffer_world[self.y * cols + self.x] = Particle(glass, self.x, self.y, self.temp)
            elif c == Comp.ACID_VAPOUR_SPREAD:
                if do_temp:
                    if not buffer_world[self.y-1 * cols + self.x] == None:
                        if buffer_world[self.y-1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y-1 * cols + self.x].temp += (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                    if not buffer_world[self.y+1 * cols + self.x] == None:
                        if buffer_world[self.y+1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y+1 * cols + self.x].temp += (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                    if self.x < cols:
                        if not buffer_world[self.y * cols + self.x+1] == None:
                            if buffer_world[self.y * cols + self.x+1].temp < self.temp:
                                buffer_world[self.y * cols + self.x+1].temp += (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                    if self.x > 0:
                        if not buffer_world[self.y * cols + self.x-1] == None:
                            if buffer_world[self.y * cols + self.x-1].temp < self.temp:
                                buffer_world[self.y * cols + self.x-1].temp += (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                    if ambient_temp_loss:
                        self.temp -= randint(0,2)
                    if ambient_temp_spread:
                        pass
                    if self.temp < 100:
                        buffer_world[self.y * cols + self.x] = Particle(acid, self.x, self.y, self.temp)
                if self.x < 1 or self.x > cols - 2: continue
                if randint(0, 1) == 0:
                    if buffer_world[(self.y) * cols + self.x + 1] is None:
                        buffer_world[self.y * cols + self.x] = None
                        self.x += 1
                        buffer_world[self.y * cols + self.x] = self
                elif buffer_world[(self.y) * cols + self.x - 1] is None:
                    buffer_world[self.y * cols + self.x] = None
                    self.x -= 1
                    buffer_world[self.y * cols + self.x] = self
            elif c == Comp.STONE_SPREAD:
                if do_temp:
                    if not buffer_world[self.y-1 * cols + self.x] == None:
                        if buffer_world[self.y-1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y-1 * cols + self.x].temp += (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                    if not buffer_world[self.y+1 * cols + self.x] == None:
                        if buffer_world[self.y+1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y+1 * cols + self.x].temp += (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                    if self.x < cols:
                        if not buffer_world[self.y * cols + self.x+1] == None:
                            if buffer_world[self.y * cols + self.x+1].temp < self.temp:
                                buffer_world[self.y * cols + self.x+1].temp += (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                    if self.x > 0:
                        if not buffer_world[self.y * cols + self.x-1] == None:
                            if buffer_world[self.y * cols + self.x-1].temp < self.temp:
                                buffer_world[self.y * cols + self.x-1].temp += (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                    if ambient_temp_loss:
                        self.temp -= randint(0,2)
                    if ambient_temp_spread:
                        pass
                    if self.temp > 699:
                        buffer_world[self.y * cols + self.x] = Particle(lava, self.x, self.y, self.temp)
            elif c == Comp.GLASS_SPREAD:
                if do_temp:
                    if not buffer_world[self.y-1 * cols + self.x] == None:
                        if buffer_world[self.y-1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y-1 * cols + self.x].temp += (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y-1 * cols + self.x].temp)/2
                    if not buffer_world[self.y+1 * cols + self.x] == None:
                        if buffer_world[self.y+1 * cols + self.x].temp < self.temp:
                            buffer_world[self.y+1 * cols + self.x].temp += (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                            self.temp -= (self.temp - buffer_world[self.y+1 * cols + self.x].temp)/2
                    if self.x < cols:
                        if not buffer_world[self.y * cols + self.x+1] == None:
                            if buffer_world[self.y * cols + self.x+1].temp < self.temp:
                                buffer_world[self.y * cols + self.x+1].temp += (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x+1].temp)/2
                    if self.x > 0:
                        if not buffer_world[self.y * cols + self.x-1] == None:
                            if buffer_world[self.y * cols + self.x-1].temp < self.temp:
                                buffer_world[self.y * cols + self.x-1].temp += (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                                self.temp -= (self.temp - buffer_world[self.y * cols + self.x-1].temp)/2
                    if ambient_temp_loss:
                        self.temp -= randint(0,2)
                    if ambient_temp_spread:
                        pass
                    if self.temp > 1399:
                        buffer_world[self.y * cols + self.x] = Particle(molten_glass, self.x, self.y, self.temp)
            else:
                raise Exception("Incorrect component")

print(f"Comp:\n{Comp.__dict__}\n")

running = True
print(f"End program var 'running' is set to {running}")

frame_tick_display = False
print(f"Debug var 'frame_tick_display' is set to {frame_tick_display}")

mode = 2

do_temp = True
ambient_temp_spread = False
ambient_temp_loss = False

print(f"do_temp: {do_temp}")
print(f"ambient_temp_spread: {ambient_temp_spread}")
print(f"ambient_temp_loss: {ambient_temp_loss}")
print(f"mode: {mode}")

sand = Element(1.2, (255,236,112), (Comp.FALLDOWN, Comp.SAND_SPREAD))
glass = Element(1, (230, 230, 230), (Comp.STATIC, Comp.GLASS_SPREAD))
molten_glass = Element(0.8, (250, 236, 205), (Comp.FALLDOWN, Comp.MOLTEN_GLASS_SPREAD))
water = Element(0.7, (51,102,255), (Comp.FALLDOWN, Comp.WATER_SPREAD))
steam = Element(0.2, (230,234,240), (Comp.FLOATUP, Comp.STEAM_SPREAD))
acid = Element(1, (0,234,0), (Comp.FALLDOWN, Comp.ACID_SPREAD))
acid_vapour = Element(0.1, (147, 240, 144), (Comp.FLOATUP, Comp.ACID_VAPOUR_SPREAD))
stone = Element(4, (107, 107, 107), (Comp.STATIC, Comp.STONE_SPREAD))
lava = Element(0.8, (255, 153, 51), (Comp.FALLDOWN, Comp.LAVA_SPREAD))
fire = Element(0.2, (0,0,0), (Comp.STATIC, Comp.FIRE_SPREAD))

sand_enabled = True
glass_enabled = True
molten_glass_enabled = True
water_enabled = True
steam_enabled = True
acid_enabled = True
acid_vapour_enabled = True
stone_enabled = True
lava_enabled = True
fire_enabled = False

print(f"{colorama.Fore.GREEN if sand_enabled else colorama.Fore.RED}Sand: {colorama.Fore.WHITE}{sand.__dict__}")
print(f"{colorama.Fore.GREEN if glass_enabled else colorama.Fore.RED}Glass: {colorama.Fore.WHITE}{glass.__dict__}")
print(f"{colorama.Fore.GREEN if molten_glass_enabled else colorama.Fore.RED}Molten Glass: {colorama.Fore.WHITE}{molten_glass.__dict__}")
print(f"{colorama.Fore.GREEN if water_enabled else colorama.Fore.RED}Water: {colorama.Fore.WHITE}{water.__dict__}")
print(f"{colorama.Fore.GREEN if steam_enabled else colorama.Fore.RED}Steam: {colorama.Fore.WHITE}{steam.__dict__}")
print(f"{colorama.Fore.GREEN if acid_enabled else colorama.Fore.RED}Acid: {colorama.Fore.WHITE}{acid.__dict__}")
print(f"{colorama.Fore.GREEN if acid_vapour_enabled else colorama.Fore.RED}Acid Vapour: {colorama.Fore.WHITE}{acid_vapour.__dict__}")
print(f"{colorama.Fore.GREEN if stone_enabled else colorama.Fore.RED}Stone: {colorama.Fore.WHITE}{stone.__dict__}")
print(f"{colorama.Fore.GREEN if lava_enabled else colorama.Fore.RED}Lava: {colorama.Fore.WHITE}{lava.__dict__}")
print(f"{colorama.Fore.GREEN if fire_enabled else colorama.Fore.RED}Fire: {colorama.Fore.WHITE}{fire.__dict__}")

def control():
    global mode

    keys = pygame.key.get_pressed()
    if keys[pygame.K_1]:
        mode = 1
    if keys[pygame.K_2]:
        mode = 2
    if keys[pygame.K_3]:
        mode = 3
    if keys[pygame.K_4]:
        mode = 4
    if keys[pygame.K_5]:
        mode = 5
    if keys[pygame.K_6]:
        mode = 6
    if keys[pygame.K_7]:
        mode = 7
    if keys[pygame.K_8]:
        mode = 8

    if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
        mx, my = pygame.mouse.get_pos()
        for x in range(max(0, mx - brush_size), min(cols - 1, mx + brush_size)):
            for y in range(max(0, my - brush_size), min(rows - 1, my + brush_size)):
                if (mx - x) ** 2 + (my - y) ** 2 > brush_size ** 2: continue
                if pygame.mouse.get_pressed()[2]:
                    world[y*cols + x] = None
                else:
                    if mode == 1 and sand_enabled:
                        world[y*cols + x] = Particle(sand, x, y, 10)
                    elif mode == 2 and water_enabled:
                        world[y*cols + x] = Particle(water, x, y, 20)
                    elif mode == 3 and steam_enabled:
                        world[y*cols + x] = Particle(steam, x, y, 110)
                    elif mode == 4 and acid_enabled:
                        world[y*cols + x] = Particle(acid, x, y, 60)
                    elif mode == 5 and lava_enabled:
                        world[y*cols + x] = Particle(lava, x, y, 1800)
                    elif mode == 6 and stone_enabled:
                        world[y*cols + x] = Particle(stone, x, y, 600)
                    elif mode == 7 and glass_enabled:
                        world[y*cols + x] = Particle(glass, x, y, 600)
                    elif mode == 8 and fire_enabled:
                        world[y*cols + x] = Particle(fire, x, y, 600)

def debug_console():
    global running, frame_tick_display
    do_extra_info = False
    while True:
        keys = pygame.key.get_pressed()
        if keys[ESC]:
            frame_tick_display = False
        inpt = input("> ")
        if inpt == "exit":
            running = False
            exit()
        elif inpt == "frame_tick_display":
            print("PRESS ESC TO STOP")
            frame_tick_display = not frame_tick_display
        elif inpt == "ex_info":
            do_extra_info = not do_extra_info
        elif inpt == "var get":
            var_name = input("Var name: ")
            try:
                try:
                    print(f"Var value: {globals()[var_name].__dict__}")
                except:
                    print(f"Var value: {globals()[var_name]}")
                    print(f"Var type: {type(globals()[var_name])}")
            except:
                print(f"{colorama.Fore.RED} INCORRECT VARIABLE NAME{colorama.Fore.RESET}")
        elif inpt == "var set":
            var_name = input("Var name: ")
            var_type = input("Var type (int,float,bool,str): ")
            var_value = input("New var value: ")
            try:
                didfail = False
                if do_extra_info:
                    temp_val = globals()[var_name]
                if var_type == "int":
                    var_value = int(var_value)
                elif var_type == "float":
                    var_value = float(var_value)
                elif var_type == "bool":
                    var_value = bool(var_value)
                elif var_type == "str":
                    pass
                else:
                    print(f"{colorama.Fore.RED} INCORRECT TYPE{colorama.Fore.RESET}")
                    didfail = True
                    
                if not didfail:
                    globals()[var_name] = var_value
                    print(f"{colorama.Fore.GREEN} Var set successfully. {colorama.Fore.RESET}")
                    if do_extra_info:
                        print(f"Registered var name: {var_name}")
                        print(f"New var value: {var_value}")
                        print(f"Old var value: {temp_val}")
                        print(f"New var type: {type(globals()[var_name])}")
            except:
                print(f"{colorama.Fore.RED} VAR SET FAILED{colorama.Fore.RESET}")

print("Entering main loop")

print("Starting debug console")
debug_thread = Thread(target=debug_console)
print(f"Debug thread: {debug_thread}")
try:
    debug_thread.start()
except:
    print(f"{colorama.Fore.RED} DEBUG THREAD FAILED {colorama.Fore.RESET}")

while running:
    scr.fill((0,0,0))
    control()
    rev_world = list(reversed(world))
    updated_particles = []
    for i in rev_world:
        if i == None or i in updated_particles: continue
        i.update(world,rev_world)
        updated_particles.append(i)
        scr.set_at((i.x, i.y), i.element.colour)
    for e in pygame.event.get():
        if e.type == pygame.QUIT or not running:
            pygame.quit()
            exit()
    pygame.display.flip()
    if frame_tick_display:
        print("Tick")

pygame.quit()
exit()