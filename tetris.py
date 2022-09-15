import pygame
import random

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode([400, 600])

running = True

tetronimoes = [
    [0x0330, 0x0330, 0x0330, 0x0330], # O
    [0x02D0, 0x0446, 0x00D8, 0x0622], # L
    [0x08D0, 0x0644, 0x00D2, 0x0226], # J
    [0x0F00, 0x2222, 0x00F0, 0x4444], # I
    [0x06C0, 0x0462, 0x006C, 0x08C4], # S
    [0x0C60, 0x0264, 0x00C6, 0x04C8], # Z
    [0x04D0, 0x0464, 0x00D4, 0x04C4]  # T
]

GRID_WIDTH = 10
GRID_HEIGHT = 24
START_POS = (4, 0)

curr_tetronimo = None
held_tetronimo = None

xoff = 0
yoff = 0
rotation = 0

grid = [0] * GRID_HEIGHT

def draw(curr):
    pass

def add():
    tetronimo = random.choice(tetronimoes)
    for i in range(4):
        grid[i] |= tetronimo[0] << START_POS[0]

    print(grid)
    

def update():
    for i in range(4):
        row = 0x000F << i
        if (curr_tetronimo[rotation] & row) & grid[yoff + 4 - i]:
            if yoff + 4 - i >= GRID_HEIGHT:
                continue
            

            pass

frames = 0

add()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    for j in range(GRID_HEIGHT):
        for i in range(GRID_WIDTH):

            pygame.draw.rect(screen, (20,20,20), pygame.Rect(i * 5, j * 5, 5, 5))

    pygame.display.flip()
    
    frames += 1
    clock.tick(30)

pygame.quit()