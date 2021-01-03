#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define PLAYFIELD_WIDTH 10
#define PLAYFIELD_HEIGHT 20

typedef enum {
    NONE = 0,
    CLOCK = 1,
    A_CLOCK = -1
} Rotation;

typedef struct {
    int type;
    int rot;
    int x, y;
} Block;

void clear();
int check_move(int xoff, int yoff, Rotation rotate);
void update();
void random_block(Block b);
void left();
void right();
void rotate(Rotation rotation);

uint_fast8_t blocks[][4][4] = {
    {{0xC0, 0xC0, 0x00, 0x00}, // O
     {0xC0, 0xC0, 0x00, 0x00},
     {0xC0, 0xC0, 0x00, 0x00},
     {0xC0, 0xC0, 0x00, 0x00}
    },

    {{0x80, 0xE0, 0x00, 0x00}, // J
     {0x60, 0x40, 0x40, 0x00},
     {0x00, 0xE0, 0x20, 0x00},
     {0x40, 0x40, 0xC0, 0x00}
    },

    {{0x40, 0xE0, 0x00, 0x00}, // T
     {0x40, 0x60, 0x40, 0x00},
     {0x40, 0xC0, 0x40, 0x00},
     {0x40, 0xC0, 0x40, 0x00}
    },

    {{0x20, 0xE0, 0x00, 0x00}, // L
     {0x40, 0x40, 0x60, 0x00},
     {0x00, 0xE0, 0x80, 0x00},
     {0xC0, 0x40, 0x40, 0x00}
    },

    {{0x00, 0xF0, 0x00, 0x00}, // I
     {0x20, 0x20, 0x20, 0x20},
     {0x00, 0x00, 0xF0, 0x00},
     {0x40, 0x40, 0x40, 0x40}
    },

    {{0x60, 0x80, 0x00, 0x00}, // S
     {0x40, 0x60, 0x20, 0x00},
     {0x00, 0x60, 0xC0, 0x00},
     {0x80, 0xC0, 0x40, 0x00}
    },

    {{0xC0, 0x60, 0x00, 0x00}, // Z
     {0x20, 0x60, 0x40, 0x00},
     {0x00, 0xC0, 0x60, 0x00},
     {0x40, 0xC0, 0x20, 0x00}
    },
};

int defaultPositions[7][2] = {
    {4,0},
    {3,0},
    {3,0},
    {3,0},
    {3,0},
    {3,0},
    {3,0}
};

uint_fast16_t playfield[PLAYFIELD_HEIGHT] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};

Block sel_block;
Block next_block;
Block stored_block;

uint8_t frames;

void clear() {
    uint8_t base_index, top_index = PLAYFIELD_HEIGHT - 1;
    while (base_index >= 0) {
        uint_fast16_t layer = 0;
        if (top_index >= 0) {
            if (playfield[base_index] = 0xFFFF) { // full layer
                top_index--;
                continue;
            }
            layer = playfield[base_index];
        }
        playfield[base_index] = layer;
        base_index--;
        top_index--;
    }
}

int check_move(int xoff, int yoff, Rotation rotate) {
    for (int i = 0; i < 4; i++) {
        if (blocks[sel_block.type][sel_block.rot + rotate][i] & playfield[sel_block.y + yoff + i] || xoff < 0) {
            return 0;
            }
        }
}

void update() {
    frames = (frames + 1) % 20;
    if (frames == 0) {
        if (check_move(0, 1, NONE)) { 
            sel_block.y++;
        } else {
            bake();
        }
    }   
}

void bake() {
    for (int i = 0; i < 4; i++) {
        playfield[sel_block.y + i] |= blocks[sel_block.type][sel_block.rot][i];
    }
    sel_block = next_block;
    random_block(next_block);
    
    if (!check_move(0, 0, NONE)) {
        //game over
    }
}

void random_block(Block b) {
    b.type = rand() % 7;
    b.rot = 0;
    b.x = b.y = 0;
}

void left() {
    sel_block.x--;
}

void right() {
    sel_block.x++;
}

void down() {
    sel_block.y++;
}

void rotate(Rotation rotation) {
    sel_block.rot = (sel_block.rot + rotation) % 4;
}

void hard_drop() {
    for (; check_move(0, 1, NONE); sel_block.y++);
    bake();
}

int main() {
    frames = 0;

    random_block(sel_block);
    random_block(next_block);

    while (1) {
        update();
        delay(16);
    }

    return 0;
}