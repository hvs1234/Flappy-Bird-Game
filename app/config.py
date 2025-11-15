from dataclasses import dataclass
from typing import Tuple

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

GRAVITY = 1500.0
JUMP_VELOCITY = -400.0

BIRD_SIZE = 30
PIPE_WIDTH = 60
PIPE_GAP = 200
PIPE_SPEED = 200.0
PIPE_SPAWN_DISTANCE = 300
PIPE_INITIAL_SPACING = 400

GROUND_HEIGHT = 50


@dataclass
class GameConfig:
    window_width: int = WINDOW_WIDTH
    window_height: int = WINDOW_HEIGHT
    fps: int = FPS
    gravity: float = GRAVITY
    jump_velocity: float = JUMP_VELOCITY
    bird_size: int = BIRD_SIZE
    pipe_width: int = PIPE_WIDTH
    pipe_gap: int = PIPE_GAP
    pipe_speed: float = PIPE_SPEED
    ground_height: int = GROUND_HEIGHT
