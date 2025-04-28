import numpy as np
import argparse
import sys
from ReadElevImg import read_png
import time
from mlCommon import GuardEnv
from common import fibonacci_lattice, square_uniform

# PPO - A policy-based method that directly learns a policy P(a|s), which
# maps states to probability distributions over actions.  PPO optimizes 
# the policy using gradient ascent.
from stable_baselines3 import PPO

# DQN - A value-based method that learns an action-value function Q(s, a) 
# to estimates the expected future reward for taking action a in state s.
# It uses neural network to approximate the function and select actions
# based on the highest Q-value.  
#from stable_baselines3 import DQN

from stable_baselines3.common.vec_env import DummyVecEnv

# ----------------------------------------------
# Evaluate model
# ----------------------------------------------
def evaluate_model(env, model, num_episodes=10):
    rewards = []
    for _ in range(num_episodes):
        obs = env.reset()
        total_reward = 0
        for _ in range(100):
            action, _ = model.predict(obs)
            obs, reward, done, _ = env.step(action)
            total_reward += reward
        rewards.append(total_reward)
    avg_reward = np.mean(rewards)
    print(f"Average Reward over {num_episodes} episodes: {avg_reward}", flush=True)


if __name__ == "__main__":
    sys.stdout = open('rlMainLog.txt', 'a')
    print("=============rlMain.py Run Start===============", flush=True)

    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('--name', type=str, help="test.png")
    parser.add_argument('--numGuards', type=int, help="50")
    parser.add_argument('--radius', type=int, help="120")
    parser.add_argument('--height', type=int, help="10")
    parser.add_argument('--ilp', action='store_true', help="Run ILP")
    parser.add_argument('--square', action='store_true', help="Square uniform")
    parser.add_argument('--randomize', action='store_true', help="Randomize Square Pos")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    parser.add_argument('--show', action='store_true', help="Enable showing frontiers")

    args = parser.parse_args()
    filename = args.name        # None if not provided
    radius = args.radius        # Default if not provided
    numGuards = args.numGuards  # Default if not provided
    guardHt = args.height       # Default if not provided
    ilp = args.ilp              # False if not provided
    squareUniform = args.square # False if not provided
    randomize = args.randomize  # False if not provided (Only applicable if squareUniform is true)
    verbose = args.verbose      # False if not provided
    enableShow = args.show      # False if not provided

    start_time = time.time()   

    # Read bitmap
    elev = read_png(filename, verbose, enableShow)
    
    # Check environment before training
    env = GuardEnv(numGuards, guardHt, radius, elev, ilp=ilp, squareUniform=squareUniform, randomize=randomize, verbose=verbose, enableShow=enableShow)
    DummyVecEnv([lambda: env])  # Make the environment single-threaded

    # Define PPO/DQN policy and model
    model = PPO(
        "MlpPolicy",
        env,
#        learning_rate=3e-4,
#        gamma=0.99,
#        n_steps=2048,
#        batch_size=64,
        verbose=1,
        tensorboard_log=None            # "./guard_rl_logs/"
    )
  
    # Train model
    model.learn(total_timesteps=100)

    # Test model
    obs = env.reset()
    for i in range(100):
        print(f"Test Iteration {i}", flush=True)
        action, _states = model.predict(obs)
        obs, reward, done, truncated, _ = env.step(action)
        env.render()  # Optional visualization

    # Evaluate the trained model
    evaluate_model(env, model)

    # Use tensorboard to see log
    # bash
    # tensorboard --logdir=./guard_rl_logs/

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds", flush=True)    


    
