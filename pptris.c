#include <stdio.h>
#include <stdint.h>
#include "inputOutput.h"

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
void bake();
int check_move(int xoff, int yoff, Rotation rotate);
void update();
void random_block(Block* b);
void left();
void right();
void rotate(Rotation rotation);

// bits go from right to left so think you might need the low nibbles(unless youre doing something im not seeing)
const uint_fast8_t blocks[][4][4] = {
    {{0x03, 0x03, 0x00, 0x00}, // O
     {0x03, 0x03, 0x00, 0x00},
     {0x03, 0x03, 0x00, 0x00},
     {0x03, 0x03, 0x00, 0x00}
    },

    {{0x01, 0x07, 0x00, 0x00}, // J
     {0x06, 0x02, 0x02, 0x00},
     {0x00, 0x07, 0x04, 0x00},
     {0x02, 0x02, 0x03, 0x00}
    },

    {{0x02, 0x07, 0x00, 0x00}, // T
     {0x02, 0x06, 0x02, 0x00},
     {0x02, 0x03, 0x02, 0x00},
     {0x02, 0x03, 0x02, 0x00}
    },

    {{0x04, 0x07, 0x00, 0x00}, // L
     {0x02, 0x02, 0x06, 0x00},
     {0x00, 0x07, 0x01, 0x00},
     {0x03, 0x02, 0x02, 0x00}
    },

    {{0x00, 0x0F, 0x00, 0x00}, // I
     {0x04, 0x04, 0x04, 0x04},
     {0x00, 0x00, 0x0F, 0x00},
     {0x02, 0x02, 0x02, 0x02}
    },

    {{0x06, 0x01, 0x00, 0x00}, // S
     {0x02, 0x06, 0x04, 0x00},
     {0x00, 0x06, 0x03, 0x00},
     {0x01, 0x03, 0x02, 0x00}
    },

    {{0x03, 0x06, 0x00, 0x00}, // Z
     {0x04, 0x06, 0x02, 0x00},
     {0x00, 0x03, 0x06, 0x00},
     {0x02, 0x03, 0x04, 0x00}
    },
};

// a part of me wants bytes or uint_fast8_t but thats the bad person part of me
const int defaultPositions[7][2] = {
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
            if (playfield[base_index] == ((1<<PLAYFIELD_WIDTH) - 1)) { // full layer
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
        uint_fast8_t shape = blocks[sel_block.type][sel_block.rot + rotate][i];
        int ypos = sel_block.y + i;
        if(ypos >= PLAYFIELD_HEIGHT){
            if(shape){
                return 0;
            }
        }
        else {
            uint_fast16_t line = playfield[ypos];
            int offset = sel_block.x + xoff;
            if ((((line << 3) | 0x2004) >> (offset + 3)) & shape) {
                return 0;
            }
        }
    }
    return 1;
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
    random_block(&next_block);
    
    if (!check_move(0, 0, NONE)) {
        //game over
    }
}

void random_block(Block* b) {
    b->type = rand() % 7;
    b->rot = 0;
    b->x = b->y = 0;
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
    sel_block.rot = (sel_block.rot + rotation + 4) % 4; //negitive numbers and % are a pain in the ass
}

void hard_drop() {
    for (; check_move(0, 1, NONE); sel_block.y++); // think this is a line too low (unsure)
    bake();
}

int main2() {
    frames = 0;

    random_block(&sel_block);
    random_block(&next_block);

    while (1) {
        update();
        //delay(16);
    }
}

void * io_manager;
int8_t sawBuffer[64];
int8_t sawBuffer2[128];
int8_t sawBuffer3[256];
/**
 * setup to emulate arduino ide
 */
void setup() {
    io_manager = IOManager_create();
    IOManager_draw_score(io_manager, 12345678);
    for(int i = 0; i < PLAYFIELD_WIDTH; ++i) {
        for(int j = 0; j < PLAYFIELD_HEIGHT; ++j) {
            IOManager_draw_playfield(io_manager, i, j, 0);
        }
    }
    for(int i = 0; i < 4; ++i) {
        for(int j = 0; j < 4; ++j) {
            IOManager_draw_next(io_manager, i, j, 0);
            IOManager_draw_held(io_manager, i, j, 0);
        }
    }
    for(int i = 0; i < 256; i+=4) sawBuffer[i>>2] = i-128;
    for(int i = 0; i < 256; i+=2) sawBuffer2[i>>1] = i-128;
    for(int i = 0; i < 256; i+=1) sawBuffer3[i] = i-128;
    IOManager_audio_load_track(io_manager, 0, sawBuffer, 64);
    IOManager_audio_load_track(io_manager, 1, sawBuffer2, 128);
    IOManager_audio_load_track(io_manager, 2, sawBuffer3, 256);
}
/**
 * loop to emulate arduino ide
 * shouldnt be bool but os's need an exit
 */
void loop() {
    if(IOManager_anticlockwise_pressed(io_manager) && !IOManager_anticlockwise_was_pressed(io_manager)){
        IOManager_draw_playfield(io_manager, 0,0,1);
        IOManager_audio_play(io_manager, 0, true);
        IOManager_audio_play(io_manager, 1, true);
        IOManager_audio_play(io_manager, 2, true);
    }
    else if ((!IOManager_anticlockwise_pressed(io_manager)) && IOManager_anticlockwise_was_pressed(io_manager)){
        IOManager_draw_playfield(io_manager, 0,0,0);
        IOManager_audio_stop(io_manager, 0);
        IOManager_audio_stop(io_manager, 1);
        IOManager_audio_stop(io_manager, 2);
    }

    IOManager_process(io_manager);
}

