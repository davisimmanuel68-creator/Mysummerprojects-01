import pygame as pg
from OpenGL.GL import *
from pygame.locals import *
from OpenGL.GLU import *
import math
pg.init()

#initialize the screen
screen = pg.display.set_mode((1000, 800), DOUBLEBUF | OPENGL)

#initialize the camera; project the world"
glMatrixMode(GL_PROJECTION)
glLoadIdentity()

glOrtho(
    -10, 10,
    -10, 10,
    -1, 1
)

glMatrixMode(GL_MODELVIEW)

#initialize the object (circle)
radius = 1
def draw_circle(radius):
    glColor3f(1,1,1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    segments = 100

    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex2f(x, y)
    glEnd()

#initialize the physical variables
position = [-5, 5]
velocity = [5, 0]
acceleration = [0, -9.8]

#time
clock = pg.time.Clock()


#running condition
running = True

while running:
    #measure time
    dt = clock.tick(60) / 1000

    #handle events
    for event in pg.event.get():
        if event.type == QUIT:
            running = False
    
    #update physics
    velocity[0] += acceleration[0] * dt
    velocity[1] += acceleration[1] * dt

    position[0] += velocity[0] * dt
    position[1] += velocity[1] * dt

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(position[0], position[1], 0)

    draw_circle(radius)

    pg.display.flip()