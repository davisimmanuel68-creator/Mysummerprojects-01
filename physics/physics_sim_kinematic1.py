from vpython import *
ball = sphere(pos=vector(0,0,0), color=color.white, make_trail = True, trail_color=color.red, retain=1000000)
mybox = box(pos=vector(0,-0.5,0), size = vector(60,0.2,0.2))
x = 0
v = 2
t = 0
dt = 0.05

while t<=10:
    rate(10)
    ball.pos = vec(x,0,0)
    x = v*dt + x
    t = t+dt
    print(x)