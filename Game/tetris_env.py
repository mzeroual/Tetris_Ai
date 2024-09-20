import pygame
import random
import gym
from gym import spaces
import numpy as np

colors = [
    (0, 0, 0),
    (121, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]

class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])


class TetrisEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(TetrisEnv, self).__init__()
        self.board_width = 10
        self.board_height = 20
        self.board = np.zeros((self.board_height, self.board_width), dtype=int)
        self.current_piece = None
        self.current_piece_position = [0, 0]
        
        # Define action and observation space
        self.action_space = spaces.Discrete(4)  # 0: left, 1: right, 2: down, 3: rotate
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.board_height, self.board_width), dtype=np.int)

        self.reset()

    def reset(self):
        self.board = np.zeros((self.board_height, self.board_width), dtype=int)
        self.current_piece = Figure(0, self.board_width // 2)
        self.current_piece_position = [0, self.board_width // 2]
        return self.get_state()

    def step(self, action):
        # Apply action
        if action == 0:  # Move left
            self.current_piece.x -= 1
            if self.intersects():
                self.current_piece.x += 1
        elif action == 1:  # Move right
            self.current_piece.x += 1
            if self.intersects():
                self.current_piece.x -= 1
        elif action == 2:  # Move down
            self.current_piece.y += 1
            if self.intersects():
                self.current_piece.y -= 1
                self.freeze()
        elif action == 3:  # Rotate
            self.current_piece.rotate()
            if self.intersects():
                self.current_piece.rotate()
                self.current_piece.rotate()
                self.current_piece.rotate()
        
        # Check for game over
        done = self.is_game_over()
        
        # Calculate reward
        reward = self.calculate_reward()
        
        # Get new state
        state = self.get_state()
        
        return state, reward, done, {}

    def render(self, mode='human'):
        pygame.init()
        screen = pygame.display.set_mode((self.board_width * 30, self.board_height * 30))
        pygame.display.set_caption("Tetris")
        screen.fill((0, 0, 0))

        for i in range(self.board_height):
            for j in range(self.board_width):
                pygame.draw.rect(screen, colors[self.board[i][j]], (j * 30, i * 30, 30, 30))

        if self.current_piece is not None:
            for i in range(4):
                for j in range(4):
                    if i * 4 + j in self.current_piece.image():
                        pygame.draw.rect(screen, colors[self.current_piece.color],
                                         ((self.current_piece.x + j) * 30, (self.current_piece.y + i) * 30, 30, 30))

        pygame.display.flip()

    def new_piece(self):
        return Figure(0, self.board_width // 2)

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.current_piece.image():
                    if i + self.current_piece.y > self.board_height - 1 or \
                            j + self.current_piece.x > self.board_width - 1 or \
                            j + self.current_piece.x < 0 or \
                            self.board[i + self.current_piece.y][j + self.current_piece.x] > 0:
                        intersection = True
        return intersection

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.current_piece.image():
                    self.board[i + self.current_piece.y][j + self.current_piece.x] = self.current_piece.color
        self.break_lines()
        self.current_piece = self.new_piece()
        if self.intersects():
            self.state = "gameover"

    def break_lines(self):
        lines = 0
        for i in range(1, self.board_height):
            zeros = 0
            for j in range(self.board_width):
                if self.board[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.board_width):
                        self.board[i1][j] = self.board[i1 - 1][j]
        self.score += lines ** 2

    def is_game_over(self):
        for j in range(self.board_width):
            if self.board[0][j] > 0:
                return True
        return False

    def calculate_reward(self):
        # Reward for clearing lines
        reward = 0
        for i in range(self.board_height):
            if all(self.board[i]):
                reward += 1
        return reward

    def get_state(self):
        state = np.copy(self.board)
        if self.current_piece is not None:
            for i in range(4):
                for j in range(4):
                    if i * 4 + j in self.current_piece.image():
                        state[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.color
        return state
