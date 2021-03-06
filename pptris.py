#!/usr/bin/env python3

#^^shebang for easy command lining^^

import tkinter as tk
import random

#set up global constants
PLAYFIELD_WIDTH = 10
PLAYFIELD_HEIGHT = 20

blooks = (
    ((1,1),
     (1,1)),

    ((1,0,0),
     (1,1,1),
     (0,0,0)),

    ((0,1,0),
     (1,1,1),
     (0,0,0)),

    ((0,0,1),
     (1,1,1),
     (0,0,0)),

    ((0,0,0,0),
     (1,1,1,1),
     (0,0,0,0),
     (0,0,0,0)),

    ((1,1,0),
     (0,1,1),
     (0,0,0)),

    ((0,1,1),
     (1,1,0),
     (0,0,0))
)

defaultPositions = ((4,0), (3,0), (3,0), (3,0), (3,0), (3,0), (3,0)) #offset for where each block starts

tileColours = ("black", "white")
#root needs to be global for some methods idk the best way to do this
scene = None

class Blook:
    def __init__(self, content, pos):
        self.segments = content
        self.position = [pos[0], pos[1]]

    def __str__(self):
        out = ""
        for s in self.segments:
            out += str(s) + "\n"
        return out[:-1]

    def rotateClockwise(self):
        #construct new array with [x,y] equal to old array [y, width - x - 1] (this is equivalent to a rotation about its centre)
        self.segments = [[self.segments[len(self.segments) - i - 1][j] for i in range(len(self.segments))] for j in range(len(self.segments))]

    def rotateAClockwise(self):
        #construct new array with [x,y] equal to old array [width - y - 1, x] (this is equivalent to a rotation about its centre)
        self.segments = [[self.segments[i][len(self.segments[0]) - 1 - j] for i in range(len(self.segments))] for j in range(len(self.segments))]
    
    def draw(self, canvas):
        #draw the playfield
        for i in range(len(self.segments)):
            for j in range(len(self.segments[i])):
                if self.segments[j][i]:
                    canvas.create_rectangle((self.position[0] + i) * 20 + 10, (self.position[1] + j) * 20 + 10,
                                            (self.position[0] + i) * 20 + 30, (self.position[1] + j) * 20 + 30, fill="white", tag='blook')
    def drawPos(self, canvas, pos):
        #draw the playfield
        for i in range(len(self.segments)):
            for j in range(len(self.segments[i])):
                if self.segments[j][i]:
                    canvas.create_rectangle((pos[0] + i) * 20 + 10, (pos[1] + j) * 20 + 10,
                                            (pos[0] + i) * 20 + 30, (pos[1] + j) * 20 + 30, fill="white", tag='blook')

class Scene:
    def __init__(self):
        self.frames = 0
        
        self.playfield = [[0 for i in range(PLAYFIELD_WIDTH)] for j in range(PLAYFIELD_HEIGHT)] #2D array 20x10
        self.selBlook = makeRandomBlock()
        self.storedBlook = makeRandomBlock()
        self.nextBlook = makeRandomBlock()

        self.root = tk.Tk() #create tkinter instance and canvas
        self.canvas = tk.Canvas(self.root, width=320, height=480)
        self.canvas.pack()

        self.root.bind("<KeyPress>", keydown)
        self.root.bind("<KeyRelease>", keyup)

        self.root.bind("<Left>", leftKey) #bind input keys
        self.root.bind("<Right>", rightKey)
        self.root.bind("<Down>", downKey)
        self.root.bind("<Up>", rotateClock)
        self.root.bind("<space>", spaceKey)
        self.root.bind("<x>", rotateClock)
        self.root.bind('<z>', rotateAClock)
        self.root.bind('<c>', hold)

        self.leftActive = 0
        self.rightActive = 0
        
    def start(self):
        self.root.after(16, update)
        self.root.mainloop()
    
    def reset(self):
        self.playfield = [[0 for i in range(PLAYFIELD_WIDTH)] for j in range(PLAYFIELD_HEIGHT)] #2D array 20x10

    def update(self):
        self.frames = (self.frames + 1) % 20 #update frames
        if self.frames == 0:
            if self.checkMove(0, 1): #checks if any blocks below selBlook
                self.selBlook.position[1] += 1 #continue moving down
            else:
                self.bake() #set block in place

    def clear(self):
        baseIndex = topIndex = PLAYFIELD_HEIGHT-1
        while baseIndex >= 0:
            layer = [0]*PLAYFIELD_WIDTH
            if topIndex >= 0:
                if [1] * PLAYFIELD_WIDTH == self.playfield[topIndex]:
                    print("full")
                    topIndex -= 1
                    continue
                layer = self.playfield[topIndex]
            print(baseIndex, topIndex)
            self.playfield[baseIndex] = layer
            baseIndex-=1
            topIndex-=1
                          
    def checkMove(self, xoff, yoff, rotate = "none"):
        sb = self.selBlook
        for y in range(len(sb.segments)):
            for x in range(len(sb.segments)):
                try:
                    if rotate == "none":
                        if sb.segments[y][x] and (self.playfield[y + sb.position[1] + yoff][x + sb.position[0] + xoff] or x + sb.position[0] + xoff < 0):
                            return False
                    if rotate == "clock":
                        if sb.segments[len(sb.segments) - x - 1][y] and (self.playfield[y + sb.position[1] + yoff][x + sb.position[0] + xoff] or x + sb.position[0] + xoff < 0):
                            return False
                    if rotate == "aclock":
                        if sb.segments[x][len(sb.segments) - y - 1] and (self.playfield[y + sb.position[1] + yoff][x + sb.position[0] + xoff] or x + sb.position[0] + xoff < 0):
                            return False
                except IndexError:
                    return False
        return True

    def bake(self):
        for y in range(len(self.selBlook.segments)):
            for x in range(len(self.selBlook.segments)):
                if self.selBlook.segments[y][x]:
                    self.playfield[y + self.selBlook.position[1]][x + self.selBlook.position[0]] = 1
        self.clear()
        self.selBlook = self.nextBlook
        self.nextBlook = makeRandomBlock()
        if not self.checkMove(0,0):
            self.reset()

    def left(self):
        if self.checkMove(-1, 0):
            self.selBlook.position[0] -= 1

    def right(self):
        if self.checkMove(1, 0):
            self.selBlook.position[0] += 1
    
    def rotate_clock(self):
        if self.checkMove(0, 0, "clock"):
            self.selBlook.rotateClockwise()
        elif self.checkMove(1, 0, "clock"):
            self.selBlook.position[0] += 1
            self.selBlook.rotateClockwise()
        elif self.checkMove(-1, 0, "clock"):
            self.selBlook.position[0] -= 1
            self.selBlook.rotateClockwise()
        elif self.checkMove(2, 0, "clock"):
            self.selBlook.position[0] += 2
            self.selBlook.rotateClockwise()
        elif self.checkMove(-2, 0, "clock"):
            self.selBlook.position[0] -= 2
            self.selBlook.rotateClockwise()
            

    def rotate_aclock(self):
        if self.checkMove(0, 0, "aclock"):
            self.selBlook.rotateAClockwise()
        elif self.checkMove(1, 0, "aclock"):
            self.selBlook.position[0] += 1
            self.selBlook.rotateAClockwise()
        elif self.checkMove(-1, 0, "aclock"):
            self.selBlook.position[0] -= 1
            self.selBlook.rotateAClockwise()
        elif self.checkMove(2, 0, "aclock"):
            self.selBlook.position[0] += 2
            self.selBlook.rotateAClockwise()
        elif self.checkMove(-2, 0, "aclock"):
            self.selBlook.position[0] -= 2
            self.selBlook.rotateAClockwise()
            
    def up(self): #rotate block clockwise
        None
    
    def down(self): #soft drop
        None

    def space(self): #hard drop
        while self.checkMove(0, 1):
            self.selBlook.position[1] += 1
        self.bake()

    def draw(self):
        self.canvas.delete("blook")
        self.drawPlayfield()
        self.selBlook.draw(self.canvas)
        self.storedBlook.drawPos(self.canvas, [11, 5])
        self.nextBlook.drawPos(self.canvas, [11, 1])
        self.canvas.update()

    def drawPlayfield(self):
        self.canvas.delete("playfield")
        for i in range(PLAYFIELD_HEIGHT): #draw to the size of the playfield
            for j in range(PLAYFIELD_WIDTH):
                #use tileColours array too choose the colour for the tile (branchless programming techiques boi)
                self.canvas.create_rectangle(j * 20 + 10, i * 20 + 10,
                                             j * 20 + 30, i * 20 + 30,
                                             fill=tileColours[self.playfield[i][j]], tag="playfield")

def makeRandomBlock():
    index = random.randint(0, 6)
    return Blook(blooks[index], defaultPositions[index])

def keydown(event):
    None

def keyup(event):
    None

def leftKey(event):
    scene.left()

def rightKey(event):
    scene.right()

def downKey(event):
    None

def upKey(event):
    None

def spaceKey(event):
    scene.space()
    
def rotateClock(event):
    scene.rotate_clock()

def rotateAClock(event):
    scene.rotate_aclock()

def hold(event):
    a = scene.nextBlook
    scene.nextBlook = scene.storedBlook
    scene.storedBlook = a

def update():
    scene.update()
    scene.draw()
    scene.root.after(20, update)  

#iff thing for easier unit testing
if __name__ == "__main__":
    scene = Scene()
    scene.start()





