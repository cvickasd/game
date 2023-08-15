import pygame as pg
import sys
import random

pg.init()

w,h = 800, 600
screen = pg.display.set_mode((w,h))
clock = pg.time.Clock()

particles = []


def emit_particle(x, y, x_vel, y_vel, radius):
    particles.append([[x, y], [x_vel, y_vel], radius])


def update_particles():
    for i, particle in reversed(list(enumerate(particles))):
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 0.1
        reversed_particle = particles[len(particles) - i - 1]
        pg.draw.circle(screen, (255, 255, 255), (int(reversed_particle[0][0]), int(reversed_particle[0][1])), reversed_particle[2])

        if particle[0][1] > 500 or particle[0][1] < 200:
            particle[1][1] = -particle[1][1]

        if particle[0][0] > 500 or particle[0][0] < 200:
            particle[0][0] = -particle[0][0]

        if particle[2] <= 0:
            particles.pop(i)

while True:
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            pg.quit()
            sys.exit()
            
    screen.fill((0, 0, 0))

    emit_particle(w//2, h//2, random.uniform(-5, 5), random.uniform(-5, 5), 10)
    update_particles()

    pg.display.flip()
    clock.tick(60)