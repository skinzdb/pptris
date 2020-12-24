import tkinter as tk
import pygame, random

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
    def __init__(self, content = []):
        self.segments = content

    def print(self):
        for s in self.segments:
            print(s)

    def rotateClockwise(self):
        self.segments = [[self.segments[len(self.segments) - i - 1][j] for i in range(len(self.segments))] for j in range(len(self.segments[0]))]
    
    def rotateAClockwise(self):
        self.segments = [[self.segments[i][len(self.segments[0]) - 1 - j] for i in range(len(self.segments))] for j in range(len(self.segments[0]))]

b = Blook(blooks[random.randint(0, 6)])

b.print()
print()

b.rotateClockwise()

b.print()
print()

b.rotateAClockwise()

b.print()
print()

print(b)
