
import pygame
import time
import skywriter

x = 0
y = 0
z = 0 

@skywriter.move()
def move(xa,ya,za):
      #print(x,y,z)
  global x,y,z
  x = xa * 255
  y = ya  * 255
  z = za  * 255
 

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption('Basic Pygame program')
# Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((x, y, z))

def sometext(output):
  font = pygame.font.Font(None, 36)
  text = font.render(str(output), 1, (10, 10, 10))
  textpos = text.get_rect()
  textpos.centerx = background.get_rect().centerx
  background.blit(text, textpos)

def main():

  # Initialise screen


 

  # Blit everything to the screen
  screen.blit(background, (0, 0))
  pygame.display.flip()

  # Event loop
  while 1:
    ev = pygame.event.poll()    # Look for any event
    if ev.type == pygame.QUIT:  # Window close button clicked?
      break                   #   ... leave game loop
    background.fill((x,y,z))
    screen.blit(background, (0, 0))
    pygame.display.flip()
    pygame.display.update()
    time.sleep(0.02)


if __name__ == '__main__': main()
