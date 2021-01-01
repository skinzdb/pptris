#include <stdint.h>
#include <stdio.h>
#include "inputOutput.h"

#define PLAYFIELD_WIDTH 10
#define PLAYFIELD_HEIGHT 20

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


