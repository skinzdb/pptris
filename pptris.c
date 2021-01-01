#include <stdint.h>
#include <stdio.h>
#include "inputOutput.h"


typedef struct {
    uint_fast8_t* segments;
    int x;
    int y;
} Block;

uint_fast16_t* playfield[PLAYFIELD_HEIGHT];

Block sel_block;
Block next_block;
Block stored_block;

void * io_manager;

/**
 * setup to emulate arduino ide
 */
void setup() {
    io_manager = IOManager_create();
    IOManager_draw_score(io_manager, 499);
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
}
/**
 * loop to emulate arduino ide
 * shouldnt be bool but os's need an exit
 */
void loop() {
    if(IOManager_anticlockwise_pressed(io_manager)){
        IOManager_draw_playfield(io_manager, 0,0,1);
    }
    else {
        IOManager_draw_playfield(io_manager, 0,0,0);
    }
    IOManager_process(io_manager);

}


