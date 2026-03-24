from typing import List
import math
import random
import pygame
from pygame import Vector2
from constants import *


class SpaceObject:
    RADIUS: float = 0.0

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
    RADIUS: float = 15.0
    EXPLOSION_DURATION: float = 1.0

    BASE_POINTS: list[Vector2] = [
        Vector2(0, -20),  # nose
        Vector2(12, 14),  # rear right
        Vector2(-12, 14),  # rear left
    ]

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.is_alive = True
        self.explosion_timer: float = 0.0

    def get_explosion_timer(self) -> float:
        return self.explosion_timer

    def handle_input(
        self, keys: pygame.key.ScancodeWrapper, delta_time: float
    ) -> None:
        if keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_j]:
            self.angle -= self.TURN_SPEED * delta_time
        if keys[pygame.K_d] or keys[pygame.K_RIGHT] or keys[pygame.K_l]:
            self.angle += self.TURN_SPEED * delta_time
        if keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_k]:
            rad = math.radians(self.angle)
            thrust_dir = Vector2(math.sin(rad), -math.cos(rad))
            self.velocity += thrust_dir * self.THRUST * delta_time

    def update(self, delta_time: float) -> None:
        self.velocity *= self.DRAG
        if not self.is_alive:
            self.explosion_timer -= delta_time
        super().update(delta_time)

    def draw(self, screen: pygame.Surface) -> None:
        if self.is_alive:
            points: List[Vector2] = self._get_rotated_points(self.BASE_POINTS)
            pygame.draw.polygon(screen, SHIP_COLOR, points, width=0)
        elif self.explosion_timer > 0:
            self.draw_explosion(screen)

    def draw_explosion(self, screen: pygame.Surface) -> None:
        progress: float = 1.0 - (
            self.explosion_timer / self.EXPLOSION_DURATION
        )
        points: List[Vector2] = self._get_rotated_points(self.BASE_POINTS)
        for point in points:
            offset: float = (point - self.position) * progress * 3
            pos: float = point + offset
            pygame.draw.circle(screen, SHIP_COLOR, (int(pos.x), int(pos.y)), 3)

    def unalive(self):
        self.is_alive = not self.is_alive
        self.explosion_timer = self.EXPLOSION_DURATION  # start the countdown

    def get_life_status(self) -> bool:
        return self.is_alive


class Asteroid(SpaceObject):
    RADIUS: float = 20.0
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
        speed: float = random.uniform(20, 80)
        angle: float = random.uniform(0, 360)
        rad: float = math.radians(angle)
        self.velocity = Vector2(math.sin(rad), -math.cos(rad)) * speed

    def draw(self, screen: pygame.Surface) -> None:
        points: List[Vector2] = self._get_rotated_points(self.BASE_POINTS)
        pygame.draw.polygon(screen, ASTEROID_COLOR, points, width=2)


class Projectile(SpaceObject):
    SPEED: float = 400.0
    RADIUS: float = 5.0
    LIFETIME: float = 2.0

    def __init__(self, ship: Ship):
        super().__init__(ship.position.x, ship.position.y)
        rad: float = math.radians(ship.angle)
        self.velocity = Vector2(math.sin(rad), -math.cos(rad)) * self.SPEED
        self.lifetime: float = self.LIFETIME

    def update(self, delta_time: float) -> None:
        self.lifetime -= delta_time
        super().update(delta_time)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(
            screen, "red", (int(self.position.x), int(self.position.y)), 3
        )

    def is_expired(self) -> bool:
        return self.lifetime <= 0
