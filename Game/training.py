from stable_baselines3 import PPO
from tetris_env import TetrisEnv
import os
import time


# Create the environment
env = TetrisEnv(mode="human")

models_dir="models/PPO"
logdir="logs"
if not os.path.exists(models_dir):
    os.makedirs(models_dir)
    
if not os.path.exists(logdir):
    os.makedirs(logdir)

time_steps=10000
model = PPO('MlpPolicy', env, verbose=1,learning_rate =1e-3,tensorboard_log=logdir)
for i in range (1,100):
    model.learn(total_timesteps=time_steps, reset_num_timesteps=False, tb_log_name="PPO")
    model.save(f"{models_dir}/{time_steps*i}")
    env.close()