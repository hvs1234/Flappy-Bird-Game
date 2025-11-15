import pygame
from dataclasses import dataclass
from typing import Tuple
from config import BIRD_SIZE, GRAVITY, JUMP_VELOCITY, YELLOW, RED, BLACK


@dataclass
class Bird:
    x: float
    y: float
    velocity: float = 0.0
    alive: bool = True
    score: int = 0

    def jump(self) -> None:
        if self.alive:
            self.velocity = JUMP_VELOCITY

    def update(self, dt: float) -> None:
        if not self.alive:
            return

        self.velocity += GRAVITY * dt
        self.y += self.velocity * dt

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x - BIRD_SIZE // 2, self.y - BIRD_SIZE // 2, BIRD_SIZE, BIRD_SIZE
        )

    def draw(self, surface: pygame.Surface, is_ai: bool = False) -> None:
        color = RED if is_ai else YELLOW
        rect = self.get_rect()
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), BIRD_SIZE // 2)
        eye_x = int(self.x + BIRD_SIZE // 4)
        eye_y = int(self.y - BIRD_SIZE // 6)
        pygame.draw.circle(surface, BLACK, (eye_x, eye_y), 3)

    def check_bounds(self, ground_y: float) -> bool:
        if self.y - BIRD_SIZE // 2 <= 0:
            return True
        if self.y + BIRD_SIZE // 2 >= ground_y:
            return True
        return False
