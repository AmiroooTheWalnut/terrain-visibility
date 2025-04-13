import numpy as np
import argparse
from ReadElevImg import read_png, show_terrain
from algBSF import runBSF, show_frontiers
from mlCommon import GuardEnv
from common import fibonacci_lattice, square_uniform, setupGraph
from TerrainInput import gGuards, gComps, gNorths, gSouths
import pyswarms as ps
from pyswarms.backend.topology import Star, Ring, Random, VonNeumann, Pyramid
import time
import copy

nFrontiers = 9999
lastComps = []
lastGuards = []

#---------------------------------------
# Particle Swarm Optimization
# guard_positions is being passed as 1-D array
#---------------------------------------
def bsfScore(guard_positions):
    global nFrontiers, iteration, lastComps, lastGuards

    # Don't move the guards that were seeing North or South
    # We don't know if the guard will still see N/S even if the guard moves E/W, 
    # So we need to keep the guard at its last position (both x and y)
    if keepNS:
        if iteration > 0:
            for comp in lastComps:
                if comp.minX == 0 or comp.maxX == nrows-1:
                    id = comp.parentID
                    guard_positions[id] = (lastGuards[id].x, lastGuards[id].y)

    # Don't move the guards that had at least N (threshold) intersecting components
    if threshold != None:
        if iteration > 0:
            for comp in lastComps:
                if len(comp.intersects) >= threshold:
                    id = comp.parentID
                    guard_positions[id] = (lastGuards[id].x, lastGuards[id].y)

    setupGraph(guard_positions, guardHt, radius, bitmap, verbose)
    num = runBSF(gGuards, gComps, gNorths, gSouths, verbose)
    #num = runILP(gGuards, gComps, gNorths, gSouths, verbose)

    print(f"Iteration: {iteration}, Cost = {num}", flush=True)
    if num < nFrontiers:
        nFrontiers = num
        if enableShow:
            show_frontiers(nrows, ncols, bitmap, gGuards, gComps)

    #print(f"Number of Frontier = {num}")
    #print(guard_positions)

    iteration += 1

    lastComps.clear()
    lastComps = gComps.copy()
    lastGuards.clear()
    lastGuards = gGuards.copy()

    return nFrontiers  # Lower cost the better

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('--name', type=str, help="test.png")
    parser.add_argument('--numGuards', type=int, help="50")
    parser.add_argument('--radius', type=int, help="120")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    parser.add_argument('--show', action='store_true', help="Enable showing frontiers")
    parser.add_argument('--keepNS', action='store_true', help="Keep NS guard pos")
    parser.add_argument('--threshold', type=int, help="Connectivity threshold to keep guard pos")

    args = parser.parse_args()
    filename = args.name        # None if not provided
    radius = args.radius        # None if not provided
    numGuards = args.numGuards  # None if not provided
    verbose = args.verbose      # False if not provided
    enableShow = args.show      # False if not provided
    keepNS = args.keepNS        # None if not provided
    threshold = args.threshold   # None if not provided

    # ----------------
    # Other options
    # ----------------
    guardHt = 10     # Guard height above terrain
    squareUniform = True # False = Fibonacci Lattice guard initial positions
    randomize = True  # Randomize square uniform guard initial positions
    # ----------------

    start_time = time.time()   

    # Read bitmap
    bitmap = read_png(filename, verbose, enableShow)
    nrows, ncols = bitmap.shape

    # Initial guard positions determined by fibonacci lattice
    if squareUniform:
        guard_positions = square_uniform(numGuards, nrows, ncols, randomize)
        numGuards = guard_positions.shape[0] # numGuards must be perfect square
    else:
        guard_positions = fibonacci_lattice(numGuards, nrows, ncols)

    # Get a baseline
    iteration = 0
    bsfScore(guard_positions)

    # Define bounds for the guards to not exceed the bitmap
    num_dimensions = 2
    lb = np.array([0, 0])
    ub = np.array([nrows-1, ncols-1])
   
    # Two approaches:
    # Option 1: n_particles = numGuards, num_dimensions = 2     - Optimize individual position    
    # Option 2: n_particles = 1, num_dimensions = numGuards * 2 - Optimize entire set
    # Options:
    # c1 [0.5 to 2.5] = Cognitive parameter (high: more based on individual memory) 
    # c2 [0.5 to 2.5] = Social parameter (high: converge quickly)
    # w [0.4 to 1.2] = Inertia weight (high: explore more wider space)
    
    # Only for GeneralOptimizerPSO:
    # my_topology = Star()
    
    optimizer = ps.single.GlobalBestPSO(n_particles=numGuards, dimensions=num_dimensions,
                                        options={'c1': 1.2, 'c2': 0.3, 'w': 1.0},
                                        bounds=(lb, ub), init_pos=guard_positions.astype(float))

    #optimizer = ps.single.GeneralOptimizerPSO(n_particles=numGuards, dimensions=num_dimensions,
    #                                    options={'c1': 1.2, 'c2': 0.3, 'w': 1.0},
    #                                    bounds=(lb, ub), init_pos=guard_positions.astype(float),
    #                                    topology=my_topology)    

    cost, pos = optimizer.optimize(bsfScore, iters=100)
    #best_positions = pos.reshape((numGuards, 2))

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds")    


    

    