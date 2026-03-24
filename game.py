from typing import List
import random
import pygame
from constants import *
from space_object import *


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption(GAME_CAPTION)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.font_large: pygame.font.Font = pygame.font.Font(FONT_FILE, 48)
        self.font_small: pygame.font.Font = pygame.font.Font(FONT_FILE, 20)
        self.font_tiny: pygame.font.Font = pygame.font.Font(FONT_FILE, 12)
        self._reset()
        self.game_state = "title"

    def _reset(self) -> None:
        self.ship: Ship = Ship(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.asteroids: List[Asteroid] = [
            self._spawn_asteroid() for _ in range(20)
        ]
        self.projectiles: List[Projectile] = []
        self.shoot_timer: float = 0.0
        self.game_state: str = "playing"  # "playing" | "paused" | "game_over"
        self.delta_time: float = 0.0

    def _spawn_asteroid(self) -> Asteroid:
        while True:
            x: float = random.uniform(0, SCREEN_WIDTH)
            y: float = random.uniform(0, SCREEN_HEIGHT)
            if (
                pygame.math.Vector2(x, y).distance_to(self.ship.position)
                > MIN_SPAWN_DISTANCE
            ):
                return Asteroid(x, y)

    def _is_colliding(self, obj1: SpaceObject, obj2: SpaceObject) -> bool:
        return (
            obj1.position.distance_to(obj2.position)
            < obj1.RADIUS + obj2.RADIUS
        )

    def _handle_projectile_collisions(self) -> None:
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
        is_running: bool = True
        while is_running:
            is_running = self._handle_events()
            self._update()
            self._draw()
            self.delta_time = self.clock.tick(FPS) / 1000
        pygame.quit()


if __name__ == "__main__":
    Game().run()
