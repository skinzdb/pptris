#include "inputOutput.h"

#define SDL_MAIN_HANDLED
#include <SDL2/SDL.h>

typedef struct {
    SDL_Window* wind;
} IOManager;

void* make_IOManager() {
    IOManager* ioMan = malloc(sizeof(IOManager));

    return ioMan;
}