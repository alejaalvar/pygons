from typing import List
import math
import pygame
from pygame import Vector2
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class SpaceObject:
    def __init__(self, x: float, y: float) -> None:
        self.position: Vector2 = Vector2(x, y)
        self.velocity: Vector2 = Vector2(0, 0)
        self.angle: float = 0.0  # degrees

    def update(self, delta_time: float) -> None:
        self.position += self.velocity * delta_time
        self.position.x %= SCREEN_WIDTH
        self.position.y %= SCREEN_HEIGHT

    def _get_rotated_points(self, base_points: list[Vector2]) -> list[Vector2]:
        rad: float = math.radians(self.angle)  # degrees -> radians
        cos_a: float = math.cos(rad)
        sin_a: float = math.sin(rad)
        return [
            Vector2(
                p.x * cos_a - p.y * sin_a + self.position.x,
                p.x * sin_a + p.y * cos_a + self.position.y,
            )
            for p in base_points
        ]


class Ship(SpaceObject):
    TURN_SPEED: float = 200.0  # degrees/sec
    THRUST: float = 400.0  # pixels/sec^2
    DRAG: float = 0.98  # velocity multiplier per frame

    BASE_POINTS: list[Vector2] = [
        Vector2(0, -20),  # nose
        Vector2(12, 14),  # rear right
        Vector2(-12, 14),  # rear left
    ]

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)

    def handle_input(
        self, keys: pygame.key.ScancodeWrapper, delta_time: float
    ) -> None:
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.angle -= self.TURN_SPEED * delta_time
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.angle += self.TURN_SPEED * delta_time
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            rad = math.radians(self.angle)
            thrust_dir = Vector2(math.sin(rad), -math.cos(rad))
            self.velocity += thrust_dir * self.THRUST * delta_time

    def update(self, delta_time: float) -> None:
        self.velocity *= self.DRAG
        super().update(delta_time)

    def draw(self, screen: pygame.Surface) -> None:
        points: List[Vector2] = self._get_rotated_points(self.BASE_POINTS)
        pygame.draw.polygon(screen, "white", points, width=2)


class Asteroid(SpaceObject):
    BASE_POINTS: list[Vector2] = [
        Vector2(0, -25),
        Vector2(15, -15),
        Vector2(20, 0),
        Vector2(12, 20),
        Vector2(-10, 22),
        Vector2(-20, 8),
        Vector2(-18, -12),
    ]

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)

    def draw(self, screen: pygame.Surface) -> None:
        points: List[Vector2] = self._get_rotated_points(self.BASE_POINTS)
        pygame.draw.polygon(screen, "white", points, width=2)
