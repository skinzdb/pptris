from re import X
import pygame
import random

GRID_WIDTH = 10
GRID_HEIGHT = 24
START_POS = (3, 0)
CLOCKWISE = 1
ANTICLOCKWISE = -1

FPS = 60
STICK_FRAMES = 90
INITIAL_SPEED = 60
INPUT_SPEED = 10

COLOURS = {
    "O": (255, 255, 0),   # Yellow
    "L": (255, 165, 0),   # Orange
    "J": (0, 0, 255),     # Dark blue
    "I": (0, 255, 255),   # Light blue
    "S": (0, 255, 0),     # Green
    "Z": (255, 0, 0),     # Red
    "T": (128 ,0, 128)    # Purple
}
NONE = (0, 0, 0)

# TETRONIMOES = {
#     "O": [[[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]]],
#     "L": [[[0,0,0,0], [0,0,1,0], [1,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,0,0], [0,1,0,0], [0,1,1,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]]],
#     "J": [[[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]]],
#     "T": [[[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]]],
#     "S": [[[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]]],
#     "Z": [[[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]]],
#     "I": [[[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
#           [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]]],    

# }

TETRONIMOES = {
    "O": [0x0660, 0x0660, 0x0660, 0x0660],
    "L": [0x02E0, 0x0446, 0x00E8, 0x0622], 
    "J": [0x08E0, 0x0644, 0x00E2, 0x0226], 
    "I": [0x0F00, 0x2222, 0x00F0, 0x4444], 
    "S": [0x06C0, 0x0462, 0x006C, 0x08C4], 
    "Z": [0x0C60, 0x0264, 0x00C6, 0x04C8], 
    "T": [0x04E0, 0x0464, 0x00E4, 0x04C4]  
}

JLTSZ_WALL_KICKS = [
    [( 0, 0), (-1, 0), (-1, 1), ( 0,-2), (-1,-2)], # 0>>1
    [( 0, 0), ( 1, 0), ( 1,-1), ( 0, 2), ( 1, 2)], # 1>>2
    [( 0, 0), ( 1, 0), ( 1, 1), ( 0,-2), ( 1,-2)], # 2>>3
    [( 0, 0), (-1, 0), (-1,-1), ( 0, 2), (-1, 2)], # 3>>0
]

I_WALL_KICKS = [
    [( 0, 0), (-2, 0), ( 1, 0), (-2,-1), ( 1, 2)], # 0>>1
    [( 0, 0), (-1, 0), ( 2, 0), (-1, 2), ( 2,-1)], # 1>>2
    [( 0, 0), ( 2, 0), (-1, 0), ( 2, 1), (-1,-2)], # 2>>3
    [( 0, 0), ( 1, 0), (-2, 0), ( 1,-2), (-2, 1)], # 3>>0
]

class Tile:
    def __init__(self, colour):
        self.colour = colour
        self.is_baked = False
    def bake(self):
        self.is_baked = True

class Tetronimo:
    def __init__(self, name, colour, data):
        self.name = name
        self.colour = colour
        self.data = data
    def to_array(self, rot):
        arr = []
        for j in range(4):
            row = []
            for i in range(4):
                row.append((self.data[rot] >> (15 - 4 * j - i)) & 1)
            arr.append(row)
        return arr

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

    def __init__(self):
        self.reset()

    def left(self):
        if self.check_move(-1, 0, self.rotation):
            self.xpos -=1
            self.update_grid()

    def right(self):
        if self.check_move(1, 0, self.rotation):
            self.xpos +=1
            self.update_grid()

    def down(self):
        if self.check_move(0, 1, self.rotation):
            self.ypos += 1
            self.update_grid()
        else:
            self.stick_time -= 1

    def hard_down(self):
        pass

    def rotate(self, direction=CLOCKWISE):
        wall_kicks = I_WALL_KICKS if self.curr_tetronimo.name == "I" else JLTSZ_WALL_KICKS
   
        for x, y in wall_kicks[self.rotation]: # If rotation is an invalid move, try and kick it into a legal position
            if self.check_move(direction * x, direction * y, (self.rotation + direction) % 4): 
                self.xpos += direction * x
                self.ypos += direction * y
                self.rotation = (self.rotation + direction) % 4
                break

    def check_move(self, x, y, rot): # Check move is valid
        for j in range(4):
            for i in range(4):
                if (not self.within_grid(i, j) or self.grid[self.ypos][self.xpos].is_baked) and self.is_filled(x + i, y + j, rot):
                    return False
        return True
        
    def within_grid(self, x, y):
        return 0 <= x + self.xpos < GRID_WIDTH and 0 <= y + self.ypos < GRID_HEIGHT

    def add(self):  # Spawn new tetronimo at top of screen
        self.xpos = START_POS[0]
        self.ypos = START_POS[1] 
        self.rotation = 0

        name, data = random.choice(list(TETRONIMOES.items())) # Choose random tetronimo
        if name == "I":
            self.ypos += 1
        self.curr_tetronimo = Tetronimo(name, get_colour(name), data)
        for tile in self.grid[2]: 
            if tile.is_baked: # Newly spawned piece is blocked out, move it up by one.
                self.ypos -= 1
                break

    def update_grid(self):
        for j in range(GRID_HEIGHT):
            for i in range(GRID_WIDTH):
                if not self.grid[j][i].is_baked:
                    self.grid[j][i] = Tile(NONE)

        arr = self.curr_tetronimo.to_array(self.rotation)
                
        for j in range(4):
            for i in range(4):
                 self.grid[self.ypos + j][self.xpos + i] = Tile(self.curr_tetronimo.colour if arr[j][i] else NONE)

    def update(self):
        if self.new_tetronimo:
            self.add()
            self.new_tetronimo = False
        else:
            self.down()
            if self.stick_time <= 0:
                self.bake()
                self.stick_time = STICK_FRAMES
                self.new_tetronimo = True
        self.update_grid()

    def bake(self):
        for j in range(4):
            for i in range(4):
                if self.within_grid(i, j) and self.grid[self.ypos + j][self.xpos + i].colour != NONE:
                    self.grid[self.ypos + j][self.xpos + i].bake()
        self.check_gameover()
        self.clear_rows()
    
    def check_gameover(self):
        for tile in self.grid[1]:
            if tile.is_baked:
                return True
        return False

    def clear_rows(self):
        for j in range(GRID_HEIGHT):
            cleared = True
            for i in range(GRID_WIDTH):
                if not self.grid[j][i].is_baked:
                    cleared = False
                    break

            if cleared:
                self.grid.pop(j)
                self.grid.insert(0, [Tile(NONE)] * GRID_WIDTH)
    
    def reset(self):
        self.curr_tetronimo = None
        self.held_tetronimo = None
    
        self.update_speed = INITIAL_SPEED # number of frames before update
        self.stick_time = STICK_FRAMES

        for _ in range(GRID_HEIGHT):
            self.grid.append([Tile(NONE)] * GRID_WIDTH)
        
        self.add()
        self.update_grid()

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode([400, 600])

running = True
frames = 0
input_ticker = INPUT_SPEED

game = Game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if input_ticker == 0:
                input_ticker = INPUT_SPEED
                if event.key == pygame.K_LEFT:
                    game.left()
                if event.key == pygame.K_RIGHT:
                    game.right()

    screen.fill((144, 144, 144))

    if frames >= game.update_speed:
        game.update()
        frames = 0

    for j in range(GRID_HEIGHT - 2):
        for i in range(GRID_WIDTH):
            pygame.draw.rect(screen, game.grid[j + 2][i].colour, pygame.Rect(i * 25, j * 25, 25, 25))

    pygame.display.flip()
    
    frames += 1
    if input_ticker > 0:
        input_ticker -= 1
    clock.tick(FPS)

pygame.quit()