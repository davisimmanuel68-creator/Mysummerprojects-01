from vpython import *
ball_1 = sphere(pos =vec(0,0,0), radius = 3, color = color.white, make_trail = True, retain = 500)
ball_2 = sphere(pos =vec(0,10,0), radius = 3, color = color.white, make_trail = True, retain = 500)


v1 = 3
v2 = 5
x1 = 0
x2 = 0
t = 0
dt = 0.1

while t <= 25:
    rate(30)
    ball_1.pos = vec(x1,0,0)
    ball_2.pos = vec(x2,10,0)
    x1 = x1 + v1*dt
    x2 = x2 + v2*dt
    t = t + dt
    print(x1, x2)

