#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#define PLAYFIELD_WIDTH 10
#define PLAYFIELD_HEIGHT 20
#define PPDEBUG

void* IOManager_create();
void IOManager_process(void* _ioMan);//need a better name
void IOManager_destroy(void* _ioMan);

bool IOManager_right_pressed(void* _ioMan);
bool IOManager_left_pressed(void* _ioMan);
bool IOManager_clockwise_pressed(void* _ioMan);
bool IOManager_anticlockwise_pressed(void* _ioMan);
bool IOManager_swap_pressed(void* _ioMan);
bool IOManager_hard_drop_pressed(void* _ioMan);

bool IOManager_right_was_pressed(void* _ioMan);
bool IOManager_left_was_pressed(void* _ioMan);
bool IOManager_clockwise_was_pressed(void* _ioMan);
bool IOManager_anticlockwise_was_pressed(void* _ioMan);
bool IOManager_swap_was_pressed(void* _ioMan);
bool IOManager_hard_drop_was_pressed(void* _ioMan);

void IOManager_draw_playfield(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour);
void IOManager_draw_score(void* _ioMan, uint32_t score);
void IOManager_draw_next(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour);
void IOManager_draw_held(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour);

void IOManager_audio_load_track(void* _ioMan, int trackNum, int8_t* buffer, uint32_t length);
bool IOManager_audio_is_playing(void* _ioMan, int trackNum);
void IOManager_audio_play(void* _ioMan, int trackNum, bool loop);
void IOManager_audio_stop(void* _ioMan, int trackNum);
void IOManager_audio_pause(void* _ioMan, int trackNum);