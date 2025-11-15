import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from bird import Bird
from pipe import Pipe


@dataclass
class NeuralNetwork:
    input_size: int
    hidden_size: int
    output_size: int
    weights1: np.ndarray = None
    weights2: np.ndarray = None
    bias1: np.ndarray = None
    bias2: np.ndarray = None

    def __post_init__(self):
        if self.weights1 is None:
            self.weights1 = np.random.randn(
                self.input_size, self.hidden_size
            ) * np.sqrt(2.0 / self.input_size)
            self.bias1 = np.zeros((1, self.hidden_size))
            self.weights2 = np.random.randn(
                self.hidden_size, self.output_size
            ) * np.sqrt(2.0 / self.hidden_size)
            self.bias2 = np.zeros((1, self.output_size))

    @staticmethod
    def relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    @staticmethod
    def sigmoid(x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def forward(self, x: np.ndarray) -> np.ndarray:
        hidden = self.relu(np.dot(x, self.weights1) + self.bias1)
        output = self.sigmoid(np.dot(hidden, self.weights2) + self.bias2)
        return output

    def mutate(
        self, mutation_rate: float = 0.1, mutation_strength: float = 0.5
    ) -> "NeuralNetwork":
        new_nn = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)

        new_nn.weights1 = self.weights1 + np.random.randn(
            *self.weights1.shape
        ) * mutation_strength * (np.random.rand(*self.weights1.shape) < mutation_rate)
        new_nn.weights2 = self.weights2 + np.random.randn(
            *self.weights2.shape
        ) * mutation_strength * (np.random.rand(*self.weights2.shape) < mutation_rate)
        new_nn.bias1 = self.bias1 + np.random.randn(
            *self.bias1.shape
        ) * mutation_strength * (np.random.rand(*self.bias1.shape) < mutation_rate)
        new_nn.bias2 = self.bias2 + np.random.randn(
            *self.bias2.shape
        ) * mutation_strength * (np.random.rand(*self.bias2.shape) < mutation_rate)

        return new_nn


class AIPlayer:

    def __init__(self, bird: Bird, network: Optional[NeuralNetwork] = None):
        self.bird = bird
        self.network = network or NeuralNetwork(
            input_size=5, hidden_size=8, output_size=1
        )
        self.fitness = 0.0

    def get_inputs(self, pipes: List[Pipe], ground_y: float) -> np.ndarray:
        nearest_pipe = None
        for pipe in pipes:
            if pipe.x + pipe.gap_y > self.bird.x:
                nearest_pipe = pipe
                break

        if nearest_pipe is None:
            return np.array(
                [[self.bird.y / ground_y, self.bird.velocity / 500.0, 0.5, 0.5, 1.0]]
            )

        inputs = np.array(
            [
                [
                    self.bird.y / ground_y,
                    self.bird.velocity / 500.0,
                    nearest_pipe.gap_y / ground_y,
                    (nearest_pipe.x - self.bird.x) / 400.0,
                    (self.bird.y - nearest_pipe.gap_y) / ground_y,
                ]
            ]
        )

        return inputs

    def decide(self, pipes: List[Pipe], ground_y: float) -> bool:
        inputs = self.get_inputs(pipes, ground_y)
        output = self.network.forward(inputs)
        return output[0, 0] > 0.5

    def calculate_fitness(self) -> float:
        self.fitness = self.bird.score * 100 + self.bird.score
        return self.fitness
