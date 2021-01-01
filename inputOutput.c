#include "inputOutput.h"

#include <SDL2/SDL.h>

#define SCREEN_WIDTH 310
#define SCREEN_HEIGHT 420
/*
0110
1001
1001
0111
0001
1001
0110
*/

typedef struct {
    uint8_t r, g, b;
} Colour;

const uint32_t digitMap[10] = {0x6999996, 0x2622227, 0x699224F, 0x6916196, 0x0266AF2, 0xF8AD196, 0x698E996, 0xF922488, 0x6996996, 0x6997296};

const Colour colours[] = {{0,0,0}, {255,255,255}};

typedef struct {
    SDL_Window* wind;
    SDL_Surface* surf;
    uint_fast8_t keys;//0:right, 1:left, 2:antiClock, 3:clock, 4:store, 5:hardDrop
} IOManager;

void get_key_state(IOManager* ioMan)
{
    ioMan->keys = 0;
    const Uint8 *kbState = SDL_GetKeyboardState(NULL);
    ioMan->keys |= kbState[SDL_SCANCODE_RIGHT];
    ioMan->keys |= kbState[SDL_SCANCODE_LEFT] << 1;
    ioMan->keys |= kbState[SDL_SCANCODE_Z] << 2;
    ioMan->keys |= kbState[SDL_SCANCODE_X] << 3;
    ioMan->keys |= kbState[SDL_SCANCODE_C] << 4;
    ioMan->keys |= kbState[SDL_SCANCODE_SPACE] << 5;
}

void* IOManager_create()
{
    if(SDL_Init(SDL_INIT_VIDEO)) {
        printf("bad init\n");
        fflush(stdout);//ensure the print goes out
    }
    IOManager* ioMan = malloc(sizeof(IOManager));
    ioMan->wind = SDL_CreateWindow("An SDL2 window", SDL_WINDOWPOS_UNDEFINED,
                                    SDL_WINDOWPOS_UNDEFINED, SCREEN_WIDTH, SCREEN_HEIGHT, 0);
    ioMan->surf = SDL_GetWindowSurface(ioMan->wind);
    memset(ioMan->surf->pixels, 0x51, SCREEN_WIDTH*SCREEN_HEIGHT*sizeof(uint32_t));

    ioMan->keys = 0;
    return ioMan;
}

void IOManager_process(void* _ioMan)
{
    IOManager* ioMan = _ioMan;

    SDL_Event event;
    while (SDL_PollEvent(&event))
    {
        if (event.type == SDL_QUIT) {
            IOManager_destroy(ioMan);
            exit(0);
        }
    }

    get_key_state(ioMan);
    SDL_UpdateWindowSurface(ioMan->wind);
}

void IOManager_destroy(void* _ioMan)
{
    IOManager* ioMan = _ioMan;
    
    SDL_DestroyWindow(ioMan->wind);

    free(ioMan);
}

bool IOManager_right_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys & 0x01;
}

bool IOManager_left_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys & 0x02;
}

bool IOManager_anticlockwise_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys & 0x04;
}

bool IOManager_clockwise_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys & 0x08;
}

bool IOManager_swap_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys & 0x10;
}

bool IOManager_hard_drop_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys & 0x20;
}

void IOManager_draw_playfield(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour)
{
#ifdef PPDEBUG
    if(x >= PLAYFIELD_WIDTH || y >= PLAYFIELD_HEIGHT || colour > 1){
        printf("error IOManager_draw_next %i, %i, %i", x, y, colour);
        exit(-1);
    }
#endif
    IOManager* ioMan = _ioMan;
    uint32_t col = SDL_MapRGB(ioMan->surf->format, colours[colour].r, colours[colour].g, colours[colour].b);
    uint32_t colBlack = SDL_MapRGB(ioMan->surf->format, 0, 0, 0);
    int startx = 10+x*20;
    int starty = 10+y*20;
    for (int i = 1; i < 20; ++i) {
        for (int j = 1; j < 20; ++j) {
            ((uint32_t*)ioMan->surf->pixels)[startx + i + SCREEN_WIDTH * (starty + j)] = col;
        }
    }
    for (int i = 0; i < 20; ++i) {
            ((uint32_t*)ioMan->surf->pixels)[startx + i + SCREEN_WIDTH * (starty)] = colBlack;
    }
    for (int i = 1; i < 20; ++i) {
            ((uint32_t*)ioMan->surf->pixels)[startx + SCREEN_WIDTH * (starty + i)] = colBlack;
    }
}
void IOManager_draw_score(void* _ioMan, uint32_t score)
{
    //IOManager* ioMan = _ioMan;
    //uint32_t col = SDL_MapRGB(ioMan->surf->format, 255, 255, 255);
    //uint32_t colBlack = SDL_MapRGB(ioMan->surf->format, 0, 0, 0);
    
}
void IOManager_draw_next(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour)
{
#ifdef PPDEBUG
    if(x >= 4 || y >= 4 || colour > 1){
        printf("error IOManager_draw_next %i, %i, %i", x, y, colour);
        exit(-1);
    }
#endif
    IOManager* ioMan = _ioMan;
    uint32_t col = SDL_MapRGB(ioMan->surf->format, colours[colour].r, colours[colour].g, colours[colour].b);
    uint32_t colBlack = SDL_MapRGB(ioMan->surf->format, 0, 0, 0);
    int startx = 220+x*20;
    int starty = 30+y*20;
    for (int i = 0; i < 20; ++i) {
        for (int j = 0; j < 20; ++j) {
            ((uint32_t*)ioMan->surf->pixels)[startx + x + SCREEN_WIDTH * (starty + j)] = col;
        }
    }
    for (int i = 0; i < 20; ++i) {
            ((uint32_t*)ioMan->surf->pixels)[startx + i + SCREEN_WIDTH * (starty)] = colBlack;
    }
    for (int i = 1; i < 20; ++i) {
            ((uint32_t*)ioMan->surf->pixels)[startx + SCREEN_WIDTH * (starty + i)] = colBlack;
    }
}
void IOManager_draw_held(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour)
{   
#ifdef PPDEBUG
    if(x >= 4 || y >= 4 || colour > 1){
        printf("error IOManager_draw_held %i, %i, %i", x, y, colour);
        exit(-1);
    }
#endif
    IOManager* ioMan = _ioMan;
    uint32_t col = SDL_MapRGB(ioMan->surf->format, colours[colour].r, colours[colour].g, colours[colour].b);
    uint32_t colBlack = SDL_MapRGB(ioMan->surf->format, 0, 0, 0);
    int startx = 220+x*20;
    int starty = 120+y*20;
    for (int i = 1; i < 20; ++i) {
        for (int j = 1; j < 20; ++j) {
            ((uint32_t*)ioMan->surf->pixels)[startx + i + SCREEN_WIDTH * (starty + j)] = col;
        }
    }
    for (int i = 0; i < 20; ++i) {
            ((uint32_t*)ioMan->surf->pixels)[startx + i + SCREEN_WIDTH * (starty)] = colBlack;
    }
    for (int i = 1; i < 20; ++i) {
            ((uint32_t*)ioMan->surf->pixels)[startx + SCREEN_WIDTH * (starty + i)] = colBlack;
    }
}



//setup, loop and main for opetating system versions
void setup();
bool loop();

int main(int iargs, char** vargs) {
    setup();
    while(true) {
        loop();
    };
}
