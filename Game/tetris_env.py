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
        self.width = 10
        self.height = 20
        self.block_size = 30
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.current_piece = None
        self.current_piece_position = [0, 0]
        
        # Define action and observation space
        self.action_space = spaces.Discrete(4)  # 0: left, 1: right, 2: down, 3: rotate
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.height, self.width), dtype=np.int)

        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.block_size, self.height * self.block_size))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        
    def reset(self):
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.current_piece = self.new_piece()
        self.current_piece_position = [0, self.width // 2]
        return self.board

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines ** 2

    def step(self, action):
        # Apply action
        if action == 0:  # Move left
            old_x = self.current_piece_position[1]
            self.current_piece_position[1] -= 1
            if self.intersects():
                self.current_piece_position[1]=old_x
        elif action == 1:  # Move right
            old_x = self.current_piece_position[1]
            self.current_piece_position[1] += 1
            if self.intersects():
                self.current_piece_position[1]=old_x
        elif action == 2:  # Move down
            self.current_piece_position[0] += 1
        elif action == 3:  # Rotate
            self.current_piece = self.rotate_piece(self.current_piece)
        
        # Check for game over
        done = self.is_game_over()
        
        # Calculate reward
        reward = self.calculate_reward()
        
        # Get new state
        state = self.board
        
        return state, reward, done, {}

    def render(self, mode='human'):
        if mode == 'human':
            self.screen.fill((0, 0, 0))  # Fill the screen with black
            # Draw the board
            for y in range(self.height):
                for x in range(self.width):
                    rect = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
                    pygame.draw.rect(self.screen, colors[self.board[y][x]], rect, 0)

            # Draw the current piece
            for i in self.current_piece[0]:
                x = i % 4
                y = i // 4
                x_pos = self.current_piece_position[1] + x
                y_pos = self.current_piece_position[0] + y
                if 0 <= y_pos < self.height and 0 <= x_pos < self.width:
                    rect = pygame.Rect(x_pos * self.block_size, y_pos * self.block_size, self.block_size, self.block_size)
                    pygame.draw.rect(self.screen, colors[1], rect, 0)

            pygame.display.flip()
            self.clock.tick(10)  # Limit to 10 frames per second

    def new_piece(self):
        return random.choice(Figure.figures)

    def rotate_piece(self, piece):
        return piece[1:] + piece[:1]

    def is_game_over(self):
        # Implement game over logic
        return False

    def calculate_reward(self):
        # Implement reward calculation logic
        return 0

# Register the environment
gym.envs.registration.register(
    id='Tetris-v0',
    entry_point='__main__:TetrisEnv',
)