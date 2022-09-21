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
L_GREY = (128, 128, 128)
D_GREY = (32, 32, 32)
WHITE  = (255, 255, 255)
RED    = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN  = (0, 255, 0)
L_BLUE = (0, 255, 255)
D_BLUE = (0, 0, 255)
PURPLE = (139, 0, 139)

COLOUR_MAP = {  # Instead of using a switch statement, made a map between a colour and its value in the grid
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
        self.data = data # List of four 16-bit integers, one to store each rotation of the tetronimo 
                         # Each integer is akin to a 4x4 grid where 0 = blank space, 1 = tetronimo tile. Every group of 4 bits represents a row. The 4 MSBs are the first row.
        # Example of L tetronimo in its initial rotation:
        # | 0, 0, 0, 0 |          
        # | 0, 0, 1, 0 |    ==> 0x02E0
        # | 1, 1, 1, 0 |
        # | 0, 0, 0, 0 |

TETRONIMOES = [
    Tetronimo("O", YELLOW, [0x0660, 0x0660, 0x0660, 0x0660]),
    Tetronimo("J", D_BLUE, [0x08E0, 0x0644, 0x00E2, 0x044C]), 
    Tetronimo("L", ORANGE, [0x02E0, 0x0446, 0x00E8, 0x0C44]), 
    Tetronimo("T", PURPLE, [0x04E0, 0x0464, 0x00E4, 0x04C4]),  
    Tetronimo("S", GREEN,  [0x06C0, 0x0462, 0x006C, 0x08C4]), 
    Tetronimo("Z", RED,    [0x0C60, 0x0264, 0x00C6, 0x04C8]), 
    Tetronimo("I", L_BLUE, [0x0F00, 0x2222, 0x00F0, 0x4444]), 
]

JLTSZ_WALL_KICKS = [ # If a tetronimo gets rotated outside the playing field, try and 'kick' it back into a legal position using these offsets
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
    next_tetronimos = []
    held_tetronimo = None
  
    xpos = START_POS[0]
    ypos = START_POS[1]
    rotation = 0

    update_speed = INITIAL_SPEED # Number of frames before update
    stick_time = STICK_FRAMES # Number of frames before tetronimo 'sticks' to the surface it is touching below

    new_tetronimo = False # Flag to wait an update cycle before spawning new tetronimo
    has_stored = False
    gameover = False

    grid = []       # Grid that stores colour information for tetronimos and position of curr_tetronimo
                    # Each row is a 30-bit (stored as 32 but 2 MSBs aren't used) integer, each 3-bit chunk is a tile
                    # LSB represents the left side of the screen
                    # 0b000 = empty tile, 0b001-0b111 = colours for each of the 7 tetronimos
    baked_grid = [] # Grid that contains tiles that have been placed/'baked'
                    # 0b000 = unbaked tile, 0b111 = baked tile

    def __init__(self):
        self.grid = [0] * GRID_HEIGHT # Initialise both grids
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
        if self.curr_tetronimo != None:
            self.ypos += self.get_gap()
            self.bake()
            self.add()
            self.update_grid()

    def rotate(self, direction=CLOCKWISE):
        if self.curr_tetronimo == None:
            return

        wall_kicks = I_WALL_KICKS if self.curr_tetronimo.name == "I" else JLTSZ_WALL_KICKS  # Choose appropriate wall kicks, I is a special case
   
        for x, y in wall_kicks[self.rotation]: # If rotation is an invalid move, try and kick it into a legal position
            if self.check_move(direction * x, direction * y, direction): 
                self.xpos += direction * x
                self.ypos += direction * y
                self.rotation = (self.rotation + direction) % 4
                break
        self.update_grid()

    def store(self):
        if not self.has_stored:
            self.has_stored = True

            tmp = self.curr_tetronimo
            self.curr_tetronimo = self.held_tetronimo
            self.held_tetronimo = tmp

            if self.curr_tetronimo == None:
                self.add()
            else: 
                self.xpos = START_POS[0]
                self.ypos = START_POS[1] 
                self.rotation = 0
                self.stick_time = STICK_FRAMES
                
                if self.curr_tetronimo.name == "I": # Default spawn for I is off-screen so move it down by one
                    self.ypos += 1   
            self.update_grid()

    def get_tile(self, x, y):
        return (self.grid[y] >> (x * 3)) & 7 # 3-bit chunk so move in multiples of 3 (hence x * 3). Only select that chunk (hence & 7)

    def get_baked_tile(self, x, y):
        return (self.baked_grid[y] >> (x * 3)) & 7 

    def is_filled(self, tetronimo, x, y, rot): # Is the tile within the tetronimo data filled or empty (not related to the grid)
        return (tetronimo.data[rot] >> (15 - 4 * y - x)) & 1

    def get_gap(self): # Get distance between tile's current position and where it can legally be baked
        yoff = 0
        while self.check_move(0, yoff + 1):
            yoff += 1
        return yoff

    def check_move(self, x, y, rot_direction=0): # Check move doesn't go off-screen and doesn't overlap baked tiles
        if self.curr_tetronimo == None:
            return False
        rot = (self.rotation + rot_direction) % 4
        for j in range(4):
            for i in range(4):
                if (not self.within_grid(self.xpos + x + i, self.ypos + y + j) or self.get_baked_tile(self.xpos + x + i, self.ypos + y + j)) and self.is_filled(self.curr_tetronimo, i, j, rot):
                    return False
        return True
        
    def within_grid(self, x, y):
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

    def add(self):  # Spawn new tetronimo at top of screen
        if self.gameover:
            return

        self.xpos = START_POS[0]
        self.ypos = START_POS[1] 
        self.rotation = 0
        self.stick_time = STICK_FRAMES

        self.next_tetronimos.append(random.choice(TETRONIMOES))
        self.curr_tetronimo = self.next_tetronimos.pop(0)
        if self.curr_tetronimo.name == "I": # Default spawn for I is off-screen so move it down by one
            self.ypos += 1   

        for i in range(GRID_WIDTH): # If newly spawned piece is blocked out, move it up by one
            if self.get_tile(i, 2) & self.get_baked_tile(i, 2) > 0:
                self.ypos -= 1
                break

    def update_grid(self):
        # Only preserve baked tiles, bitwise AND will remove everything else
        for j in range(GRID_HEIGHT):
           self.grid[j] &= self.baked_grid[j] 

        # Encode position of curr_tetronimo into the grid
        if self.curr_tetronimo != None: 
            for j in range(4):
                for i in range(4):
                    if self.within_grid(self.xpos + i, self.ypos + j): # If tiles go outside of the grid, don't care about them
                        data = COLOUR_MAP[self.curr_tetronimo.colour] if self.is_filled(self.curr_tetronimo, i, j, self.rotation) else COLOUR_MAP[NONE]
                        self.grid[self.ypos + j] |= data << ((self.xpos + i) * 3) 
                
    def update(self, frames):
        if not self.gameover:
            if frames >= self.update_speed: # Once certain number of frames reached, perform update
                if self.new_tetronimo:
                    self.add()
                    self.new_tetronimo = False
                else:
                    if self.check_move(0, 1):
                        self.down()
                self.update_grid()
                frames = 0
            
            if not self.check_move(0, 1): # This happens on every frame curr_tetronimo is sticking to tiles below it
                self.stick_time -= 1

            if self.stick_time <= 0 and not self.new_tetronimo and not self.check_move(0, 1):
                self.bake()
                self.new_tetronimo = True

        return frames 

    def bake(self):
        for j in range(4):
            for i in range(4):
                if self.within_grid(self.xpos + i, self.ypos + j) and not self.get_baked_tile(self.xpos + i, self.ypos + j) and self.is_filled(self.curr_tetronimo, i, j, self.rotation):
                    self.baked_grid[self.ypos + j] |= 7 << ((self.xpos + i) * 3)
        self.update_grid() # Update grid to add final position of curr_tetronimo
        self.curr_tetronimo = None
        self.has_stored = False
        self.gameover = self.check_gameover() 
        if not self.gameover: # Don't bother clearing rows if it's game over
            self.clear_rows()
    
    def check_gameover(self):
        return self.baked_grid[1] > 0 # If the first off-screen row has baked tile inside it then it's gameover

    def clear_rows(self):
        for j in range(GRID_HEIGHT): # Not the most efficient way (O(N^2)) but it's simple
            if self.baked_grid[j] == 0x3FFFFFFF: # 0b00111111111111111111111111111111
                self.grid.pop(j)    
                self.grid.insert(0, 0)
                self.baked_grid.pop(j)
                self.baked_grid.insert(0, 0)
        self.update_grid()
    
    def reset(self):
        self.next_tetronimos.clear()
        self.next_tetronimos.append(random.choice(TETRONIMOES))
        self.curr_tetronimo = None
        self.held_tetronimo = None

        self.new_tetronimo = False 
        self.has_stored = False
        self.gameover = False
    
        self.update_speed = INITIAL_SPEED
        self.stick_time = STICK_FRAMES

        for j in range(GRID_HEIGHT):
            self.grid[j] = 0
            self.baked_grid[j] = 0
        
        self.add()
        self.update_grid()

def draw_rect(screen, left, top, width, height, fill, border=NONE, border_width=0): # Helper function to draw rects with borders
    pygame.draw.rect(screen, border, pygame.Rect(left, top, width, height))
    pygame.draw.rect(screen, fill, pygame.Rect(left + border_width, top + border_width, width - border_width, height - border_width))

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode([400, 550])
pygame.display.set_caption('Tetris')

icon = pygame.Surface((48, 48))
pygame.draw.rect(icon, PURPLE, pygame.Rect(16, 16, 16, 16))
for i in range(3):
    pygame.draw.rect(icon, PURPLE, pygame.Rect(i * 16, 32, 16, 16))

pygame.display.set_icon(icon)

gameover_font = pygame.font.SysFont(None, 48)
gameover_img = gameover_font.render("GAME OVER", True, WHITE)
heading_font = pygame.font.SysFont(None, 32)
next_img = heading_font.render("NEXT", True, WHITE)
held_img = heading_font.render("HELD", True, WHITE)
label_font = pygame.font.SysFont(None, 20)
restart_img = label_font.render("PRESS [R] TO RESTART", True, WHITE)

ghost_img = pygame.Surface((25, 25), pygame.SRCALPHA)  # Contains a flag telling pygame that the Surface is per-pixel alpha
ghost_img.set_alpha(96)

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
                game.rotate(CLOCKWISE)
            if event.key == pygame.K_z:
                game.rotate(ANTICLOCKWISE)
            if event.key == pygame.K_LEFT:
                game.left()
                lr_pressed = True
            if event.key == pygame.K_RIGHT:
                game.right()
                lr_pressed = True
            if event.key == pygame.K_SPACE:
                game.hard_down()
            if event.key == pygame.K_c:
                game.store()
            if event.key == pygame.K_r:
                if game.gameover:
                    game.reset()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                lr_pressed = False
                lr_delay = LR_DELAY

    keys = pygame.key.get_pressed() # This method of getting key input allows for holding down
    if input_delay == 0: # Once input delay has counted down to zero
        input_delay = INPUT_DELAY
        if lr_delay == 0: # Start moving left/right fast after left/right key has been held down for lr_delay frames
            if keys[pygame.K_LEFT]:
                game.left()
            if keys[pygame.K_RIGHT]:
                game.right()
        if keys[pygame.K_DOWN]:
            game.down()

    screen.fill(D_GREY)
    frames = game.update(frames)

    for j in range(GRID_HEIGHT - 2):
        for i in range(GRID_WIDTH):
            fill = list(COLOUR_MAP.keys())[game.get_tile(i, j + 2)] # Offset by 2 as there are two rows of hidden tiles at the top of the screen
            if game.gameover:
                fill = NONE if fill == NONE else L_GREY # Turn all tiles grey if game over
            draw_rect(screen, i * 25, j * 25, 25, 25, fill, D_GREY, 1 if fill == NONE else 0)

            # #debug
            # phil = L_GREY if game.get_baked_tile(i, j+2) > 0 else NONE
            # draw_rect(screen, i * 10 + 275, j * 10, 10, 10, phil)
    
    if game.curr_tetronimo != None:
        yoff = game.get_gap()  # Draw ghost tetronimo (where tetronimo would be placed if it were hard dropped)
        for j in range(4): 
            for i in range(4):
                if game.is_filled(game.curr_tetronimo, i, j, game.rotation):
                    pygame.draw.rect(ghost_img, game.curr_tetronimo.colour, ghost_img.get_rect(), 25)
                    screen.blit(ghost_img, ((game.xpos + i) * 25, (game.ypos + yoff + j - 2) * 25))

    screen.blit(next_img, (275, 20))
    offset = 50
    for t in game.next_tetronimos:  # Draw upcoming tetronimoes to the side
        left_adj = -1 if t.name == "O" else 0
        for j in range(4):
            for i in range(4):
                if game.is_filled(t, i, j, 0):
                    draw_rect(screen, 275 + (i + left_adj) * 25, offset + j * 25, 25, 25, t.colour)
        offset += 100

    screen.blit(held_img, (275, 20 + offset))
    if game.held_tetronimo != None:
        left_adj = -1 if game.held_tetronimo == "O" else 0
        for j in range(4):
            for i in range(4):
                if game.is_filled(game.held_tetronimo, i, j, 0):
                    draw_rect(screen, 275 + (i + left_adj) * 25, 45 + offset + j * 25, 25, 25, game.held_tetronimo.colour)

    if game.gameover:
        draw_rect(screen, 0, 225, 250, 60, NONE)
        screen.blit(gameover_img, (25, 225))
        screen.blit(restart_img, (25, 260))

    pygame.display.flip()
    
    frames += 1 # Update frame and delay counters
    if input_delay > 0:
        input_delay -= 1
    if lr_pressed and lr_delay > 0:
        lr_delay -= 1
    clock.tick(FPS)

pygame.quit()