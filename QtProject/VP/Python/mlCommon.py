"""
  Common code for Machine Learning methods

"""
import numpy as np
import time
import gymnasium as gym
from gymnasium import spaces
from scipy.spatial import distance
from TerrainInput import classComp, classGuard, findIntersections, findConnected, printGuards, clearAll
from TerrainInput import gGuards, gComps, gNorths, gSouths
from ilpAlgGenBSF import runBSF, show_frontiers
from Visibility import calc_vis

# Environment setup for multi-level RL
class GuardEnv(gym.Env):
    def __init__(self, num_guards, elev, radius, bitmap, squareUniform=False, verbose=False):
        super(GuardEnv, self).__init__()

        self.num_guards = num_guards
        nrows, ncols = bitmap.shape
        self.grid_size = (nrows, ncols)
        self.squareUniform = squareUniform
        self.verbose = verbose
        self.nFrontiers = 9999

        self.reset()  # Can change num_guards

        self.state_dim = self.num_guards * 2  # x, y positions for each guard
        self.action_dim = self.num_guards * 8  # 8 actions: Up, Down, Left, Right, UL, UR, DL, DR
        self.elev = elev
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
            self.guard_positions = square_uniform(self.num_guards, self.grid_size[0], self.grid_size[1])
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
            x = self.guard_positions[i][0]
            y = self.guard_positions[i][1]
            xmax = self.grid_size[0]
            ymax = self.grid_size[1]
            if act == 0:  # Up
                self.guard_positions[i][1] = max(0, y - 1)
            elif act == 1:  # Down
                self.guard_positions[i][1] = min(ymax - 1, y + 1)
            elif act == 2:  # Left
                self.guard_positions[i][0] = max(0, x - 1)
            elif act == 3:  # Right
                self.guard_positions[i][0] = min(xmax - 1, x + 1)
            elif act == 0:  # UL
                self.guard_positions[i][1] = max(0, y - 1)
                self.guard_positions[i][0] = max(0, x - 1)
            elif act == 1:  # DL
                self.guard_positions[i][1] = min(ymax - 1, y + 1)
                self.guard_positions[i][0] = max(0, x - 1)
            elif act == 2:  # UR
                self.guard_positions[i][1] = max(0, y - 1)
                self.guard_positions[i][0] = min(xmax - 1, x + 1)
            elif act == 3:  # DR
                self.guard_positions[i][1] = min(ymax - 1, y + 1)
                self.guard_positions[i][0] = min(xmax - 1, x + 1)
        
        # Set up G(V, E)
        setupGraph(self.guard_positions, self.elev, self.radius, self.bitmap, self.verbose)

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
        self.nFrontiers = runBSF(gGuards, gComps, gNorths, gSouths, self.verbose)
        print(f"Iteration: {self.iteration}, Cost = {self.nFrontiers}", flush=True)
        self.iteration += 1
        return (-self.nFrontiers)

    def render(self):
        show_frontiers(self.grid_size[0], self.grid_size[1], self.bitmap, gGuards, gComps)

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
# randomize=set the guard positions randomly inside their cell
#---------------------------------------
def square_uniform(n_points, nrows, ncols, randomize=True):
    
    #np.random.seed(42) # Set the seed so we can repeat the results
    xoff = 1.0
    yoff = 1.0

    nGRows = max(1.0, np.sqrt(float(n_points)*float(nrows)/float(ncols)))
    nGCols = max(1.0, np.sqrt(float(n_points)*float(ncols)/float(nrows)))
    nRowGuardPixels = np.floor(max(1.0, float(ncols)/(nGCols+1.0)))
    nColGuardPixels = np.floor(max(1.0, float(nrows)/(nGRows+1.0)))

    points = []
    for i in range(int(nGRows)):
        for j in range(int(nGCols)):
            if randomize:
                xoff = np.random.rand()
                yoff = np.random.rand()
            x = min(max(int((float(i)+xoff)*nRowGuardPixels), 0), nrows-1) # Make sure in range
            y = min(max(int((float(j)+yoff)*nColGuardPixels), 0), ncols-1) # Make sure in range
            points.append((x,y))

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
