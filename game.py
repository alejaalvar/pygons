"""
game.py

Defines the Game class, which manages the games loop and resources.
"""

from typing import List
import os
import sys
import random
import pygame
from constants import *
from space_object import *


def resource_path(relative_path: str) -> str:
    """Resolve a resource path for both development and PyInstaller bundles

    Args:
        relative_path (str): the relative path to the resource

    Returns:
        str: the absolute path to the resource
    """
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, relative_path)


class Game:
    """Represents the Game manager - controls game resources and the game loop

    Attributes:
        screen: the screen that will be drawn on
        clock: controls and tracks the game's framerate
        font_large: large font used for menu headers
        font_small: small font used for menu options
        font_tiny: tiny font usesd for menu footers
        game_state: represents if the game is paused, gameover, or playing
    """

    def __init__(self) -> None:
        """Initialize pygame, the display, clock, fonts, and starting game state"""
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption(GAME_CAPTION)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.font_large: pygame.font.Font = pygame.font.Font(
            resource_path(FONT_FILE), 48
        )
        self.font_small: pygame.font.Font = pygame.font.Font(
            resource_path(FONT_FILE), 20
        )
        self.font_tiny: pygame.font.Font = pygame.font.Font(
            resource_path(FONT_FILE), 12
        )
        self._reset()
        self.game_state = "title"

    def _reset(self) -> None:
        """Reset all game objects and state to their starting values"""
        self.ship: Ship = Ship(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.asteroids: List[Asteroid] = [
            self._spawn_asteroid() for _ in range(20)
        ]
        self.projectiles: List[Projectile] = []
        self.shoot_timer: float = 0.0
        self.game_state: str = "playing"  # "playing" | "paused" | "game_over"
        self.delta_time: float = 0.0

    def _spawn_asteroid(self) -> Asteroid:
        """Spawn an asteroid at a random position at least MIN_SPAWN_DISTANCE from the ship

        Returns:
            Asteroid: a new asteroid at a valid spawn position
        """
        while True:
            x: float = random.uniform(0, SCREEN_WIDTH)
            y: float = random.uniform(0, SCREEN_HEIGHT)
            if (
                pygame.math.Vector2(x, y).distance_to(self.ship.position)
                > MIN_SPAWN_DISTANCE
            ):
                return Asteroid(x, y)

    def _is_colliding(self, obj1: SpaceObject, obj2: SpaceObject) -> bool:
        """Check whether two space objects are overlapping based on their radii

        Args:
            obj1 (SpaceObject): the first space object
            obj2 (SpaceObject): the second space object

        Returns:
            bool: True if the objects are colliding, False otherwise
        """
        return (
            obj1.position.distance_to(obj2.position)
            < obj1.RADIUS + obj2.RADIUS
        )

    def _handle_projectile_collisions(self) -> None:
        """Detect and remove any projectiles and asteroids that have collided"""
        hit_asteroids: set[Asteroid] = set()
        hit_projectiles: set[Projectile] = set()

        for projectile in self.projectiles:
            for asteroid in self.asteroids:
                if self._is_colliding(projectile, asteroid):
                    hit_asteroids.add(asteroid)
                    hit_projectiles.add(projectile)

        self.projectiles = [
            p for p in self.projectiles if p not in hit_projectiles
        ]
        self.asteroids = [a for a in self.asteroids if a not in hit_asteroids]

    def _handle_events(self) -> bool:
        """Process pygame events and update game state based on player input

        Returns:
            bool: False if the game should exit, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.game_state == "title" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_RETURN:
                    self.game_state = "playing"
            elif (
                self.game_state == "game_over" and event.type == pygame.KEYDOWN
            ):
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False
                if event.key == pygame.K_r:
                    self._reset()
            elif self.game_state == "playing" and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.game_state = "paused"
            elif self.game_state == "paused" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_r:
                    self._reset()
                if event.key in (pygame.K_k, pygame.K_p, pygame.K_ESCAPE):
                    self.game_state = "playing"
        return True

    def _update(self) -> None:
        """Update all game object states and check for collisions - skipped when not playing"""
        if self.game_state != "playing":
            return

        self.shoot_timer -= self.delta_time

        keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        self.ship.handle_input(keys, self.delta_time)
        if keys[pygame.K_SPACE] and self.shoot_timer <= 0:
            self.projectiles.append(Projectile(self.ship))
            self.shoot_timer = SHOOT_COOLDOWN

        self.ship.update(self.delta_time)

        for projectile in self.projectiles:
            projectile.update(self.delta_time)
        self.projectiles = [p for p in self.projectiles if not p.is_expired()]

        for asteroid in self.asteroids:
            asteroid.update(self.delta_time)

        self._handle_projectile_collisions()

        for asteroid in self.asteroids:
            if self._is_colliding(asteroid, self.ship):
                if self.ship.get_life_status():
                    self.ship.unalive()

        if (
            not self.ship.get_life_status()
            and self.ship.get_explosion_timer() <= 0
        ):
            self.game_state = "game_over"

    def _draw_title_screen(self) -> None:
        """Draw the title screen with start and quit options and developer credits"""
        center_x: int = SCREEN_WIDTH // 2
        center_y: int = SCREEN_HEIGHT // 2
        title: pygame.Surface = self.font_large.render(
            GAME_CAPTION, True, "white"
        )
        start: pygame.Surface = self.font_small.render(
            "ENTER  -  Start", True, "yellow"
        )
        quit_text: pygame.Surface = self.font_small.render(
            "Q  -  Quit", True, "yellow"
        )
        margin: int = 20
        dev: pygame.Surface = self.font_tiny.render(
            "Developed by: " + DEVELOPER_NAME, True, "gray"
        )
        discord: pygame.Surface = self.font_tiny.render(
            "Discord: " + DEVELOPER_DISCORD, True, "gray"
        )
        github: pygame.Surface = self.font_tiny.render(
            "GitHub: " + DEVELOPER_GITHUB, True, "gray"
        )
        self.screen.blit(
            title, title.get_rect(center=(center_x, center_y - 60))
        )
        self.screen.blit(
            start, start.get_rect(center=(center_x, center_y + 20))
        )
        self.screen.blit(
            quit_text, quit_text.get_rect(center=(center_x, center_y + 70))
        )
        self.screen.blit(
            dev,
            dev.get_rect(
                bottomright=(SCREEN_WIDTH - margin, SCREEN_HEIGHT - margin)
            ),
        )
        self.screen.blit(
            discord,
            discord.get_rect(bottomleft=(margin, SCREEN_HEIGHT - margin)),
        )
        self.screen.blit(
            github,
            github.get_rect(midbottom=(center_x, SCREEN_HEIGHT - margin)),
        )

    def _draw_pause_menu(self) -> None:
        """Draw the pause menu with continue, restart, and quit options"""
        center_x: int = SCREEN_WIDTH // 2
        center_y: int = SCREEN_HEIGHT // 2
        title: pygame.Surface = self.font_large.render("PAUSE", True, "white")

        keep_playing_text: pygame.Surface = self.font_small.render(
            "K  -  Keep Playing", True, "yellow"
        )
        restart: pygame.Surface = self.font_small.render(
            "R  -  Restart", True, "yellow"
        )
        quit_text: pygame.Surface = self.font_small.render(
            "Q  -  Quit", True, "yellow"
        )
        self.screen.blit(
            title, title.get_rect(center=(center_x, center_y - 60))
        )
        self.screen.blit(
            keep_playing_text,
            keep_playing_text.get_rect(center=(center_x, center_y + 20)),
        )
        self.screen.blit(
            restart, restart.get_rect(center=(center_x, center_y + 70))
        )
        self.screen.blit(
            quit_text, quit_text.get_rect(center=(center_x, center_y + 120))
        )

    def _draw_game_over_menu(self) -> None:
        """Draw the game over menu with restart and quit options"""
        center_x: int = SCREEN_WIDTH // 2
        center_y: int = SCREEN_HEIGHT // 2
        title: pygame.Surface = self.font_large.render(
            "GAME OVER", True, "white"
        )
        restart: pygame.Surface = self.font_small.render(
            "R  -  Restart", True, "yellow"
        )
        quit_text: pygame.Surface = self.font_small.render(
            "Q  -  Quit", True, "yellow"
        )
        self.screen.blit(
            title, title.get_rect(center=(center_x, center_y - 60))
        )
        self.screen.blit(
            restart, restart.get_rect(center=(center_x, center_y + 20))
        )
        self.screen.blit(
            quit_text, quit_text.get_rect(center=(center_x, center_y + 70))
        )

    def _draw(self) -> None:
        """Clear the screen and draw all game objects and the active menu overlay"""
        self.screen.fill("black")
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        if self.game_state == "playing":
            self.ship.draw(self.screen)
            for projectile in self.projectiles:
                projectile.draw(self.screen)
        if self.game_state == "title":
            self._draw_title_screen()
        elif self.game_state == "game_over":
            self._draw_game_over_menu()
        elif self.game_state == "paused":
            self._draw_pause_menu()
        pygame.display.flip()

    def run(self) -> None:
        """Start and run the main game loop until the player quits"""
        is_running: bool = True
        while is_running:
            is_running = self._handle_events()
            self._update()
            self._draw()
            self.delta_time = self.clock.tick(FPS) / 1000
        pygame.quit()
