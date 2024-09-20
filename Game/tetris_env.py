import gym
from gym import spaces
import numpy as np
import random
import pygame

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
        self.color = 2
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])

class TetrisEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,mode="human"):
        super(TetrisEnv, self).__init__()
        self.mode=mode
        self.field = []
        self.width = 10
        self.height = 20
        self.zoom = 20
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.current_piece = None
        self.current_piece_position = [0, 0]
        
        # Define action and observation space
        self.action_space = spaces.Discrete(4)  # 0: left, 1: right, 2: down, 3: rotate
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.height, self.width), dtype=int)
        
        # Initialize the game engine
        pygame.init()
        
        

        pygame.display.set_caption("Tetris")
        
        self.reset()

    def reset(self):
        self.score=0
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.current_piece = Figure(0, self.width // 2)
        self.current_piece_position = [0, self.width // 2]
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
        if self.mode=="human": 
            clock = pygame.time.Clock()
            BLACK = (0, 0, 0)
            WHITE = (255, 255, 255)
            GRAY = (128, 128, 128)
            size = (400, 500)
            screen = pygame.display.set_mode(size)
            for i in range(self.height):
                for j in range(self.width):
                    pygame.draw.rect(screen, GRAY, [self.current_piece.x + self.zoom * j, self.current_piece.y + self.zoom * i, self.zoom, self.zoom], 1)
                    if self.board[i][j] > 0:
                        pygame.draw.rect(screen, colors[1],
                                        [self.current_piece.x + self.zoom * j + 1, self.current_piece.y + self.zoom * i + 1, self.zoom - 2, self.zoom - 1])

            if self.current_piece is not None:
                for i in range(4):
                    for j in range(4):
                        p = i * 4 + j
                        if p in self.current_piece.image():
                            pygame.draw.rect(screen, colors[self.current_piece.color],
                                            [self.current_piece.x + self.zoom * (j + self.current_piece.x) + 1,
                                            self.current_piece.y + self.zoom * (i + self.current_piece.y) + 1,
                                            self.zoom - 2, self.zoom - 2])
            pygame.display.flip()
            clock.tick(5)
        return state, reward, done, {}



    def new_piece(self):
        return Figure(0, self.width // 2)

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.current_piece.image():
                    if i + self.current_piece.y > self.height - 1 or \
                            j + self.current_piece.x > self.width - 1 or \
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
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.board[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.board[i1][j] = self.board[i1 - 1][j]
        self.score += lines ** 2

    def is_game_over(self):
        for j in range(self.width):
            if self.board[0][j] > 0:
                self.score=0
                return True
        return False

    def calculate_reward(self):
        # Reward for clearing lines
        reward = self.score
        return reward

    def get_state(self):
        state = np.copy(self.board)
        if self.current_piece is not None:
            for i in range(4):
                for j in range(4):
                    if i * 4 + j in self.current_piece.image():
                        state[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.color
        return state
