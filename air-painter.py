
import pygame
import time


x = 1
y = 50
z = 50
pygame.init()
screen = pygame.display.set_mode((600, 600))
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


  # Display some text
  font = pygame.font.Font(None, 36)
  text = font.render("Hello There", 1, (10, 10, 10))
  textpos = text.get_rect()
  textpos.centerx = background.get_rect().centerx
  background.blit(text, textpos)

  # Blit everything to the screen
  screen.blit(background, (0, 0))
  pygame.display.flip()
  xz = 0

  # Event loop
  while 1:
    xz = xz +1
    sometext((x,y,z))
    background.fill((xz,y,z))
    screen.blit(background, (0, 0))
    pygame.display.flip()
    pygame.display.update()
    time.sleep(0.5)


if __name__ == '__main__': main()
