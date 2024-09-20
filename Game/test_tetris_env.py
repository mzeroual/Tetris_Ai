from stable_baselines3 import PPO
from tetris_env import TetrisEnv
import os
import time



# Create the environment
env = TetrisEnv(mode="human")

# Reset the environment
state = env.reset()

# Run the environment for a few steps
for _ in range(100):
    action = env.action_space.sample()  # Take a random action
    state, reward, done, info = env.step(action)

    time.sleep(0.1)  # Add a small delay to see the rendering


