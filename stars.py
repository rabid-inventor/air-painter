import pygame
import random
import time

SCREENSIZE = 640, 480

class Rain(object):
#Rain generator.
  drops = []
  height = 160
  speed = 1
  color = (255, 255, 255, 255)
  chance = .05

def __init__(self, **kwargs):
# Allow programmer to change settings of rain generator.
  self.__dict__.update(kwargs)

def Render(self, screen):
# Render the rain.
  dirtyrects = []
  for drop in self.drops:
    dr = drop.Render(dirtyrects, screen)

  if drop.dead:
    self.drops.remove(drop)
    dirtyrects.append(dr)
  if random.random() self.maxy:
    self.dead = 1
  else:
    screen.blit(self.pic, self.pos)
  return r

def main():
# Initialize pygame
  pygame.init()
  screen = pygame.display.set_mode(SCREENSIZE, 0, 32)

# Create rain generator
  rain = Rain()

# Main loop
  nexttime = time.time()
  ctr = 0
  quit = 0
  while not quit:

# Uncomment the following line to make the rain go slower
#time.sleep(.01)

# Track FPS
    if time.time() > nexttime:
      nexttime = time.time() + 1
      print .%d fps. % ctr
      ctr = 0
      ctr += 1

# Draw rain
    screen.fill((0, 0, 0, 0))
    r = rain.Render(screen)

# Look for user quit
    pygame.display.update(r)
    pygame.event.pump()
    for e in pygame.event.get():
      if e.type in [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
        quit = 1
        break

# Terminate pygame
  pygame.quit()

if __name__ == .__main__.:
  main()
