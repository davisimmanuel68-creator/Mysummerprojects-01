from pygame.locals import *
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
pg.init()

screen = pg.display.set_mode((1000,800), DOUBLEBUF | OPENGL)

glViewport(0, 0, 1000, 800)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()

gluPerspective(
    45,
    1000/800,
    0.1,
    50
)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()

glEnable(GL_DEPTH_TEST)
glClearColor(0, 0, 0, 1)



glEnable(GL_DEPTH_TEST)


sphere = gluNewQuadric()

x = 0
y = 0
z = 0

vx = 2
vy = 0
vz = 2

ax = 0.5
ay = 0
az = 1

camera_x = 0
camera_y = 0
camera_z = 20

running = True


clock = pg.time.Clock()


while running:
    dt = clock.tick(60)/1000
    
    for event in pg.event.get():
        if event.type == QUIT:
            running = False

    vx += ax * dt
    vy += ay * dt
    vz += az * dt

    x += vx * dt
    y += vy * dt
    z += vz * dt

    camera_x += (x - camera_x) * 0.002

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(-camera_x, -camera_y, -camera_z)
    glTranslatef(x, y, z)
    glColor3f(1,1,1)
    gluSphere(sphere, 1, 32, 32)

    pg.display.flip()