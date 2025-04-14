"""
  Common code for Machine Learning methods

"""
import numpy as np
import time
import gymnasium as gym
from gymnasium import spaces
from algBSF import runBSF, show_frontiers
from Visibility import calc_vis
from common import calc_diameter, fibonacci_lattice, square_uniform, setupGraph, stepMove

# Environment setup for multi-level RL
class GuardEnv(gym.Env):
    def __init__(self, num_guards, guardHt, radius, bitmap, squareUniform=False, randomize=False, verbose=False):
        super(GuardEnv, self).__init__()

        self.num_guards = num_guards
        nrows, ncols = bitmap.shape
        self.grid_size = (nrows, ncols)
        self.squareUniform = squareUniform
        self.randomize = randomize
        self.verbose = verbose
        self.nFrontiers = 9999
        self.gGuards = None
        self.gComps = None
        self.gNorths = None
        self.gSouths = None

        self.reset()  # Can change num_guards

        self.state_dim = self.num_guards * 2  # x, y positions for each guard
        self.action_dim = self.num_guards * 8  # 8 actions: N, NE, E, SE, S, SW, W, NW
        self.guardHt = guardHt
        self.radius = radius
        self.bitmap = bitmap.copy()

        # Define action and observation space
        self.action_space = spaces.MultiDiscrete([8] * self.num_guards)
        self.observation_space = spaces.Box(low=0, high=max(self.grid_size), shape=(self.state_dim,), dtype=np.int32)
   

    def reset(self, seed=None, **kwargs):   
        """Reset environment to initial state."""
        super().reset(seed=seed)

        # Initialize guard positions
        if self.squareUniform:
            self.guard_positions = square_uniform(self.num_guards, self.grid_size[0], self.grid_size[1], self.randomize)
            self.num_guards = self.guard_positions.shape[0] # num_guards must be perfect square
        else:
            self.guard_positions = fibonacci_lattice(self.num_guards, self.grid_size[0], self.grid_size[1])
        if self.verbose:
            print(self.guard_positions)
        self.iteration = 0
        return self._get_obs(), {}

    def step(self, action):
        """Take actions and update environment."""
        for i, act in enumerate(action):
            # Up, Down, Left, Right, UL, DL, UR, DR
            
            pt = (self.guard_positions[i][0], self.guard_positions[i][1])
            bound = (self.grid_size[0], self.grid_size[1])
            self.guard_positions[i] = stepMove(pt, bound, act)
        
        # Set up G(V, E)
        self.gGuards, self.gComps, self.gNorths, self.gSouths = setupGraph(self.guard_positions, self.guardHt, self.radius, self.bitmap, self.verbose)

        reward, done = self._compute_reward()
        truncated = False
        return self._get_obs(), reward, done, truncated, {}

    def _get_obs(self):
        """Return current state as flattened positions."""
        return self.guard_positions.flatten()

    def _compute_reward(self):
        """Compute multi-level reward based on objectives."""
        visibility_reward = self._visibility_score()
        connectivity_reward = self._connectivity_score()
        coverage_reward = self._coverage_score()

        if self.verbose:
            print(f"Visibility reward = {visibility_reward:.4g}")
            print(f"Connectivity reward = {connectivity_reward:.4g}")
            print(f"Coverage reward = {coverage_reward:.4g}")

        # Weighted sum of the three levels
        total_reward = 0.4 * visibility_reward + 0.3 * connectivity_reward + 0.3 * coverage_reward
        done = False  # Continue until maximum steps
        return total_reward, done

    def _visibility_score(self):
        """Compute visibility reward."""
        # Score = sum of diameters of the connected components
        sum = 0
        for comp in self.gComps:
            sum += calc_diameter(comp.bitmap)
        return sum

    def _connectivity_score(self):
        """Compute connectivity reward."""
        # Build a connectivity graph based on guard positions
        # Score = total number of edges in G(V, E)
        #       = sum of comp.intersects / 2 (since each edge is owned by both comp)
        sum = 0
        for comp in self.gComps:
            sum += len(comp.intersects)
        return sum

    def _coverage_score(self):
        """Compute coverage reward."""
        # Score = - number of guards/frontiers
        self.nFrontiers = runBSF(self.gGuards, self.gComps, self.gNorths, self.gSouths, self.verbose)
        print(f"Iteration: {self.iteration}, Cost = {self.nFrontiers}", flush=True)
        self.iteration += 1
        return (-self.nFrontiers)

    def render(self):
        # Should only show frontiers when running single-threaded
        show_frontiers(self.grid_size[0], self.grid_size[1], self.bitmap, self.gGuards, self.gComps)


