import numpy as np
import argparse
from ReadElevImg import read_png
import time
from mlCommon import GuardEnv, fibonacci_lattice, square_uniform, setupGraph

# Alternative to use DQN instead of PPO
from stable_baselines3 import PPO

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
    print(f"Average Reward over {num_episodes} episodes: {avg_reward}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('--name', type=str, help="test.png")
    parser.add_argument('--numGuards', type=int, help="50")
    parser.add_argument('--radius', type=int, help="120")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    parser.add_argument('--show', action='store_true', help="Enable showing frontiers")

    args = parser.parse_args()
    filename = args.name        # None if not provided
    radius = args.radius        # None if not provided
    numGuards = args.numGuards  # None if not provided
    verbose = args.verbose      # False if not provided
    enableShow = args.show      # False if not provided

    elev = 10     # Default = 10

    start_time = time.time()   

    # Read bitmap
    bitmap = read_png(filename, verbose, enableShow)
    
    # Check environment before training
    env = GuardEnv(numGuards, elev, radius, bitmap, squareUniform=False, verbose=verbose)

    # Define PPO policy and model
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        gamma=0.99,
        n_steps=2048,
        batch_size=64,
        verbose=1,
        tensorboard_log="./guard_rl_logs/"
    )
  
    # Train PPO agent for 100,000 timesteps
    model.learn(total_timesteps=100000)

    # Save the trained model
    model.save("guard_ppo_model")

    # Test the trained model
    obs = env.reset()
    for i in range(100):
        action, _ = model.predict(obs)
        obs, reward, done, _ = env.step(action)
        env.render()  # Optional visualization

    # Evaluate the trained model
    evaluate_model(env, model)

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds")    


    