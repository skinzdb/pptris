import pygame
import random

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode([400, 600])

running = True

GRID_WIDTH = 10
GRID_HEIGHT = 24
START_POS = (3, 0)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255,165,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
L_BLUE = (0,255,255)
D_BLUE = (0,0,255)
PURPLE = (128,0,128)

class Tile:
    def __init__(self, colour):
        self.colour = colour
        self.is_baked = False
    def bake(self):
        self.is_baked = True

tetronimoes = [
    [0x0660, 0x0660, 0x0660, 0x0660], # O
    [0x02E0, 0x0446, 0x00E8, 0x0622], # L
    [0x08E0, 0x0644, 0x00E2, 0x0226], # J
    [0x0F00, 0x2222, 0x00F0, 0x4444], # I
    [0x06C0, 0x0462, 0x006C, 0x08C4], # S
    [0x0C60, 0x0264, 0x00C6, 0x04C8], # Z
    [0x04E0, 0x0464, 0x00E4, 0x04C4]  # T
]

curr_tetronimo = None
held_tetronimo = None

xoff = 0
yoff = 0
rotation = 0

grid = []

for j in range(GRID_HEIGHT):
    row = []
    for i in range(GRID_WIDTH):
        row.append(Tile(BLACK))
    grid.append(row)

def draw(curr):
    pass

def add():
    for row in grid:
        for i in range(len(row)):
            row[i] = Tile(BLACK)

    xoff = START_POS[0]
    yoff = START_POS[1] 

    tetronimo = random.choice(tetronimoes)
    for j in range(4):
        for i in range(4):
            is_full = tetronimo[0]
            grid[j + yoff][i + xoff] = (tetronimo[0] >> (12 - 4 * i) & 0xF) << (7 - START_POS[0])
    
    print(grid)


def update():
    for i in range(4):
        row = 0x000F << i
        if (curr_tetronimo[rotation] & row) & grid[yoff + 4 - i]:
            if yoff + 4 - i >= GRID_HEIGHT:
                continue
            
            pass

frames = 0
update_speed = 30 # number of frames before update

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((144, 144, 144))
    add()

    if frames >= update_speed:
        update()
        frames = 0

    for j in range(GRID_HEIGHT - 2):
        for i in range(GRID_WIDTH):
            isFull = (grid[j + 2] & (1 << (GRID_WIDTH - i))) > 0 
            colour = (255, 255, 255) if isFull else (0, 0, 0) 
            pygame.draw.rect(screen, colour, pygame.Rect(i * 25, j * 25, 25, 25))

    pygame.display.flip()
    
    frames += 1
    clock.tick(30)

pygame.quit()