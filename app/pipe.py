import pygame
from dataclasses import dataclass
from typing import Tuple
from config import PIPE_WIDTH, PIPE_GAP, GREEN, DARK_GREEN, BLACK


@dataclass
class Pipe:
    x: float
    gap_y: float
    scored: bool = False

    def update(self, dt: float, speed: float) -> None:
        self.x -= speed * dt

    def is_offscreen(self) -> bool:
        return self.x + PIPE_WIDTH < 0

    def get_top_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), 0, PIPE_WIDTH, int(self.gap_y - PIPE_GAP // 2))

    def get_bottom_rect(self, ground_y: float) -> pygame.Rect:
        top_height = self.gap_y + PIPE_GAP // 2
        return pygame.Rect(
            int(self.x), int(top_height), PIPE_WIDTH, int(ground_y - top_height)
        )

    def check_collision(self, bird_rect: pygame.Rect, ground_y: float) -> bool:
        return bird_rect.colliderect(self.get_top_rect()) or bird_rect.colliderect(
            self.get_bottom_rect(ground_y)
        )

    def draw(self, surface: pygame.Surface, ground_y: float) -> None:
        top_rect = self.get_top_rect()
        pygame.draw.rect(surface, GREEN, top_rect)
        pygame.draw.rect(surface, DARK_GREEN, top_rect, 3)

        cap_rect = pygame.Rect(
            top_rect.x - 5, top_rect.bottom - 20, PIPE_WIDTH + 10, 20
        )
        pygame.draw.rect(surface, GREEN, cap_rect)
        pygame.draw.rect(surface, DARK_GREEN, cap_rect, 3)

        bottom_rect = self.get_bottom_rect(ground_y)
        pygame.draw.rect(surface, GREEN, bottom_rect)
        pygame.draw.rect(surface, DARK_GREEN, bottom_rect, 3)

        cap_rect = pygame.Rect(bottom_rect.x - 5, bottom_rect.top, PIPE_WIDTH + 10, 20)
        pygame.draw.rect(surface, GREEN, cap_rect)
        pygame.draw.rect(surface, DARK_GREEN, cap_rect, 3)
