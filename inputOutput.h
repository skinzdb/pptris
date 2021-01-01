#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#define X86

void* IOManager_create();
void IOManager_process(void* _ioMan);//need a better name
void IOManager_destroy(void* _ioMan);

bool IOManager_right_pressed(void* _ioMan);
bool IOManager_left_pressed(void* _ioMan);
bool IOManager_clockwise_pressed(void* _ioMan);
bool IOManager_anticlockwise_pressed(void* _ioMan);
bool IOManager_swap_pressed(void* _ioMan);
bool IOManager_hard_drop_pressed(void* _ioMan);

void IOManager_draw_playfield(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour);
void IOManager_draw_score(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint32_t score);
void IOManager_draw_next(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour);
void IOManager_draw_held(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour);