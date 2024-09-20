import gym
import time

# Register the environment
gym.envs.registration.register(
    id='Tetris-v0',
    entry_point='tetris_game:TetrisEnv',
)

# Create the environment
env = gym.make('Tetris-v0')

# Reset the environment
state = env.reset()

# Run the environment for a few steps
for _ in range(100):
    action = env.action_space.sample()  # Take a random action
    state, reward, done, info = env.step(action)
    env.render()
    time.sleep(0.1)  # Add a small delay to see the rendering

    if done:
        print("Game Over")
        break

env.close()