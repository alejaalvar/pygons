from typing import List
import random
import pygame
from constants import *
from space_object import *


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
pygame.display.set_caption(GAME_CAPTION)
clock = pygame.time.Clock()

# Fill the map with space objects
ship = Ship(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
asteroids: List[Asteroid] = [spawn_asteroid(ship) for _ in range(20)]
projectiles: List[Projectile] = []

running = True
delta_time: float = 0.0
shoot_timer: float = 0.0
# ========== End Game Setup ==========

# ========== Game Loop ==========
while running:

    shoot_timer -= delta_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get input from the player
    keys = pygame.key.get_pressed()
    ship.handle_input(keys, delta_time)
    if keys[pygame.K_SPACE] and shoot_timer <= 0:
        print("Firing!")
        projectiles.append(Projectile(ship))
        shoot_timer = SHOOT_COOLDOWN

    # Update the game objects
    ship.update(delta_time)

    for projectile in projectiles:
        projectile.update(delta_time)
    projectiles = [p for p in projectiles if not p.is_expired()]

    for asteroid in asteroids:
        asteroid.update(delta_time)

    # Check if the player has collided w/asteroid
    for asteroid in asteroids:
        if is_colliding(asteroid, ship):
            print("Collide!")  # placeholder for explosion logic

    # Clear the frame and draw the new one
    screen.fill("black")
    for asteroid in asteroids:
        asteroid.draw(screen)
    ship.draw(screen)
    for projectile in projectiles:
        projectile.draw(screen)

    pygame.display.flip()
    delta_time = clock.tick(FPS) / 1000
# ========== End Game Loop ==========

pygame.quit()
