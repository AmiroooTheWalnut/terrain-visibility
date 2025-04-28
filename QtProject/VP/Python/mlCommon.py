"""
  Common code for Machine Learning methods

"""
import numpy as np
import time
import gc
import gymnasium as gym
from gymnasium import spaces
from algBSF import runBSF
from ilpAlgGen import runILP
from Visibility import calc_vis
from common import calc_diameter, fibonacci_lattice, square_uniform, setupGraph, unwrapComp, vprint

lastSavedPos = []
lastSavedIds = []

# Environment setup for multi-level RL
class GuardEnv(gym.Env):
    def __init__(self, num_guards, guardHt, radius, elev, ilp=False, squareUniform=False, randomize=False, verbose=False, enableShow=False):
        super(GuardEnv, self).__init__()

        self.num_guards = num_guards
        nrows, ncols = elev.shape
        self.grid_size = (nrows, ncols)
        self.ilp = ilp
        self.squareUniform = squareUniform
        self.randomize = randomize
        self.verbose = verbose
        self.enableShow = enableShow
        self.cost = 9999
        self.gGuards = None
        self.gComps = None
        self.gNorths = None
        self.gSouths = None

        self.reset()  # Can change num_guards

        self.state_dim = self.num_guards * 2  # x, y positions for each guard
        self.action_dim = self.num_guards * 8  # 8 actions: N, NE, E, SE, S, SW, W, NW
        self.guardHt = guardHt
        self.radius = radius
        self.elev = elev.copy()  # Save a copy of the elevation bitmap

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
        vprint(self.verbose, self.guard_positions, flush=True)
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
        self.gGuards, self.gComps, self.gNorths, self.gSouths = setupGraph(self.guard_positions, self.guardHt, self.radius, self.elev, self.verbose)

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

        vprint(self.verbose, f"Visibility reward = {visibility_reward:.4g}", flush=True)
        vprint(self.verbose, f"Connectivity reward = {connectivity_reward:.4g}", flush=True)
        vprint(self.verbose, f"Coverage reward = {coverage_reward:.4g}", flush=True)

        # Weighted sum of the three levels
        total_reward = 0.4 * visibility_reward + 0.3 * connectivity_reward + 0.3 * coverage_reward
        done = False  # Continue until maximum steps
        return total_reward, done

    def _visibility_score(self):
        """Compute visibility reward."""
        # Score = sum of diameters of the connected components
        sum = 0
        for comp in self.gComps:
            bitmap = unwrapComp(comp)
            sum += calc_diameter(bitmap)
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
        if self.ilp:
            self.cost = runILP(self.elev, self.gGuards, self.gComps, self.gNorths, self.gSouths, self.verbose, self.enableShow)
        else:
            self.cost = runBSF(self.elev, self.gGuards, self.gComps, self.gNorths, self.gSouths, self.verbose, self.enableShow)

        print(f"Iteration: {self.iteration}, Cost = {self.cost}", flush=True)
        self.iteration += 1
        return (-self.cost)

    def render(self):
        # Should only show frontiers when running single-threaded
        return

#---------------------------------------
# Step to neighbor
# pt = (x, y)
# bound = (xmax, ymax)
#---------------------------------------
def stepMove(pt, bound, direction):
    assert(direction >= 0 and direction < 8), "Direction out of range"

    if direction == 0:  # North
        newpt = (pt[0], 
                 max(0           , pt[1] - 1))

    elif direction == 1:  # NorthEast
        newpt = (min(bound[0] - 1, pt[0] + 1), 
                 max(0           , pt[1] - 1))

    elif direction == 2:  # East
        newpt = (min(bound[0] - 1, pt[0] + 1),
                 pt[1])

    elif direction == 3:  # SouthEast
        newpt = (min(bound[0] - 1, pt[0] + 1),
                 min(bound[1] - 1, pt[1] + 1))

    elif direction == 4:  # South
        newpt = (pt[0], 
                 min(bound[1] - 1, pt[1] + 1))

    elif direction == 5:  # SouthWest
        newpt = (max(0           , pt[0] - 1),
                 min(bound[1] - 1, pt[1] + 1))

    elif direction == 6:  # West
        newpt = (max(0           , pt[0] - 1),
                 pt[1])

    elif direction == 7:  # NorthWest
        newpt = (max(0           , pt[0] - 1),
                 max(0           , pt[1] - 1))

    return newpt

#---------------------------------------
# Do not move guards that saw N/S but no longer
# Do not move a guard that was has connected components previously selected and 
# if moving it will break the "critical" connection.
#---------------------------------------
def best_move(guard_positions, ht, radius, elev, lastGuards, lastComps, verbose=False):

    nrows, ncols = elev.shape
    restored = []

    # Keep position if moving will leave N/S
    for guard in lastGuards:
        if guard.xmin == 0 or guard.xmax == ncols-1:
            id = guard.id
            print(f"Restoring guard {id} that previously crossed N/S", flush=True)
            guard_positions[id] = (guard.row, guard.col)
            restored.append(id)

    # Keep guard position if the connected component was selected last time
    for comp in lastComps:
        if comp.selected:
            id = comp.parentID
            if id not in restored:
                print(f"Restoring guard {id} with previously selected components", flush=True)
                guard_positions[id] = (guard.row, guard.col)
    
    return guard_positions                              
                 

#---------------------------------------
# Calculate visibility sum
# If keepNS, do not move the guards that reach N/S
#---------------------------------------
def visibilitySum(guard_positions, guardHt, radius, elev, diam=False, keepNS=False, verbose=False):
    global lastSavedPos, lastSavedIds

    # To be sure positions are integral as they are passed by the optimizer
    guard_positions=guard_positions.astype(int)

    if keepNS:
        savePos = lastSavedPos.copy() # Copy of all of last guard positions
        saveIds = lastSavedIds.copy() # List of IDs that reach N/S
        del lastSavedPos
        del lastSavedIds
        gc.collect
        lastSavedPos = []
        lastSavedIds = []

    visTotal = 0
    nrows, ncols = elev.shape
    id = 0

    for position in guard_positions:
        if keepNS:
            if id in saveIds: # Crossed N/S last time
                viewshed = calc_vis(position[0], position[1], guardHt, radius, elev, verbose)
                if np.sum(viewshed[0][:]) == 0 and np.sum(viewshed[ncols-1][:]) == 0: # Does not cross N/S this time
                    position = savePos[id] # Move back to the old position

        viewshed = calc_vis(position[0], position[1], guardHt, radius, elev, verbose)
        if diam:
            visTotal += calc_diameter(viewshed)
        else:
            visTotal += np.sum(viewshed)

        if keepNS:
            if np.sum(viewshed[0][:]) > 0 or np.sum(viewshed[ncols-1][:]) > 0:
                lastSavedIds.append(id)

        id += 1

    if keepNS:
        lastSavedPos = guard_positions.copy()

    return visTotal