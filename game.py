from typing import List
import random
import pygame
from constants import *
from space_object import SpaceObject, Ship, Asteroid


def spawn_asteroid(ship: Ship) -> Asteroid:
    while True:
        x: float = random.uniform(0, SCREEN_WIDTH)
        y: float = random.uniform(0, SCREEN_HEIGHT)
        if (
            pygame.math.Vector2(x, y).distance_to(ship.position)
            > MIN_SPAWN_DISTANCE
        ):
            return Asteroid(x, y)


def is_colliding(space_obj1: SpaceObject, space_obj2: SpaceObject) -> bool:
    return (
        space_obj1.position.distance_to(space_obj2.position)
        < space_obj1.RADIUS + space_obj2.RADIUS
    )


# ========== Game Setup ==========
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygons")
clock = pygame.time.Clock()

# Fill the map with space objects
ship = Ship(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
asteroids: List[Asteroid] = [spawn_asteroid(ship) for _ in range(10)]

running = True
delta_time: float = 0.0
# ========== End Game Setup ==========

# ========== Game Loop ==========
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    ship.handle_input(keys, delta_time)
    ship.update(delta_time)
    for asteroid in asteroids:
        asteroid.update(delta_time)
    for asteroid in asteroids:
        if is_colliding(asteroid, ship):
            print("Collide!")  # placeholder for explosion logic

    screen.fill("black")
    ship.draw(screen)
    for asteroid in asteroids:
        asteroid.draw(screen)

    pygame.display.flip()
    delta_time = clock.tick(FPS) / 1000
# ========== End Game Loop ==========

pygame.quit()
