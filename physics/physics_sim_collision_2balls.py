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

#initialize objects
ball_1 = { 
    "position" : [0, 0],
    "velocity" : [6, 4],
    "acceleration" : [0, -9.8],
    "radius" : 0.5
}

ball_2 = { 
    "position" : [0, 5],
    "velocity" : [0, 4],
    "acceleration" : [0, -9.8],
    "radius" : 0.5
}

balls = [ball_1, ball_2]

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


floor = -8
ceiling = 8
L_wall = -10
R_wall = 10

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
    for ball in balls:
        ball["velocity"][0] += ball["acceleration"][0] * dt
        ball["velocity"][1] += ball["acceleration"][1] * dt
        ball["position"][0] += ball["velocity"][0] * dt
        ball["position"][1] += ball["velocity"][1] * dt

    #collision with walls, floor, and ceiling

    for ball in balls:
        #floor & ceiling
        if ball["position"][1] - ball["radius"] <= floor:
            ball["position"][1] = floor + ball["radius"]
            ball["velocity"][1] *= -1
            ball["velocity"][1] *= 0.8
        
        if ball["position"][1] + ball["radius"] >= ceiling:
            ball["position"][1] = ceiling - ball["radius"]
            ball["velocity"][1] *= -1
            ball["velocity"][1] *= 0.8

        #left & right wall
        if ball["position"][0] - ball["radius"] <= L_wall:
            ball["position"][0] = L_wall + ball["radius"]
            ball["velocity"][0] *= -1
            ball["velocity"][0] *= 0.8
        
        if ball["position"][0] + ball["radius"] >= R_wall:
            ball["position"][0] = R_wall - ball["radius"]
            ball["velocity"][0] *= -1
            ball["velocity"][0] *= 0.8
        

    #rendering the circles ("or balls")
    glClear(GL_COLOR_BUFFER_BIT)

    for ball in balls:
        glLoadIdentity()

        glTranslatef(
            ball["position"][0],
            ball["position"][1],
            0

        )

        draw_circle(ball["radius"])
    
      
    pg.display.flip()