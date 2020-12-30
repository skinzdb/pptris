#include <stdint.h>

#define PLAYFIELD_WIDTH 10
#define PLAYFIELD_HEIGHT 20

typedef struct {
    uint_fast16_t* segments;
    int x;
    int y;
} Block;

uint_fast16_t* playfield[PLAYFIELD_HEIGHT];

Block sel_block;
Block next_block;
Block stored_block;

int main() {


    return 0;
}