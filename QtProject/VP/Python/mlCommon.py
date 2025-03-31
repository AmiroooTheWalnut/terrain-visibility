"""
  Common code for Machine Learning methods

"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from scipy.spatial import distance
from TerrainInput import classComp, classGuard, findIntersections, findConnected, printGuards, clearAll
from TerrainInput import gGuards, gComps, gNorths, gSouths
from ilpAlgGenBSF import runBSF
from Visibility import calc_vis

# Environment setup for multi-level RL
class GuardEnv(gym.Env):
    def __init__(self, num_guards, elev, radius, bitmap, squareUniform=False, verbose=False):
        super(GuardEnv, self).__init__()

        self.num_guards = num_guards
        nrows, ncols = bitmap.shape
        self.grid_size = (nrows, ncols)
        self.state_dim = self.num_guards * 2  # x, y positions for each guard
        self.action_dim = self.num_guards * 4  # 4 actions: up, down, left, right
        self.elev = elev
        self.radius = radius
        self.bitmap = bitmap.copy()
        self.squareUniform = squareUniform
        self.verbose = verbose

        # Define action and observation space
        self.action_space = spaces.MultiDiscrete([4] * self.num_guards)
        self.observation_space = spaces.Box(low=0, high=max(self.grid_size), shape=(self.state_dim,), dtype=np.int32)
   
        self.reset()

    def reset(self, seed=None, **kwargs):   
        """Reset environment to initial state."""
        super().reset(seed=seed)

        # Initialize guard positions
        if self.squareUniform:
            self.guard_positions = square_uniform(self.num_guards, self.grid_size[0], self.grid_size[1])
        else:
            self.guard_positions = fibonacci_lattice(self.num_guards, self.grid_size[0], self.grid_size[1])
        if self.verbose:
            print(self.guard_positions)
        return self._get_state(), {}

    def step(self, action):
        """Take actions and update environment."""
        for i, act in enumerate(action):
            if act == 0:  # Up
                self.guard_positions[i][1] = max(0, self.guard_positions[i][1] - 1)
            elif act == 1:  # Down
                self.guard_positions[i][1] = min(self.grid_size[1] - 1, self.guard_positions[i][1] + 1)
            elif act == 2:  # Left
                self.guard_positions[i][0] = max(0, self.guard_positions[i][0] - 1)
            elif act == 3:  # Right
                self.guard_positions[i][0] = min(self.grid_size[0] - 1, self.guard_positions[i][0] + 1)
        
        # Set up G(V, E)
        setupGraph(self.guard_positions, self.elev, self.radius, self.bitmap, self.verbose)

        reward, done = self._compute_reward()
        return self._get_state(), reward, done, {}

    def _get_state(self):
        """Return current state as flattened positions."""
        return self.guard_positions.flatten()

    def _compute_reward(self):
        """Compute multi-level reward based on objectives."""
        visibility_reward = self._visibility_score()
        connectivity_reward = self._connectivity_score()
        coverage_reward = self._coverage_score()

        # Weighted sum of the three levels
        total_reward = 0.5 * visibility_reward + 0.3 * connectivity_reward + 0.2 * coverage_reward
        done = False  # Continue until maximum steps
        return total_reward, done

    def _visibility_score(self):
        """Compute visibility reward."""
        # Score = sum of diameters of the connected components
        sum = 0
        for comp in gComps:
            sum += calc_diameter(comp.bitmap)
        return sum

    def _connectivity_score(self):
        """Compute connectivity reward."""
        # Build a connectivity graph based on guard positions
        # Score = total number of edges in G(V, E)
        #       = sum of comp.intersects / 2 (since each edge is owned by both comp)
        sum = 0
        for comp in gComps:
            sum += len(comp.intersects)
        return sum

    def _coverage_score(self):
        """Compute coverage reward."""
        # Score = - number of guards/frontiers
        return runBSF(gGuards, gComps, gNorths, gSouths, self.verbose)

# ========================================
# Find the diameter of a visibility region
# ========================================
def calc_diameter(npArray):
    y, x = np.where(npArray == 1)
    coords = np.column_stack((x, y))
    diameter = 0
    if len(coords) > 1:
        dist_matrix = distance.cdist(coords, coords, metric='euclidean')
        diameter = np.max(dist_matrix)
    return diameter

#---------------------------------------
# Function to generate Fibonacci lattice
#---------------------------------------
def fibonacci_lattice(n_points, nrows, ncols):
    gR = (1.0 + np.sqrt(5.0)) / 2.0

    points = []
    for count in range(n_points):
        x = float(count+1) / gR
        x -= int(x)
        y = float(count+1) / (n_points+1)
        points.append((int(x*nrows), int(y*ncols)))
    
    return np.array(points)

#---------------------------------------
# Function to generate guard positions in square uniform
#---------------------------------------
def square_uniform(n_points, nrows, ncols):
    global numGuards
    
    nGRows = max(1.0, np.sqrt(float(n_points)*float(nrows)/float(ncols)))
    nGCols = max(1.0, np.sqrt(float(n_points)*float(ncols)/float(nrows)))
    nRowGuardPixels = np.floor(max(1.0, float(ncols)/(nGCols+1.0)))
    nColGuardPixels = np.floor(max(1.0, float(nrows)/(nGRows+1.0)))

    points = []
    for i in range(int(nGRows)):
        for j in range(int(nGCols)):
            points.append(((i+1)*int(nRowGuardPixels), (j+1)*int(nColGuardPixels)))

    # Update numGuards based on how many points it ends up
    numGuards = len(points)

    return np.array(points)

#---------------------------------------
# Set up G(V, E)
# Visibility, guard/connected component information
#---------------------------------------
def setupGraph(guard_positions, elev, radius, bitmap, verbose=False):
    
    if verbose:
        start_time = time.time()

    clearAll()
    for guardnum in range(len(guard_positions)):
        guard = classGuard(guardnum)
        gGuards.append(guard)
        guard.setLocation(guard_positions[guardnum][0], guard_positions[guardnum][1], elev, radius)
        viewshed = calc_vis(guard, bitmap, verbose)
        findConnected(guard, viewshed, verbose)

    findIntersections(verbose)
    printGuards(verbose)

    if verbose:
        end_time = time.time()
        print(f"Time to set up guard/connected components = {end_time - start_time:.2g} seconds")
