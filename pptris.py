import tkinter as tk
import random

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

class Blook:
    def init(self, content = []):
        self.segments = content

    def print(self):
        for s in self.segments:
            print(s)

    def rotateClockwise(self):
        self.segments = [[self.segments[len(self.segments) - i - 1][j] for i in range(len(self.segments))] for j in range(len(self.segments[0]))]

    def rotateAClockwise(self):
        self.segments = [[self.segments[i][len(self.segments[0]) - 1 - j] for i in range(len(self.segments))] for j in range(len(self.segments[0]))]

b = Blook(blooks[random.randint(0, 6)])

sel_blook = None
stored_blook = None
next_blook = None

playfield = [[0 for i in range(10)] for j in range(20)] # 2D array 20x10

blooks = [
    [[1,1],
     [1,1]],

canvas = tk.Canvas(root, width=320, height=480)
canvas.pack()

def leftKey(event):
    None

def rightKey(event):
    None

def upKey(event):
    None

def downKey(event):
    None

root.bind('<Left>', leftKey)
root.bind('<Right>', rightKey)
root.bind('<Up>', upKey)
root.bind('<Down>', downKey)

def draw_playfield():
    canvas.delete('playfield')
    for i in range(20):
        col = None
        for j in range(10):
            if playfield[i][j] == 1:
                col = 'black'
            else:
                col = 'white'
            canvas.create_rectangle(j * 20 + 10, i * 20 + 10, j * 20 + 30, i * 20 + 30, fill=col, tag='playfield')
    canvas.update()

def update():
    draw_playfield()
    root.after(20, update)    

root.after(20, update)

root.mainloop()





