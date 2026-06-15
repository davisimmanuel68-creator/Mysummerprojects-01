import pygame as pg
from OpenGL.GL import *
from pygame.locals import *

pg.init()

#the subject
def square():
    glBegin(GL_QUADS)

    glColor3f(1.0,1.0,1.0)

    glVertex2f(-0.5, -0.5)

    glVertex2f(0.5, -0.5)

    glVertex2f(0.5, 0.5)

    glVertex2f(-0.5, 0.5)

    glEnd()


#kinematic necessities
x = 0
y = 5
vx = 0
ax = 0
vy = 0
ay = -9.8

#screens
screen = pg.display.set_mode((1000,800), DOUBLEBUF | OPENGL)

#cameras
camera_x = 0
camera_y = 0

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(-10, 10, -10, 10, -1, 1)
glMatrixMode(GL_MODELVIEW)
glTranslatef(-camera_x, -camera_y, 0)

#time
clock = pg.time.Clock()
dt = clock.tick(60)/1000

#the running loop
running = True

while running:
    for event in pg.event.get():
        if event.type == QUIT:
            running = False

    #physics
    x += vx * dt
    vx += ax * dt
    y += vy * dt
    vy += ay * dt

    #render
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()


    glTranslatef(x,y,0)
     
    square()

    clock.tick(60)

    pg.display.flip()

