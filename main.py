import pygame
from random import randint
from enum import Enum, auto
from typing import Tuple
print("Imports successful")

pygame.init()

class Comp(Enum):
    FALLDOWN = auto()
    FLOATUP = auto()
    SAND_SPREAD = auto()
    WATER_SPREAD = auto()
    STEAM_SPREAD = auto()

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
    def __init__(self, element: Element, x: int, y: int) -> None:
        self.element = element
        self.x = x
        self.y = y
    def update(self, buffer_world):
        moved_down = False

        for c in self.element.comps:
            if c == Comp.FALLDOWN:
                if self.y >= rows - 1: continue
                if buffer_world[(self.y + 1) * cols + self.x] is not None: continue
                buffer_world[self.y * cols + self.x] = None
                self.y += 1
                moved_down = True
                buffer_world[self.y * cols + self.x] = self
            elif c == Comp.FLOATUP:
                if self.y <= 0: continue
                if buffer_world[(self.y - 1) * cols + self.x] is not None: continue
                buffer_world[self.y * cols + self.x] = None
                self.y -= 1
                buffer_world[self.y * cols + self.x] = self
            elif c == Comp.SAND_SPREAD:
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
            elif c == Comp.STEAM_SPREAD:
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
            else:
                raise Exception("Incorrect component")

mode = 2

sand = Element(1.0, (255,236,112), (Comp.FALLDOWN, Comp.SAND_SPREAD))
water = Element(0.9, (51,102,255), (Comp.FALLDOWN, Comp.WATER_SPREAD))
steam = Element(0.2, (230,234,240), (Comp.FLOATUP, Comp.STEAM_SPREAD))

print(f"Sand: {sand}")
print(f"Water: {water}")
print(f"Steam: {steam}")

def control():
    global mode

    keys = pygame.key.get_pressed()
    if keys[pygame.K_1]:
        mode = 1
    if keys[pygame.K_2]:
        mode = 2
    if keys[pygame.K_3]:
        mode = 3

    if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
        mx, my = pygame.mouse.get_pos()
        for x in range(max(0, mx - brush_size), min(cols - 1, mx + brush_size)):
            for y in range(max(0, my - brush_size), min(rows - 1, my + brush_size)):
                if (mx - x) ** 2 + (my - y) ** 2 > brush_size ** 2: continue
                if pygame.mouse.get_pressed()[2]:
                    world[y*cols + x] = None
                else:
                    if mode == 1:
                        world[y*cols + x] = Particle(sand, x, y)
                    elif mode == 2:
                        world[y*cols + x] = Particle(water, x, y)
                    elif mode == 3:
                        world[y*cols + x] = Particle(steam, x, y)

print("Entering main loop")

while __name__ == "__main__":
    scr.fill((0,0,0))
    control()
    #buffer_world = list(reversed(world))
    buffer_world = []
    for i in world:
        buffer_world.append(i)
    for i in buffer_world:
        if i == None: continue
        i.update(buffer_world)
        scr.set_at((i.x, i.y), i.element.colour)
    world = buffer_world
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.flip()