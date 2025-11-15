import pygame
import random
from typing import List, Optional
from bird import Bird
from pipe import Pipe
from ai_player import AIPlayer, NeuralNetwork
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    PIPE_SPAWN_DISTANCE,
    PIPE_SPEED,
    PIPE_GAP,
    SKY_BLUE,
    WHITE,
    BLACK,
    GREEN,
    GROUND_HEIGHT,
    PIPE_INITIAL_SPACING,
)


class Game:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.ground_y = WINDOW_HEIGHT - GROUND_HEIGHT

        self.mode = "menu"
        self.player_bird: Optional[Bird] = None
        self.ai_players: List[AIPlayer] = []
        self.pipes: List[Pipe] = []
        self.next_pipe_x = WINDOW_WIDTH + 100
        self.generation = 1
        self.best_score = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if self.mode == "menu":
                if event.key == pygame.K_SPACE:
                    self.start_player_game()
                elif event.key == pygame.K_a:
                    self.start_ai_game()
            elif self.mode == "play":
                if event.key == pygame.K_SPACE and self.player_bird:
                    self.player_bird.jump()
                elif event.key == pygame.K_r:
                    self.mode = "menu"
            elif self.mode == "ai":
                if event.key == pygame.K_r:
                    self.mode = "menu"
            elif self.mode == "gameover":
                if event.key == pygame.K_SPACE:
                    self.start_player_game()
                elif event.key == pygame.K_r:
                    self.mode = "menu"

    def start_player_game(self) -> None:
        self.mode = "play"
        self.player_bird = Bird(x=100, y=WINDOW_HEIGHT // 2)
        self.pipes = []
        self.next_pipe_x = WINDOW_WIDTH + 100
        self.initialize_pipes()

    def start_ai_game(self, population_size: int = 20) -> None:
        self.mode = "ai"
        self.pipes = []
        self.next_pipe_x = WINDOW_WIDTH + 100
        self.initialize_pipes()

        if not self.ai_players or all(not p.bird.alive for p in self.ai_players):
            if self.ai_players:
                self.evolve_population()
            else:
                self.ai_players = [
                    AIPlayer(Bird(x=100, y=WINDOW_HEIGHT // 2))
                    for _ in range(population_size)
                ]

    def initialize_pipes(self) -> None:
        current_x = WINDOW_WIDTH + 100
        screen_width = self.screen.get_width()
        for _ in range(5):
            gap_y = random.randint(150, int(self.ground_y - 150))
            self.pipes.append(Pipe(x=current_x, gap_y=gap_y))
            current_x += PIPE_SPAWN_DISTANCE
        self.next_pipe_x = current_x

    def evolve_population(self) -> None:
        for player in self.ai_players:
            player.calculate_fitness()

        self.ai_players.sort(key=lambda p: p.fitness, reverse=True)

        survivors = self.ai_players[:5]
        self.best_score = max(p.bird.score for p in survivors)

        new_population = []

        for survivor in survivors[:2]:
            bird = Bird(x=100, y=WINDOW_HEIGHT // 2)
            new_population.append(AIPlayer(bird, survivor.network))

        while len(new_population) < 20:
            parent = random.choice(survivors)
            bird = Bird(x=100, y=WINDOW_HEIGHT // 2)
            mutated_network = parent.network.mutate()
            new_population.append(AIPlayer(bird, mutated_network))

        self.ai_players = new_population
        self.generation += 1

    def spawn_pipe(self) -> None:
        gap_y = random.randint(150, int(self.ground_y - 150))
        self.pipes.append(Pipe(x=self.next_pipe_x, gap_y=gap_y))
        self.next_pipe_x += PIPE_SPAWN_DISTANCE

    def update(self, dt: float) -> None:
        if self.mode == "menu":
            return

        screen_width = self.screen.get_width()
        while self.next_pipe_x < screen_width + PIPE_SPAWN_DISTANCE:
            self.spawn_pipe()

        for pipe in self.pipes:
            pipe.update(dt, PIPE_SPEED)

        self.pipes = [p for p in self.pipes if not p.is_offscreen()]

        if self.mode == "play" and self.player_bird:
            self.update_player(dt)
        elif self.mode == "ai":
            self.update_ai(dt)

    def update_player(self, dt: float) -> None:
        if not self.player_bird.alive:
            return

        self.player_bird.update(dt)

        bird_rect = self.player_bird.get_rect()
        for pipe in self.pipes:
            if pipe.check_collision(bird_rect, self.ground_y):
                self.player_bird.alive = False
                self.mode = "gameover"

            if not pipe.scored and pipe.x + PIPE_WIDTH < self.player_bird.x:
                pipe.scored = True
                self.player_bird.score += 1

        if self.player_bird.check_bounds(self.ground_y):
            self.player_bird.alive = False
            self.mode = "gameover"

    def update_ai(self, dt: float) -> None:
        alive_count = 0

        for player in self.ai_players:
            if not player.bird.alive:
                continue

            alive_count += 1

            if player.decide(self.pipes, self.ground_y):
                player.bird.jump()

            player.bird.update(dt)

            bird_rect = player.bird.get_rect()
            for pipe in self.pipes:
                if pipe.check_collision(bird_rect, self.ground_y):
                    player.bird.alive = False

                if not pipe.scored and pipe.x + PIPE_WIDTH < player.bird.x:
                    player.bird.score += 1

            for pipe in self.pipes:
                if not pipe.scored and pipe.x + PIPE_WIDTH < player.bird.x:
                    pipe.scored = True
                    break

            if player.bird.check_bounds(self.ground_y):
                player.bird.alive = False

        if alive_count == 0:
            self.start_ai_game()

    def draw(self) -> None:
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.ground_y = screen_height - GROUND_HEIGHT

        self.screen.fill(SKY_BLUE)

        if self.mode == "menu":
            self.draw_menu(screen_width, screen_height)
        else:
            for pipe in self.pipes:
                pipe.draw(self.screen, self.ground_y)

            if self.mode == "play" and self.player_bird:
                self.player_bird.draw(self.screen)
                self.draw_score(self.player_bird.score)
            elif self.mode == "ai":
                for player in self.ai_players:
                    if player.bird.alive:
                        player.bird.draw(self.screen, is_ai=True)
                self.draw_ai_stats()
            elif self.mode == "gameover":
                self.player_bird.draw(self.screen)
                self.draw_gameover(screen_width, screen_height)

            pygame.draw.rect(
                self.screen, GREEN, (0, self.ground_y, screen_width, GROUND_HEIGHT)
            )

    def draw_menu(self, screen_width: int, screen_height: int) -> None:
        title = self.font.render("Flappy Bird", True, BLACK)
        play_text = self.small_font.render("Press SPACE to Play", True, BLACK)
        ai_text = self.small_font.render("Press A for AI Mode", True, BLACK)
        fullscreen_text = self.small_font.render(
            "Press F11 for Fullscreen", True, BLACK
        )

        self.screen.blit(
            title,
            (screen_width // 2 - title.get_width() // 2, screen_height // 2 - 100),
        )
        self.screen.blit(
            play_text,
            (screen_width // 2 - play_text.get_width() // 2, screen_height // 2),
        )
        self.screen.blit(
            ai_text,
            (screen_width // 2 - ai_text.get_width() // 2, screen_height // 2 + 40),
        )
        self.screen.blit(
            fullscreen_text,
            (
                screen_width // 2 - fullscreen_text.get_width() // 2,
                screen_height // 2 + 80,
            ),
        )

    def draw_score(self, score: int) -> None:
        text = self.font.render(f"Score: {score}", True, WHITE)
        self.screen.blit(text, (10, 10))

    def draw_ai_stats(self) -> None:
        alive = sum(1 for p in self.ai_players if p.bird.alive)
        max_score = max(p.bird.score for p in self.ai_players)

        gen_text = self.small_font.render(f"Generation: {self.generation}", True, WHITE)
        alive_text = self.small_font.render(
            f"Alive: {alive}/{len(self.ai_players)}", True, WHITE
        )
        score_text = self.small_font.render(f"Best: {max_score}", True, WHITE)
        best_text = self.small_font.render(f"All-time: {self.best_score}", True, WHITE)

        self.screen.blit(gen_text, (10, 10))
        self.screen.blit(alive_text, (10, 40))
        self.screen.blit(score_text, (10, 70))
        self.screen.blit(best_text, (10, 100))

    def draw_gameover(self, screen_width: int, screen_height: int) -> None:
        text = self.font.render("Game Over!", True, BLACK)
        score_text = self.small_font.render(
            f"Score: {self.player_bird.score}", True, BLACK
        )
        restart_text = self.small_font.render("Press SPACE to Restart", True, BLACK)
        menu_text = self.small_font.render("Press R for Menu", True, BLACK)

        self.screen.blit(
            text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - 100)
        )
        self.screen.blit(
            score_text,
            (screen_width // 2 - score_text.get_width() // 2, screen_height // 2 - 50),
        )
        self.screen.blit(
            restart_text,
            (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2),
        )
        self.screen.blit(
            menu_text,
            (screen_width // 2 - menu_text.get_width() // 2, screen_height // 2 + 30),
        )
