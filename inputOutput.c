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

const uint32_t digitMap[10] = {0x6999996, 0x2622227, 0x699224F, 0x6916196, 0x2266AF2, 0xF8AD196, 0x698E996, 0xF922488, 0x6996996, 0x6997196};

#define numColours 2
const Colour colours[] = {{0,0,0}, {255,255,255}};
const Colour backgroundCol = {0x51, 0x51, 0x51};

#define NUM_AUDIO_TRACKS 8
typedef struct {
    bool playing;
    bool loop;
    int8_t* track_data;
    uint32_t track_length;
    uint32_t read_head;
} AudioTrack;

typedef struct {
    AudioTrack tracks[NUM_AUDIO_TRACKS];
    SDL_mutex* muts[NUM_AUDIO_TRACKS];
} AudioManager;

typedef struct {
    SDL_Window* wind;
    SDL_Surface* surf;
    uint_fast8_t keys;//0:right, 1:left, 2:antiClock, 3:clock, 4:store, 5:hardDrop
    uint_fast8_t keys_old;
    AudioManager audio;
} IOManager;

void intmalloc(uint32_t* arr, uint32_t n, uint32_t len) {
    for (int i = 0; i < len; i++) {
        arr[i] = n;
    }
}

void init_audio(AudioManager* audio);
void audio_player(void* audio, int8_t* buf, int length);

void* IOManager_create()
{
    if(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO)) {
        printf("bad init\n");
        exit(-1);
    }
    IOManager* ioMan = malloc(sizeof(IOManager));
    //setup screen
    ioMan->wind = SDL_CreateWindow("pptris", SDL_WINDOWPOS_UNDEFINED,
                                    SDL_WINDOWPOS_UNDEFINED, SCREEN_WIDTH, SCREEN_HEIGHT, 0);
    ioMan->surf = SDL_GetWindowSurface(ioMan->wind);
    uint32_t col = SDL_MapRGB(ioMan->surf->format, backgroundCol.r, backgroundCol.g, backgroundCol.b);
    intmalloc(ioMan->surf->pixels, col, SCREEN_WIDTH*SCREEN_HEIGHT);

    //initialize keyboard input
    ioMan->keys = 0;

    init_audio(&ioMan->audio);

    return ioMan;
}

void init_audio(AudioManager* audio)
{
    SDL_AudioSpec spec;
    spec.freq = 44100;
    spec.format = AUDIO_S8;
    spec.channels = 1;
    spec.samples = 128;
    spec.callback = audio_player;
    spec.userdata = audio;
    SDL_OpenAudio(&spec, NULL);

    for(int i = 0; i < NUM_AUDIO_TRACKS; ++i) {
        audio->muts[i] = SDL_CreateMutex();
        audio->tracks[i].playing = false;
        audio->tracks[i].track_data = NULL;
        audio->tracks[i].read_head = 0;
        audio->tracks[i].track_length = 0;
    }
	SDL_PauseAudio(0);
}

void get_key_state(IOManager* ioMan)
{
    ioMan->keys_old = ioMan->keys;
    ioMan->keys = 0;
    const Uint8 *kbState = SDL_GetKeyboardState(NULL);
    ioMan->keys |= kbState[SDL_SCANCODE_RIGHT];
    ioMan->keys |= kbState[SDL_SCANCODE_LEFT] << 1;
    ioMan->keys |= kbState[SDL_SCANCODE_Z] << 2;
    ioMan->keys |= kbState[SDL_SCANCODE_X] << 3;
    ioMan->keys |= kbState[SDL_SCANCODE_C] << 4;
    ioMan->keys |= kbState[SDL_SCANCODE_SPACE] << 5;
    //printf("%X %X\n", ioMan->keys_old, ioMan->keys);
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

bool IOManager_right_was_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys_old & 0x01;
}

bool IOManager_left_was_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys_old & 0x02;
}

bool IOManager_anticlockwise_was_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys_old & 0x04;
}

bool IOManager_clockwise_was_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys_old & 0x08;
}

bool IOManager_swap_was_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys_old & 0x10;
}

bool IOManager_hard_drop_was_pressed(void* _ioMan) 
{
    IOManager* ioMan = _ioMan;
    return ioMan->keys_old & 0x20;
}

void IOManager_draw_playfield(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour)
{
#ifdef PPDEBUG
    if(x >= PLAYFIELD_WIDTH || y >= PLAYFIELD_HEIGHT || colour >= numColours){
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

void drawDigit(void* _ioMan, uint_fast16_t x, uint_fast16_t y, uint_fast8_t digit) {
#ifdef PPDEBUG
    if(x >= SCREEN_WIDTH-10 || y >= SCREEN_HEIGHT - 14 || digit >= 10){
        printf("error IOManager_draw_next %li, %li, %i", x, y, digit);
        exit(-1);
    }
#endif
    IOManager* ioMan = _ioMan;
    uint32_t col = SDL_MapRGB(ioMan->surf->format, 255, 255, 255);
    uint32_t colBack = SDL_MapRGB(ioMan->surf->format, backgroundCol.r, backgroundCol.g, backgroundCol.b);
    uint32_t dig = digitMap[digit];
    for(int i = 12; i >= 0; i-=2) {
        for(int j = 6; j >= 0; j-=2) {
            uint32_t mcol = (dig&1) ? col : colBack;
            ((uint32_t*)ioMan->surf->pixels)[x + j +     SCREEN_WIDTH * (y + i    )] = mcol;
            ((uint32_t*)ioMan->surf->pixels)[x + j +     SCREEN_WIDTH * (y + i + 1)] = mcol;
            ((uint32_t*)ioMan->surf->pixels)[x + j + 1 + SCREEN_WIDTH * (y + i    )] = mcol;
            ((uint32_t*)ioMan->surf->pixels)[x + j + 1 + SCREEN_WIDTH * (y + i + 1)] = mcol;
            dig>>=1;
        }
    }
}

void IOManager_draw_score(void* _ioMan, uint32_t score)
{
    IOManager* ioMan = _ioMan;
    for(int i = 7; i >=0; --i) {
        drawDigit(ioMan, 220 + i*10, 10, score%10);
        score /= 10;
    }
    
}

void IOManager_draw_next(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour)
{
#ifdef PPDEBUG
    if(x >= 4 || y >= 4 || colour >= numColours){
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

void IOManager_draw_held(void* _ioMan, uint_fast8_t x, uint_fast8_t y, uint_fast8_t colour)
{   
#ifdef PPDEBUG
    if(x >= 4 || y >= 4 || colour >= numColours){
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

void IOManager_audio_load_track(void* _ioMan, int trackNum, int8_t* buffer, uint32_t length)
{
    IOManager* ioMan = _ioMan;
    SDL_LockMutex(ioMan->audio.muts[trackNum]);
    ioMan->audio.tracks[trackNum].track_data = buffer;
    ioMan->audio.tracks[trackNum].track_length = length;
    ioMan->audio.tracks[trackNum].read_head = 0;
    SDL_UnlockMutex(ioMan->audio.muts[trackNum]);
}

bool IOManager_audio_is_playing(void* _ioMan, int trackNum)
{
    IOManager* ioMan = _ioMan;
    SDL_LockMutex(ioMan->audio.muts[trackNum]);
    bool playing = ioMan->audio.tracks[trackNum].playing;
    SDL_UnlockMutex(ioMan->audio.muts[trackNum]);
    return playing;
}

void IOManager_audio_play(void* _ioMan, int trackNum, bool loop)
{
    IOManager* ioMan = _ioMan;
    SDL_LockMutex(ioMan->audio.muts[trackNum]);
    ioMan->audio.tracks[trackNum].playing = true;
    ioMan->audio.tracks[trackNum].loop = loop;
    SDL_UnlockMutex(ioMan->audio.muts[trackNum]);
}

void IOManager_audio_stop(void* _ioMan, int trackNum)
{
    IOManager* ioMan = _ioMan;
    SDL_LockMutex(ioMan->audio.muts[trackNum]);
    ioMan->audio.tracks[trackNum].playing = false;
    ioMan->audio.tracks[trackNum].read_head = 0;
    SDL_UnlockMutex(ioMan->audio.muts[trackNum]);
}

void IOManager_audio_pause(void* _ioMan, int trackNum)
{
    IOManager* ioMan = _ioMan;
    SDL_LockMutex(ioMan->audio.muts[trackNum]);
    ioMan->audio.tracks[trackNum].playing = false;
    SDL_UnlockMutex(ioMan->audio.muts[trackNum]);
}

void audio_player(void* _audio, int8_t* buf, int length) 
{
    AudioManager* audio = _audio;
    for (int i = 0; i < length; ++i) {
        buf[i] = 0;
    }
    for(int j = 0; j < NUM_AUDIO_TRACKS; ++j) {
        SDL_LockMutex(audio->muts[j]);
        for (int i = 0; i < length; ++i) {
            int sample = buf[i];
            if(audio->tracks[j].playing) {
                sample = audio->tracks[j].track_data[audio->tracks[j].read_head++];
                if(audio->tracks[j].read_head >= audio->tracks[j].track_length) {
                    if(audio->tracks[j].loop){
                        audio->tracks[j].read_head = 0;
                    }
                    else {
                        audio->tracks[j].playing = false;
                    }
                }
                sample = (sample > 127) ? 127 : sample;
                buf[i] = (sample < -128) ? -128 : sample;
            }
        }
        SDL_UnlockMutex(audio->muts[j]);

    }
    for (int i = 0; i < length; ++i) {
        printf("%i, ", buf[i]);
    }
    printf("\n");
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
