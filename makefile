CC = gcc
FLAGS = -O3 -Wall -lSDL2 -flto
LINKER_FLAGS = -lSDL2 -flto

pptris: pptris.o inputOutput.o
	$(CC) $(LINKER_FLAGS) -o pptris pptris.o inputOutput.o -lSDL2

pptris.o: pptris.c
	$(CC) $(FLAGS) pptris.c -c -o pptris.o

inputOutput.o: inputOutput.c
	$(CC) $(FLAGS) inputOutput.c -c -o inputOutput.o
