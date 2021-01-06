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
void random_block(Block* b);
void left();
void right();
void rotate(Rotation rotation);
void draw_sel();
void draw_next();
void draw_store();



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
     {0x00, 0x07, 0x02, 0x00},
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

    {{0x06, 0x03, 0x00, 0x00}, // S
     {0x02, 0x06, 0x04, 0x00},
     {0x00, 0x06, 0x03, 0x00},
     {0x01, 0x03, 0x02, 0x00}
    },

    {{0x03, 0x06, 0x00, 0x00}, // Z
     {0x04, 0x06, 0x02, 0x00},
     {0x00, 0x03, 0x06, 0x00},
     {0x02, 0x03, 0x01, 0x00}
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

void * io_manager;
int8_t sawBuffer[64];
int8_t sawBuffer2[128];
int8_t sawBuffer3[256];

uint_fast16_t playfield[PLAYFIELD_HEIGHT] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};

Block sel_block;
Block next_block;
Block stored_block;

uint8_t frames;
uint_fast32_t left_time, right_time, clock_time, aclock_time, h_drop_time, swap_time, s_drop_time;
uint32_t score;

void clear() {
    int8_t base_index = PLAYFIELD_HEIGHT - 1;
    int8_t top_index = PLAYFIELD_HEIGHT - 1;
    int clearedLines = 0;
    while (base_index >= 0) {
        uint_fast16_t layer = 0;
        if (top_index >= 0) {
            if (playfield[top_index] == ((1<<PLAYFIELD_WIDTH) - 1)) { // full layer
                top_index--;
                clearedLines++;
                continue;
            }
            layer = playfield[top_index];
        }
        playfield[base_index] = layer;
        base_index--;
        top_index--;
    }
    score += clearedLines*clearedLines*10;
    IOManager_draw_score(io_manager, score);
}

int check_move(int xoff, int yoff, Rotation rotate) {
    printf("checkMove1\n");
    for (int i = 0; i < 4; i++) {
        uint_fast8_t shape = blocks[sel_block.type][(sel_block.rot + rotate+4)%4][i];
        int ypos = sel_block.y + i + yoff;
        if(ypos >= PLAYFIELD_HEIGHT){
            if(shape){
                printf("checkMove2\n");
                return 0;
            }
        }
        else {
            uint_fast16_t line = playfield[ypos];
            int offset = sel_block.x + xoff;
            if ((((line << 3) | 0x2004) >> (offset + 3)) & shape) {
                printf("checkMove3\n");
                return 0;
            }
        }
    }
    printf("checkMove4\n");
    return 1;
}

void bake() {
    for (int i = 0; i < 4; i++) {
        if(blocks[sel_block.type][sel_block.rot%4][i]) {
            playfield[sel_block.y + i] |= (blocks[sel_block.type][sel_block.rot%4][i] << (sel_block.x+2)) >> 2;
            printf("line %02d - %03lX\n", sel_block.y + i, playfield[sel_block.y + i]);
        }
    }

    sel_block = next_block;
    random_block(&next_block);
    
    clear();

    if (!check_move(0, 0, NONE)) {
        memset(playfield, 0, sizeof(playfield));
        score = 0;
    }
    

}

void random_block(Block* b) {
    b->type = rand() % 7;
    b->rot = 0;
    b->x = defaultPositions[b->type][0];
    b->y = 0;
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

void rotate_clock() {
    if (check_move(0, 0, CLOCK)) {
        rotate(CLOCK);
    } else if (check_move(1, 0, CLOCK)) {
        sel_block.x += 1;
        rotate(CLOCK);
    } else if (check_move(-1, 0, CLOCK)) {
        sel_block.x -= 1;
        rotate(CLOCK);
    } else if (check_move(2, 0, CLOCK)) {
        sel_block.x += 2;
        rotate(CLOCK);
    } else if (check_move(-2, 0, CLOCK)) {
        sel_block.x -= 2;
        rotate(CLOCK);
    }
}

void rotate_a_clock() {
    if (check_move(0, 0, A_CLOCK)) {
        rotate(A_CLOCK);
    } else if (check_move(1, 0, A_CLOCK)) {
        sel_block.x += 1;
        rotate(A_CLOCK);
    } else if (check_move(-1, 0, A_CLOCK)) {
        sel_block.x -= 1;
        rotate(A_CLOCK);
    } else if (check_move(2, 0, A_CLOCK)) {
        sel_block.x += 2;
        rotate(A_CLOCK);
    } else if (check_move(-2, 0, A_CLOCK)) {
        sel_block.x -= 2;
        rotate(A_CLOCK);
    }
}

void hard_drop() {
    ppf("hard1\n");
    for (; check_move(0, 1, NONE); sel_block.y++);
    bake();
    ppf("hard2\n");
}

void draw_sel()
{
    for(int i = 0; i < 4; ++i) {
        for(int j = 0; j < 4; ++j) {
            if((blocks[sel_block.type][sel_block.rot%4][i]>>j)&1){
                IOManager_draw_playfield(io_manager, sel_block.x + j, sel_block.y + i, 1);
            }
        }
    }
}

void draw_next()
{
    for(int i = 0; i < 4; ++i) {
        for(int j = 0; j < 4; ++j) {
            IOManager_draw_next(io_manager, j, i, (blocks[next_block.type][next_block.rot%4][i]>>j)&1);
        }
    }
}

void draw_store()
{
    for(int i = 0; i < 4; ++i) {
        for(int j = 0; j < 4; ++j) {
            IOManager_draw_held(io_manager, j, i, (blocks[stored_block.type][stored_block.rot%4][i]>>j)&1);
        }
    }
}



void draw()
{
    draw_store();
    draw_next();
    for(int i = 0; i < PLAYFIELD_HEIGHT; ++i){
        uint_fast16_t line = playfield[i];
        for(int j = 0; j < PLAYFIELD_WIDTH; ++j){
            IOManager_draw_playfield(io_manager, j, i, line&1);
            line >>= 1;
        }
    }
    draw_sel();
}

void handle_input()
{
    left_time   = (left_time+1)   * IOManager_left_pressed(io_manager);
    right_time  = (right_time+1)  * IOManager_right_pressed(io_manager);
    clock_time  = (clock_time+1)  * IOManager_clockwise_pressed(io_manager);
    aclock_time = (aclock_time+1) * IOManager_anticlockwise_pressed(io_manager);
    swap_time   = (swap_time+1)   * IOManager_swap_pressed(io_manager);
    h_drop_time = (h_drop_time+1) * IOManager_hard_drop_pressed(io_manager);

    if(left_time && (left_time+9)/10 != (left_time+8)/10 && check_move(-1, 0, NONE)) {
        sel_block.x--;
    }
    if(right_time && (right_time+9)/10 != (right_time+8)/10 && check_move(1, 0, NONE)) {
        sel_block.x++;
    }

    if(clock_time && (clock_time+9)/10 != (clock_time+8)/10) {
        rotate_clock();
    }
    if(aclock_time && (aclock_time+9)/10 != (aclock_time+8)/10) {
        rotate_a_clock();
    }

    if(h_drop_time && (h_drop_time+9)/10 != (h_drop_time+8)/10) {
        hard_drop();
    }

    if(swap_time && (swap_time+9)/10 != (swap_time+8)/10) {
        Block b = stored_block;
        stored_block = next_block;
        next_block = b;
    }
}

/**
 * setup to emulate arduino ide
 */
void setup() {
    io_manager = IOManager_create();
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

    frames = 0;
    score = 0;
    left_time = right_time = clock_time = aclock_time = h_drop_time = swap_time = s_drop_time = 0;

    printf("random1\n");
    random_block(&sel_block);
    random_block(&next_block);
    printf("random1\n");
    draw();
    IOManager_draw_score(io_manager, score);
}
/**
 * loop to emulate arduino ide
 * shouldnt be bool but os's need an exit
 */
void loop() {
    //printf("loop\n");
    frames = (frames + 1) % 20;
    handle_input();
    if (frames == 0) {
        if (check_move(0, 1, NONE)) { 
            sel_block.y++;
        } else {
            bake();
            ppf("bake\n");
        }
        printf("doodle\n");
    }   
    draw();//optimize drawing may be necesary
    IOManager_process(io_manager);
}

