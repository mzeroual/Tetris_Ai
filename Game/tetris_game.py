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

    def step(self, action,mode="human"):
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
        if mode=="human":
            
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

# Register the environment
gym.envs.registration.register(
    id='Tetris-v0',
    entry_point='tetris_game:TetrisEnv',
)



# Initialize the game engine
pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

size = (400, 500)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Tetris")

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()
fps = 25
game = Tetris(20, 10)
counter = 0

pressing_down = False

while not done:
    if game.figure is None:
        game.new_figure()
    counter += 1
    if counter > 100000:
        counter = 0

    if counter % (fps // game.level // 2) == 0 or pressing_down:
        if game.state == "start":
            game.go_down()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.rotate()
            if event.key == pygame.K_DOWN:
                pressing_down = True
            if event.key == pygame.K_LEFT:
                game.go_side(-1)
            if event.key == pygame.K_RIGHT:
                game.go_side(1)
            if event.key == pygame.K_SPACE:
                game.go_space()
            if event.key == pygame.K_ESCAPE:
                game.__init__(20, 10)

    if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False

    screen.fill(WHITE)

    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
            if game.field[i][j] > 0:
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                 [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(screen, colors[game.figure.color],
                                     [game.x + game.zoom * (j + game.figure.x) + 1,
                                      game.y + game.zoom * (i + game.figure.y) + 1,
                                      game.zoom - 2, game.zoom - 2])

    font = pygame.font.SysFont('Calibri', 25, True, False)
    font1 = pygame.font.SysFont('Calibri', 65, True, False)
    text = font.render("Score: " + str(game.score), True, BLACK)
    text_game_over = font1.render("Game Over", True, (255, 125, 0))
    text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

    screen.blit(text, [0, 0])
    if game.state == "gameover":
        screen.blit(text_game_over, [20, 200])
        screen.blit(text_game_over1, [25, 265])

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()