#!/usr/bin/env python3

#^^shebang for easy command lining^^

import tkinter as tk
import random

#set up global constants
PLAYFIELD_WIDTH = 10
PLAYFIELD_HEIGHT = 20

blooks = [
    [[1,1],
     [1,1]],

    [[1,0,0],
     [1,1,1],
     [0,0,0]],

    [[0,1,0],
     [1,1,1],
     [0,0,0]],

    [[1,0,0],
     [1,1,1],
     [0,0,0]],

    [[0,0,0,0],
     [1,1,1,1],
     [0,0,0,0],
     [0,0,0,0]],

    [[1,1,0],
     [0,1,1],
     [0,0,0]],

    [[0,1,1],
     [1,1,0],
     [0,0,0]]
]

defaultPositions = [(4,0), (3,0), (3,0), (3,0), (3,0), (3,0), (3,0)]

tileColours = ["black", "white"]
#root needs to be global for some methods idk the best way to do this
scene = None

class Blook:
    def __init__(self, content, pos):
        self.segments = content
        self.position = pos

    def __str__(self):
        out = ""
        for s in self.segments:
            out += str(s) + "\n"
        return out[:-1]

    def rotateClockwise(self):
        #cunstruct new array with [x,y] equal to old array [y, width - x - 1] (this is equivelent to a rotation about its center)
        self.segments = [[self.segments[len(self.segments) - i - 1][j] for i in range(len(self.segments))] for j in range(len(self.segments[0]))]

    def rotateAClockwise(self):
        #cunstruct new array with [x,y] equal to old array [width - y - 1, x] (this is equivelent to a rotation about its center)
        self.segments = [[self.segments[i][len(self.segments[0]) - 1 - j] for i in range(len(self.segments))] for j in range(len(self.segments[0]))]
    
    def draw(self, canvas):
        for i in range(len(self.segments)):
            for j in range(len(self.segments[i])):
                if self.segments[j][i]:
                    canvas.create_rectangle((self.position[0] + i) * 20 + 10, (self.position[1] + j) * 20 + 10,
                                            (self.position[0] + i) * 20 + 30, (self.position[1] + j) * 20 + 30, fill="white", tag='blook')

class Scene:
    def __init__(self):
        self.activeBlock = makeRandomBlock()
        self.playfield = [[0 for i in range(PLAYFIELD_WIDTH)] for j in range(PLAYFIELD_HEIGHT)] # 2D array 20x10
        self.sel_blook = makeRandomBlock()
        self.stored_blook = None
        self.next_blook = None

        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=320, height=480)
        self.canvas.pack()

        self.root.bind('<Left>', leftKey)
        self.root.bind('<Right>', rightKey)
        self.root.bind('<Up>', upKey)
        self.root.bind('<Down>', downKey)
        

    def start(self):
        self.root.after(20, update)
        self.root.mainloop()

    def update(self):
        print("update")
        print(self.activeBlock)
    def draw(self):
        self.draw_playfield()
        self.sel_blook.draw(self.canvas)
        self.canvas.update()
    def draw_playfield(self):
        self.canvas.delete('playfield')
        for i in range(PLAYFIELD_HEIGHT):#draw to the size of the play field not random constants
            col = None
            for j in range(PLAYFIELD_WIDTH):
                #use tileColours array too choose the colour for the tile (branchless programming techiques boi)
                self.canvas.create_rectangle(j * 20 + 10, i * 20 + 10,
                                             j * 20 + 30, i * 20 + 30,
                                             fill=tileColours[self.playfield[i][j]], tag='playfield')


def makeRandomBlock():
    index = random.randint(0, 6)
    return Blook(blooks[index], defaultPositions[index])

def leftKey(event):
    None

def rightKey(event):
    None

def upKey(event):
    None

def downKey(event):
    None

def update():
    scene.update()
    scene.draw()
    scene.root.after(20, update)  

#iff thing for easier unit testing
if __name__ == "__main__":
    scene = Scene()
    scene.start()





