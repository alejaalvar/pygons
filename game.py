import pygame
from constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from space_object import Ship

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygons")
clock = pygame.time.Clock()

ship = Ship(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

running = True
delta_time: float = 0.0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    ship.handle_input(keys, delta_time)
    ship.update(delta_time)

    screen.fill("black")
    ship.draw(screen)

    pygame.display.flip()
    delta_time = clock.tick(FPS) / 1000

pygame.quit()
