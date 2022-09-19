import pygame
import random

GRID_WIDTH = 10
GRID_HEIGHT = 24
START_POS = (3, 0)
CLOCKWISE = 1
ANTICLOCKWISE = -1

FPS = 60
STICK_FRAMES = 90
INITIAL_SPEED = 45
INPUT_DELAY = 1
LR_DELAY = 10

NONE   = (0, 0, 0)
RED    = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN  = (0, 255, 0)
L_BLUE = (0, 255, 255)
D_BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

COLOUR_MAP = {
    NONE    : 0,
    RED     : 1,
    ORANGE  : 2,
    YELLOW  : 3,
    GREEN   : 4,
    L_BLUE  : 5,
    D_BLUE  : 6,
    PURPLE  : 7
}

class Tetronimo:
    def __init__(self, name, colour, data):
        self.name = name
        self.colour = colour
        self.data = data

TETRONIMOES = [
    Tetronimo("O", YELLOW, [0x0660, 0x0660, 0x0660, 0x0660]),
    Tetronimo("J", D_BLUE, [0x08E0, 0x0644, 0x00E2, 0x044C]), 
    Tetronimo("L", ORANGE, [0x02E0, 0x0446, 0x00E8, 0x0C44]), 
    Tetronimo("T", PURPLE, [0x04E0, 0x0464, 0x00E4, 0x04C4]),  
    Tetronimo("S", GREEN,  [0x06C0, 0x0462, 0x006C, 0x08C4]), 
    Tetronimo("Z", RED,    [0x0C60, 0x0264, 0x00C6, 0x04C8]), 
    Tetronimo("I", L_BLUE, [0x0F00, 0x2222, 0x00F0, 0x4444]), 
]

JLTSZ_WALL_KICKS = [
    [( 0, 0), (-1, 0), (-1,-1), ( 0, 2), (-1, 2)], # 0>>1
    [( 0, 0), ( 1, 0), ( 1, 1), ( 0,-2), ( 1,-2)], # 1>>2
    [( 0, 0), ( 1, 0), ( 1,-1), ( 0, 2), ( 1, 2)], # 2>>3
    [( 0, 0), (-1, 0), (-1, 1), ( 0,-2), (-1,-2)], # 3>>0
]

I_WALL_KICKS = [
    [( 0, 0), (-2, 0), ( 1, 0), (-2, 1), ( 1,-2)], # 0>>1
    [( 0, 0), (-1, 0), ( 2, 0), (-1,-2), ( 2, 1)], # 1>>2
    [( 0, 0), ( 2, 0), (-1, 0), ( 2,-1), (-1, 2)], # 2>>3
    [( 0, 0), ( 1, 0), (-2, 0), ( 1, 2), (-2,-1)], # 3>>0
]

class Game:
    curr_tetronimo = None
    held_tetronimo = None
  
    xpos = START_POS[0]
    ypos = START_POS[1]
    rotation = 0

    update_speed = INITIAL_SPEED # number of frames before update
    stick_time = STICK_FRAMES

    new_tetronimo = False

    grid = []
    baked_grid = []

    def __init__(self):
        self.grid = [0] * GRID_HEIGHT
        self.baked_grid = [0] * GRID_HEIGHT
        self.reset()

    def left(self):
        if self.check_move(-1, 0):
            self.xpos -=1
            self.update_grid()

    def right(self):
        if self.check_move(1, 0):
            self.xpos +=1
            self.update_grid()

    def down(self):
        if self.check_move(0, 1):
            self.ypos += 1
            self.update_grid()
        else:
            self.stick_time -= 15

    def hard_down(self):
        pass

    def rotate(self, direction=CLOCKWISE):
        if self.curr_tetronimo == None:
            return

        wall_kicks = I_WALL_KICKS if self.curr_tetronimo.name == "I" else JLTSZ_WALL_KICKS
   
        for x, y in wall_kicks[self.rotation]: # If rotation is an invalid move, try and kick it into a legal position
            if self.check_move(direction * x, direction * y, direction): 
                self.xpos += direction * x
                self.ypos += direction * y
                self.rotation = (self.rotation + direction) % 4
                break
        self.update_grid()

    def get_tile(self, x, y):
        return (self.grid[y] >> (x * 3)) & 7

    def get_baked_tile(self, x, y):
        return (self.baked_grid[y] >> (x * 3)) & 7

    def is_filled(self, x, y, rot):
        return (self.curr_tetronimo.data[rot] >> (15 - 4 * y - x)) & 1

    def check_move(self, x, y, rot_direction=0): # Check move is valid
        if self.curr_tetronimo == None:
            return False
        rot = (self.rotation + rot_direction) % 4
        for j in range(4):
            for i in range(4):
                if (not self.within_grid(self.xpos + x + i, self.ypos + y + j) or self.get_baked_tile(self.xpos + x + i, self.ypos + y + j)) and self.is_filled(i, j, rot):
                    return False
        return True
        
    def within_grid(self, x, y):
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

    def add(self):  # Spawn new tetronimo at top of screen
        self.xpos = START_POS[0]
        self.ypos = START_POS[1] 
        self.rotation = 0
        self.stick_time = STICK_FRAMES

        self.curr_tetronimo = random.choice(TETRONIMOES)
        if self.curr_tetronimo.name == "I":
            self.ypos += 1   

        if self.baked_grid[2] == 0x3FFFFFFF: # TODO: Use |= and see if it has changed  Newly spawned piece is blocked out, move it up by one.
            self.ypos -= 1

    def update_grid(self):
        for j in range(GRID_HEIGHT):
           self.grid[j] &= self.baked_grid[j]

        if self.curr_tetronimo != None: 
            for j in range(4):
                for i in range(4):
                    if self.within_grid(self.xpos + i, self.ypos + j):
                        data = COLOUR_MAP[self.curr_tetronimo.colour] if self.is_filled(i, j, self.rotation) else COLOUR_MAP[NONE]
                        self.grid[self.ypos + j] |= data << ((self.xpos + i) * 3)
                
    def update(self, frames):
        if frames >= self.update_speed:
            if self.new_tetronimo:
                self.add()
                self.new_tetronimo = False
            else:
                if self.check_move(0, 1, self.rotation):
                    self.down()
                else:
                    self.stick_time -= 60
            self.update_grid()
            frames = 0

        if self.stick_time <= 0 and not self.new_tetronimo:
            self.bake()
            self.curr_tetronimo = None
            self.new_tetronimo = True
            self.update_grid()

        return frames

    def bake(self):
        for j in range(4):
            for i in range(4):
                if self.within_grid(self.xpos + i, self.ypos + j) and not self.get_baked_tile(self.xpos + i, self.ypos + j) and self.is_filled(i, j, self.rotation):
                    self.baked_grid[self.ypos + j] |= 7 << ((self.xpos + i) * 3)
        self.check_gameover()
        self.clear_rows()
    
    def check_gameover(self):
        return self.baked_grid[1] > 0

    def clear_rows(self):
        for j in range(GRID_HEIGHT):
            if self.baked_grid[j] == 0x3FFFFFFF:
                self.grid.pop(j)
                self.grid.insert(0, 0)
                self.baked_grid.pop(j)
                self.baked_grid.insert(0, 0)
        self.update_grid()
    
    def reset(self):
        self.curr_tetronimo = None
        self.held_tetronimo = None
    
        self.update_speed = INITIAL_SPEED # number of frames before update
        self.stick_time = STICK_FRAMES

        for j in range(GRID_HEIGHT):
            self.grid[j] = 0
            self.baked_grid[j] = 0
        
        self.add()
        self.update_grid()

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode([400, 600])

running = True
frames = 0
input_delay = INPUT_DELAY
lr_delay = LR_DELAY
lr_pressed = False

game = Game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.rotate()
            if event.key == pygame.K_LEFT:
                game.left()
                lr_pressed = True
            if event.key == pygame.K_RIGHT:
                game.right()
                lr_pressed = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                lr_pressed = False
                lr_delay = LR_DELAY

    keys = pygame.key.get_pressed() 
    if input_delay == 0:
        input_delay = INPUT_DELAY
        if lr_delay == 0:
            if keys[pygame.K_LEFT]:
                game.left()
            if keys[pygame.K_RIGHT]:
                game.right()
        if keys[pygame.K_DOWN]:
            game.down()

    screen.fill((144, 144, 144))

    frames = game.update(frames)

    for j in range(GRID_HEIGHT - 2):
        for i in range(GRID_WIDTH):
            pygame.draw.rect(screen, list(COLOUR_MAP.keys())[game.get_tile(i, j + 2)], pygame.Rect(i * 25, j * 25, 25, 25))
            pygame.draw.rect(screen, list(COLOUR_MAP.keys())[game.get_baked_tile(i, j+2)], pygame.Rect(i * 10 + 275, j * 10, 10, 10))

    pygame.display.flip()
    
    frames += 1
    if input_delay > 0:
        input_delay -= 1
    if lr_pressed and lr_delay > 0:
        lr_delay -= 1
    clock.tick(FPS)

pygame.quit()